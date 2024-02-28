import telebot
from telebot import types
import requests
import os

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
        # Obtener información del archivo PDF
        file_info = bot.get_file(message.document.file_id)
        user_data[message.chat.id] = {'file_info': file_info, 'file_id': message.document.file_id}
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
    # Formatea y envía el mensaje con la información al canal
    caption = f"📕 {user_data[user_id]['titulo']}\n✍️ {user_data[user_id]['autor']}\n\n#{' #'.join(user_data[user_id]['tags'].split())}"
    # Descargar el PDF desde los servidores de Telegram
    file_path = user_data[user_id]['file_info'].file_path
    file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
    response = requests.get(file_url)

    # Crear un nombre de archivo seguro para el PDF basado en el título del libro
    # Reemplaza espacios con guiones bajos y elimina caracteres no alfanuméricos
    safe_title = ''.join(c for c in user_data[user_id]['titulo'] if c.isalnum() or c in [' ', '_']).replace(' ', '_')
    pdf_path = f"{safe_title}.pdf"

    with open(pdf_path, 'wb') as f:
        f.write(response.content)
    # Enviar el PDF al canal con el subtítulo
    with open(pdf_path, 'rb') as f:
        bot.send_document(TARGET_CHANNEL_ID, f, caption=caption)
    # Limpiar los datos del usuario y eliminar el archivo PDF temporal
    del user_data[user_id]
    os.remove(pdf_path)

bot.polling()
