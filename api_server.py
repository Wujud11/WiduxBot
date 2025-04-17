from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import json

from settings_manager import BotSettings

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/Panel", StaticFiles(directory="Panel"), name="panel")

settings = BotSettings()

@app.get("/")
def root():
    return FileResponse("Panel/control_panel.html")

# ========== إعدادات المنشن ==========
class MentionSettings(BaseModel):
    mention_limit: int
    mention_guard_warn_msg: str
    mention_guard_timeout_msg: str
    mention_guard_duration: int
    mention_guard_cooldown: int
    mention_daily_cooldown: bool

@app.get("/api/settings/mention")
def get_mention_settings():
    return {
        "mention_limit": settings.get_setting("mention_limit") or 2,
        "mention_guard_warn_msg": settings.get_setting("mention_guard_warn_msg") or "",
        "mention_guard_timeout_msg": settings.get_setting("mention_guard_timeout_msg") or "",
        "mention_guard_duration": settings.get_setting("mention_guard_duration") or 5,
        "mention_guard_cooldown": settings.get_setting("mention_guard_cooldown") or 86400,
        "mention_daily_cooldown": settings.get_setting("mention_daily_cooldown") or False,
    }

@app.post("/api/settings/mention")
def update_mention_settings(data: MentionSettings):
    settings.update_bot_settings(data.dict())
    return {"status": "mention settings updated"}

# ========== ردود اللعبة ==========
@app.get("/api/responses/{key}")
def get_responses(key: str):
    responses = settings.get_setting("custom_responses") or {}
    return responses.get(key, [])

@app.post("/api/responses/{key}")
def update_responses(key: str, responses: List[str]):
    all_responses = settings.get_setting("custom_responses") or {}
    all_responses[key] = responses
    settings.update_setting("custom_responses", all_responses)
    return {"status": "responses updated"}

@app.post("/api/import/responses/{key}")
async def import_responses(key: str, file: UploadFile = File(...)):
    data = await file.read()
    try:
        responses = json.loads(data)
        if isinstance(responses, list):
            all_responses = settings.get_setting("custom_responses") or {}
            all_responses[key] = responses
            settings.update_setting("custom_responses", all_responses)
            return {"status": "imported"}
        else:
            return JSONResponse(status_code=400, content={"error": "Invalid JSON format"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

# ========== ردود المنشن العامة ==========
@app.get("/api/mention_responses")
def get_mention_general_responses():
    return settings.get_setting("mention_responses") or []

@app.post("/api/mention_responses")
def update_mention_general_responses(responses: List[str]):
    settings.update_setting("mention_responses", responses)
    return {"status": "mention responses updated"}

@app.post("/api/import/mention_responses")
async def import_mention_general_responses(file: UploadFile = File(...)):
    data = await file.read()
    try:
        responses = json.loads(data)
        if isinstance(responses, list):
            settings.update_setting("mention_responses", responses)
            return {"status": "mention responses imported"}
        else:
            return JSONResponse(status_code=400, content={"error": "Invalid JSON format"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

# ========== إدارة الأسئلة ==========
@app.get("/api/questions")
def get_questions():
    return settings.get_setting("questions") or []

class QuestionItem(BaseModel):
    question: str
    correct_answer: str
    alt_answers: List[str]
    q_type: str
    category: str

@app.post("/api/questions")
def add_single_question(item: QuestionItem):
    questions = settings.get_setting("questions") or []
    questions.append(item.dict())
    settings.update_setting("questions", questions)
    return {"status": "single question added"}

@app.post("/api/questions/bulk")
def add_bulk_questions(questions: List[QuestionItem]):
    stored = settings.get_setting("questions") or []
    stored.extend([q.dict() for q in questions])
    settings.update_setting("questions", stored)
    return {"status": "bulk questions added"}

@app.post("/api/import/questions")
async def import_questions(file: UploadFile = File(...)):
    data = await file.read()
    try:
        new_questions = json.loads(data)
        if isinstance(new_questions, list):
            stored = settings.get_setting("questions") or []
            stored.extend(new_questions)
            settings.update_setting("questions", stored)
            return {"status": "bulk questions imported"}
        else:
            return JSONResponse(status_code=400, content={"error": "Invalid JSON format"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

# ========== إدارة القنوات ==========
@app.get("/api/channels")
def get_channels():
    return settings.get_setting("channels") or []

class ChannelItem(BaseModel):
    name: str

@app.post("/api/channels")
def add_channel(item: ChannelItem):
    channels = settings.get_setting("channels") or []
    if item.name not in channels:
        channels.append(item.name)
    settings.update_setting("channels", channels)
    return {"status": "channel added"}

@app.delete("/api/channels/{name}")
def delete_channel(name: str):
    channels = settings.get_setting("channels") or []
    channels = [c for c in channels if c != name]
    settings.update_setting("channels", channels)
    return {"status": "channel deleted"}

# ========== إدارة الردود الخاصة ==========
@app.get("/api/special")
def get_special_responses():
    return settings.get_setting("special_responses") or {}

class SpecialUser(BaseModel):
    username: str
    responses: List[str]

@app.post("/api/special")
def add_special_response(item: SpecialUser):
    specials = settings.get_setting("special_responses") or {}
    specials[item.username] = item.responses
    settings.update_setting("special_responses", specials)
    return {"status": "special response added"}

@app.post("/api/import/special")
async def import_special_responses(file: UploadFile = File(...)):
    data = await file.read()
    try:
        special_data = json.loads(data)
        if isinstance(special_data, dict):
            settings.update_setting("special_responses", special_data)
            return {"status": "special responses imported"}
        else:
            return JSONResponse(status_code=400, content={"error": "Invalid JSON format"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.delete("/api/special/{username}")
def delete_special_user(username: str):
    specials = settings.get_setting("special_responses") or {}
    if username in specials:
        del specials[username]
    settings.update_setting("special_responses", specials)
    return {"status": "special user deleted"}
