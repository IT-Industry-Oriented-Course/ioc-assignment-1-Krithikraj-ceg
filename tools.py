# tools.py

def search_patient(name: str):
    return {
        "patient_id": "PAT001",
        "name": name,
        "dob": "1992-04-10"
    }

def check_insurance_eligibility(patient_id: str):
    return {
        "patient_id": patient_id,
        "provider": "ABC Health",
        "eligible": True
    }

def find_available_slots(specialty: str, timeframe: str):
    return [
        {
            "slot_id": "SLOT123",
            "doctor": "Dr. Sharma",
            "time": "2025-12-23 10:00"
        }
    ]

def book_appointment(patient_id: str, slot_id: str):
    return {
        "appointment_id": "APT789",
        "status": "CONFIRMED"
    }
