from odoo import fields, models


class G2PFarmerRegistry(models.Model):
    _name = "g2p.register.farmers"
    _description = "Farmer Registry"
    _inherit = "g2p.registry"
    _auto = False

    # G2PRegister fields
    # Not part of the DCI spec. Usable with the DB connector only.
    functional_record_id = fields.Char(string="Functional Record ID", index=True)
    # Not part of the DCI spec. Usable with the DB connector only.
    link_internal_record_id = fields.Char(string="Link Internal Record ID", index=True)
    # Not part of the DCI spec. Usable with the DB connector only.
    link_foundational_id = fields.Char(string="Link Foundational ID", index=True)
    # Not part of the DCI spec. Usable with the DB connector only.
    record_name = fields.Char(string="Record Name")
    # Not part of the DCI spec. Usable with the DB connector only.
    record_image_storage_id = fields.Text(string="Record Image Storage ID")
    # Not part of the DCI spec. Usable with the DB connector only.
    created_by = fields.Char(string="Created By")
    # Not part of the DCI spec. Usable with the DB connector only.
    created_at = fields.Datetime(string="Created At")
    # Not part of the DCI spec. Usable with the DB connector only.
    last_approved_at = fields.Datetime(string="Last Approved At")
    # Not part of the DCI spec. Usable with the DB connector only.
    last_approved_by = fields.Char(string="Last Approved By")
    # Not part of the DCI spec. Usable with the DB connector only.
    search_text = fields.Text(string="Search Text")
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

    # G2PPerson fields. These names are what the farmer DCI template reads.
    foundational_id = fields.Char(string="Foundational ID", index=True)
    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Middle Name")
    last_name = fields.Char(string="Last Name")
    # Not part of the DCI spec. Usable with the DB connector only.
    given_name = fields.Char(string="Given Name")
    prefix = fields.Char(string="Prefix")
    suffix = fields.Char(string="Suffix")
    gender = fields.Selection(
        selection=[
            ("MALE", "Male"),
            ("FEMALE", "Female"),
            ("OTHERS", "Others"),
            ("UNKNOWN", "Unknown"),
        ],
        string="Gender",
    )
    birth_date = fields.Date(string="Birth Date")
    phone_numbers = fields.Json(string="Phone Numbers")
    # Not part of the DCI spec. Usable with the DB connector only.
    emails = fields.Json(string="Emails")
    marital_status = fields.Selection(
        selection=[
            ("SINGLE", "Single"),
            ("MARRIED", "Married"),
            ("DIVORCED", "Divorced"),
            ("WIDOWED", "Widowed"),
            ("SEPARATED", "Separated"),
            ("UNKNOWN", "Unknown"),
        ],
        string="Marital Status",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    occupation = fields.Char(string="Occupation")
    # Not part of the DCI spec. Usable with the DB connector only.
    income_level = fields.Char(string="Income Level")
    # Not part of the DCI spec. Usable with the DB connector only.
    language_code = fields.Char(string="Language Code")
    registration_date = fields.Date(string="Registration Date")

    # G2PGeo fields
    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")
    # Not part of the DCI spec. Usable with the DB connector only.
    altitude = fields.Char(string="Altitude")
    # Not part of the DCI spec. Usable with the DB connector only.
    plus_code = fields.Char(string="Plus Code", index=True)
    # Not part of the DCI spec. Usable with the DB connector only.
    address_line_1 = fields.Char(string="Address Line 1")
    # Not part of the DCI spec. Usable with the DB connector only.
    address_line_2 = fields.Char(string="Address Line 2")
    # Not part of the DCI spec. Usable with the DB connector only.
    postal_code = fields.Char(string="Postal Code", index=True)
    # Not part of the DCI spec. Usable with the DB connector only.
    country_code = fields.Char(string="Country Code", index=True)
    # Not part of the DCI spec. Usable with the DB connector only.
    geo_lowest_level_value_id = fields.Char(
        string="Geo Lowest Level Value ID", index=True
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    geo_code_hierarchy_json = fields.Json(string="Geo Code Hierarchy")

    # G2PFarmer fields
    # Not part of the DCI spec. Usable with the DB connector only.
    estimated_age = fields.Integer(string="Estimated Age")
    # Not part of the DCI spec. Usable with the DB connector only.
    has_personal_phone = fields.Boolean(string="Has Personal Phone")
    disabled = fields.Boolean(string="Disabled")
    # Not part of the DCI spec. Usable with the DB connector only.
    disability_type = fields.Selection(
        selection=[
            ("VISION", "Vision"),
            ("HEARING", "Hearing"),
            ("MOBILITY", "Mobility"),
            ("COGNITION", "Cognition"),
            ("SELF_CARE", "Self Care"),
            ("COMMUNICATION", "Communication"),
        ],
        string="Disability Type",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    disability_severity = fields.Selection(
        selection=[
            ("NO_DIFFICULTY", "No Difficulty"),
            ("SOME_DIFFICULTY", "Some Difficulty"),
            ("A_LOT_OF_DIFFICULTY", "A Lot of Difficulty"),
            ("CANNOT_DO_AT_ALL", "Cannot Do At All"),
        ],
        string="Disability Severity",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    source_of_income = fields.Selection(
        selection=[
            ("CROP_PRODUCTION", "Crop Production"),
            ("LIVESTOCK_PRODUCTION", "Livestock Production"),
            ("GOVERNMENT_NGO_SUPPORT", "Government / NGO Support"),
            ("OTHERS", "Others"),
        ],
        string="Source of Income",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    source_of_income_other = fields.Char(string="Source of Income (Other)")
    language_spoken = fields.Char(string="Language Spoken")
    education_level = fields.Selection(
        selection=[
            ("ILLITERATE", "Illiterate"),
            ("CAN_READ_AND_WRITE", "Can Read and Write"),
            ("BASIC", "Basic"),
            ("INTERMEDIARY", "Intermediary"),
            ("HIGHER_EDUCATION", "Higher Education"),
        ],
        string="Education Level",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    national_id_masked = fields.Char(string="National ID (Masked)")
