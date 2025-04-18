from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # إضافة لاستيراد StaticFiles
import json
import os

app = FastAPI()

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# إعداد تقديم الملفات الثابتة من مجلد Panel
app.mount("/Panel", StaticFiles(directory="Panel"), name="Panel")

# المسارات الخاصة بكل ملف بيانات
DATA_PATHS = {
    "settings": "data/bot_settings.json",
    "game_responses": "data/game_responses.json",
    "mention_replies": "data/mention_responses.json",
    "questions": "data/questions_bank.json",
    "channels": "data/channels.json",
    "special_responses": "data/special_responses.json"
}

# دالة تحميل ملف
def load_json(file):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)
    with open(file, "r") as f:
        return json.load(f)

# دالة حفظ ملف
def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ========== إعدادات المنشن ==========
@app.get("/settings")
def get_settings():
    return load_json(DATA_PATHS["settings"])

@app.post("/settings")
def update_settings(settings: dict):
    save_json(DATA_PATHS["settings"], settings)
    return {"message": "Settings updated"}

# ========== ردود اللعبة ==========
@app.get("/game-responses")
def get_game_responses():
    return load_json(DATA_PATHS["game_responses"])

@app.put("/game/{index}")
def update_game_response(index: int, item: dict):
    data = load_json(DATA_PATHS["game_responses"])
    if index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    data[index] = item["value"]
    save_json(DATA_PATHS["game_responses"], data)
    return {"message": "Game response updated"}

@app.delete("/game/{index}")
def delete_game_response(index: int):
    data = load_json(DATA_PATHS["game_responses"])
    if index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    data.pop(index)
    save_json(DATA_PATHS["game_responses"], data)
    return {"message": "Game response deleted"}

@app.post("/import-game-responses")
def import_game_responses(responses: list):
    save_json(DATA_PATHS["game_responses"], responses)
    return {"message": "Imported successfully"}

# ========== ردود المنشن العامة ==========
@app.get("/mention-replies")
def get_mention_replies():
    return load_json(DATA_PATHS["mention_replies"])

@app.put("/mention/{index}")
def update_mention_reply(index: int, item: dict):
    data = load_json(DATA_PATHS["mention_replies"])
    if index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    data[index] = item["value"]
    save_json(DATA_PATHS["mention_replies"], data)
    return {"message": "Mention reply updated"}

@app.delete("/mention/{index}")
def delete_mention_reply(index: int):
    data = load_json(DATA_PATHS["mention_replies"])
    if index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    data.pop(index)
    save_json(DATA_PATHS["mention_replies"], data)
    return {"message": "Mention reply deleted"}

@app.post("/import-mention-replies")
def import_mention_replies(responses: list):
    save_json(DATA_PATHS["mention_replies"], responses)
    return {"message": "Imported successfully"}

# ========== الأسئلة ==========
@app.get("/questions")
def get_questions():
    return load_json(DATA_PATHS["questions"])

@app.put("/questions/{index}")
def update_question(index: int, question: dict):
    data = load_json(DATA_PATHS["questions"])
    if index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    data[index] = question
    save_json(DATA_PATHS["questions"], data)
    return {"message": "Question updated"}

@app.delete("/questions/{index}")
def delete_question(index: int):
    data = load_json(DATA_PATHS["questions"])
    if index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    data.pop(index)
    save_json(DATA_PATHS["questions"], data)
    return {"message": "Question deleted"}

@app.post("/import-questions")
def import_questions(questions: list):
    save_json(DATA_PATHS["questions"], questions)
    return {"message": "Imported successfully"}

# ========== القنوات ==========
@app.get("/channels")
def get_channels():
    return load_json(DATA_PATHS["channels"])

@app.put("/channel/{index}")
def update_channel(index: int, item: dict):
    data = load_json(DATA_PATHS["channels"])
    if index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    data[index] = item["value"]
    save_json(DATA_PATHS["channels"], data)
    return {"message": "Channel updated"}

@app.delete("/channel/{index}")
def delete_channel(index: int):
    data = load_json(DATA_PATHS["channels"])
    if index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    data.pop(index)
    save_json(DATA_PATHS["channels"], data)
    return {"message": "Channel deleted"}

# ========== الردود الخاصة ==========
@app.get("/special-responses")
def get_special_responses():
    return load_json(DATA_PATHS["special_responses"])

@app.put("/special-responses/{index}")
def update_special_user(index: int, user: dict):
    data = load_json(DATA_PATHS["special_responses"])
    if index >= len(data):
        raise HTTPException(status_code=404, detail="User not found")
    data[index] = user
    save_json(DATA_PATHS["special_responses"], data)
    return {"message": "Special user updated"}

@app.delete("/special-responses/{index}")
def delete_special_user(index: int):
    data = load_json(DATA_PATHS["special_responses"])
    if index >= len(data):
        raise HTTPException(status_code=404, detail="User not found")
    data.pop(index)
    save_json(DATA_PATHS["special_responses"], data)
    return {"message": "Special user deleted"}

@app.post("/import-special-responses")
def import_special_responses(users: list):
    save_json(DATA_PATHS["special_responses"], users)
    return {"message": "Imported successfully"}
