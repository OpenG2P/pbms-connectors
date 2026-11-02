from ..dci import identifier_value
from ..models import G2PRegisterHousehold
from ..schema import G2PRegisterHouseholdPayload
from ._base import RegistryDB, RegistryDCI
from ._dci_records import as_int
from ._summary import HouseholdSummaries


class HouseholdDB(HouseholdSummaries, RegistryDB):
    model = G2PRegisterHousehold
    payload = G2PRegisterHouseholdPayload


class HouseholdDCI(HouseholdSummaries, RegistryDCI):
    payload = G2PRegisterHouseholdPayload
    reg_type = "Household"
    reg_record_type = "Household"
    match_field = "functional_record_id"
    fields = {
        "functional_record_id",
        "latitude",
        "longitude",
        "address_line_1",
        "address_line_2",
        "household_head_name",
        "size_total",
        "number_of_female_members",
        "number_of_male_members",
        "created_at",
        "last_approved_at",
    }

    @staticmethod
    def flat(record: dict) -> dict:
        family = record.get("family_details") or {}
        place = family.get("place") or {}
        geo = place.get("geo") or {}
        head = (
            (family.get("group_head_info") or {}).get("demographic_info") or {}
        ).get("name") or {}
        extra = (record.get("additional_attributes") or [{}])[0]
        return {
            "functional_record_id": identifier_value(
                record, ("family_details", "group_identifier")
            ),
            "latitude": geo.get("latitude"),
            "longitude": geo.get("longitude"),
            "address_line_1": place.get("name"),
            "address_line_2": None,
            "household_head_name": head.get("given_name"),
            "size_total": as_int(family.get("group_size")),
            "number_of_female_members": as_int(extra.get("number_of_female_members")),
            "number_of_male_members": as_int(extra.get("number_of_male_members")),
            "created_at": family.get("registration_date"),
            "last_approved_at": family.get("last_updated"),
        }
