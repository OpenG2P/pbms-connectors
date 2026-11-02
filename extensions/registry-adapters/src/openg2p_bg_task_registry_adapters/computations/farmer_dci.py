from typing import Optional

from openg2p_bg_task_models.schemas import BeneficiarySearchResponsePayload

from ..config import RegistryAdapterSettings
from ..interface import RegistryInterface
from . import _transport
from ._dci_records import (
    FARMER_DCI_FIELDS,
    farmer_flat,
    farmer_id,
    farmer_payload,
    farmer_row,
)
from ._summary import FarmerSummaries


class FarmerDCI(FarmerSummaries, RegistryInterface):
    """Farmer eligibility, entitlement, and search via POST /dci/sync/search."""

    def registrant_id_of(self, farmer) -> str:
        return str(farmer.internal_record_id)

    def fetch_by_ids(self, registrant_ids: list[str]):
        settings = RegistryAdapterSettings.get_config()
        return _transport.fetch_dci(
            registrant_ids,
            FARMER_DCI_FIELDS,
            "foundational_id",
            settings.farmer_reg_type,
            settings.farmer_reg_record_type,
            farmer_id,
            farmer_row,
        )

    def iter_eligible_ids(self, rules, batch_size: int):
        settings = RegistryAdapterSettings.get_config()
        return _transport.iter_eligible_dci(
            rules,
            batch_size,
            FARMER_DCI_FIELDS,
            "foundational_id",
            settings.farmer_reg_type,
            settings.farmer_reg_record_type,
            farmer_id,
        )

    def iter_priority_ids(
        self, priority_domains, enrolled_ids, fallback_rules, batch_size
    ):
        settings = RegistryAdapterSettings.get_config()
        return _transport.iter_priority_dci(
            priority_domains,
            enrolled_ids,
            fallback_rules,
            batch_size,
            FARMER_DCI_FIELDS,
            "foundational_id",
            settings.farmer_reg_type,
            settings.farmer_reg_record_type,
            farmer_id,
        )

    def entitlement_multipliers(
        self,
        registrant_ids: list[str],
        pbms_domain: str,
        multiplier_field: Optional[str] = None,
    ) -> dict[str, float]:
        settings = RegistryAdapterSettings.get_config()
        return _transport.multipliers_dci(
            registrant_ids,
            pbms_domain,
            multiplier_field,
            FARMER_DCI_FIELDS,
            "foundational_id",
            settings.farmer_reg_type,
            settings.farmer_reg_record_type,
            farmer_id,
            farmer_flat,
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
        settings = RegistryAdapterSettings.get_config()
        rows, total = _transport.search_dci(
            registrant_ids,
            search_domain,
            page,
            page_size,
            FARMER_DCI_FIELDS,
            "foundational_id",
            settings.farmer_reg_type,
            settings.farmer_reg_record_type,
            farmer_id,
            farmer_payload,
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
