from fastapi import FastAPI, HTTPException
import requests
import json
import os
import io
from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

app = FastAPI()

app.add.middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class IdeaModel(BaseModel):
    name: str
    mission: str
    goals: List[str]
    targetMarket: Dict[str, Any]
    primaryProduct: str
    sdgs: List[str]

class ChatRequest(BaseModel):
    # name: str
    idea: IdeaModel

@app.post("/business-plan-roadmap")
async def getPlanning(request: ChatRequest):
    try:
        request_json = request.json()
        response = requests.post(
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateConten?key=" + GEMINI_API_KEY,
            headers={
                "Content-Type": "application/json",
            },
            json={
                "system_instruction": {
                    "parts": {
                        "text": "You are Neko the cat respond like one"
                    },
                    "contents": {
                        "parts": {
                            "text": {
                                "Good morning how are you"
                            }
                        }
                    }
                }
            }
        )

        response.raise_for_status()
        result = response.json()
        return response
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling Gemini API: {str(e)}")