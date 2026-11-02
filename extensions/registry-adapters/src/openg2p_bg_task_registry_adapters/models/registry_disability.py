from openg2p_pbms_models.models import G2PRegistry
from sqlalchemy import JSON, Boolean, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class G2PDisabilityRegistry(G2PRegistry):
    __tablename__ = "g2p_register_persons_with_disability"

    # G2PRegister identity fields
    functional_record_id: Mapped[str] = mapped_column(String, nullable=True)
    link_internal_record_id: Mapped[str] = mapped_column(String, nullable=True)
    link_foundational_id: Mapped[str] = mapped_column(String, nullable=True)
    record_name: Mapped[str] = mapped_column(String, nullable=True)
    record_status: Mapped[str] = mapped_column(String, nullable=True)
    record_status_reason: Mapped[str] = mapped_column(String, nullable=True)

    # Person (DO.DR.01 DRPerson, DO.DR.02 Member)
    foundational_id: Mapped[str] = mapped_column(String, nullable=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    middle_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    given_name: Mapped[str] = mapped_column(String, nullable=True)
    prefix: Mapped[str] = mapped_column(String, nullable=True)
    suffix: Mapped[str] = mapped_column(String, nullable=True)
    gender: Mapped[str] = mapped_column(String, nullable=True)
    birth_date: Mapped[Date] = mapped_column(Date, nullable=True)
    phone_numbers: Mapped[list] = mapped_column(JSON, nullable=True)
    emails: Mapped[list] = mapped_column(JSON, nullable=True)
    marital_status: Mapped[str] = mapped_column(String, nullable=True)
    occupation: Mapped[str] = mapped_column(String, nullable=True)
    income_level: Mapped[str] = mapped_column(String, nullable=True)
    language_code: Mapped[str] = mapped_column(String, nullable=True)
    education_level: Mapped[str] = mapped_column(String, nullable=True)
    registration_date: Mapped[Date] = mapped_column(Date, nullable=True)

    # Geo
    latitude: Mapped[str] = mapped_column(String, nullable=True)
    longitude: Mapped[str] = mapped_column(String, nullable=True)
    altitude: Mapped[str] = mapped_column(String, nullable=True)
    plus_code: Mapped[str] = mapped_column(String, nullable=True)
    address_line_1: Mapped[str] = mapped_column(String, nullable=True)
    address_line_2: Mapped[str] = mapped_column(String, nullable=True)
    postal_code: Mapped[str] = mapped_column(String, nullable=True)
    country_code: Mapped[str] = mapped_column(String, nullable=True)
    geo_lowest_level_value_id: Mapped[str] = mapped_column(String, nullable=True)
    geo_code_hierarchy_json: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Identity and provenance
    foundational_id_masked: Mapped[str] = mapped_column(String, nullable=True)
    foundational_id_verification_status: Mapped[str] = mapped_column(
        String, nullable=True
    )
    identity_evidence_type: Mapped[str] = mapped_column(String, nullable=True)
    registration_channel: Mapped[str] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    death_date: Mapped[Date] = mapped_column(Date, nullable=True)
    estimated_age: Mapped[int] = mapped_column(Integer, nullable=True)

    # DO.DR.02 self-identification and socio-economic attributes
    self_id_disability: Mapped[bool] = mapped_column(Boolean, nullable=True)
    employment_status: Mapped[str] = mapped_column(String, nullable=True)

    # DO.DR.03 assessed status
    disability_status: Mapped[str] = mapped_column(String, nullable=True)
    disability_status_level: Mapped[str] = mapped_column(String, nullable=True)
    support_needs_level: Mapped[str] = mapped_column(String, nullable=True)
    assessment_date: Mapped[Date] = mapped_column(Date, nullable=True)
    assessment_authority: Mapped[str] = mapped_column(String, nullable=True)
    disability_certificate_number: Mapped[str] = mapped_column(String, nullable=True)
    certificate_issue_date: Mapped[Date] = mapped_column(Date, nullable=True)
    certificate_expiry_date: Mapped[Date] = mapped_column(Date, nullable=True)
    next_reassessment_date: Mapped[Date] = mapped_column(Date, nullable=True)

    # DO.DR.03 living situation and mobility
    transport_requirement: Mapped[str] = mapped_column(String, nullable=True)
    housing_type: Mapped[str] = mapped_column(String, nullable=True)
    lives_alone: Mapped[bool] = mapped_column(Boolean, nullable=True)

    # Accessibility, capacity and contact
    communication_needs: Mapped[list] = mapped_column(JSON, nullable=True)
    preferred_contact_method: Mapped[str] = mapped_column(String, nullable=True)
    legal_capacity_status: Mapped[str] = mapped_column(String, nullable=True)
    guardian_required: Mapped[bool] = mapped_column(Boolean, nullable=True)

    # Support sub-register summary, recomputed by the registry
    unmet_support_needs_count: Mapped[int] = mapped_column(Integer, nullable=True)
    has_unmet_support_need: Mapped[bool] = mapped_column(Boolean, nullable=True)
