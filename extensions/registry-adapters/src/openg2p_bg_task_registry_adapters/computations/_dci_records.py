"""Flatten a rendered DCI reg_record onto the Odoo field names."""

from datetime import date
from types import SimpleNamespace

from ..dci import identifier_value
from ..schema import (
    G2PDisabilityRegistryPayload,
    G2PFarmerRegistryPayload,
    G2PRegisterHouseholdPayload,
)

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

# Register columns that dr_person_to_dci.json.j2 renders. The Partner API
# filters on these columns, so the disability registry must also list them in
# REGISTRY_PARTNER_API_DCI_ALLOWED_SEARCH_FIELDS.
DISABILITY_DCI_FIELDS = {
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


def farmer_id(record: dict) -> str:
    return identifier_value(
        record,
        ("farmer_personal_details", "member_identifier"),
        ("farmer_personal_details", "demographic_info", "identifier"),
    )


def household_id(record: dict) -> str:
    return identifier_value(record, ("family_details", "group_identifier"))


def disability_id(record: dict) -> str:
    return identifier_value(record, ("member_identifier",))


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


def disability_flat(record: dict) -> dict:
    demographic = record.get("demographic_info") or {}
    name = demographic.get("name") or {}
    address = (demographic.get("address") or [{}])[0]
    extra = (record.get("additional_attributes") or [{}])[0]
    unmet = _as_int(extra.get("unmet_support_needs_count"))
    return {
        "functional_record_id": disability_id(record),
        "foundational_id": _text(identifier_value(demographic, ("identifier",))),
        "disability_certificate_number": _identifier_of_type(
            record.get("member_identifier"), "DisabilityCertificate"
        ),
        "first_name": _text(name.get("given_name")),
        "middle_name": _text(name.get("second_name")),
        "last_name": _text(name.get("surname")),
        "prefix": _text(name.get("prefix")),
        "suffix": _text(name.get("suffix")),
        "gender": _code(demographic.get("sex")),
        "birth_date": _text(demographic.get("birth_date")),
        "death_date": _text(demographic.get("death_date")),
        "address_line_1": _text(address.get("address_line_1")),
        "address_line_2": _text(address.get("address_line_2")),
        "postal_code": _text(address.get("postal_code")),
        "country_code": _text(address.get("country_code")),
        "registration_date": _text(record.get("registration_date")),
        "marital_status": _code(record.get("marital_status")),
        "employment_status": _code(record.get("employment_status")),
        "occupation": _code(record.get("occupation")),
        "income_level": _code(record.get("income_level")),
        "education_level": _code(record.get("education_level")),
        "self_id_disability": _as_bool(record.get("self_id_disability")),
        "disability_status": _code(record.get("disability_status")),
        "disability_status_level": _code(record.get("disability_status_level")),
        "support_needs_level": _code(extra.get("support_needs_level")),
        "legal_capacity_status": _code(extra.get("legal_capacity_status")),
        "transport_requirement": _code(record.get("transport_requirement")),
        "housing_type": _code(record.get("housing_type")),
        "assessment_date": _text(extra.get("assessment_date")),
        "assessment_authority": _text(extra.get("assessment_authority")),
        "certificate_expiry_date": _text(extra.get("certificate_expiry_date")),
        "registration_channel": _code(extra.get("registration_channel")),
        "unmet_support_needs_count": unmet,
        "has_unmet_support_need": None if unmet is None else unmet > 0,
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


def disability_row(record: dict):
    flat = disability_flat(record)
    flat["internal_record_id"] = flat["functional_record_id"]
    flat["estimated_age"] = age_from_birth_date(flat["birth_date"])
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


def disability_payload(record: dict) -> G2PDisabilityRegistryPayload:
    flat = disability_flat(record)
    return G2PDisabilityRegistryPayload(
        internal_record_id=flat["functional_record_id"] or "",
        functional_record_id=flat["functional_record_id"],
        first_name=flat["first_name"],
        last_name=flat["last_name"],
        gender=flat["gender"],
        birth_date=flat["birth_date"],
        estimated_age=age_from_birth_date(flat["birth_date"]),
        disability_status=flat["disability_status"],
        disability_status_level=flat["disability_status_level"],
        support_needs_level=flat["support_needs_level"],
        unmet_support_needs_count=flat["unmet_support_needs_count"],
        has_unmet_support_need=flat["has_unmet_support_need"],
        employment_status=flat["employment_status"],
        housing_type=flat["housing_type"],
        country_code=flat["country_code"],
    )


def age_from_birth_date(value):
    if not value:
        return None
    if isinstance(value, str):
        try:
            value = date.fromisoformat(value[:10])
        except ValueError:
            return None
    today = date.today()
    return (
        today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    )


def _as_bool(value):
    if isinstance(value, bool):
        return value
    if value in (None, ""):
        return None
    return str(value).lower() in ("true", "1")


def _as_int(value):
    if value in (None, ""):
        return None
    return int(value)


def _text(value):
    return value if value not in (None, "") else None


def _code(value):
    """Undo the template's display casing: "Assessed disabled" -> "ASSESSED_DISABLED"."""
    if value in (None, ""):
        return None
    return str(value).strip().upper().replace(" ", "_")


def _identifier_of_type(identifiers, identifier_type: str):
    for item in identifiers or []:
        if isinstance(item, dict) and item.get("identifier_type") == identifier_type:
            return _text(item.get("identifier_value"))
    return None
