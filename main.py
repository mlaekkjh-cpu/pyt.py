from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from openai import OpenAI
import re

# 🔐 التوكنات
BOT_TOKEN = "1773136914:AAFfr1mDuydKuS3Zwh40GHuJEAxkxvBEddI"
OPENAI_API_KEY = "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"

# حساب الادمن
ADMIN_ID = 6632799705 # <-- حط هنا رقم الايدي مالتك

# القنوات المطلوبة (اسم القناة فقط بدون @)
REQUIRED_CHANNELS = ["EETFR"]

client = OpenAI(api_key=OPENAI_API_KEY)

# دالة لتحديد لغة الرسالة
def detect_language(text):
    # إذا يحتوي حروف عربية
    if re.search(r'[\u0600-\u06FF]', text):
        return "arabic"
    else:
        return "english"

async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    username = user.username or "NoUsername"
    first_name = user.first_name or "NoName"

    # تحقق الاشتراك بالقنوات
    subscribed = True
    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=f"@{channel}", user_id=user_id)
            if member.status in ["left", "kicked"]:
                subscribed = False
        except:
            subscribed = False

    # إرسال تقرير للإدمن
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"User: {first_name} (@{username})\nID: {user_id}\nSubscribed: {subscribed}"
    )

    if not subscribed:
        await update.message.reply_text(
            f"هلا {first_name} 🙏 اشترك بالقنوات التالية أولاً:\n" +
            "\n".join([f"@{ch}" for ch in REQUIRED_CHANNELS])
        )
        return

    # تحديد اللغة
    user_message = update.message.text
    language = detect_language(user_message)

    system_prompt = ""
    if language == "arabic":
        system_prompt = "أنت مساعد ذكي يرد باللهجة العراقية وبأسلوب لطيف."
    else:
        system_prompt = "You are a smart assistant. Reply in English politely."

    # طلب الرد من الذكاء الاصطناعي
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))

print("🤖 Bot running...")
app.run_polling()
