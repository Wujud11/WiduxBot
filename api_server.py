from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import json

# ========= مسارات البيانات ==========
DATA_PATHS = {
    "settings": "data/bot_settings.json",
    "game_responses": "data/game_responses.json",
    "mention_responses": "data/mention_responses.json",
    "questions": "data/questions_bank.json",
    "channels": "data/channels.json",
    "special_responses": "data/special_responses.json",
}

# ========= دوال مساعدة للقراءة والكتابة ==========
def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ========= إنشاء تطبيق FastAPI ==========
app = FastAPI()

# ========= إعدادات CORS ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========= تقديم الملفات الثابتة (Static Files) ==========
app.mount("/Panel", StaticFiles(directory="Panel"), name="Panel")

# ========= نقطة البداية (فتح واجهة التحكم) ==========
@app.get("/")
def read_root():
    return FileResponse("Panel/control_panel.html")

# ========= إعدادات البوت ==========
@app.get("/settings")
def get_settings():
    return load_json(DATA_PATHS["settings"])

@app.post("/settings")
def update_settings(settings: dict):
    save_json(DATA_PATHS["settings"], settings)
    return {"message": "Settings updated successfully"}

# ========= ردود الألعاب ==========
@app.get("/game-responses")
def get_game_responses():
    return load_json(DATA_PATHS["game_responses"])

@app.post("/import-game-responses")
def import_game_responses(responses: list):
    save_json(DATA_PATHS["game_responses"], responses)
    return {"message": "Game responses imported successfully"}

# ========= ردود المنشن ==========
@app.get("/mention-replies")
def get_mention_replies():
    return load_json(DATA_PATHS["mention_responses"])

@app.post("/import-mention-replies")
def import_mention_replies(responses: list):
    save_json(DATA_PATHS["mention_responses"], responses)
    return {"message": "Mention replies imported successfully"}

# ========= بنك الأسئلة ==========
@app.get("/questions")
def get_questions():
    return load_json(DATA_PATHS["questions"])

@app.post("/import-questions")
def import_questions(questions: list):
    save_json(DATA_PATHS["questions"], questions)
    return {"message": "Questions imported successfully"}

# ========= القنوات ==========
@app.get("/channels")
def get_channels():
    return load_json(DATA_PATHS["channels"])

@app.put("/channel/{index}")
def update_channel(index: int, channel: dict):
    channels = load_json(DATA_PATHS["channels"])
    if 0 <= index < len(channels):
        channels[index] = channel
        save_json(DATA_PATHS["channels"], channels)
        return {"message": "Channel updated successfully"}
    return {"error": "Invalid index"}

@app.delete("/channel/{index}")
def delete_channel(index: int):
    channels = load_json(DATA_PATHS["channels"])
    if 0 <= index < len(channels):
        channels.pop(index)
        save_json(DATA_PATHS["channels"], channels)
        return {"message": "Channel deleted successfully"}
    return {"error": "Invalid index"}

# ========= استيراد قنوات جديدة ==========
@app.post("/import-channels")
def import_channels(channels: list):
    save_json(DATA_PATHS["channels"], channels)
    return {"message": "Channels imported successfully"}

# ========= الردود الخاصة ==========
@app.get("/special-responses")
def get_special_responses():
    return load_json(DATA_PATHS["special_responses"])

@app.post("/import-special-responses")
def import_special_responses(responses: list):
    save_json(DATA_PATHS["special_responses"], responses)
    return {"message": "Special responses imported successfully"}
