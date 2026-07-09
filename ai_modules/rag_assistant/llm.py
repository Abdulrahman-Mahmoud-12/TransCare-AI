import os
from groq import Groq
from ai_modules.rag_assistant.prompt import build_system_prompt

# Initialize client using GROQ_API_KEY pulled directly from your environmental session
# (Groq's SDK reads GROQ_API_KEY automatically if the api_key arg is omitted)
client = Groq()

async def generate_answer(query: str, context: str) -> str:
    """
    Submits user text along with retrieved database facts to a Groq-hosted model.
    """
    model_name = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")

    # Populate the system rules with the real-time pulled database context
    formatted_system_instruction = build_system_prompt(context)

    try:
        # Request content from Groq (OpenAI-compatible chat.completions interface)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": formatted_system_instruction},
                {"role": "user", "content": f"Customer Question: {query}"},
            ],
            temperature=0.1,  # Keeps behavior strictly factual
            response_format={"type": "json_object"},  # Forces JSON response layout
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"[LLM ERROR] Groq content generation failed: {str(e)}")
        raise e