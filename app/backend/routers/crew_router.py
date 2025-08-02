from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.crew_service import run_crew

router = APIRouter()

class CrewInput(BaseModel):
    text: str

@router.post("/")
def run_crew_pipeline(input_data: CrewInput):
    return run_crew(input_data.text)
