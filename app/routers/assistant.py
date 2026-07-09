from fastapi import APIRouter, HTTPException
from app.schemas.assistant import AssistantQuery, AssistantResponse
from ai_modules.rag_assistant.rag_pipeline import run_rag_pipeline

router = APIRouter(prefix="/api/customer/assistant", tags=["AI Assistant"])

@router.post("/", response_model=AssistantResponse)
async def chat_with_assistant(payload: AssistantQuery):
    try:
        reply_text, rich_data = await run_rag_pipeline(payload.text)
        return AssistantResponse(text=reply_text, data=rich_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Pipeline Error: {str(e)}")