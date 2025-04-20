from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import json
import os

app = FastAPI()

# تثبيت ملفات لوحة التحكم
app.mount("/Panel", StaticFiles(directory="Panel"), name="panel")

# ---------------------------------------
# قنوات
# ---------------------------------------

CHANNELS_FILE = 'data/channels.json'

def load_channels():
    if not os.path.exists(CHANNELS_FILE):
        return []
    with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_channels(channels):
    with open(CHANNELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(channels, f, ensure_ascii=False, indent=4)

@app.get("/api/channels")
async def get_channels():
    channels = load_channels()
    return {"channels": channels}

@app.post("/api/channels/add")
async def add_channel(request: Request):
    data = await request.json()
    channel = data.get('channel')
    if not channel:
        return {"success": False, "error": "اسم القناة مفقود"}
    channels = load_channels()
    if channel in channels:
        return {"success": False, "error": "القناة موجودة بالفعل"}
    channels.append(channel)
    save_channels(channels)
    return {"success": True}

@app.post("/api/channels/delete")
async def delete_channel(request: Request):
    data = await request.json()
    channel = data.get('channel')
    if not channel:
        return {"success": False, "error": "اسم القناة مفقود"}
    channels = load_channels()
    if channel in channels:
        channels.remove(channel)
        save_channels(channels)
        return {"success": True}
    else:
        return {"success": False, "error": "القناة غير موجودة"}

# ---------------------------------------
# إعدادات المنشن
# ---------------------------------------

@app.get("/api/settings")
async def get_settings():
    settings_path = 'data/bot_settings.json'
    if not os.path.exists(settings_path):
        return {}
    with open(settings_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.post("/api/settings")
async def save_settings(request: Request):
    data = await request.json()
    settings_path = 'data/bot_settings.json'
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return {"success": True}

# ---------------------------------------
# الردود العامة للمنشن
# ---------------------------------------

@app.get("/api/mention_replies")
async def get_mention_replies():
    replies_path = 'data/mention_responses.json'
    if not os.path.exists(replies_path):
        return {"mention_general_responses": []}
    with open(replies_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.post("/api/mention_replies")
async def save_mention_replies(request: Request):
    data = await request.json()
    replies_path = 'data/mention_responses.json'
    with open(replies_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return {"success": True}

# ---------------------------------------
# الردود الخاصة
# ---------------------------------------

@app.get("/api/special_replies")
async def get_special_replies():
    path = 'data/special_responses.json'
    if not os.path.exists(path):
        return {"special_mentions": {}}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.post("/api/special_replies/add")
async def add_special_reply(request: Request):
    data = await request.json()
    username = data.get('username')
    replies = data.get('replies')
    if not username or not isinstance(replies, list):
        return {"success": False, "error": "بيانات غير مكتملة"}

    path = 'data/special_responses.json'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            special_data = json.load(f)
    else:
        special_data = {"special_mentions": {}}

    special_data["special_mentions"][username] = replies
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(special_data, f, indent=4, ensure_ascii=False)

    return {"success": True}

@app.post("/api/special_replies/delete")
async def delete_special_reply(request: Request):
    data = await request.json()
    username = data.get('username')
    if not username:
        return {"success": False, "error": "اسم المستخدم مفقود"}

    path = 'data/special_responses.json'
    if not os.path.exists(path):
        return {"success": False, "error": "لا توجد ردود خاصة"}

    with open(path, 'r', encoding='utf-8') as f:
        special_data = json.load(f)

    if username in special_data.get("special_mentions", {}):
        del special_data["special_mentions"][username]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(special_data, f, indent=4, ensure_ascii=False)
        return {"success": True}
    else:
        return {"success": False, "error": "المستخدم غير موجود"}

# ---------------------------------------
# إدارة الأسئلة
# ---------------------------------------

@app.get("/api/questions")
async def get_questions():
    path = 'data/questions_bank.json'
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.post("/api/questions/add")
async def add_question(request: Request):
    data = await request.json()
    required_fields = ["question", "answer", "alternatives", "type"]
    if not all(field in data for field in required_fields):
        return {"success": False, "error": "بيانات السؤال ناقصة"}

    path = 'data/questions_bank.json'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    else:
        questions = []

    questions.append(data)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=4, ensure_ascii=False)

    return {"success": True}

@app.post("/api/questions/delete")
async def delete_question(request: Request):
    data = await request.json()
    index = data.get('index')

    if index is None:
        return {"success": False, "error": "رقم السؤال مفقود"}

    path = 'data/questions_bank.json'
    if not os.path.exists(path):
        return {"success": False, "error": "لا توجد أسئلة"}

    with open(path, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    if 0 <= index < len(questions):
        del questions[index]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=4, ensure_ascii=False)
        return {"success": True}
    else:
        return {"success": False, "error": "رقم السؤال غير صالح"}

# ---------------------------------------
# ردود اللعبة والطقطقة
# ---------------------------------------

@app.get("/api/game_responses/get")
async def get_game_responses(type: str):
    path = 'data/game_responses.json'
    if not os.path.exists(path):
        return {"responses": []}

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    responses = data.get(type, [])
    return {"responses": responses}

@app.post("/api/game_responses/save")
async def save_game_responses(request: Request):
    data = await request.json()
    type_ = data.get('type')
    responses = data.get('responses')

    if not type_ or not isinstance(responses, list):
        return {"success": False, "error": "بيانات غير مكتملة"}

    path = 'data/game_responses.json'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            current_data = json.load(f)
    else:
        current_data = {}

    current_data[type_] = responses
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, indent=4, ensure_ascii=False)

    return {"success": True}
