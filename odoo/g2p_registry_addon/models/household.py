from odoo import fields, models


class G2PRegisterHousehold(models.Model):
    _name = "g2p.register.households"
    _description = "Register Household"
    _inherit = "g2p.registry"
    _auto = False

    # Group identifier in the household DCI template.
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
    created_at = fields.Datetime(string="Created At")
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

    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")
    # Not part of the DCI spec. Usable with the DB connector only.
    altitude = fields.Char(string="Altitude")
    # Not part of the DCI spec. Usable with the DB connector only.
    plus_code = fields.Char(string="Plus Code", index=True)
    address_line_1 = fields.Char(string="Address Line 1")
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

    # Not part of the DCI spec. Usable with the DB connector only.
    household_head_internal_record_id = fields.Char(
        string="Household Head Internal Record ID", index=True
    )
    household_head_name = fields.Char(string="Household Head Name")
    # Not part of the DCI spec. Usable with the DB connector only.
    headship_type = fields.Selection(
        selection=[
            ("MALE_HEADED", "Male Headed"),
            ("FEMALE_HEADED", "Female Headed"),
            ("CHILD_HEADED", "Child Headed"),
            ("ELDERLY_HEADED", "Elderly Headed"),
            ("DISABLED_HEADED", "Disabled Headed"),
        ],
        string="Headship Type",
    )

    size_total = fields.Integer(string="Total Size")
    # Not part of the DCI spec. Usable with the DB connector only.
    size_adults = fields.Integer(string="Adults")
    # Not part of the DCI spec. Usable with the DB connector only.
    size_children_u5 = fields.Integer(string="Children Under 5")
    # Not part of the DCI spec. Usable with the DB connector only.
    size_school_age = fields.Integer(string="School Age")
    # Not part of the DCI spec. Usable with the DB connector only.
    size_elderly = fields.Integer(string="Elderly")
    number_of_female_members = fields.Integer(string="Number of Female Members")
    number_of_male_members = fields.Integer(string="Number of Male Members")
    # Not part of the DCI spec. Usable with the DB connector only.
    elderly_member_present = fields.Boolean(string="Elderly Member Present")

    # Not part of the DCI spec. Usable with the DB connector only.
    dwelling_type = fields.Selection(
        selection=[
            ("PERMANENT", "Permanent"),
            ("SEMI_PERMANENT", "Semi-Permanent"),
            ("TEMPORARY", "Temporary"),
        ],
        string="Dwelling Type",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    roof_material = fields.Selection(
        selection=[
            ("THATCH", "Thatch"),
            ("CORRUGATED_IRON", "Corrugated Iron"),
            ("CONCRETE", "Concrete"),
            ("TILE", "Tile"),
            ("PLASTIC_SHEET", "Plastic Sheet"),
            ("OTHER", "Other"),
        ],
        string="Roof Material",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    wall_material = fields.Selection(
        selection=[
            ("MUD", "Mud"),
            ("WOOD", "Wood"),
            ("BAMBOO", "Bamboo"),
            ("STONE", "Stone"),
            ("BRICK", "Brick"),
            ("CONCRETE", "Concrete"),
            ("OTHER", "Other"),
        ],
        string="Wall Material",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    floor_material = fields.Selection(
        selection=[
            ("EARTH", "Earth"),
            ("WOOD", "Wood"),
            ("CEMENT", "Cement"),
            ("TILE", "Tile"),
            ("OTHER", "Other"),
        ],
        string="Floor Material",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    tenure_status = fields.Selection(
        selection=[
            ("OWNED", "Owned"),
            ("RENTED", "Rented"),
            ("HOSTED", "Hosted"),
            ("TEMPORARY", "Temporary"),
        ],
        string="Tenure Status",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    rooms_count = fields.Integer(string="Rooms Count")
    # Not part of the DCI spec. Usable with the DB connector only.
    overcrowding_indicator = fields.Float(string="Overcrowding Indicator")

    # Not part of the DCI spec. Usable with the DB connector only.
    water_source_type = fields.Selection(
        selection=[
            ("PIPED", "Piped"),
            ("PUBLIC_TAP", "Public Tap"),
            ("WELL", "Well"),
            ("SPRING", "Spring"),
            ("SURFACE_WATER", "Surface Water"),
            ("RAINWATER", "Rainwater"),
            ("TANKER_TRUCK", "Tanker Truck"),
            ("OTHER", "Other"),
        ],
        string="Water Source Type",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    water_distance_minutes = fields.Integer(string="Water Distance (Minutes)")
    # Not part of the DCI spec. Usable with the DB connector only.
    sanitation_type = fields.Selection(
        selection=[
            ("FLUSH_TOILET", "Flush Toilet"),
            ("PIT_LATRINE", "Pit Latrine"),
            ("COMPOSTING_TOILET", "Composting Toilet"),
            ("SHARED", "Shared"),
            ("OPEN", "Open"),
            ("OTHER", "Other"),
        ],
        string="Sanitation Type",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    lighting_source = fields.Selection(
        selection=[
            ("GRID", "Grid"),
            ("SOLAR", "Solar"),
            ("GENERATOR", "Generator"),
            ("KEROSENE", "Kerosene"),
            ("CANDLE", "Candle"),
            ("NONE", "None"),
        ],
        string="Lighting Source",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    cooking_fuel_type = fields.Selection(
        selection=[
            ("ELECTRICITY", "Electricity"),
            ("GAS", "Gas"),
            ("KEROSENE", "Kerosene"),
            ("CHARCOAL", "Charcoal"),
            ("FIREWOOD", "Firewood"),
            ("BIOMASS", "Biomass"),
            ("OTHER", "Other"),
        ],
        string="Cooking Fuel Type",
    )
    # Not part of the DCI spec. Usable with the DB connector only.
    mobile_phone_type = fields.Selection(
        selection=[
            ("NONE", "None"),
            ("BASIC", "Basic"),
            ("SMARTPHONE", "Smartphone"),
        ],
        string="Mobile Phone Type",
    )

    # Not part of the DCI spec. Usable with the DB connector only.
    husband_dead = fields.Boolean(string="Is Husband Dead")
    # Not part of the DCI spec. Usable with the DB connector only.
    husband_death_date = fields.Datetime(string="Husband Death Date")
