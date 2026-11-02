from typing import Optional

from .registry import G2PRegistryPayload


class G2PDisabilityRegistryPayload(G2PRegistryPayload):
    functional_record_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    estimated_age: Optional[int] = None
    disability_status: Optional[str] = None
    disability_status_level: Optional[str] = None
    support_needs_level: Optional[str] = None
    unmet_support_needs_count: Optional[int] = None
    has_unmet_support_need: Optional[bool] = None
    employment_status: Optional[str] = None
    housing_type: Optional[str] = None
    country_code: Optional[str] = None
