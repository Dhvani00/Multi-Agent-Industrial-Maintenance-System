import os

def synthesize_with_llm(question, evidence):
    """Optional OpenAI synthesis. Returns None when not configured or unavailable."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        response = client.chat.completions.create(
            model=model,
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an industrial maintenance analysis assistant. "
                        "Use only the supplied evidence. Do not invent causes, dates, "
                        "measurements, or maintenance actions. Distinguish statistical "
                        "anomalies from confirmed faults. If evidence is insufficient, say so. "
                        "Give a concise summary, evidence, uncertainties, and safe next checks. "
                        "State that recommendations require qualified human review."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Question: {question}\n\nEvidence:\n{evidence}",
                },
            ],
        )
        return response.choices[0].message.content
    except Exception:
        return None
