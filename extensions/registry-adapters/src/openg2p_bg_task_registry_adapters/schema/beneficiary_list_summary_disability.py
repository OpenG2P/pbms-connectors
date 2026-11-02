from typing import Optional

from pydantic import BaseModel

from .beneficiary_list_summary import BeneficiaryListSummaryPayload


class BeneficiaryListSummaryDisability(BaseModel):
    estimated_age_mean: Optional[str] = None
    estimated_age_q3: Optional[str] = None
    estimated_age_q2: Optional[str] = None
    estimated_age_q1: Optional[str] = None
    unmet_support_needs_count_mean: Optional[str] = None
    unmet_support_needs_count_q3: Optional[str] = None
    unmet_support_needs_count_q2: Optional[str] = None
    unmet_support_needs_count_q1: Optional[str] = None
    average_entitlement_female: Optional[dict] = None
    average_entitlement_male: Optional[dict] = None
    entitlement_amount_q3: Optional[dict] = None
    entitlement_amount_q2: Optional[dict] = None
    entitlement_amount_q1: Optional[dict] = None
    entitlement_amount_male_q3: Optional[dict] = None
    entitlement_amount_male_q2: Optional[dict] = None
    entitlement_amount_male_q1: Optional[dict] = None
    entitlement_amount_female_q3: Optional[dict] = None
    entitlement_amount_female_q2: Optional[dict] = None
    entitlement_amount_female_q1: Optional[dict] = None


class BeneficiaryListSummaryDisabilityPayload(BeneficiaryListSummaryPayload):
    registry_summary: BeneficiaryListSummaryDisability
