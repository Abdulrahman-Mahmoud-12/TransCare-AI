import json
from ai_modules.rag_assistant.retriever import retrieve_context
from ai_modules.rag_assistant.llm import generate_answer

async def run_rag_pipeline(user_query: str):
    """
    Coordinates the complete RAG cycle: retrieves matching database context files,
    prompts Gemini, and parses structured payloads safely back to the FastAPI router.
    
    Returns:
        tuple: (reply_text, rich_data_dict_or_none)
    """
    try:
        # 1. Look up data inside Chroma database
        context = retrieve_context(user_query, k=3)
        
        # 2. Forward context to your Gemini generation engine
        raw_json_response = await generate_answer(user_query, context)
        
        # 3. Safely decode the structural output
        parsed_response = json.loads(raw_json_response)
        
        reply_text = parsed_response.get("text", "I found matching records for that request.")
        rich_data = parsed_response.get("data", None)
        
        return reply_text, rich_data
        
    except Exception as e:
        print(f"[PIPELINE RUNTIME CRASH] Failure during lifecycle processing: {str(e)}")
        # Clean safe degradation fallback message to prevent app visualization crashes
        fallback_text = "I'm having a little trouble checking our store records right now, but I'll be back shortly!"
        return fallback_text, None