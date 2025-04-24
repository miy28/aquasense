# backend/llm_server.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)
CORS(app)

# Load a compact causal model for on-device inference
MODEL_NAME = "distilgpt2"  
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model     = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

@app.route('/infer', methods=['POST'])
def infer():
    """
    Expects JSON { "prompt": "<your prompt text>" }
    Returns     { "text": "<LLM generated text>" }
    """
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"text": ""}), 400

    # Tokenize and move to model
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
        do_sample=True,
        top_p=0.9,
        temperature=0.8,
        pad_token_id=tokenizer.eos_token_id
    )

    # Decode full output (prompt + generated) and strip the prompt
    full = tokenizer.decode(outputs[0], skip_special_tokens=True)
    continuation = full[len(prompt):].strip()

    return jsonify({"text": continuation})

if __name__ == "__main__":
    # Start on port 8000 to match your recommend() proxy
    app.run(host="0.0.0.0", port=8000)
