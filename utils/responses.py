import random
from settings_manager import BotSettings  # تم تعديل الاستيراد

settings = BotSettings()  # تم تعديل الإنشاء

def get_response(key: str, context: dict = None) -> str:
    """
    يرجع رد عشوائي من الردود المخصصة حسب المفتاح المحدد.
    إذا الرد يحتوي على متغيرات ({player}، {leader}، إلخ) يتم استبدالها من الـ context.
    """
    responses = settings.get_setting("custom_responses") or {}
    response_data = responses.get(key)

    if not response_data:
        return "..."

    # إذا كان الرد قائمة → نختار عشوائي
    if isinstance(response_data, list):
        selected = random.choice(response_data)
    else:
        selected = response_data  # نص مفرد

    # استبدال المتغيرات داخل الرد إذا فيه context
    if context:
        for var, value in context.items():
            selected = selected.replace(f"{{{var}}}", str(value))

    return selected
