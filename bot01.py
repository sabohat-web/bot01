from telegram import Update, ChatMember, ChatMemberUpdated
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes,
    ConversationHandler, ChatMemberHandler
)

# Admin chat ID sini o'zgartiring
ADMIN_CHAT_ID = 744635508  # bu yerga adminning Telegram ID sini yozing

# State lar
(
    CHECK_MEMBER,
    ASK_NAME,
    ASK_ID_CARD,
    ASK_PHOTO_3x4,
    ASK_TABEL,
    ASK_PARENT_PASSPORT,
    ASK_PHONE,
    FINISH,
) = range(8)

async def check_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = await context.bot.get_chat("@ITMA_AngorIM")  # Kanal usernameni kiriting
    member = await chat.get_member(user.id)

    if member.status in ['member', 'creator', 'administrator']:
        await update.message.reply_text("Siz kanalga a'zo ekanligingiz tasdiqlandi. Ismingiz va familiyangizni kiriting:")
        return ASK_NAME
    else:
        await update.message.reply_text("Iltimos, avval @ITMA_AngorIM kanaliga a'zo bo'ling va keyin /start ni bosing.")
        return ConversationHandler.END

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Iltimos, guvohnomangizning rasmni yuboring (foto sifatida).")
    return ASK_ID_CARD

async def ask_id_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['id_card'] = update.message.photo[-1].file_id
        await update.message.reply_text("Iltimos, tiniq 3x4 formatdagi rasmingizni yuboring (foto sifatida).")
        return ASK_PHOTO_3x4
    else:
        await update.message.reply_text("Iltimos, faqat rasm yuboring!")
        return ASK_ID_CARD

async def ask_photo_3x4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['photo_3x4'] = update.message.photo[-1].file_id
        await update.message.reply_text("Iltimos, tabelingizning rasmni yuboring (foto sifatida).")
        return ASK_TABEL
    else:
        await update.message.reply_text("Iltimos, faqat rasm yuboring!")
        return ASK_PHOTO_3x4

async def ask_tabel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['tabel'] = update.message.photo[-1].file_id
        await update.message.reply_text("Iltimos, ota yoki onangizning pasport rasmni yuboring (foto sifatida).")
        return ASK_PARENT_PASSPORT
    else:
        await update.message.reply_text("Iltimos, faqat rasm yuboring!")
        return ASK_TABEL

async def ask_parent_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['parent_passport'] = update.message.photo[-1].file_id
        await update.message.reply_text("Oxirgi qadam, ishlaydigan telefon raqamingizni kiriting:")
        return ASK_PHONE
    else:
        await update.message.reply_text("Iltimos, faqat rasm yuboring!")
        return ASK_PARENT_PASSPORT

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text and len(text) >= 9:  # oddiy tekshiruv, kerak bo'lsa regex bilan telefonni yaxshilash mumkin
        context.user_data['phone'] = text

        # Ma'lumotlarni admin ga yuborish
        user = update.effective_user
        msg = (
            f"Yangi ro'yxatdan o'tgan foydalanuvchi:\n"
            f"Ism familiya: {context.user_data.get('name')}\n"
            f"Telefon: {context.user_data.get('phone')}\n"
            f"Telegram ID: @{user.username if user.username else 'yo\'q'} ({user.id})"
        )

        # Rasm fayllarini yuborish (file_id orqali)
        media = []
        media.append(InputFile(context.user_data['id_card'], filename="Guvohnoma.jpg"))
        media.append(InputFile(context.user_data['photo_3x4'], filename="3x4.jpg"))
        media.append(InputFile(context.user_data['tabel'], filename="Tabel.jpg"))
        media.append(InputFile(context.user_data['parent_passport'], filename="ParentPassport.jpg"))

        # Yoki oddiy xabar sifatida faqat file_id ni yuborish mumkin
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)

        # Rasm fayllarini ketma-ket yuborish
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=context.user_data['id_card'], caption="Guvohnoma")
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=context.user_data['photo_3x4'], caption="3x4 rasmi")
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=context.user_data['tabel'], caption="Tabel rasmi")
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=context.user_data['parent_passport'], caption="Ota/ona pasporti")

        await update.message.reply_text("Murojaatingiz adminga yuborildi. Tez orada aloqaga chiqiladi.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Iltimos, to'g'ri telefon raqamini kiriting!")
        return ASK_PHONE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ro'yxatdan o'tish bekor qilindi.")
    return ConversationHandler.END

if __name__ == "__main__":
    from telegram import InputFile

    app = ApplicationBuilder().token("7983334223:AAGt4mM4JqXLYW3k2uv0PCpYWDyecX1Acbo").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', check_member)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_ID_CARD: [MessageHandler(filters.PHOTO, ask_id_card)],
            ASK_PHOTO_3x4: [MessageHandler(filters.PHOTO, ask_photo_3x4)],
            ASK_TABEL: [MessageHandler(filters.PHOTO, ask_tabel)],
            ASK_PARENT_PASSPORT: [MessageHandler(filters.PHOTO, ask_parent_passport)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    app.add_handler(conv_handler)

    print("Bot ishga tushdi...")
    app.run_polling()
