import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from groq import Groq
from ..core.security import get_current_user
from ..db.models import UserDB
from .schemas import AgentRequest, AgentResponse
from ..core.config import settings

logger = logging.getLogger(__name__)

agent_router = APIRouter(prefix="/agent", tags=["AI Agent"])


groq_client = Groq(api_key=settings.GROQ_API_KEY)
MODELO_GROQ = "llama-3.3-70b-versatile"

@agent_router.post("/generate", response_model=AgentResponse)
def ask_agent(request: AgentRequest, current_user: UserDB = Depends(get_current_user)):
    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    system_prompt = f"""You are an expert fashion assistant. The user will give you a plan or event.
    Your task is to extract data and reply STRICTLY with a valid JSON object (no text before or after) containing these exact keys:
    - "ciudad": the name of the city.
    - "fecha": the calculated date in YYYY-MM-DD format (keep in mind that TODAY is {fecha_actual}).
    - "estilo": choose the style that best fits the plan, STRICTLY one of: ["Casual", "Formal", "Streetwear", "Bohemian", "Sporty", "Elegant", "Vintage", "Minimalist"].
    - "clima": deduce the typical weather for that city on that date and STRICTLY choose one of: ["Summer", "Winter", "Transitional"].
    - "mensaje_respuesta": A friendly 1 or 2-line message written in English, addressed to the user, confirming the plan, the city, and the style you are going to look for.
    """

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.prompt}
            ],
            model=MODELO_GROQ,
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        result_json_str = chat_completion.choices[0].message.content
        extracted_data = json.loads(result_json_str)
        
        return AgentResponse(
            agent_reply=extracted_data.get("mensaje_respuesta", ""),
            extracted_data=extracted_data,
            weather=extracted_data.get("clima", "Transitional") 
        )

    except Exception as e:
        logger.exception("Error en el agente: %s", e)
        raise HTTPException(status_code=500, detail="Error al procesar la petición del agente.")