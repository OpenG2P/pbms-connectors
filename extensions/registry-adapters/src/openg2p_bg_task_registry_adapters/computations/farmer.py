from ..dci import identifier_value
from ..models import G2PFarmerRegistry
from ..schema import G2PFarmerRegistryPayload
from ._base import RegistryDB, RegistryDCI
from ._dci_records import as_bool
from ._summary import FarmerSummaries


class FarmerDB(FarmerSummaries, RegistryDB):
    model = G2PFarmerRegistry
    payload = G2PFarmerRegistryPayload


class FarmerDCI(FarmerSummaries, RegistryDCI):
    payload = G2PFarmerRegistryPayload
    reg_type = "Farmer"
    reg_record_type = "Farmer"
    match_field = "foundational_id"
    fields = {
        "foundational_id",
        "first_name",
        "middle_name",
        "last_name",
        "prefix",
        "suffix",
        "gender",
        "birth_date",
        "phone_numbers",
        "marital_status",
        "registration_date",
        "disabled",
        "education_level",
        "language_spoken",
        "latitude",
        "longitude",
    }

    @staticmethod
    def flat(record: dict) -> dict:
        personal = record.get("farmer_personal_details") or {}
        demographic = personal.get("demographic_info") or {}
        name = demographic.get("name") or {}
        family = record.get("family_details") or {}
        geo = (family.get("place") or {}).get("geo") or {}
        languages = personal.get("language_code") or []
        return {
            "foundational_id": identifier_value(
                record,
                ("farmer_personal_details", "member_identifier"),
                ("farmer_personal_details", "demographic_info", "identifier"),
            ),
            "first_name": name.get("given_name"),
            "middle_name": name.get("second_name"),
            "last_name": name.get("surname"),
            "prefix": name.get("prefix"),
            "suffix": name.get("suffix"),
            "gender": demographic.get("sex"),
            "birth_date": demographic.get("birth_date"),
            "phone_numbers": demographic.get("phone_number"),
            "marital_status": personal.get("marital_status"),
            "registration_date": personal.get("registration_date"),
            "disabled": as_bool(personal.get("self_id_disability")),
            "education_level": personal.get("education_level"),
            "language_spoken": languages[0]
            if isinstance(languages, list) and languages
            else None,
            "latitude": geo.get("latitude"),
            "longitude": geo.get("longitude"),
        }
