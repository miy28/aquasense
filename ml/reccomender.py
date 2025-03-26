"""
recommender.py

this file activates after an anomaly is found and will give user a prompt that they can digest and use.

Purpose:
Hosts the logic for generating personalized, context-aware feedback
using fine-tuned large language models (LLMs). This will take flagged anomalies,
analyze user trends, and return natural language explanations or recommendations.

In the future, this will:
- Connect to a fine-tuned LLM or OpenAI API
- Generate alerts like "Water temperature is unusually high—consider moving tank"
- Personalize responses based on user history
"""
