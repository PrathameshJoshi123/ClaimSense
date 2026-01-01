from pydantic import BaseModel, Field
from typing import Dict, List, Union, Optional

class PolicyMetadata(BaseModel):
    policy_id_uin: Optional[str]
    insurer: str
    policy_name: str
    overall_security_score: float

class RoomRentLimit(BaseModel):
    limit_type: str
    value: Optional[Union[str, float]]
    proportionate_deduction: bool
    excludes_icu_and_pharmacy: bool

class CoPay(BaseModel):
    percentage: float
    is_entry_age_based: bool
    threshold_age: Optional[int]
    is_zone_based: bool

class WaitingPeriodsMonths(BaseModel):
    initial: Optional[int]
    specific_illnesses: Optional[int]
    pre_existing_diseases: Optional[int]

class ModernTreatment(BaseModel):
    covered: bool
    limit: str

class RiskAnalysis(BaseModel):
    hidden_clauses: List[str]
    negative_features: List[str]
    positive_features: List[str]

class NoticePeriod(BaseModel):
    planned_hours: Optional[int]
    emergency_hours: Optional[int]

class PolicyDNA(BaseModel):
    policy_metadata: PolicyMetadata
    room_rent_limit: RoomRentLimit
    co_pay: CoPay
    waiting_periods_months: WaitingPeriodsMonths
    modern_treatments: Dict[str, ModernTreatment]
    risk_analysis: RiskAnalysis
    notice_period: NoticePeriod
    non_payable_items: List[str]
    plain_english_summary: str
    sum_insured: float = 0.0  # Added for simulation logic
    user_entry_age: int = 40  # Added for simulation logic
