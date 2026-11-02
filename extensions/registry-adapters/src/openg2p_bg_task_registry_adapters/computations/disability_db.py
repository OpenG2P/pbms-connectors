from typing import Optional

from openg2p_bg_task_models.schemas import BeneficiarySearchResponsePayload

from ..interface import RegistryInterface
from ..models import G2PDisabilityRegistry
from ..schema import G2PDisabilityRegistryPayload
from . import _transport
from ._dci_records import age_from_birth_date
from ._summary import DisabilitySummaries


class DisabilityDB(DisabilitySummaries, RegistryInterface):
    """Disability eligibility, entitlement, and search against the registry database."""

    def registrant_id_of(self, person) -> str:
        return str(person.internal_record_id)

    def fetch_by_ids(self, registrant_ids: list[str]):
        return _transport.fetch_db(G2PDisabilityRegistry, registrant_ids)

    def iter_eligible_ids(self, rules, batch_size: int):
        return _transport.iter_eligible_db(G2PDisabilityRegistry, rules, batch_size)

    def iter_priority_ids(
        self, priority_domains, enrolled_ids, fallback_rules, batch_size
    ):
        return _transport.iter_priority_db(
            G2PDisabilityRegistry,
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
            G2PDisabilityRegistry, registrant_ids, pbms_domain, multiplier_field
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
            G2PDisabilityRegistry,
            bg_task_session,
            beneficiary_list_id,
            search_domain,
            page,
            page_size,
            order_by,
            _disability_payload,
        )
        return (
            BeneficiarySearchResponsePayload(
                beneficiary_count=total,
                page=page,
                page_size=page_size,
                beneficiaries=rows,
            ),
            total,
        )


def _disability_payload(person) -> G2PDisabilityRegistryPayload:
    estimated_age = person.estimated_age
    if estimated_age is None:
        estimated_age = age_from_birth_date(person.birth_date)
    return G2PDisabilityRegistryPayload(
        internal_record_id=str(person.internal_record_id),
        functional_record_id=person.functional_record_id,
        first_name=person.first_name,
        last_name=person.last_name,
        gender=person.gender,
        birth_date=person.birth_date.isoformat() if person.birth_date else None,
        estimated_age=estimated_age,
        disability_status=person.disability_status,
        disability_status_level=person.disability_status_level,
        support_needs_level=person.support_needs_level,
        unmet_support_needs_count=person.unmet_support_needs_count,
        has_unmet_support_need=person.has_unmet_support_need,
        employment_status=person.employment_status,
        housing_type=person.housing_type,
        country_code=person.country_code,
    )
