from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from settings_manager import BotSettings

app = FastAPI()
app.mount("/Panel", StaticFiles(directory="Panel"), name="panel")

# تم تعديل الميدل وير
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # اسمح لكل النطاقات، يفضل تغييره لاحقًا
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

settings = BotSettings()

@app.get("/")
def root():
    return FileResponse("Panel/control_panel.html")

# إعدادات المنشن
@app.post("/api/settings/mention")
async def update_mention_settings(data: dict):
    settings.update_bot_settings(data)
    return {"status": "updated"}

# الردود العامة
@app.get("/api/responses")
def get_all_responses():
    return settings.get_setting("custom_responses") or {}

@app.post("/api/responses/{key}")
def update_response(key: str, data: dict):
    responses = settings.get_setting("custom_responses") or {}
    responses[key] = data.get("responses", [])
    settings.update_setting("custom_responses", responses)
    return {"status": "updated"}

# الأسئلة
@app.get("/api/questions")
def get_questions():
    return settings.get_setting("questions") or []

@app.post("/api/questions")
def add_question(data: dict):
    all_qs = settings.get_setting("questions") or []
    data["id"] = len(all_qs) + 1
    all_qs.append(data)
    settings.update_setting("questions", all_qs)
    return {"status": "added"}

@app.delete("/api/questions/{qid}")
def delete_question(qid: int):
    all_qs = settings.get_setting("questions") or []
    all_qs = [q for q in all_qs if q.get("id") != qid]
    settings.update_setting("questions", all_qs)
    return {"status": "deleted"}

# القنوات
@app.get("/api/channels")
def get_channels():
    return settings.get_setting("channels") or []

@app.post("/api/channels")
def add_channel(data: dict):
    settings.add_channel(data.get("name"))
    return {"status": "added"}

@app.delete("/api/channels/{name}")
def delete_channel(name: str):
    settings.delete_channel(name)
    return {"status": "deleted"}

# الردود الخاصة
@app.get("/api/special")
def get_special():
    return settings.get_setting("special_responses") or {}

@app.post("/api/special")
def add_special_user(data: dict):
    responses = settings.get_setting("special_responses") or {}
    responses[data["user"]] = data["responses"]
    settings.update_setting("special_responses", responses)
    return {"status": "added"}

@app.delete("/api/special/{user}")
def delete_special_user(user: str):
    responses = settings.get_setting("special_responses") or {}
    if user in responses:
        del responses[user]
    settings.update_setting("special_responses", responses)
    return {"status": "deleted"}
