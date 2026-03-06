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


GROQ_API_KEY = "gsk_tu_clave_larga_aqui..." # RECUERDA PONER TU CLAVE
groq_client = Groq(api_key=settings.GROQ_API_KEY)
MODELO_GROQ = "llama-3.3-70b-versatile"

#TODO: el dia debe cambiar segun la fecha actual
@agent_router.post("/generate", response_model=AgentResponse)
def ask_agent(request: AgentRequest, current_user: UserDB = Depends(get_current_user)):
    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    system_prompt = f"""Eres un asistente experto en moda. El usuario te dará un plan o evento.
    Tu tarea es extraer datos y responder ESTRICTAMENTE con un objeto JSON válido (sin texto antes ni después) con estas claves:
    - "ciudad": nombre de la ciudad
    - "fecha": la fecha calculada en formato YYYY-MM-DD (ten en cuenta que HOY es {fecha_actual})
    - "estilo": elige según el que más se adecua al plan ESTRICTAMENTE uno de: ["Casual", "Formal", "Streetwear", "Bohemian", "Sporty", "Elegant", "Vintage", "Minimalist"]
    - "clima": deduce el clima típico de esa ciudad en esa fecha y elige ESTRICTAMENTE uno de: ["Summer", "Winter", "Transitional"]
    - "mensaje_respuesta": Un mensaje amigable de 1 o 2 líneas dirigido al usuario, confirmando el plan, la ciudad y el estilo que vas a buscar.
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