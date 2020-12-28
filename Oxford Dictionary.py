from flask import Flask, request
import os
import json
import requests
import telebot
from telebot import types 
from telebot import util

# Setting up Bot
TOKEN = '<token>'
WEBHOOK_URL = '<url>'
app_id  = "<oxford-api-id>"
app_key  = "<oxford-api-key>"
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

# Making Bot do Something
@bot.message_handler(commands=['start','help'])
def send_info(message):
    '''Sends Start and Help Message.'''
    text = (
    "<b>Welcome to the Oxford Dictionary.\nA Word Meaning Finder!</b>\n"
    "Use /find {your word} to get info."

    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Maintained By",url="t.me/error404_inline1"))
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup, disable_web_page_preview=True)

@bot.message_handler(commands=['find'])
def definition(message):
    '''Sends Definitions and Pronunciations.'''
    endpoint = "entries"
    language_code = "en-us"
    word_id = message.text
    word_id = util.extract_arguments(word_id)
    url = "https://od-api.oxforddictionaries.com/api/v2/" + endpoint + "/" + language_code + "/" + word_id.lower()
    r = requests.get(url, headers = {"app_id": app_id, "app_key": app_key})

    bot.send_message(message.chat.id,word_id)
    try:
        try:
            definitions = r.json()['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['definitions'][0]
            sentence = r.json()['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['examples'][0]['text']
            bot.send_message(message.chat.id, f'Word - {word_id}\nDefinition - {definitions}\nExample Sentence - {sentence.capitalize()}.')
        except:
            bot.send_message(message.chat.id, 'Meaning not found!')
        try:
            audio_file = r.json()['results'][0]['lexicalEntries'][0]['entries'][0]['pronunciations'][1]['audioFile']
            bot.send_audio(message.chat.id, audio=audio_file)
        except:
            bot.send_message(message.chat.id, 'Pronunciation not found!')
    except:
        bot.send_message(message.chat.id, 'Something went wrong...')

# Setting up Web Hook
app = Flask(__name__)
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():  
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200
@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + TOKEN)
    return "!", 200
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


