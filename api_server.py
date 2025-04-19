
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List
import sqlite3
import os

# إنشاء تطبيق FastAPI
app = FastAPI()

# ربط الجذر
@app.get("/")
async def root():
    return RedirectResponse(url="/control_panel.html")

# تجهيز مجلد Panel لخدمة الملفات الثابتة
if not os.path.exists("Panel"):
    os.makedirs("Panel")

app.mount("/", StaticFiles(directory="Panel", html=True), name="panel")

# الاتصال بالقاعدة
def get_db_connection():
    conn = sqlite3.connect("widux_panel.db")
    conn.row_factory = sqlite3.Row
    return conn

# إنشاء جدول الإعدادات إذا ماكان موجود
def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS panel_settings (
            section TEXT PRIMARY KEY,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# النماذج
class SectionData(BaseModel):
    section: str
    content: str

# حفظ قسم
@app.post("/api/save")
async def save_section(data: SectionData):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO panel_settings (section, content) 
        VALUES (?, ?)
        ON CONFLICT(section) DO UPDATE SET content=excluded.content
    """, (data.section, data.content))
    conn.commit()
    conn.close()
    return {"message": "تم حفظ البيانات"}

# استرجاع كل الإعدادات
@app.get("/api/get-settings")
async def get_all_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM panel_settings")
    rows = cursor.fetchall()
    conn.close()
    return {row["section"]: row["content"] for row in rows}
