"""Partner API client for POST /dci/sync/search."""

import json
import ssl
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import RegistryAdapterSettings


class DciError(RuntimeError):
    pass


def search(
    expression: dict,
    reg_type: str,
    reg_record_type: str,
    page: int = 1,
    page_size: int = 200,
) -> tuple[list[dict], int]:
    settings = RegistryAdapterSettings.get_config()
    body = _envelope(expression, reg_type, reg_record_type, page, page_size)
    url = settings.partner_api_url.rstrip("/") + "/dci/sync/search"
    request = Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    context = (
        None if settings.partner_api_ssl_verify else ssl._create_unverified_context()
    )
    try:
        with urlopen(
            request,
            timeout=settings.partner_api_timeout,
            context=context,
        ) as response:
            payload = json.loads(response.read().decode())
    except HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise DciError(f"DCI search failed ({exc.code}): {detail}") from exc
    except URLError as exc:
        raise DciError(f"DCI search failed: {exc.reason}") from exc
    return _records(payload)


def _envelope(expression, reg_type, reg_record_type, page, page_size) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    reference_id = uuid.uuid4().hex[:20]
    return {
        "signature": "",
        "header": {
            "version": "1.0.0",
            "message_id": uuid.uuid4().hex,
            "message_ts": now,
            "action": "search",
            "sender_id": "pbms",
            "receiver_id": "registry",
            "total_count": 1,
        },
        "message": {
            "transaction_id": uuid.uuid4().hex[:20],
            "search_request": [
                {
                    "reference_id": reference_id,
                    "timestamp": now,
                    "locale": "eng",
                    "search_criteria": {
                        "version": "1.0.0",
                        "reg_type": reg_type,
                        "reg_record_type": reg_record_type,
                        "query_type": "expression",
                        "query": {
                            "type": "expression",
                            "value": {"expression": {"query": expression}},
                        },
                        "pagination": {
                            "page_size": page_size,
                            "page_number": page,
                        },
                    },
                }
            ],
        },
    }


def _records(payload: dict) -> tuple[list[dict], int]:
    message = payload.get("message") or {}
    items = message.get("search_response") or []
    if not items:
        return [], 0
    item = items[0]
    status = str(item.get("status") or "").lower()
    if status in {"rjct", "rejected"}:
        reason = item.get("status_reason_message") or item.get("status")
        raise DciError(f"DCI search rejected: {reason}")
    data = item.get("data") or {}
    records = []
    for record in data.get("reg_records") or []:
        if isinstance(record, str):
            record = json.loads(record)
        if isinstance(record, dict):
            records.append(record)
    pagination = item.get("pagination") or {}
    total = pagination.get("total_count")
    if total is None:
        total = len(records)
    return records, int(total)


def identifier_value(record: dict, *paths: tuple[str, ...]) -> str:
    for path in paths:
        value = _dig(record, path)
        if value:
            return str(value)
    return ""


def _dig(record: Any, path: tuple[str, ...]) -> Any:
    current = record
    for key in path:
        if isinstance(current, list):
            current = current[0] if current else None
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    if isinstance(current, list):
        current = current[0] if current else None
    if isinstance(current, dict):
        return current.get("identifier_value") or current.get("value")
    return current
