from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import requests
import time
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from duckduckgo_search import DDGS
from cache_manager import ResponseCache, RateLimiter

load_dotenv()

app = FastAPI()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

print(f"ElevenLabs API Key loaded: {ELEVENLABS_API_KEY[:10] if ELEVENLABS_API_KEY else 'None'}...")

client = ElevenLabs(
  api_key=ELEVENLABS_API_KEY
)

# Initialize caching system
# Cache responses for 24 hours to reduce API calls
cache = ResponseCache(cache_dir=".cache", ttl_hours=24)

# Initialize rate limiter
# Wait at least 60 seconds between OpenRouter API calls
rate_limiter = RateLimiter(min_interval_seconds=60)

# Clean up expired cache on startup
cache.clear_expired()
print(f"📊 Cache stats: {cache.get_stats()}")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


def ddg_search(query: str, max_results: int = 3) -> list:
    """Performs DuckDuckGo search and returns results with retry logic"""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            time.sleep(1)  # Add delay to avoid rate limiting
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                return results
        except Exception as e:
            print(f"DuckDuckGo search error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
    return []


# Added: Corrected integrate_duckduckgo function to use 'href' instead of 'link'
def integrate_duckduckgo(query: str, max_results: int = 3) -> str:
    """Fetches DuckDuckGo search results and formats them as citations."""
    try:
        results = ddg_search(query, max_results=max_results)
        if not results:
            return "\n\nCitations: No relevant citations found."
        citations = "\n".join([f"[{i+1}] {res['title']}: {res['href']}" for i, res in enumerate(results)])
        return f"\n\nCitations:\n{citations}"
    except Exception as e:
        return f"\n\nCitations: DuckDuckGo search error: {str(e)}"



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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def call_gemini_api(messages: list) -> dict:
    """
    Call Google Gemini API (Provider 1)
    
    Args:
        messages: List of message dictionaries for the chat completion
        
    Returns:
        dict: Response in OpenRouter-compatible format
        
    Raises:
        Exception: If the API call fails
    """
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY not configured")
    
    # Convert messages to Gemini format
    # Gemini uses a different format: contents with role and parts
    gemini_contents = []
    system_instruction = None
    
    for msg in messages:
        if msg["role"] == "system":
            # Gemini handles system messages differently
            system_instruction = msg["content"]
        else:
            gemini_contents.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [{"text": msg["content"]}]
            })
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": gemini_contents,
        "generationConfig": {
            "temperature": 0.7,
            "responseMimeType": "text/plain"
        }
    }
    
    # Add system instruction if present
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
    
    response = requests.post(
        url=url,
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=30
    )
    
    response.raise_for_status()
    data = response.json()
    
    # Extract content from Gemini response
    content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    
    if not content:
        raise Exception("Gemini response missing content")
    
    # Convert to OpenRouter-compatible format
    return {
        "choices": [{
            "message": {
                "content": content,
                "role": "assistant"
            }
        }]
    }


def call_openrouter_api(messages: list, max_retries: int = 3) -> dict:
    """
    Call OpenRouter API (Provider 2)
    
    Args:
        messages: List of message dictionaries for the chat completion
        max_retries: Maximum number of retry attempts
        
    Returns:
        dict: The API response JSON
        
    Raises:
        Exception: If all retries fail
    """
    if not OPENROUTER_API_KEY:
        raise Exception("OPENROUTER_API_KEY not configured")
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                },
                json={
                    "model": "meta-llama/llama-3.2-3b-instruct:free",
                    "messages": messages
                },
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:  # Rate limit error
                wait_time = (2 ** attempt) * 2  # Exponential backoff: 2, 4, 8 seconds
                print(f"OpenRouter rate limited. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
            raise Exception(f"OpenRouter API error {response.status_code}: {str(e)}")
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise Exception(f"Error calling OpenRouter API: {str(e)}")
    
    raise Exception("Max retries exceeded for OpenRouter API")


def make_openrouter_request(messages: list, endpoint_name: str = "openrouter", max_retries: int = 3, use_cache: bool = True) -> dict:
    """
    Make a request to LLM providers with multi-provider fallback, caching, and rate limiting
    
    Provider order:
    1. Google Gemini API (if GEMINI_API_KEY is set)
    2. OpenRouter API (if OPENROUTER_API_KEY is set)
    
    Args:
        messages: List of message dictionaries for the chat completion
        endpoint_name: Name of the endpoint for cache/rate limit tracking
        max_retries: Maximum number of retry attempts per provider
        use_cache: Whether to use caching (default: True)
        
    Returns:
        dict: The API response JSON in OpenRouter-compatible format
        
    Raises:
        HTTPException: If all providers fail
    """
    # Check cache first
    if use_cache:
        cache_key = {"messages": messages}
        cached_response = cache.get(endpoint_name, cache_key)
        if cached_response is not None:
            print(f"✅ Cache hit for {endpoint_name}")
            return cached_response
    
    # Build list of available providers
    providers = []
    if GEMINI_API_KEY:
        providers.append(("Google Gemini", call_gemini_api))
        print(f"🔵 Google Gemini API available for {endpoint_name}")
    if OPENROUTER_API_KEY:
        providers.append(("OpenRouter", lambda msgs: call_openrouter_api(msgs, max_retries)))
        print(f"🟢 OpenRouter API available for {endpoint_name}")
    
    if not providers:
        raise HTTPException(status_code=500, detail="No LLM API keys configured")
    
    print(f"📡 Attempting {len(providers)} provider(s) for {endpoint_name}")
    
    # Try each provider in order
    last_error = None
    for provider_name, provider_func in providers:
        try:
            print(f"🔄 Trying {provider_name}...")
            
            # Apply rate limiting before making API call
            rate_limiter.wait_if_needed(f"{endpoint_name}_{provider_name}")
            
            result = provider_func(messages)
            
            # Cache successful response
            if use_cache:
                cache.set(endpoint_name, cache_key, result)
            
            print(f"✅ {provider_name} succeeded for {endpoint_name}")
            return result
            
        except Exception as e:
            last_error = e
            print(f"❌ {provider_name} failed: {str(e)}")
            continue
    
    # All providers failed
    error_msg = f"All LLM providers failed. Last error: {str(last_error)}"
    print(f"🚨 {error_msg}")
    raise HTTPException(status_code=500, detail=error_msg)


class IdeaModel(BaseModel):
    name: str
    mission: str
    goals: List[str]
    targetMarket: Dict[str, Any]
    primaryProduct: str
    sdgs: List[str]

class ChatRequest(BaseModel):
    idea: IdeaModel


class PitchTextRequest(BaseModel):
    pitch_text: str

# class ChatRequest(BaseModel):
#     message: str


@app.post("/investors")
async def getInvestors(request: ChatRequest):
    try:
        request_json = request.json()
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant, expert in starting non profits. Provide concise and accurate responses."
            },
            {
                "role": "user",
                "content": "The JSON file I provided contains the content of my non-profit idea. Use this to identify potential investors for my non-profit. Create a list of what categories of entities would be interested in investing in non-profits with a mission like mine. Examples of entity categories can be corporations, celebrities, or charities. Create a list of names for each category of entities. Each list should include at least 2 names. Your output should be in markdown format"
            },
            {
                "role": "user",
                "content": request_json
            }
        ]
        
        result = make_openrouter_request(messages, endpoint_name="investors")
        
        if "choices" in result and len(result["choices"]) > 0:
            main_content = result["choices"][0]["message"]["content"]
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from OpenRouter API")
        
        query = f"Investors for {request.idea.mission}"
        citations = integrate_duckduckgo(query)
        return main_content + citations

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")




@app.post("/grantInfo")
async def getGrantInfo(request: ChatRequest):
    try:
        request_json = request.json()
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant, expert in starting non profits. Provide concise and accurate responses."
            },
            {
                "role": "user",
                "content": "The JSON file I provided contains the content of my non-profit idea. Use this to identify potential grants I can apply to, for my non-profit. Create a list of entities that would be interested in providing grants to non-profits with a mission like mine. Your output should be in markdown format"
            },
            {
                "role": "user",
                "content": request_json
            }
        ]
        
        result = make_openrouter_request(messages, endpoint_name="grantInfo")
        
        if "choices" in result and len(result["choices"]) > 0:
            main_content = result["choices"][0]["message"]["content"]
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from OpenRouter API")

        query = f"Grants for {request.idea.mission}"
        citations = integrate_duckduckgo(query)
        return main_content + citations

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")




@app.post("/getGrantProposal")
async def getGrantProposal(request: ChatRequest):
    try:
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

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant, expert in writing grant proposals for non-profits. Provide compelling, concise and accurate responses."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        result = make_openrouter_request(messages, endpoint_name="getGrantProposal")
        
        if "choices" in result and len(result["choices"]) > 0:
            propContent = result["choices"][0]["message"]["content"]

            query = f"Grant proposal examples for {request.idea.mission}"
            citations = integrate_duckduckgo(query)
            combined_content = propContent + citations

            return combined_content
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from OpenRouter API")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")




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

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant, expert in CREATING STELLAR elevator pitches for non-profits. Provide concise and accurate responses."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        result = make_openrouter_request(messages, endpoint_name="generatePitchText")
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from OpenRouter API")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")




# from fastapi import FastAPI, HTTPException, Request
# from fastapi.responses import Response
# from io import BytesIO
# import asyncio

# @app.post("/generatePitchAudio")
# async def generatePitchAudio(request: Request):
#     try:
#         body = await request.json()
#         pitch_text = body.get("pitch_text")

#         if not pitch_text or not isinstance(pitch_text, str):
#             raise ValueError("Invalid or missing pitch_text in request body")

#         print(f"Received pitch_text: {pitch_text[:100]}...")

#         # Use asyncio.wait_for to add a timeout
#         audio_generator = await asyncio.wait_for(
#             client.generate(
#                 text=pitch_text,
#                 voice="bIHbv24MWmeRgasZH58o"
#             ),
#             timeout=30  # Adjust timeout as needed
#         )

#         audio_chunks = b''.join(chunk for chunk in audio_generator)

#         # Use BytesIO instead of writing to disk
#         audio_buffer = BytesIO(audio_chunks)
#         audio_buffer.seek(0)

#         return Response(
#             content=audio_buffer.getvalue(),
#             media_type="audio/wav",
#             headers={"Content-Disposition": "attachment; filename=pitch.wav"}
#         )



#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=str(ve))
#     except asyncio.TimeoutError:
#         raise HTTPException(status_code=504, detail="Audio generation timed out")
#     except Exception as e:
#         print(f"Error details: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

@app.post("/generatePitchAudio")
async def generatePitchAudio(request: PitchTextRequest):
    try:
        # body = await request.json()
        pitch_text = request.pitch_text

        if not pitch_text or not isinstance(pitch_text, str):
            raise ValueError("Invalid or missing pitch_text in request body")

        print(f"Received pitch_text: {pitch_text[:100]}...")

        audio_generator = client.generate(
            text=pitch_text,
            voice="bIHbv24MWmeRgasZH58o"
        )

        audio_chunks = b''.join(chunk for chunk in audio_generator)

        with open("pitch.wav", "wb") as f:
            f.write(audio_chunks)

        return FileResponse("pitch.wav", media_type="audio/wav", filename="pitch.wav")

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error details: {str(e)}")  # Log the full error details
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")


# @app.post("/generatePitchAudio")
# async def generatePitchAudio(pitch_text: PitchTextRequest):
#     try:
#         audio_generator = client.generate(
#             text=pitch_text,
#             voice="bIHbv24MWmeRgasZH58o"
#         )

#         audio_chunks = b''.join(chunk for chunk in audio_generator)

#         with open("pitch.wav", "wb") as f:
#             f.write(audio_chunks)

#         return FileResponse("pitch.wav", media_type="audio/wav", filename="pitch.wav")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")



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

# from biz_roadmap_generation.gemini_roadmap import gemini_roadmap
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# @app.post("/business_plan_roadmap")
# # async def getPlanning(request: ChatRequest):
# async def getPlanning(request):
#     response = gemini_roadmap()
#     return response


@app.post("/business_plan_roadmap")
async def getPlan(request: ChatRequest):
    try:
        request_json = request.json()
        
        messages = [
            {
                "role": "system",
                "content": "You are a consultant for non-profits. You receive details on the type of non-profit your client wants to create. You have 20 years of experience advising for clients across the globe, and specialize in creating business plans and actionable roadmaps for aspirational non-profit founders. You consider your clients' country of operation when providing advice. When you provide advice, you include website links to resources for your clients to follow. Double check these links work. Your output is a step-by-step non-profit creation plan with a timeline. Exclude fundraising from the step-by-step plan but include it in the timeline"
            },
            {
                "role": "user",
                "content": request_json
            }
        ]
        
        result = make_openrouter_request(messages, endpoint_name="business_plan_roadmap")
        
        if "choices" in result and len(result["choices"]) > 0:
            response_content = result["choices"][0]["message"]["content"]
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from OpenRouter API")

        query = f"Business plan roadmap for {request.idea.mission}"
        citations = integrate_duckduckgo(query)
        combined_response = response_content + citations
        return combined_response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

