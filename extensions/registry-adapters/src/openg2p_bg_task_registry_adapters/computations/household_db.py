from typing import Optional

from openg2p_bg_task_models.schemas import BeneficiarySearchResponsePayload

from ..interface import RegistryInterface
from ..models import G2PRegisterHousehold
from ..schema import G2PRegisterHouseholdPayload
from . import _transport
from ._summary import HouseholdSummaries


class HouseholdDB(HouseholdSummaries, RegistryInterface):
    """Household eligibility, entitlement, and search against the registry database."""

    def registrant_id_of(self, household) -> str:
        return str(household.internal_record_id)

    def fetch_by_ids(self, registrant_ids: list[str]):
        return _transport.fetch_db(G2PRegisterHousehold, registrant_ids)

    def iter_eligible_ids(self, rules, batch_size: int):
        return _transport.iter_eligible_db(G2PRegisterHousehold, rules, batch_size)

    def iter_priority_ids(
        self, priority_domains, enrolled_ids, fallback_rules, batch_size
    ):
        return _transport.iter_priority_db(
            G2PRegisterHousehold,
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
            G2PRegisterHousehold, registrant_ids, pbms_domain, multiplier_field
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
            G2PRegisterHousehold,
            bg_task_session,
            beneficiary_list_id,
            search_domain,
            page,
            page_size,
            order_by,
            _household_payload,
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


def _household_payload(household) -> G2PRegisterHouseholdPayload:
    return G2PRegisterHouseholdPayload(
        internal_record_id=str(household.internal_record_id),
        functional_record_id=household.functional_record_id,
        household_head_name=household.household_head_name,
        headship_type=household.headship_type,
        size_total=household.size_total,
        size_children_u5=household.size_children_u5,
        size_elderly=household.size_elderly,
        number_of_female_members=household.number_of_female_members,
        number_of_male_members=household.number_of_male_members,
        dwelling_type=household.dwelling_type,
        tenure_status=household.tenure_status,
        rooms_count=household.rooms_count,
        overcrowding_indicator=household.overcrowding_indicator,
        water_source_type=household.water_source_type,
        sanitation_type=household.sanitation_type,
        lighting_source=household.lighting_source,
        cooking_fuel_type=household.cooking_fuel_type,
        address_line_1=household.address_line_1,
        address_line_2=household.address_line_2,
        postal_code=household.postal_code,
        country_code=household.country_code,
    )
