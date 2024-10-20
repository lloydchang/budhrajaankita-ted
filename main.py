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
from elevenlabs import text_to_speech
from elevenlabs.client import ElevenLabs
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from fastapi import FastAPI, HTTPException, Response
import requests
from pydub.playback import play as pydub_play
from pydub import AudioSegment

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

ElevenLabs.api_key = os.getenv("ELEVENLABS_API_KEY")


client = ElevenLabs(
  api_key=ElevenLabs.api_key
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


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
            return response.json()["choices"][0]["message"]["content"]

            # pdf_bytes = text_to_pdf(propContent)
            # # Return the PDF as a downloadable file
            # return Response(
            #     content=pdf_bytes,
            #     media_type="application/pdf",
            #     headers={"Content-Disposition": "attachment; filename=grant_proposal.pdf"}
            # )
            #     # return FileResponse(
            #     #     pdf_buffer,
            #     #     media_type="application/pdf",
            #     #     headers={"Content-Disposition": "attachment; filename=grant_proposal.pdf"}
            #     # )


        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from OpenRouter API")
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenRouter API: {str(e)}")



@app.post("/generatePitchText")
async def generatePitchText(request: ChatRequest):
    try:

        request_json = request.json()
        prompt = f"""Create the transcript for a short compelling elevator pitch for this project {request_json} that aligns with the United Nations Sustainable Development Goals (SDGs). It should include:
        A Clear Introduction: Briefly introduce the project or idea and its relevance to sustainability.
        The Problem Statement: Identify the specific environmental or social issue your idea addresses.
        The Solution: Explain how your project provides a unique and effective solution to this problem.
        Impact on SDGs: Highlight how your idea contributes to one or more SDGs, particularly focusing on climate action, clean water, or sustainable communities.
        Call to Action: Encourage listeners to get involved, support the project, or learn more.
        Make sure the pitch is engaging, concise (around 30-60 seconds), and emotionally resonant, appealing to the audience's sense of responsibility towards a sustainable future. Only generate the transcript, no ** or ##. Just output the transcript."""

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
                        "content": "You are a helpful assistant, expert in CREATING STELLAR elevator pitches for non-profits. Provide concise and accurate responses."
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
            return response.json()["choices"][0]["message"]["content"]
            # cont = result["choices"][0]["message"]["content"]
            # return {"pitch_text": cont}
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from OpenRouter API")

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenRouter API: {str(e)}")




@app.post("/generatePitchAudio")
async def generatePitchAudio(pitch_text: str):
    try:
        audio_generator = client.generate(
            text=pitch_text,
            voice="bIHbv24MWmeRgasZH58o"
        )

        audio_chunks = b''.join(chunk for chunk in audio_generator)

        with open("pitch.wav", "wb") as f:
            f.write(audio_chunks)

        return FileResponse("pitch.wav", media_type="audio/wav", filename="pitch.wav")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")



# @app.post("/generatePitch")
# async def generatePitch(request: ChatRequest):
#     try:
#         prompt = f"""Create the transcript for a short compelling elevator pitch for this project {request_json} that aligns with the United Nations Sustainable Development Goals (SDGs). It should include:
# A Clear Introduction: Briefly introduce the project or idea and its relevance to sustainability.
# The Problem Statement: Identify the specific environmental or social issue your idea addresses.
# The Solution: Explain how your project provides a unique and effective solution to this problem.
# Impact on SDGs: Highlight how your idea contributes to one or more SDGs, particularly focusing on climate action, clean water, or sustainable communities.
# Call to Action: Encourage listeners to get involved, support the project, or learn more.
# Make sure the pitch is engaging, concise (around 30-60 seconds), and emotionally resonant, appealing to the audience's sense of responsibility towards a sustainable future. Only generate the transcript, no ** or ##. Just output the transcript."""

#         response = requests.post(
#             url="https://openrouter.ai/api/v1/chat/completions",
#             headers={
#                 "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#             },
#             json={
#                 "model": "meta-llama/llama-3.2-3b-instruct:free",
#                 "messages": [
#                     {
#                         "role": "system",
#                         "content": "You are a helpful assistant, expert in CREATING STELLAR elevator pitches for non-profits. Provide concise and accurate responses."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ]
#             }
#         )

#         response.raise_for_status()
#         result = response.json()
        
#         if "choices" in result and len(result["choices"]) > 0:
#             cont =  response.json()["choices"][0]["message"]["content"]



#             audio_generator = client.generate(
#                 text=cont,
#                 voice="bIHbv24MWmeRgasZH58o"
#                 # "cjVigY5qzO86Huf0OWal"
#             )

#             audio_chunks = b''.join(chunk for chunk in audio_generator)

#             try:
#                 with open("pitch.wav", "wb") as f:
#                     f.write(audio_chunks)

#                 if os.path.exists("pitch.wav"):
#                     audio_segment = AudioSegment.from_wav("pitch.wav")
#                     pydub_play(audio_segment)
#                 else:
#                     print("Error: pitch.wav file not found")

#             except Exception as e:
#                 print(f"Error playing audio: {str(e)}")
                
#             # with open("pitch.wav", "wb") as f:
#             #     f.write(audio_chunks)

#             # # Play the audio using pydub
#             # audio_segment = AudioSegment.from_wav("pitch.wav")
#             # pydub_play(audio_segment)

#     except requests.RequestException as e:
#         raise HTTPException(status_code=500, detail=f"Error calling OpenRouter API: {str(e)}")


# # request_json = request.json()
#         idea_description = request.json()
        
#         import requests

#         url = "https://studio.infinity.ai/api/v2/generate"
#         headers = {
#             "accept": "application/json",
#             "authorization": "Bearer YOUR_API_TOKEN",
#             "content-type": "application/json"
#         }
#         data = {
#             "resolution": "320",
#             "crop_head": False,
#             "make_stable": False,
#             "img_url": "https://6ammc3n5zzf5ljnz.public.blob.vercel-storage.com/inf2-defaults/cool_man-AZGi3AIjUGN47rGxA8xdHMBGr1Qqha.png",
#             "audio_url": "https://6ammc3n5zzf5ljnz.public.blob.vercel-storage.com/cool_man-eUP4h3ET8OHCP2ScZvei5CVnQUx2Mi.mp3"
#         }

#         response = requests.post(url, headers=headers, json=data)

#         print(response.json())
#     except requests.RequestException as e:
#         raise HTTPException(status_code=500, detail=f"Error calling OpenRouter API: {str(e)}")

from biz_roadmap_generation.gemini_roadmap import gemini_roadmap
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
@app.post("/business_plan_roadmap")
async def getPlanning(request: ChatRequest):
    response = gemini_roadmap()
    return response
