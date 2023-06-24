from dotenv.main import load_dotenv
import os
import openai
import telebot
import json
from time import sleep

load_dotenv()
API_KEY = os.environ['OPENAI_API_KEY']
TG_KEY = os.environ['TELEGRAM_TOKEN']
openai.api_key = API_KEY

tb = telebot.AsyncTeleBot(TG_KEY)

bot = telebot.TeleBot(TG_KEY)

def updateUsers():
    with open('log.json', 'r', encoding='utf8') as file:
        data = json.loads(file.read())
    return data

updateUsers()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    data = updateUsers()
    usersId = [i["id"] for i in data]

    data.append(message.from_user.__dict__)
    
    if(message.from_user.id not in usersId):
        with open('log.json', 'w', encoding='utf8') as file:
            file.write(json.dumps(data, indent=4, ensure_ascii=False))

    bot.send_message(message.chat.id, "This is a telegram bot based on Chat-GPT.\nType your question to get started!")



@bot.message_handler(content_types=['text'])
def dialog(message):

    tbp = 'Answer:\n' #to be printed
    orig_message = bot.send_message(message.chat.id, tbp)
    typing_symbol = '▒'

    response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'user', 'content': f'{message.text}'}
    ],
    temperature=0.5,
    stream=True
)

    for chunk in response:
        try:
            tbp = tbp + (chunk['choices'][0]['delta']['content'] if 'content' in chunk['choices'][0]['delta'] else '')
            
            sleep(0.2)

            if(chunk['choices'][0]['finish_reason']):
                bot.edit_message_text(tbp, chat_id=message.chat.id, message_id=orig_message.message_id)
            else:
                bot.edit_message_text(tbp+typing_symbol, chat_id=message.chat.id, message_id=orig_message.message_id)

        except:
            # sleep(10)
            pass

        # print(chunk['choices'][0]['delta']['content'] if 'content' in chunk['choices'][0]['delta'] else '' )


bot.infinity_polling()