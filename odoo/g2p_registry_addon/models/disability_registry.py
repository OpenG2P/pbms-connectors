from odoo import fields, models


def _codes(*values):
    return [(value, value.replace("_", " ").title()) for value in values]


class G2PDisabilityRegistry(models.Model):
    _name = "g2p.register.persons_with_disability"
    _description = "Disability Registry"
    _inherit = "g2p.registry"
    _auto = False

    # G2PRegister fields. functional_record_id is the UIN in the DCI record.
    functional_record_id = fields.Char(string="Functional Record ID", index=True)
    # Not part of the DCI spec. Usable with the DB connector only.
    link_internal_record_id = fields.Char(string="Link Internal Record ID", index=True)
    # Not part of the DCI spec. Usable with the DB connector only.
    link_foundational_id = fields.Char(string="Link Foundational ID", index=True)
    # Not part of the DCI spec. Usable with the DB connector only.
    record_name = fields.Char(string="Record Name")
    # Not part of the DCI spec. Usable with the DB connector only.
    record_status = fields.Selection(
        selection=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("archived", "Archived"),
        ],
        string="Record Status",
        default="active",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    record_status_reason = fields.Char(string="Record Status Reason")

    # DO.DR.01 DRPerson / DO.DR.02 Member
    foundational_id = fields.Char(string="Foundational ID", index=True)
    # Not part of the DCI spec. Usable with the DB connector only.
    foundational_id_masked = fields.Char(string="Foundational ID (Masked)")
    disability_certificate_number = fields.Char(
        string="Disability Certificate Number", index=True
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    full_name = fields.Char(string="Full Name")
    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Middle Name")
    last_name = fields.Char(string="Last Name")
    # Not part of the DCI spec. Usable with the DB connector only.
    given_name = fields.Char(string="Given Name")
    prefix = fields.Char(string="Prefix")
    suffix = fields.Char(string="Suffix")
    gender = fields.Selection(
        selection=_codes("MALE", "FEMALE", "OTHERS", "UNKNOWN"), string="Gender"
    )
    birth_date = fields.Date(string="Birth Date")
    death_date = fields.Date(string="Death Date")
    # Not part of the DCI spec. Usable with the DB connector only.
    estimated_age = fields.Integer(string="Estimated Age")
    marital_status = fields.Selection(
        selection=_codes(
            "SINGLE", "MARRIED", "DIVORCED", "WIDOWED", "SEPARATED", "UNKNOWN"
        ),
        string="Marital Status",
    )
    employment_status = fields.Selection(
        selection=_codes(
            "EMPLOYED",
            "SELF_EMPLOYED",
            "SHELTERED_EMPLOYMENT",
            "SUPPORTED_EMPLOYMENT",
            "UNEMPLOYED_SEEKING",
            "UNEMPLOYED_NOT_SEEKING",
            "STUDENT",
            "RETIRED",
            "UNABLE_TO_WORK",
            "OTHER",
        ),
        string="Employment Status",
    )
    occupation = fields.Char(string="Occupation")
    income_level = fields.Char(string="Income Level")
    education_level = fields.Char(string="Education Level")
    registration_date = fields.Date(string="Registration Date")
    registration_channel = fields.Selection(
        selection=_codes(
            "SELF_REGISTRATION",
            "ASSISTED_REGISTRATION",
            "HOME_VISIT",
            "HEALTH_FACILITY_REFERRAL",
            "SCHOOL_REFERRAL",
            "OPD_REFERRAL",
            "SOCIAL_REGISTRY_TRANSFER",
            "CRVS_TRANSFER",
            "OTHER",
        ),
        string="Registration Channel",
    )

    # G2PGeo fields
    # Not part of the DCI spec. Usable with the DB connector only.
    latitude = fields.Char(string="Latitude")
    # Not part of the DCI spec. Usable with the DB connector only.
    longitude = fields.Char(string="Longitude")
    address_line_1 = fields.Char(string="Address Line 1")
    address_line_2 = fields.Char(string="Address Line 2")
    postal_code = fields.Char(string="Postal Code", index=True)
    country_code = fields.Char(string="Country Code", index=True)
    # Not part of the DCI spec. Usable with the DB connector only.
    geo_lowest_level_value_id = fields.Char(
        string="Geo Lowest Level Value ID", index=True
    )

    # DO.DR.03 PersonwithDisability
    self_id_disability = fields.Boolean(string="Self-identified Disability")
    disability_status = fields.Selection(
        selection=_codes(
            "ASSESSED_DISABLED",
            "ASSESSED_NOT_DISABLED",
            "PENDING_ASSESSMENT",
            "SELF_DECLARED",
            "UNKNOWN",
        ),
        string="Disability Status",
    )
    disability_status_level = fields.Selection(
        selection=_codes("NONE", "MILD", "MODERATE", "SEVERE", "PROFOUND"),
        string="Disability Status Level",
    )
    support_needs_level = fields.Selection(
        selection=_codes(
            "INDEPENDENT",
            "INTERMITTENT_SUPPORT",
            "LIMITED_SUPPORT",
            "EXTENSIVE_SUPPORT",
            "PERVASIVE_SUPPORT",
        ),
        string="Support Needs Level",
    )
    assessment_date = fields.Date(string="Assessment Date")
    assessment_authority = fields.Char(string="Assessment Authority")
    # Not part of the DCI spec. Usable with the DB connector only.
    certificate_issue_date = fields.Date(string="Certificate Issue Date")
    certificate_expiry_date = fields.Date(string="Certificate Expiry Date")
    # Not part of the DCI spec. Usable with the DB connector only.
    next_reassessment_date = fields.Date(string="Next Reassessment Date")
    transport_requirement = fields.Selection(
        selection=_codes(
            "NONE",
            "ACCESSIBLE_PUBLIC_TRANSPORT",
            "ADAPTED_VEHICLE",
            "WHEELCHAIR_ACCESSIBLE_VEHICLE",
            "ESCORTED_TRAVEL",
            "AMBULANCE_TRANSPORT",
            "TRANSPORT_ALLOWANCE",
            "OTHER",
        ),
        string="Transport Requirement",
    )
    housing_type = fields.Selection(
        selection=_codes(
            "INDEPENDENT_HOME",
            "FAMILY_HOME",
            "SUPPORTED_LIVING",
            "GROUP_HOME",
            "RESIDENTIAL_INSTITUTION",
            "HOSPITAL_LONG_STAY",
            "TEMPORARY_SHELTER",
            "HOMELESS",
            "OTHER",
        ),
        string="Housing Type",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    lives_alone = fields.Boolean(string="Lives Alone")
    legal_capacity_status = fields.Selection(
        selection=_codes(
            "FULL_CAPACITY",
            "SUPPORTED_DECISION_MAKING",
            "PARTIAL_GUARDIANSHIP",
            "FULL_GUARDIANSHIP",
            "UNDER_REVIEW",
            "UNKNOWN",
        ),
        string="Legal Capacity Status",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    guardian_required = fields.Boolean(string="Guardian Required")
    # Not part of the DCI spec. Usable with the DB connector only.
    preferred_contact_method = fields.Selection(
        selection=_codes(
            "CALL",
            "SMS",
            "EMAIL",
            "SIGN_LANGUAGE_VIDEO_CALL",
            "VIA_CAREGIVER",
            "VIA_LOCAL_OFFICE",
            "NONE",
        ),
        string="Preferred Contact Method",
    )

    # Summary of the DO.DR.05 support sub-registers, recomputed by the registry.
    unmet_support_needs_count = fields.Integer(string="Unmet Support Needs")
    has_unmet_support_need = fields.Boolean(string="Has Unmet Support Need")
