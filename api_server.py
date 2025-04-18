from fastapi import FastAPI, UploadFile, File
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
async def serve_panel():
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


# ========== ردود المنشن العامة ==========
@app.get("/api/mention_responses")
def get_mention_responses():
    return settings.get_setting("mention_responses") or []

@app.post("/api/mention_responses")
def update_mention_responses(responses: List[str]):
    settings.update_setting("mention_responses", responses)
    return {"status": "mention responses updated"}


# ========== إدارة الأسئلة ==========
class QuestionItem(BaseModel):
    question: str
    correct_answer: str
    alt_answers: List[str]
    q_type: str
    category: str

@app.get("/api/questions")
def get_questions():
    return settings.get_setting("questions") or []

@app.post("/api/questions")
def add_single_question(item: QuestionItem):
    questions = settings.get_setting("questions") or []
    questions.append(item.dict())
    settings.update_setting("questions", questions)
    return {"status": "question added"}

@app.post("/api/questions/bulk")
def add_bulk_questions(questions: List[QuestionItem]):
    existing = settings.get_setting("questions") or []
    existing.extend([q.dict() for q in questions])
    settings.update_setting("questions", existing)
    return {"status": "bulk questions added"}


# ========== إدارة القنوات ==========
class ChannelItem(BaseModel):
    name: str

@app.get("/api/channels")
def get_channels():
    return settings.get_setting("channels") or []

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
    channels = [ch for ch in channels if ch != name]
    settings.update_setting("channels", channels)
    return {"status": "channel deleted"}


# ========== إدارة الردود الخاصة ==========
class SpecialUser(BaseModel):
    username: str
    responses: List[str]

@app.get("/api/special")
def get_special_responses():
    return settings.get_setting("special_responses") or {}

@app.post("/api/special")
def add_special_user(item: SpecialUser):
    specials = settings.get_setting("special_responses") or {}
    specials[item.username] = item.responses
    settings.update_setting("special_responses", specials)
    return {"status": "special user added"}

@app.delete("/api/special/{username}")
def delete_special_user(username: str):
    specials = settings.get_setting("special_responses") or {}
    if username in specials:
        del specials[username]
    settings.update_setting("special_responses", specials)
    return {"status": "special user deleted"}

@app.post("/api/special/cleanup")
def cleanup_special_users():
    specials = settings.get_setting("special_responses") or {}
    specials = {user: responses for user, responses in specials.items() if responses}
    settings.update_setting("special_responses", specials)
    return {"status": "cleanup done"}
