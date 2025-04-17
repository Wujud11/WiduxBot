from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from settings_manager import BotSettings

app = FastAPI()
app.mount("/Panel", StaticFiles(directory="Panel"), name="panel")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = BotSettings()

@app.get("/")
def root():
    return FileResponse("Panel/control_panel.html")

# ---------- إعدادات المنشن ----------
class MentionSettings(BaseModel):
    mention_limit: int
    mention_guard_warn_msg: str
    mention_guard_timeout_msg: str
    mention_guard_duration: int
    mention_guard_cooldown: int
    mention_daily_cooldown: bool

@app.post("/api/settings/mention")
def update_mention_settings(data: MentionSettings):
    settings.update_bot_settings(data.dict())
    return {"status": "updated"}

@app.get("/api/settings/mention")
def get_mention_settings():
    return {
        "mention_limit": settings.get_setting("mention_limit") or 0,
        "mention_guard_warn_msg": settings.get_setting("mention_guard_warn_msg") or "",
        "mention_guard_timeout_msg": settings.get_setting("mention_guard_timeout_msg") or "",
        "mention_guard_duration": settings.get_setting("mention_guard_duration") or 0,
        "mention_guard_cooldown": settings.get_setting("mention_guard_cooldown") or 0,
        "mention_daily_cooldown": settings.get_setting("mention_daily_cooldown") or False,
    }

# ---------- الردود العامة ----------
@app.get("/api/responses")
def get_all_responses():
    return settings.get_setting("custom_responses") or {}

@app.get("/api/responses/{key}")
def get_response(key: str):
    responses = settings.get_setting("custom_responses") or {}
    return responses.get(key, [])

class ResponsesPayload(BaseModel):
    responses: List[str]

@app.post("/api/responses/{key}")
def update_response(key: str, data: ResponsesPayload):
    responses = settings.get_setting("custom_responses") or {}
    responses[key] = data.responses
    settings.update_setting("custom_responses", responses)
    return {"status": "updated"}

# ---------- الأسئلة ----------
@app.get("/api/questions")
def get_questions():
    return settings.get_setting("questions") or []

class Question(BaseModel):
    question: str
    correct_answer: str
    alt_answers: List[str]
    category: str
    q_type: str

@app.post("/api/questions")
def add_question(data: Question):
    all_qs = settings.get_setting("questions") or []
    item = data.dict()
    item["id"] = len(all_qs) + 1
    all_qs.append(item)
    settings.update_setting("questions", all_qs)
    return {"status": "added"}

@app.delete("/api/questions/{qid}")
def delete_question(qid: int):
    all_qs = settings.get_setting("questions") or []
    all_qs = [q for q in all_qs if q.get("id") != qid]
    settings.update_setting("questions", all_qs)
    return {"status": "deleted"}

# ---------- القنوات ----------
@app.get("/api/channels")
def get_channels():
    return settings.get_setting("channels") or []

class ChannelPayload(BaseModel):
    name: str

@app.post("/api/channels")
def add_channel(data: ChannelPayload):
    settings.add_channel(data.name)
    return {"status": "added"}

@app.delete("/api/channels/{name}")
def delete_channel(name: str):
    settings.delete_channel(name)
    return {"status": "deleted"}

# ---------- الردود الخاصة ----------
@app.get("/api/special")
def get_special():
    return settings.get_setting("special_responses") or {}

class SpecialUser(BaseModel):
    user: str
    responses: List[str]

@app.post("/api/special")
def add_special_user(data: SpecialUser):
    if not data.user.strip():
        return {"status": "error", "message": "اسم المستخدم مطلوب"}
    responses = settings.get_setting("special_responses") or {}
    responses[data.user] = data.responses
    settings.update_setting("special_responses", responses)
    return {"status": "added"}

@app.delete("/api/special/{user}")
def delete_special_user(user: str):
    responses = settings.get_setting("special_responses") or {}
    if user in responses:
        del responses[user]
    settings.update_setting("special_responses", responses)
    return {"status": "deleted"}

# ---------- تنظيف الردود التالفة ----------
@app.post("/api/special/cleanup")
def cleanup_special_users():
    responses = settings.get_setting("special_responses") or {}
    cleaned = {}

    for user, resps in responses.items():
        if user.strip() and user != "mention_responses":
            cleaned[user] = resps

    deleted_count = len(responses) - len(cleaned)
    settings.update_setting("special_responses", cleaned)

    return {"status": "cleaned", "count": deleted_count}
