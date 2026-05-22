from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import logging
import json

app = FastAPI(title="Valkyrie AI Incident Engine", version="1.0.0")

class AlertPayload(BaseModel):
    alerts: list
    commonLabels: dict
    commonAnnotations: dict

logger = logging.getLogger("valkyrie-ai-engine")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3" # or user's preferred model

@app.post("/webhook")
async def handle_alert(payload: Request):
    """
    Ingest Prometheus alerts via webhook.
    """
    data = await payload.json()
    alerts = data.get("alerts", [])
    
    responses = []
    for alert in alerts:
        status = alert.get("status")
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        
        # In a real scenario, we would query Loki/Tempo here using the labels.
        incident_context = f"Alert: {labels.get('alertname')} - {annotations.get('description')}"
        
        # Analyze with local LLM
        analysis = await analyze_incident_with_llm(incident_context)
        responses.append(analysis)
        
    return {"status": "success", "analysis": responses}

async def analyze_incident_with_llm(context: str):
    """
    Sends the context to a local Ollama instance for analysis.
    Falls back to a structured mock response if Ollama is unreachable.
    """
    prompt = f"""
    You are an SRE AI assistant. Analyze the following incident context and output a JSON response.
    Context: {context}
    
    Required JSON format:
    {{
      "incident": "Short description of the incident",
      "probable_cause": "Likely root cause",
      "severity": "high/medium/low",
      "recommended_action": "Action to fix it"
    }}
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OLLAMA_URL, json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }, timeout=10.0)
            
            if response.status_code == 200:
                result = response.json()
                return json.loads(result.get("response", "{}"))
    except Exception as e:
        logger.warning(f"Ollama not reachable or failed. Using fallback. Error: {e}")
        
    # Fallback
    return {
      "incident": "API latency spike",
      "probable_cause": "Redis saturation",
      "severity": "high",
      "recommended_action": "Scale Redis deployment"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
