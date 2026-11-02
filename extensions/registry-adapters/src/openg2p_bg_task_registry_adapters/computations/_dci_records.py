"""Flatten a rendered DCI reg_record onto the Odoo field names."""

from types import SimpleNamespace

from ..dci import identifier_value
from ..schema import G2PFarmerRegistryPayload, G2PRegisterHouseholdPayload

FARMER_DCI_FIELDS = {
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

HOUSEHOLD_DCI_FIELDS = {
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


def farmer_id(record: dict) -> str:
    return identifier_value(
        record,
        ("farmer_personal_details", "member_identifier"),
        ("farmer_personal_details", "demographic_info", "identifier"),
    )


def household_id(record: dict) -> str:
    return identifier_value(record, ("family_details", "group_identifier"))


def farmer_flat(record: dict) -> dict:
    personal = record.get("farmer_personal_details") or {}
    demographic = personal.get("demographic_info") or {}
    name = demographic.get("name") or {}
    family = record.get("family_details") or {}
    place = family.get("place") or {}
    geo = place.get("geo") or {}
    languages = personal.get("language_code") or []
    return {
        "foundational_id": farmer_id(record),
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
        "disabled": personal.get("self_id_disability"),
        "education_level": personal.get("education_level"),
        "language_spoken": languages[0]
        if isinstance(languages, list) and languages
        else None,
        "latitude": geo.get("latitude"),
        "longitude": geo.get("longitude"),
    }


def household_flat(record: dict) -> dict:
    family = record.get("family_details") or {}
    place = family.get("place") or {}
    geo = place.get("geo") or {}
    head = ((family.get("group_head_info") or {}).get("demographic_info") or {}).get(
        "name"
    ) or {}
    extra = (record.get("additional_attributes") or [{}])[0]
    return {
        "functional_record_id": household_id(record),
        "latitude": geo.get("latitude"),
        "longitude": geo.get("longitude"),
        "address_line_1": place.get("name"),
        "address_line_2": None,
        "household_head_name": head.get("given_name"),
        "size_total": family.get("group_size"),
        "number_of_female_members": extra.get("number_of_female_members"),
        "number_of_male_members": extra.get("number_of_male_members"),
        "created_at": family.get("registration_date"),
        "last_approved_at": family.get("last_updated"),
    }


def farmer_row(record: dict):
    flat = farmer_flat(record)
    flat["internal_record_id"] = flat["foundational_id"]
    flat["estimated_age"] = None
    return SimpleNamespace(**flat)


def household_row(record: dict):
    flat = household_flat(record)
    flat["internal_record_id"] = flat["functional_record_id"]
    flat["size_children_u5"] = None
    flat["size_elderly"] = None
    flat["rooms_count"] = None
    flat["overcrowding_indicator"] = None
    return SimpleNamespace(**flat)


def farmer_payload(record: dict) -> G2PFarmerRegistryPayload:
    flat = farmer_flat(record)
    return G2PFarmerRegistryPayload(
        internal_record_id=flat["foundational_id"] or "",
        first_name=flat.get("first_name"),
        last_name=flat.get("last_name"),
        gender=flat.get("gender"),
        disabled=_as_bool(flat.get("disabled")),
        education_level=flat.get("education_level"),
    )


def household_payload(record: dict) -> G2PRegisterHouseholdPayload:
    flat = household_flat(record)
    return G2PRegisterHouseholdPayload(
        internal_record_id=flat["functional_record_id"] or "",
        functional_record_id=flat.get("functional_record_id"),
        household_head_name=flat.get("household_head_name"),
        size_total=_as_int(flat.get("size_total")),
        number_of_female_members=_as_int(flat.get("number_of_female_members")),
        number_of_male_members=_as_int(flat.get("number_of_male_members")),
        address_line_1=flat.get("address_line_1"),
    )


def _as_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    return str(value).lower() == "true"


def _as_int(value):
    if value in (None, ""):
        return None
    return int(value)
