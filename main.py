
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import JobQueue
from telegram.ext import Job
import time
import requests
import json
import os.path
from VARIABLES import *

updater = Updater(token=TOKEN_VAR, use_context=True)
dispatcher = updater.dispatcher
job_queue = updater.job_queue
url = "https://api.binance.com/api/v3/ticker/price"

currency = {}


def callback_USD(price,id):
    if (price.isnumeric() and os.path.isfile(f'./data/{id}.json')):
        number = int(price)
        
        def callback_end(context):
            total = 0
            with open(f"./data/{context.job.name}.json") as json_file:
                data = json.load(json_file)
                for key in data.keys():
                    if key in currency:
                        total += float(data[key]) * float(currency[key])
            if total >= number:
                job_queue.get_jobs_by_name(context.job.name)[0].schedule_removal()
                context.bot.send_message(chat_id=context.job.name, 
                                    text="Logró la meta de " + str(total) + "\n Se eliminó el loop")
        
        return [True, callback_end]
    else:
        return [False, None]
        


def callback_minute(context):
    total = 0
    with open(f"./data/{context.job.name}.json") as json_file:
        data = json.load(json_file)
        for key in data.keys():
            if key in currency:
                total += data[key] * currency[key]
    context.bot.send_message(chat_id=context.job.name, 
                             text=str(total))

def update_values(context):
    global currency
    response = requests.request("GET", url)
    currency = {moneda['symbol'] : moneda['price'] for moneda in response.json() }
    return


def start(update, context):
    if (str(update.effective_chat.id) != ADMIN_ID):
        return

    elif (len(job_queue.get_jobs_by_name(str("requester"))) == 0):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Updater Started")
        job_queue.run_repeating(update_values,interval=QUERY_TIME_API,first=0.0,context=context,name="requester")
        return
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Updater is Working")
        return

def start_loop(update, context):
    inputs = update['message']['text'].split()
    if (len(inputs) != 2):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Usar \start_loop HMny")
        return

    result = callback_USD(inputs[1],update.effective_chat.id)

    if (not result[0]):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Valor no válido o no tiene data")
        return   

    if (len(job_queue.get_jobs_by_name(str(update.effective_chat.id))) == 0):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Se ha lanzado un loop")
        job_queue.run_repeating(result[1],interval=5.0,first=0.0,context=context,name=str(update.effective_chat.id))
    
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ya tiene un loop")
    return

def end_loop(update,context):
    if (len(job_queue.get_jobs_by_name(str(update.effective_chat.id))) != 0):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Se ha removido el loop")
        job_queue.get_jobs_by_name(str(update.effective_chat.id))[0].schedule_removal()
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No tiene un loop")
    return

def get_total_USD(update,context):
    total = 0
    if not os.path.isfile(f'./data/{update.effective_chat.id}.json'):
        context.bot.send_message(chat_id=update.effective_chat.id, text="No tiene data")
        return
    with open(f"./data/{update.effective_chat.id}.json") as json_file:
                data = json.load(json_file)
                for key in data.keys():
                    if key in currency:
                        total += float(data[key]) * float(currency[key])
    context.bot.send_message(chat_id=update.effective_chat.id, text="Tiene: "+str(total))
    return
    
def make_data(update,context):
    inputs = update['message']['text'].split()
    if (len(inputs) != 2):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Usar /make_data {moneda : cantidad,...}")
        return
    try:
        dict_res = json.loads(inputs[1])
        f = open(f"./data/{update.effective_chat.id}.json", "w")
        f.write(inputs[1])
        f.close()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Creado")
        context.bot.send_message(chat_id=ADMIN_ID, text="Se creó el perfil: " + str(update.effective_chat.id))
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Falló")
    return
    

#### Handlers SetUp ####
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

start_loop_handler = CommandHandler('start_loop', start_loop)
dispatcher.add_handler(start_loop_handler)

end_loop_handler = CommandHandler('end_loop', end_loop)
dispatcher.add_handler(end_loop_handler)

get_total_handler = CommandHandler('get_total', get_total_USD)
dispatcher.add_handler(get_total_handler)

make_data_handler = CommandHandler('make_data', make_data)
dispatcher.add_handler(make_data_handler)


#### Run ####
updater.start_polling()
updater.idle()
