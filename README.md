# ويدوكس بوت (WiduxBot)

بوت تفاعلي للأسئلة والمسابقات مخصص لمنصة تويتش، يقدم تجربة لعب تفاعلية باللغة العربية مع أنماط متنوعة ومميزات متقدمة.

## المميزات الرئيسية

- **دعم متعدد لأنماط اللعب**:
  - نمط فردي: للعب الفردي ضد البوت
  - نمط التحدي: لعب ضد متابعين آخرين
  - نمط الفريق: تقسيم المتابعين إلى فريقين للتنافس

- **أنواع متنوعة من الأسئلة**:
  - أسئلة عادية
  - Golden Question: سؤال بقيمة 50 نقطة
  - Test of Fate: سلسلة من 5 أسئلة متتالية
  - Steal Question: سؤال يمكن سرقة النقاط من خلاله
  - Sabotage Question: سؤال لإقصاء لاعب من الفريق المنافس
  - Doom Question: سؤال قد يضاعف النقاط أو يفقدها كلياً

## الإعداد التقني

### متطلبات التشغيل
- Python 3.7+
- قاعدة بيانات PostgreSQL
- حساب على منصة Twitch

### المتغيرات البيئية المطلوبة
```
TWITCH_OAUTH_TOKEN=your_twitch_oauth_token
TWITCH_CLIENT_ID=your_twitch_client_id
DATABASE_URL=postgresql://username:password@host:port/database_name
FLASK_SECRET_KEY=your_flask_secret_key
```
