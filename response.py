import random
from settings_manager import BotSettings

# تحميل الإعدادات
settings = BotSettings()

def get_response(key: str, context: dict = {}) -> str:
    # نحاول نحصل الردود من custom_responses
    responses = settings.get_setting("custom_responses") or {}
    options = responses.get(key, [])

    if not options:
        return f"⚠️ ما لقيت رد من النوع: {key}"

    # نختار رد عشوائي
    chosen = random.choice(options)

    # إذا فيه متغيرات مثل {player} أو {team}، نبدلها
    for k, v in context.items():
        chosen = chosen.replace(f"{{{k}}}", str(v))

    return chosen
