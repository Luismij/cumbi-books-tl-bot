import telebot
from telebot import types

TOKEN = '7049180757:AAEh-XqUZd5nQ9l64pFw98h22uYufPgZiG0'
TARGET_CHANNEL_ID = '@CumbiBooksLibrary'

bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Envíame un PDF y te haré algunas preguntas.")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.document.mime_type == 'application/pdf':
        user_data[message.chat.id] = {'pdf_message_id': message.message_id}
        msg = bot.reply_to(message, "📕 ¿Cuál es el título del libro?")
        bot.register_next_step_handler(msg, process_title_step, message.chat.id)

def process_title_step(message, user_id):
    user_data[user_id]['titulo'] = message.text
    msg = bot.reply_to(message, "✍️ ¿Quién es el autor del libro?")
    bot.register_next_step_handler(msg, process_author_step, user_id)

def process_author_step(message, user_id):
    user_data[user_id]['autor'] = message.text
    msg = bot.reply_to(message, "Tags: (escribe los tags separados por espacios)")
    bot.register_next_step_handler(msg, process_tags_step, user_id)

def process_tags_step(message, user_id):
    user_data[user_id]['tags'] = message.text
    # Formatea y envía el mensaje al canal
    mensaje = f"📕 {user_data[user_id]['titulo']}\n✍️ {user_data[user_id]['autor']}\n\n#{' #'.join(user_data[user_id]['tags'].split())}"
    bot.send_message(TARGET_CHANNEL_ID, mensaje)
    # Reenvía el PDF al canal
    bot.forward_message(TARGET_CHANNEL_ID, message.chat.id, user_data[user_id]['pdf_message_id'])
    # Limpia los datos del usuario
    del user_data[user_id]

bot.polling()
