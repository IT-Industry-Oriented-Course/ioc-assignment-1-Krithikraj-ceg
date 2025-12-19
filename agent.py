# agent.py

import json
from huggingface_hub import InferenceClient

from tools import *
from schemas import FUNCTION_SCHEMAS

# -------------------------------------------------
# LLM SETUP
# -------------------------------------------------
# Uses token from: huggingface-cli login

llm = InferenceClient(
    model="HuggingFaceH4/zephyr-7b-beta"
)

SYSTEM_PROMPT = """
You are a clinical workflow orchestration agent.

STRICT RULES:
- You MUST NOT give medical advice
- You MUST output ONLY valid JSON
- Do NOT include explanations, markdown, or comments
- Do NOT invent IDs (patient_id, slot_id)
- Use "FROM_CONTEXT" where an ID is required

Allowed functions:
- search_patient(name)
- check_insurance_eligibility(patient_id)
- find_available_slots(specialty, timeframe)
- book_appointment(patient_id, slot_id)

IMPORTANT:
- For check_insurance_eligibility → patient_id = "FROM_CONTEXT"
- For book_appointment → patient_id & slot_id = "FROM_CONTEXT"

OUTPUT FORMAT:
{
  "steps": [
    {
      "function": "<function_name>",
      "arguments": { "<key>": "<value>" }
    }
  ]
}
"""

# -------------------------------------------------
# LLM → PLAN GENERATION (ROBUST)
# -------------------------------------------------

def get_llm_plan(user_input: str):
    response = llm.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        max_tokens=300
    )

    content = response.choices[0].message.content

    if not content or not content.strip():
        raise ValueError("LLM returned empty response")

    # Extract JSON safely
    start = content.find("{")
    end = content.rfind("}") + 1

    if start == -1 or end == 0:
        raise ValueError("No JSON found in LLM output")

    return json.loads(content[start:end])


# -------------------------------------------------
# AGENT EXECUTION
# -------------------------------------------------

def run_agent(user_input: str):
    # Retry once if LLM fails

    if "insurance" in user_input.lower():
      user_input += "\nEnsure you identify the patient before checking insurance."

    try:
        plan = get_llm_plan(user_input)
    except Exception:
        strict_input = user_input + "\nReturn ONLY valid JSON."
        plan = get_llm_plan(strict_input)

    audit_log = []
    context = {}

    for step in plan.get("steps", []):
        fn = step.get("function")
        args = step.get("arguments", {})

        # Inject runtime context
        if fn == "check_insurance_eligibility":
            args["patient_id"] = context.get("patient_id")

        if fn == "book_appointment":
            args["patient_id"] = context.get("patient_id")
            args["slot_id"] = context.get("slot_id")

        # Schema validation
        required_fields = FUNCTION_SCHEMAS.get(fn)
        if not required_fields:
            return {"status": "FAILED", "reason": f"Unknown function {fn}"}

        for field in required_fields:
            if field not in args or args[field] is None:
                return {
                    "status": "FAILED",
                    "reason": f"Missing field '{field}' for function '{fn}'"
                }

        # Execute tools
        if fn == "search_patient":
            result = search_patient(**args)
            context["patient_id"] = result["patient_id"]

        elif fn == "check_insurance_eligibility":
            result = check_insurance_eligibility(**args)

        elif fn == "find_available_slots":
            result = find_available_slots(**args)
            context["slot_id"] = result[0]["slot_id"]

        elif fn == "book_appointment":
            result = book_appointment(**args)

        audit_log.append({
            "function": fn,
            "arguments": args,
            "output": result
        })

    return {
        "status": "SUCCESS",
        "audit_log": audit_log
    }


# -------------------------------------------------
# RUN LOOP
# -------------------------------------------------

if __name__ == "__main__":
    while True:
        user_input = input("\nEnter request: ")
        if user_input.lower() == "exit":
            break

        result = run_agent(user_input)
        print(json.dumps(result, indent=2))

