from typing import Optional

from openg2p_bg_task_models.schemas import BeneficiarySearchResponsePayload

from ..interface import RegistryInterface
from ..models import G2PFarmerRegistry
from ..schema import G2PFarmerRegistryPayload
from . import _transport
from ._summary import FarmerSummaries


class FarmerDB(FarmerSummaries, RegistryInterface):
    """Farmer eligibility, entitlement, and search against the registry database."""

    def registrant_id_of(self, farmer) -> str:
        return str(farmer.internal_record_id)

    def fetch_by_ids(self, registrant_ids: list[str]):
        return _transport.fetch_db(G2PFarmerRegistry, registrant_ids)

    def iter_eligible_ids(self, rules, batch_size: int):
        return _transport.iter_eligible_db(G2PFarmerRegistry, rules, batch_size)

    def iter_priority_ids(
        self, priority_domains, enrolled_ids, fallback_rules, batch_size
    ):
        return _transport.iter_priority_db(
            G2PFarmerRegistry,
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
            G2PFarmerRegistry, registrant_ids, pbms_domain, multiplier_field
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
            G2PFarmerRegistry,
            bg_task_session,
            beneficiary_list_id,
            search_domain,
            page,
            page_size,
            order_by,
            _farmer_payload,
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


def _farmer_payload(farmer) -> G2PFarmerRegistryPayload:
    return G2PFarmerRegistryPayload(
        internal_record_id=str(farmer.internal_record_id),
        functional_record_id=farmer.functional_record_id,
        first_name=farmer.first_name,
        last_name=farmer.last_name,
        gender=farmer.gender,
        estimated_age=farmer.estimated_age,
        disabled=farmer.disabled,
        source_of_income=farmer.source_of_income,
        education_level=farmer.education_level,
        country_code=farmer.country_code,
    )
