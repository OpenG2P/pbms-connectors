"""DB and DCI computations shared by every register.

A register subclasses both with its summaries mixin and sets class attributes:

    RegistryDB:  model, payload
    RegistryDCI: payload, reg_type, reg_record_type, match_field, fields, flat()
"""

from datetime import date
from types import SimpleNamespace
from typing import Optional

from openg2p_bg_task_models.schemas import BeneficiarySearchResponsePayload

from ..interface import RegistryInterface
from . import _transport
from ._dci_records import age_from_birth_date


def to_payload(payload_cls, row):
    """Copy the payload's fields from a DB row or a DCI row."""
    values = {name: getattr(row, name, None) for name in payload_cls.model_fields}
    values["internal_record_id"] = str(row.internal_record_id)
    for name, value in values.items():
        if isinstance(value, date):
            values[name] = value.isoformat()
    if "estimated_age" in values and values["estimated_age"] is None:
        values["estimated_age"] = age_from_birth_date(getattr(row, "birth_date", None))
    return payload_cls(**values)


def _search_response(rows, total, page, page_size):
    return (
        BeneficiarySearchResponsePayload(
            beneficiary_count=total,
            page=page,
            page_size=page_size,
            beneficiaries=rows,
        ),
        total,
    )


class RegistryDB(RegistryInterface):
    """Eligibility, entitlement, and search against the registry database."""

    model = None
    payload = None

    def registrant_id_of(self, row) -> str:
        return str(row.internal_record_id)

    def fetch_by_ids(self, registrant_ids: list[str]):
        return _transport.fetch_db(self.connection, self.model, registrant_ids)

    def iter_eligible_ids(self, rules, batch_size: int):
        return _transport.iter_eligible_db(
            self.connection, self.model, rules, batch_size
        )

    def iter_priority_ids(
        self, priority_domains, enrolled_ids, fallback_rules, batch_size
    ):
        return _transport.iter_priority_db(
            self.connection,
            self.model,
            priority_domains,
            enrolled_ids,
            fallback_rules,
            batch_size,
        )

    def entitlement_multipliers(
        self,
        registrant_ids: list[str],
        pbms_domain: str,
        multiplier_field: Optional[str] = None,
    ) -> dict[str, float]:
        return _transport.multipliers_db(
            self.connection, self.model, registrant_ids, pbms_domain, multiplier_field
        )

    async def search_beneficiaries(
        self,
        bg_task_session,
        beneficiary_list_id: str,
        target_registry: str,
        search_domain: Optional[str],
        page: int = 1,
        page_size: int = 10,
        order_by: str = "internal_record_id asc",
    ):
        rows, total = await _transport.search_db(
            self.connection,
            self.model,
            bg_task_session,
            beneficiary_list_id,
            search_domain,
            page,
            page_size,
            order_by,
            lambda row: to_payload(self.payload, row),
        )
        return _search_response(rows, total, page, page_size)


class RegistryDCI(RegistryInterface):
    """Eligibility, entitlement, and search via the register's DCI search URL.

    ``flat(record)`` maps a DCI reg_record onto the register's column names and
    must include ``match_field``, the id the Partner API filters on. ``fields``
    are the columns the Partner API can filter on.
    """

    payload = None
    reg_type = ""
    reg_record_type = ""
    match_field = ""
    fields: set[str] = set()

    @staticmethod
    def flat(record: dict) -> dict:
        raise NotImplementedError

    def registrant_id_of(self, row) -> str:
        return str(row.internal_record_id)

    def _id(self, record: dict) -> str:
        return self.flat(record)[self.match_field] or ""

    def _row(self, record: dict):
        row = self.flat(record)
        row["internal_record_id"] = row[self.match_field]
        return SimpleNamespace(**row)

    def fetch_by_ids(self, registrant_ids: list[str]):
        return _transport.fetch_dci(
            self.connection,
            registrant_ids,
            self.fields,
            self.match_field,
            self._id,
            self._row,
        )

    def iter_eligible_ids(self, rules, batch_size: int):
        return _transport.iter_eligible_dci(
            self.connection,
            rules,
            batch_size,
            self.fields,
            self.match_field,
            self._id,
        )

    def iter_priority_ids(
        self, priority_domains, enrolled_ids, fallback_rules, batch_size
    ):
        return _transport.iter_priority_dci(
            self.connection,
            priority_domains,
            enrolled_ids,
            fallback_rules,
            batch_size,
            self.fields,
            self.match_field,
            self._id,
        )

    def entitlement_multipliers(
        self,
        registrant_ids: list[str],
        pbms_domain: str,
        multiplier_field: Optional[str] = None,
    ) -> dict[str, float]:
        return _transport.multipliers_dci(
            self.connection,
            registrant_ids,
            pbms_domain,
            multiplier_field,
            self.fields,
            self.match_field,
            self._id,
            self.flat,
        )

    async def search_beneficiaries(
        self,
        bg_task_session,
        beneficiary_list_id: str,
        target_registry: str,
        search_domain: Optional[str],
        page: int = 1,
        page_size: int = 10,
        order_by: str = "internal_record_id asc",
    ):
        registrant_ids = await _transport._beneficiary_ids(
            bg_task_session, beneficiary_list_id
        )
        rows, total = _transport.search_dci(
            self.connection,
            registrant_ids,
            search_domain,
            page,
            page_size,
            self.fields,
            self.match_field,
            self._id,
            lambda record: to_payload(self.payload, self._row(record)),
        )
        return _search_response(rows, total, page, page_size)
