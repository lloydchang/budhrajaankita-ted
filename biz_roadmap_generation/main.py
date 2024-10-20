# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"message": "Hello, FastAPI!"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str = None):
#     return {"item_id": item_id, "query": q}

# Ankita's code
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import os
from pydantic import BaseModel
from typing import List, Dict, Any
from dotenv import load_dotenv
load_dotenv()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# OPENROUTER_API_KEY="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"

class IdeaModel(BaseModel):
    name: str
    goals: List[str]
    targetMarket: Dict[str, Any]
    geography: Dict[str, Any]
    keyPrograms: List[str]
    missionStatement: str

class ChatRequest(BaseModel):
    name: str
    idea: IdeaModel

# class ChatRequest(BaseModel):
#     message: str


@app.post("/investors")
async def getInvestors(request: ChatRequest):
    try:
        request_json = request.json()
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            },
           json={
                "model": "meta-llama/llama-3.2-3b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant, expert in starting non profits. Provide concise and accurate responses."
                    },
                    {
                        "role": "user",
                        # "content": "Considering this particular idea, Please provide steps on how I can connect with investors and list the investors I can potentially connect with, steps to take, and things to keep in mind during this."
                        "content": "The JSON file I provided contains the content of my non-profit idea. Use this to identify potential investors for my non-profit. Create a list of what categories of entities would be interested in investing in non-profits with a mission like mine. Examples of entity categories can be corporations, celebrities, or charities. Create a list of names for each category of entities. Each list should include at least 2 names. Your output should be in markdown format"
                    },
                    {
                        "role": "user",
                        "content": request_json
                    }
                ]
            }
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from OpenRouter API")
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenRouter API: {str(e)}")



@app.post("/grantInfo")
async def getGrantInfo(request: ChatRequest):
    try:
        request_json = request.json()
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            },
           json={
                "model": "meta-llama/llama-3.2-3b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant, expert in starting non profits. Provide concise and accurate responses."
                    },
                    {
                        "role": "user",
                        # "content": "Considering this particular idea, Please provide steps on how I can connect with investors and list the investors I can potentially connect with, steps to take, and things to keep in mind during this."
                        "content": "The JSON file I provided contains the content of my non-profit idea. Use this to identify potential grants I can apply to, for my non-profit. Create a list of entities that would be interested in providing grants to non-profits with a mission like mine. Your output should be in markdown format"
                    },
                    {
                        "role": "user",
                        "content": request_json
                    }
                ]
            }
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from OpenRouter API")
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenRouter API: {str(e)}")



# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)