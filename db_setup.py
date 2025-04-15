import sqlite3

conn = sqlite3.connect("widux_panel.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    alt_answers TEXT,
    category TEXT,
    type TEXT CHECK(type IN ('Normal', 'Golden', 'Steal', 'Sabotage', 'Doom', 'Fate'))
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    messages TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS mention_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mention_limit INTEGER DEFAULT 3,
    warn_msg TEXT,
    timeout_msg TEXT,
    timeout_duration INTEGER DEFAULT 30,
    cooldown INTEGER DEFAULT 60,
    daily_cooldown BOOLEAN DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
)
""")

conn.commit()
conn.close()
print("تم إنشاء قاعدة البيانات والجداول بنجاح.")

