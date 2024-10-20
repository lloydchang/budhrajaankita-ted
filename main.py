from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import os
from pydantic import BaseModel
from typing import List, Dict, Any
from fpdf import FPDF
from fastapi.responses import FileResponse
import io
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
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from fastapi import FastAPI, HTTPException, Response
import requests

def text_to_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    flowables = []

    for line in text.split('\n'):
        para = Paragraph(line, styles['Normal'])
        flowables.append(para)

    doc.build(flowables)
    buffer.seek(0)
    return buffer.getvalue()




OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class IdeaModel(BaseModel):
    name: str
    mission: str
    goals: List[str]
    targetMarket: Dict[str, Any]
    primaryProduct: str
    sdgs: List[str]

class ChatRequest(BaseModel):
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



@app.post("/getGrantProposal")
async def getGrantProposal(request: ChatRequest):
    try:
        # request_json = request.json()
        idea_description = request.json()
        
        prompt = f"""Write a persuasive grant proposal for a non-profit organization based on this {idea_description}. Include:

1. A captivating executive summary that highlights the problem, your solution, and potential impact
2. A clear problem statement with supporting data and real-world examples
3. Your organization's unique approach and proposed solution
4. Specific, measurable goals and objectives
5. A detailed implementation plan with timeline and milestones
6. Expected outcomes and how you'll measure success
7. A realistic budget breakdown
8. Your team's qualifications and relevant experience
9. Sustainability plan for long-term impact
10. Compelling conclusion that reinforces the urgency and importance of your project

Use a conversational yet professional tone, incorporate storytelling elements, and emphasize the human impact of your work. Provide concrete examples and data to support your claims. Tailor the proposal to align with the goals and values of potential funders."""

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
                        "content": "You are a helpful assistant, expert in writing grant proposals for non-profits. Provide compelling, concise and accurate responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            propContent = response.json()["choices"][0]["message"]["content"]

            pdf_bytes = text_to_pdf(propContent)
            # Return the PDF as a downloadable file
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=grant_proposal.pdf"}
            )
                # return FileResponse(
                #     pdf_buffer,
                #     media_type="application/pdf",
                #     headers={"Content-Disposition": "attachment; filename=grant_proposal.pdf"}
                # )


        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from OpenRouter API")
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenRouter API: {str(e)}")


