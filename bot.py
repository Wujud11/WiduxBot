import twitchio
import json
import asyncio
import os
import logging
from datetime import datetime
import random

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('widuxbot')

# قراءة الإعدادات والقنوات من ملفات JSON
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading JSON from {file_path}: {str(e)}")
        if 'settings' in file_path:
            return {}
        return []

# تحميل الإعدادات
def load_settings():
    settings = load_json('data/settings.json')
    # تحميل التوكن من متغير البيئة TWITCH_ACCESS_TOKEN مباشرة
    token = os.environ.get('TWITCH_ACCESS_TOKEN')

    if not token:
        logger.error("No Twitch token found in environment variable TWITCH_ACCESS_TOKEN")
        raise ValueError("Twitch token is required to run the bot. Please set TWITCH_ACCESS_TOKEN environment variable.")

    return settings, token

# الدالة الرئيسية لبدء تشغيل البوت
async def main():
    try:
        # تحميل الإعدادات
        settings, token = load_settings()

        # تحميل القنوات
        channels_data = load_json('data/channels.json')

        # استخراج القنوات المفعلة فقط
        active_channels = [ch['channel_name'] for ch in channels_data if ch.get('is_enabled', True)]

        if not active_channels:
            logger.warning("No active channels found. Bot will connect but won't join any channels.")
            active_channels = []  # تأكد من وجود قائمة فارغة على الأقل

        # إنشاء عميل البوت
        bot = twitchio.Client(token=token)

        # إضافة المستمعين للأحداث
        @bot.event()
        async def event_ready():
            logger.info(f'Bot is ready | Connected as: {bot.nick}')
            logger.info(f'Active channels: {", ".join(active_channels) if active_channels else "None"}')

        # متغيرات لحفظ حالة الأسئلة والنقاط
        current_question = None
        question_start_time = None
        user_streaks = {}


        # مستمع الرسائل
        @bot.event()
        async def event_message(message):
            # تجاهل رسائل البوت نفسه
            if message.echo:
                return

            # معالجة الرسالة
            logger.info(f'Message received from {message.author.name}: {message.content}')

            # تحميل إعدادات النقاط
            points_settings = load_json('data/points_settings.json')

            # إذا كانت هناك إجابة على سؤال
            if current_question and message.content.lower() == current_question['correct_answer'].lower():
                # حساب الوقت المستغرق
                elapsed_time = (datetime.now() - question_start_time).total_seconds()

                # تحديد النقاط حسب الوقت
                points = 0
                if elapsed_time <= points_settings['quick_answer_time']:
                    points = points_settings['quick_answer_points']
                elif elapsed_time <= points_settings['normal_answer_time']:
                    points = points_settings['normal_answer_points']
                else:
                    points = points_settings['late_answer_points']

                # تحديث السلسلة (الستريك)
                user_streaks[message.author.name] = user_streaks.get(message.author.name, 0) + 1
                streak_count = user_streaks[message.author.name]
                streak_message = ""
                streak_bonus = 0

                # حساب مكافأة الستريك إذا كان مفعلاً
                if points_settings['streak_enabled'] and streak_count >= points_settings['streak_threshold']:
                    if points_settings.get('streak_increase_enabled', False):
                        # مكافأة متزايدة: تزداد مع كل مجموعة من الإجابات المتتالية
                        streak_multiplier = (streak_count - 1) // points_settings['streak_threshold']
                        streak_bonus = points_settings['streak_bonus_points'] * (streak_multiplier + 1)
                    else:
                        # مكافأة ثابتة
                        streak_bonus = points_settings['streak_bonus_points']

                    streak_message = f"\n🔥 سلسلة {streak_count} إجابات صحيحة! (+{streak_bonus} نقطة إضافية)\n"
                    if points_settings['streak_messages']:
                        streak_message += random.choice(points_settings['streak_messages'])

                # إضافة النقاط الإجمالية
                total_points = points + streak_bonus

                # إرسال الرد
                await message.channel.send(f"صحيح يا {message.author.name}! 🎉 (+{points} نقطة أساسية{' + ' + str(streak_bonus) + ' نقطة مكافأة' if streak_bonus > 0 else ''}){streak_message}")
                current_question = None # إعادة تعيين السؤال بعد الإجابة الصحيحة

            elif message.content.startswith('!hello'):
                await message.channel.send(f'مرحباً {message.author.name}!')
            
            elif message.content.strip() == 'وج؟':
                await message.channel.send(f'أهلاً {message.author.name}! أنا بوت المسابقات WiduxBot. استخدم !help للمساعدة.')

            # Add logic to start a new question here (This part is missing from the provided information)
            #  This section requires implementation to fetch a question from a database or a file,
            #  set current_question and question_start_time.  Example:
            #  if message.content.startswith('!newquestion'):
            #      new_question = get_next_question() # Implement get_next_question() function
            #      current_question = new_question
            #      question_start_time = datetime.now()
            #      await message.channel.send(f"السؤال الجديد: {current_question['question']}")


        # بدء تشغيل البوت وحذف الاستثناءات لتجنب توقف البوت بسبب أخطاء اتصال
        try:
            await bot.connect()
            await bot.join_channels(active_channels)
            await bot.start()
        except Exception as e:
            logger.error(f"Error while running the bot: {str(e)}")

    except Exception as e:
        logger.error(f"Failed to start the bot: {str(e)}")

# تشغيل البوت إذا تم تنفيذ الملف مباشرة
if __name__ == "__main__":
    asyncio.run(main())