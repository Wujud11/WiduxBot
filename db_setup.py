
import sqlite3

# اتصال أو إنشاء قاعدة البيانات
conn = sqlite3.connect("widux_panel.db")
cursor = conn.cursor()

# إنشاء جدول الأسئلة
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    alternative_answers TEXT
)
""")

# إنشاء جدول ردود اللعبة
cursor.execute("""
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    response_type TEXT NOT NULL,
    message TEXT NOT NULL
)
""")

# إنشاء جدول إعدادات المنشن
cursor.execute("""
CREATE TABLE IF NOT EXISTS mention_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    limit INTEGER NOT NULL,
    duration INTEGER NOT NULL,
    cooldown INTEGER NOT NULL,
    warn_msg TEXT NOT NULL,
    timeout_msg TEXT NOT NULL
)
""")

# إنشاء جدول القنوات
cursor.execute("""
CREATE TABLE IF NOT EXISTS channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")

# إنشاء جدول الردود الخاصة
cursor.execute("""
CREATE TABLE IF NOT EXISTS special_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    message TEXT NOT NULL
)
""")

# تأكيد حفظ التغييرات
conn.commit()
conn.close()

print("✅ تم إنشاء قاعدة البيانات widux_panel.db مع جميع الجداول المطلوبة بنجاح!")
