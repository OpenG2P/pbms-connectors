from openg2p_bg_task_models.models import BeneficiaryListSummary
from sqlalchemy import JSON, Float, String
from sqlalchemy.orm import mapped_column


class BeneficiaryListSummaryDisability(BeneficiaryListSummary):
    __tablename__ = "beneficiary_list_summary_disability"

    estimated_age_q1 = mapped_column(Float, nullable=True, default=0)
    estimated_age_q2 = mapped_column(Float, nullable=True, default=0)
    estimated_age_q3 = mapped_column(Float, nullable=True, default=0)
    estimated_age_mean = mapped_column(Float, nullable=True, default=0)
    estimated_age_units = mapped_column(String, nullable=False, default="years")

    unmet_support_needs_count_q1 = mapped_column(Float, nullable=True, default=0)
    unmet_support_needs_count_q2 = mapped_column(Float, nullable=True, default=0)
    unmet_support_needs_count_q3 = mapped_column(Float, nullable=True, default=0)
    unmet_support_needs_count_mean = mapped_column(Float, nullable=True, default=0)
    unmet_support_needs_count_units = mapped_column(
        String, nullable=False, default="needs"
    )

    average_entitlement_female = mapped_column(JSON, nullable=True)
    average_entitlement_male = mapped_column(JSON, nullable=True)
    entitlement_amount_male_q1 = mapped_column(JSON, nullable=True)
    entitlement_amount_male_q2 = mapped_column(JSON, nullable=True)
    entitlement_amount_male_q3 = mapped_column(JSON, nullable=True)
    entitlement_amount_female_q1 = mapped_column(JSON, nullable=True)
    entitlement_amount_female_q2 = mapped_column(JSON, nullable=True)
    entitlement_amount_female_q3 = mapped_column(JSON, nullable=True)
    entitlement_amount_q1 = mapped_column(JSON, nullable=True)
    entitlement_amount_q2 = mapped_column(JSON, nullable=True)
    entitlement_amount_q3 = mapped_column(JSON, nullable=True)
    entitlement_units = mapped_column(JSON, nullable=True)
