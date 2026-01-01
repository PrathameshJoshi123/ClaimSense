from pydantic import BaseModel
from typing import List, Dict, Any

class ProcedureMatchRequest(BaseModel):
    query: str

class ProcedureMatchResult(BaseModel):
    procedure: str
    base_cost: float
    standard_room_rate: float
    similarity_score: float

class ProcedureMatchResponse(BaseModel):
    results: List[ProcedureMatchResult]

class HospitalEstimate(BaseModel):
    room_charges: float
    icu_charges: float
    medical_procedures: float

class Selection(BaseModel):
    chosen_room_category: str
    actual_room_rent_per_day: float

class HospitalBillItem(BaseModel):
    name: str
    category: str  # e.g., "Nursing", "ICU", "Pharmacy", "Implants", "Diagnostics", "OT", "Surgeon", "Anesthetist", "Consultant", "Specialist"
    amount: float

class StayContext(BaseModel):
    chosen_category: str
    actual_rent: float
    eligible_category_rate: float
    admission_date: str  # ISO format date string, e.g., "2023-10-01"

class PayoutSimulationRequest(BaseModel):
    hospital_bill: List[HospitalBillItem]
    stay_context: StayContext

class DeductionDetail(BaseModel):
    amount: float
    reason: str

class DeductionDetails(BaseModel):
    proportionate_deduction: DeductionDetail
    non_medical_items: DeductionDetail
    co_pay: DeductionDetail
    modern_treatment_deduction: DeductionDetail

class Summary(BaseModel):
    total_hospital_bill: float
    estimated_payout: float
    out_of_pocket_expense: float

class ShavedPayoutBreakdown(BaseModel):
    total_claimed: float
    admissible_amount: float
    savings_lost_to_shaving: float
    modern_treatment_deduction: float
    non_payable_deduction: float

class PayoutSimulationResponse(BaseModel):
    summary: Summary
    deduction_details: DeductionDetails
    actionable_advice: str
    shaved_breakdown: ShavedPayoutBreakdown  # New field for the shaving logic output
