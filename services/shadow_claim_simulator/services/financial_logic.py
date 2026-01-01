from datetime import datetime, timedelta
from services.shadow_claim_simulator.schemas.models import PayoutSimulationResponse, ShavedPayoutBreakdown

def calculate_shaved_payout(policy_dna_shaving: dict, modern_treatments: dict, non_payable_items: list, 
                            hospital_bill: list, stay_context: dict, sum_insured: float) -> ShavedPayoutBreakdown:
    
    # 1. Setup Normalization
    allowed_room_category = policy_dna_shaving.get("allowed_room_category", "Private Single A/C Room")
    shaving_applies = policy_dna_shaving.get("shaving_applies", True)
    protected_categories = policy_dna_shaving.get("protected_categories", ["ICU", "Pharmacy", "Implants", "Diagnostics"])
    
    # Slugify modern treatments (remove spaces/case) for fuzzy matching
    normalized_modern_map = {"".join(k.lower().split()): v for k, v in modern_treatments.items()}
    # Normalize non-payables for exact upper-case matching
    non_payables_set = {item.strip().upper() for item in non_payable_items}
    
    # 2. Multiplier Calculation
    actual_rent = stay_context.get("actual_rent", 0)
    eligible_rate = stay_context.get("eligible_category_rate", 0)
    multiplier = 1.0
    if shaving_applies and stay_context.get("chosen_category") != allowed_room_category:
        if actual_rent > 0 and eligible_rate > 0:
            multiplier = min(eligible_rate / actual_rent, 1.0)

    # 3. Process Bill Items
    total_claimed = 0
    admissible_amount = 0
    savings_lost_shaving = 0
    modern_deduction = 0
    non_payable_total = 0

    for item in hospital_bill:
        amount = item['amount']
        total_claimed += amount
        category = item.get('category', 'Associated')
        
        # Step A: Scrub Non-Payables
        if item['name'].strip().upper() in non_payables_set:
            non_payable_total += amount
            continue # Insurance pays 0 for this

        # Step B: Apply Modern Treatment Caps (Slug-based Fuzzy Match)
        item_slug = "".join(item['name'].lower().split())
        current_item_base = amount
        
        for slug, caps in normalized_modern_map.items():
            if slug in item_slug or item_slug in slug:
                cap_str = caps.get(str(int(sum_insured)), "Up to Sum Insured")
                if cap_str != "Up to Sum Insured":
                    cap_limit = float(cap_str)
                    if amount > cap_limit:
                        modern_deduction += (amount - cap_limit)
                        current_item_base = cap_limit
                break

        # Step C: Apply Shaving to the Capped Amount
        if category in protected_categories:
            admissible_amount += current_item_base
        else:
            shaved_val = current_item_base * multiplier
            admissible_amount += shaved_val
            savings_lost_shaving += (current_item_base - shaved_val)

    return ShavedPayoutBreakdown(
        total_claimed=total_claimed,
        admissible_amount=admissible_amount,
        savings_lost_to_shaving=savings_lost_shaving,
        modern_treatment_deduction=modern_deduction,
        non_payable_deduction=non_payable_total
    )

def simulate_payout(policy_dna: dict, hospital_bill: list, stay_context: dict):
    # Prepare Data from DNA
    room_limit_cfg = policy_dna.get("room_rent_limit", {})
    excludes_icu_pharmacy = room_limit_cfg.get("excludes_icu_and_pharmacy", True)
    
    protected = ["ICU", "Pharmacy", "Implants", "Diagnostics"] if excludes_icu_pharmacy else []
    
    policy_shaving_cfg = {
        "allowed_room_category": room_limit_cfg.get("value", "Private Single A/C Room"),
        "shaving_applies": room_limit_cfg.get("proportionate_deduction", True),
        "protected_categories": protected
    }

    # Co-pay Logic
    cp_cfg = policy_dna.get("co_pay", {})
    user_entry_age = policy_dna.get("user_entry_age", 40)
    effective_cp_pct = cp_cfg.get("percentage", 0) / 100
    
    if cp_cfg.get("is_entry_age_based") and user_entry_age < cp_cfg.get("threshold_age", 61):
        effective_cp_pct = 0.0

    sum_insured = policy_dna.get("sum_insured", 0)

    # Execute Core Logic
    shaved_report = calculate_shaved_payout(
        policy_shaving_cfg, 
        policy_dna.get("modern_treatments", {}),
        policy_dna.get("non_payable_items", []),
        hospital_bill, 
        stay_context, 
        sum_insured
    )

    # Final Math
    co_pay_amt = shaved_report.admissible_amount * effective_cp_pct
    estimated_payout = shaved_report.admissible_amount - co_pay_amt
    out_of_pocket = shaved_report.total_claimed - estimated_payout

    # Intervention Advice
    advice = []
    if stay_context.get("actual_rent", 0) > stay_context.get("eligible_category_rate", 0):
        # Calculate potential savings if room is downgraded
        potential_gain = (shaved_report.savings_lost_to_shaving * (1 - effective_cp_pct))
        advice.append(f"Downgrading to {policy_shaving_cfg['allowed_room_category']} could save you ₹{potential_gain:.0f} in 'shaving' penalties.")

    # 48-hour Notice Guard
    admission_str = stay_context.get("admission_date")
    if admission_str:
        try:
            days_to_admission = (datetime.fromisoformat(admission_str) - datetime.now()).total_seconds() / 3600
            if days_to_admission < policy_dna.get("notice_period", {}).get("planned_hours", 48):
                advice.append("CRITICAL: Planned admission notice is < 48hrs. Inform TPA immediately to prevent cashless rejection.")
        except: pass

    return PayoutSimulationResponse(
        summary={
            "total_hospital_bill": shaved_report.total_claimed,
            "estimated_payout": estimated_payout,
            "out_of_pocket_expense": out_of_pocket
        },
        deduction_details={
            "proportionate_deduction": {"amount": shaved_report.savings_lost_to_shaving, "reason": "Associated expenses reduced due to room category upgrade."},
            "non_medical_items": {"amount": shaved_report.non_payable_deduction, "reason": "Excluded consumables scrubbed from bill."},
            "co_pay": {"amount": co_pay_amt, "reason": "Waived based on entry age." if effective_cp_pct == 0 else f"Applied at {int(effective_cp_pct*100)}%."},
            "modern_treatment_deduction": {"amount": shaved_report.modern_treatment_deduction, "reason": "Costs exceeded policy sub-limits for advanced procedures."}
        },
        actionable_advice=" | ".join(advice),
        shaved_breakdown=shaved_report
    )
