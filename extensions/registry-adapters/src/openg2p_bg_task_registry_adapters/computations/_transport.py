"""Shared DB and DCI transport used by the four computation classes."""

from typing import Callable, Iterator, Optional

from openg2p_bg_task_models.models import BeneficiaryListDetails
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select as async_select

from .. import dci
from ..domain import dci_expression, sqlalchemy_clause
from ..engine import async_session, sync_session

_PAGE = 500


def iter_eligible_db(
    model, rules: list[tuple[str, str]], batch_size: int
) -> Iterator[list[str]]:
    statement = _combine_db(model, rules, allowed=None)
    if statement is None:
        return
    yield from _stream(statement, batch_size)


def iter_priority_db(
    model,
    priority_domains: list[str],
    enrolled_ids: list[str],
    fallback_rules: list[tuple[str, str]],
    batch_size: int,
) -> Iterator[list[str]]:
    id_column = model.internal_record_id
    if priority_domains:
        if not enrolled_ids:
            return
        rules = [(domain, "INTERSECT") for domain in priority_domains]
        combined = _combine_db(model, rules, allowed=None)
        enrolled = select(id_column).where(
            id_column.in_([str(item) for item in enrolled_ids])
        )
        statement = combined.intersect(enrolled) if combined is not None else enrolled
    else:
        statement = _combine_db(model, fallback_rules, allowed=None)
    if statement is None:
        return
    yield from _stream(statement, batch_size)


def multipliers_db(
    model,
    registrant_ids: list[str],
    pbms_domain: str,
    multiplier_field: Optional[str],
    allowed: Optional[set[str]] = None,
) -> dict[str, float]:
    if not registrant_ids:
        return {}
    id_column = model.internal_record_id
    use_field = multiplier_field and multiplier_field != "none"
    if use_field and allowed is not None and multiplier_field not in allowed:
        raise ValueError(
            f"Field '{multiplier_field}' is not part of the DCI spec and cannot be "
            "used with the DCI connector."
        )
    columns = [id_column]
    if use_field:
        columns.append(getattr(model, multiplier_field))
    statement = select(*columns).where(
        id_column.in_([str(item) for item in registrant_ids])
    )
    clause = sqlalchemy_clause(pbms_domain, model, allowed)
    if clause is not None:
        statement = statement.where(clause)
    found: dict[str, float] = {}
    with sync_session() as session:
        for row in session.execute(statement):
            registrant_id = str(row[0])
            if not use_field or row[1] is None:
                found[registrant_id] = 1.0
            else:
                found[registrant_id] = float(row[1])
    return found


async def search_db(
    model,
    bg_task_session: AsyncSession,
    beneficiary_list_id: str,
    search_domain: Optional[str],
    page: int,
    page_size: int,
    order_by: str,
    to_payload: Callable,
):
    registrant_ids = await _beneficiary_ids(bg_task_session, beneficiary_list_id)
    if not registrant_ids:
        return [], 0
    id_column = model.internal_record_id
    statement = select(model).where(id_column.in_(registrant_ids))
    clause = sqlalchemy_clause(search_domain, model, None) if search_domain else None
    if clause is not None:
        statement = statement.where(clause)
    field_name, descending = _order(order_by)
    column = getattr(model, field_name, id_column)
    statement = statement.order_by(column.desc() if descending else column.asc())
    async with async_session() as session:
        count = await session.scalar(
            select(func.count()).select_from(statement.subquery())
        )
        rows = (
            await session.scalars(
                statement.offset(page_size * (page - 1)).limit(page_size)
            )
        ).all()
    return [to_payload(row) for row in rows], int(count or 0)


def fetch_db(model, registrant_ids: list[str]):
    if not registrant_ids:
        return []
    with sync_session() as session:
        rows = session.query(model).filter(
            model.internal_record_id.in_([str(item) for item in registrant_ids])
        )
        return list(rows.yield_per(500))


def iter_eligible_dci(
    rules: list[tuple[str, str]],
    batch_size: int,
    allowed: set[str],
    match_all_field: str,
    reg_type: str,
    reg_record_type: str,
    id_of: Callable[[dict], str],
) -> Iterator[list[str]]:
    ids = _combine_dci(
        rules, allowed, match_all_field, reg_type, reg_record_type, id_of
    )
    yield from _batches(ids, batch_size)


def iter_priority_dci(
    priority_domains: list[str],
    enrolled_ids: list[str],
    fallback_rules: list[tuple[str, str]],
    batch_size: int,
    allowed: set[str],
    match_all_field: str,
    reg_type: str,
    reg_record_type: str,
    id_of: Callable[[dict], str],
) -> Iterator[list[str]]:
    if priority_domains:
        rules = [(domain, "INTERSECT") for domain in priority_domains]
        ids = _combine_dci(
            rules, allowed, match_all_field, reg_type, reg_record_type, id_of
        )
        enrolled = {str(item) for item in enrolled_ids}
        ids = [item for item in ids if item in enrolled]
    else:
        ids = _combine_dci(
            fallback_rules, allowed, match_all_field, reg_type, reg_record_type, id_of
        )
    yield from _batches(ids, batch_size)


def multipliers_dci(
    registrant_ids: list[str],
    pbms_domain: str,
    multiplier_field: Optional[str],
    allowed: set[str],
    match_all_field: str,
    reg_type: str,
    reg_record_type: str,
    id_of: Callable[[dict], str],
    flat_of: Callable[[dict], dict],
) -> dict[str, float]:
    if not registrant_ids:
        return {}
    use_field = multiplier_field and multiplier_field != "none"
    if use_field and multiplier_field not in allowed:
        raise ValueError(
            f"Field '{multiplier_field}' is not part of the DCI spec and cannot be "
            "used with the DCI connector."
        )
    wanted = {str(item) for item in registrant_ids}
    expression = dci_expression(pbms_domain, allowed, match_all_field)
    expression = {"$and": [expression, {match_all_field: {"$in": list(wanted)}}]}
    found: dict[str, float] = {}
    for record in _pages(expression, reg_type, reg_record_type):
        registrant_id = id_of(record)
        if registrant_id not in wanted:
            continue
        if not use_field:
            found[registrant_id] = 1.0
            continue
        value = flat_of(record).get(multiplier_field)
        found[registrant_id] = 1.0 if value in (None, "") else float(value)
    return found


def fetch_dci(
    registrant_ids: list[str],
    allowed: set[str],
    match_all_field: str,
    reg_type: str,
    reg_record_type: str,
    id_of: Callable[[dict], str],
    to_row: Callable[[dict], object],
):
    if not registrant_ids:
        return []
    wanted = [str(item) for item in registrant_ids]
    expression = {match_all_field: {"$in": wanted}}
    rows = []
    for record in _pages(expression, reg_type, reg_record_type):
        if id_of(record) in set(wanted):
            rows.append(to_row(record))
    return rows


def search_dci(
    registrant_ids: list[str],
    search_domain: Optional[str],
    page: int,
    page_size: int,
    allowed: set[str],
    match_all_field: str,
    reg_type: str,
    reg_record_type: str,
    id_of: Callable[[dict], str],
    to_payload: Callable,
):
    if not registrant_ids:
        return [], 0
    parts = [{match_all_field: {"$in": registrant_ids}}]
    if search_domain and search_domain.strip() and search_domain.strip() != "[]":
        parts.append(dci_expression(search_domain, allowed, match_all_field))
    expression = parts[0] if len(parts) == 1 else {"$and": parts}
    records, total = dci.search(expression, reg_type, reg_record_type, page, page_size)
    return [to_payload(record) for record in records if id_of(record)], total


def _combine_db(model, rules, allowed):
    statement = None
    id_column = model.internal_record_id
    for domain, operator in rules:
        part = select(id_column)
        clause = sqlalchemy_clause(domain, model, allowed)
        if clause is not None:
            part = part.where(clause)
        if statement is None:
            statement = part
            continue
        op = (operator or "UNION").upper()
        if op == "INTERSECT":
            statement = statement.intersect(part)
        elif op == "EXCEPT":
            statement = statement.except_(part)
        else:
            statement = statement.union(part)
    return statement


def _stream(statement, batch_size: int) -> Iterator[list[str]]:
    with sync_session() as session:
        result = session.execute(statement)
        while True:
            rows = result.fetchmany(batch_size)
            if not rows:
                break
            yield [str(row[0]) for row in rows if row[0] is not None]


def _combine_dci(
    rules, allowed, match_all_field, reg_type, reg_record_type, id_of
) -> list[str]:
    combined: Optional[set[str]] = None
    for domain, operator in rules:
        expression = dci_expression(domain, allowed, match_all_field)
        found = {
            id_of(record)
            for record in _pages(expression, reg_type, reg_record_type)
            if id_of(record)
        }
        if combined is None:
            combined = found
            continue
        op = (operator or "UNION").upper()
        if op == "INTERSECT":
            combined &= found
        elif op == "EXCEPT":
            combined -= found
        else:
            combined |= found
    return sorted(combined or [])


def _pages(expression, reg_type, reg_record_type):
    page = 1
    seen = 0
    while True:
        records, total = dci.search(expression, reg_type, reg_record_type, page, _PAGE)
        if not records:
            break
        yield from records
        seen += len(records)
        if seen >= total:
            break
        page += 1


def _batches(ids: list[str], batch_size: int) -> Iterator[list[str]]:
    for start in range(0, len(ids), batch_size):
        yield ids[start : start + batch_size]


async def _beneficiary_ids(
    bg_task_session: AsyncSession, beneficiary_list_id: str
) -> list[str]:
    result = await bg_task_session.execute(
        async_select(BeneficiaryListDetails.registrant_details).where(
            BeneficiaryListDetails.beneficiary_list_id == beneficiary_list_id
        )
    )
    ids = []
    for registrant_details in result.scalars().all():
        for registrant in registrant_details or []:
            registrant_id = registrant.get("registrant_id")
            if registrant_id is not None:
                ids.append(str(registrant_id))
    return ids


def _order(order_by: str) -> tuple[str, bool]:
    parts = (order_by or "internal_record_id asc").split()
    field_name = parts[0] if parts else "internal_record_id"
    descending = len(parts) > 1 and parts[1].lower() == "desc"
    return field_name, descending
