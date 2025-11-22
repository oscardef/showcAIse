from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import sys
sys.path.append('/app')

app = FastAPI(title="Analytics Service")


class AggregateRequest(BaseModel):
    session_id: str
    speech_results: Dict
    vision_results: Dict


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "analytics"}


@app.post("/aggregate")
async def aggregate_results(request: AggregateRequest):
    """Aggregate analysis results and generate recommendations."""
    # TODO: Implement analytics aggregation
    # - Combine speech and vision results
    # - Generate personalized recommendations
    # - Calculate overall scores
    # - Store in database
    
    recommendations = [
        "Reduce filler words by 40%",
        "Maintain eye contact more consistently",
        "Improve posture - stand straighter",
        "Vary your tone more for emphasis"
    ]
    
    return {
        "session_id": request.session_id,
        "status": "completed",
        "recommendations": recommendations
    }
