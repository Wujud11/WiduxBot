from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import sqlite3
import os

# إنشاء تطبيق FastAPI
app = FastAPI()

# تجهيز مجلد Panel لخدمة الملفات الثابتة
if not os.path.exists("Panel"):
    os.makedirs("Panel")

app.mount("/", StaticFiles(directory="Panel", html=True), name="panel")

# الاتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect("widux_panel.db")
    conn.row_factory = sqlite3.Row
    return conn

# النماذج
class MentionSettings(BaseModel):
    limit: int
    duration: int
    cooldown: int
    warn_msg: str
    timeout_msg: str

class Question(BaseModel):
    type: str
    text: str
    correct_answer: str
    alternative_answers: List[str]

class ResponseData(BaseModel):
    type: str
    message: str

class ChannelData(BaseModel):
    name: str

class SpecialResponseData(BaseModel):
    username: str
    message: str

# API حفظ إعدادات المنشن
@app.post("/api/mention-settings")
async def save_mention_settings(settings: MentionSettings):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mention_settings")
    cursor.execute("""
        INSERT INTO mention_settings (id, limit, duration, cooldown, warn_msg, timeout_msg)
        VALUES (1, ?, ?, ?, ?, ?)
    """, (settings.limit, settings.duration, settings.cooldown, settings.warn_msg, settings.timeout_msg))
    conn.commit()
    conn.close()
    return {"message": "تم حفظ إعدادات المنشن بنجاح"}

# API إضافة سؤال
@app.post("/api/questions")
async def add_question(question: Question):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO questions (type, text, correct_answer, alternative_answers)
        VALUES (?, ?, ?, ?)
    """, (question.type, question.text, question.correct_answer, ','.join(question.alternative_answers)))
    conn.commit()
    question_id = cursor.lastrowid
    conn.close()
    return {"message": "تمت إضافة السؤال", "id": question_id}

# API تعديل سؤال
@app.put("/api/questions/{question_id}")
async def edit_question(question_id: int, question: Question):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE questions
        SET type = ?, text = ?, correct_answer = ?, alternative_answers = ?
        WHERE id = ?
    """, (question.type, question.text, question.correct_answer, ','.join(question.alternative_answers), question_id))
    conn.commit()
    conn.close()
    return {"message": "تم تعديل السؤال"}

# API حذف سؤال
@app.delete("/api/questions/{question_id}")
async def delete_question(question_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()
    return {"message": "تم حذف السؤال"}

# API إضافة رد للعبة
@app.post("/api/responses")
async def add_response(response: ResponseData):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO responses (response_type, message)
        VALUES (?, ?)
    """, (response.type, response.message))
    conn.commit()
    conn.close()
    return {"message": "تمت إضافة الرد"}

# API إضافة قناة
@app.post("/api/channels")
async def add_channel(channel: ChannelData):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO channels (name)
        VALUES (?)
    """, (channel.name,))
    conn.commit()
    conn.close()
    return {"message": "تمت إضافة القناة"}

# API إضافة رد خاص
@app.post("/api/special-responses")
async def add_special_response(special: SpecialResponseData):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO special_responses (username, message)
        VALUES (?, ?)
    """, (special.username, special.message))
    conn.commit()
    conn.close()
    return {"message": "تمت إضافة الرد الخاص"}
