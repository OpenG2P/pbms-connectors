from ..dci import identifier_value
from ..models import G2PDisabilityRegistry
from ..schema import G2PDisabilityRegistryPayload
from ._base import RegistryDB, RegistryDCI
from ._dci_records import as_bool, as_int, code, identifier_of_type, text
from ._summary import DisabilitySummaries


class DisabilityDB(DisabilitySummaries, RegistryDB):
    model = G2PDisabilityRegistry
    payload = G2PDisabilityRegistryPayload


class DisabilityDCI(DisabilitySummaries, RegistryDCI):
    payload = G2PDisabilityRegistryPayload
    reg_type = "PersonWithDisability"
    reg_record_type = "spdci-extensions-dci:PersonwithDisability"
    match_field = "functional_record_id"
    # Columns dr_person_to_dci.json.j2 renders. The disability registry must
    # also list them in REGISTRY_PARTNER_API_DCI_ALLOWED_SEARCH_FIELDS.
    fields = {
        "functional_record_id",
        "foundational_id",
        "disability_certificate_number",
        "first_name",
        "middle_name",
        "last_name",
        "prefix",
        "suffix",
        "gender",
        "birth_date",
        "death_date",
        "address_line_1",
        "address_line_2",
        "postal_code",
        "country_code",
        "registration_date",
        "marital_status",
        "employment_status",
        "occupation",
        "income_level",
        "education_level",
        "self_id_disability",
        "disability_status",
        "disability_status_level",
        "support_needs_level",
        "legal_capacity_status",
        "transport_requirement",
        "housing_type",
        "assessment_date",
        "assessment_authority",
        "certificate_expiry_date",
        "registration_channel",
        "unmet_support_needs_count",
        "has_unmet_support_need",
    }

    @staticmethod
    def flat(record: dict) -> dict:
        demographic = record.get("demographic_info") or {}
        name = demographic.get("name") or {}
        address = (demographic.get("address") or [{}])[0]
        extra = (record.get("additional_attributes") or [{}])[0]
        unmet = as_int(extra.get("unmet_support_needs_count"))
        return {
            "functional_record_id": identifier_value(record, ("member_identifier",)),
            "foundational_id": text(identifier_value(demographic, ("identifier",))),
            "disability_certificate_number": identifier_of_type(
                record.get("member_identifier"), "DisabilityCertificate"
            ),
            "first_name": text(name.get("given_name")),
            "middle_name": text(name.get("second_name")),
            "last_name": text(name.get("surname")),
            "prefix": text(name.get("prefix")),
            "suffix": text(name.get("suffix")),
            "gender": code(demographic.get("sex")),
            "birth_date": text(demographic.get("birth_date")),
            "death_date": text(demographic.get("death_date")),
            "address_line_1": text(address.get("address_line_1")),
            "address_line_2": text(address.get("address_line_2")),
            "postal_code": text(address.get("postal_code")),
            "country_code": text(address.get("country_code")),
            "registration_date": text(record.get("registration_date")),
            "marital_status": code(record.get("marital_status")),
            "employment_status": code(record.get("employment_status")),
            "occupation": code(record.get("occupation")),
            "income_level": code(record.get("income_level")),
            "education_level": code(record.get("education_level")),
            "self_id_disability": as_bool(record.get("self_id_disability")),
            "disability_status": code(record.get("disability_status")),
            "disability_status_level": code(record.get("disability_status_level")),
            "support_needs_level": code(extra.get("support_needs_level")),
            "legal_capacity_status": code(extra.get("legal_capacity_status")),
            "transport_requirement": code(record.get("transport_requirement")),
            "housing_type": code(record.get("housing_type")),
            "assessment_date": text(extra.get("assessment_date")),
            "assessment_authority": text(extra.get("assessment_authority")),
            "certificate_expiry_date": text(extra.get("certificate_expiry_date")),
            "registration_channel": code(extra.get("registration_channel")),
            "unmet_support_needs_count": unmet,
            "has_unmet_support_need": None if unmet is None else unmet > 0,
        }
