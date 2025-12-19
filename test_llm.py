import os
from huggingface_hub import InferenceClient

token = os.environ.get("HF_TOKEN")
if not token:
    raise RuntimeError("HF_TOKEN not found")

client = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token=token
)

output = client.text_generation(
    "Say: LLM is working.",
    max_new_tokens=20
)

print(output)
