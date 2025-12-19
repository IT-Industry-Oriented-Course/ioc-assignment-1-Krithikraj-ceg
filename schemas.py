# schemas.py

FUNCTION_SCHEMAS = {
    "search_patient": ["name"],
    "check_insurance_eligibility": ["patient_id"],
    "find_available_slots": ["specialty", "timeframe"],
    "book_appointment": ["patient_id", "slot_id"]
}
