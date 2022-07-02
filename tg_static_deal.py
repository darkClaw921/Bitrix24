from bitrix24 import Bitrix24
from loguru import logger 
from pprint import pprint
from art import text2art
import matplotlib.pyplot as plt
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters.builtin import Text
from aiogram.types.message import ContentType 
from aiogram.types import InputFile
TOKEN = '5530309347:AAGq09LtXQXdAsL3f2Tq_8Zf25P6YZayCVA'
#from datetime import datetime
bot = Bot(token=TOKEN) 
dp = Dispatcher(bot,storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

markup_first = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Получить отчет')
)

webhook = ''
bit = Bitrix24(webhook)
deal = 6155

entity = "DEAL_STAGE"
id_status = "2"

dateBit = '2022-06-30T00:00:00+03:00'
stringT= 'T00:00:00+03:00'

#UF_CRM_1651825495017 - дата актуализации потребности
#UF_CRM_1656505452008 - тестовое поле для статистики 0 нет 1 да
#UF_CRM_1651741689379 - результат презинтации str

@logger.catch
def get_user_name(ID:str):
    b = bit.callMethod('user.get', ID=ID)[0]
    #pprint(b)
    return f"{b['NAME']}\n{b['LAST_NAME']}" 

@logger.catch
def prepare_date_to_int(string: str)->int:
    """ Преобразует строку 2022-06-30T00:00:00+03:00 в 20220630
    """
    string = string.split('T')[0].replace('-','')
    return int(string)
#начало конец
date = '2022-05-30/2022-06-30'

@logger.catch
def get_deal(date:str):
    #b = bit.callMethod('crm.dealcategory.list',
    #b = bit.callMethod('crm.dealcategory.stage.list',
    dateList = date.split('/')
    b = bit.callMethod('crm.deal.list',
            #ID=deal,
            #entityTypeId=2, 
            FILTER={"ENTITY_ID": "DEAL_STAGE", 
                'STATUS_ID': id_status, 
                ">=DATE_CREATE": dateList[0], 
                "<=DATE_CREATE": dateList[1], 
                #'!UF_CRM_1651825495017': ''},
                'UF_CRM_1656505452008': '1'},
            #FILTER={"ID": 6075,},
            select=[ "ID", "TITLE", "CREATED_TIME",'OWNER_ID','ASSIGNED_BY_ID' ])
   
    #pprint(b)
    return b

@logger.catch
def prepare_dict_to_name_managers(managers:dict):
    """
    return:
    [list],[lsit] - name, count
    """
    listNames=[]
    listCounts=[]
    for managerID, count in managers.items():
        name = get_user_name(managerID)
        listNames.append(name)
        listCounts.append(count)
    return listNames, listCounts

@logger.catch
def create_histogram(names, counts):
    
    #ax.set_ylim(ax.get_ylim()[0],
    #ax.get_ylim()[1]+ax.get_ylim()[1]/5)
    #fig = plt.figure()
    fig, ax = plt.subplots()
    position = range(len(names))
    ax.barh(position, counts)
    #plt.bar(names, users,)
    ax.set_yticks(position)
    ax.set_yticklabels(names,
                   fontsize = 13,
                   verticalalignment =  'center')
    fig.set_figwidth(15)
    for index, value in enumerate(counts):
        label = format(int(value), ',')
        plt.annotate(label, xy=(value/2, index-0.1), color='black')
    
    #fig.set_figheight(6)
    plt.title('Статистика менеджеров')
    #save(name='pic_2_2', fmt='png')
    plt.savefig('test', ftm='png')
    #plt.show()

def create_pie(names, counts):
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot()
    ax.pie(counts, labels=names,autopct='%.f')
    plt.show()

@dp.message_handler(state='date') 
async def aboniment_state(msg: types.Message):
   
    date = msg.text
    print(date)
    deals = get_deal(date)
    managers={}

    for deal in deals:
        try:
            managers[deal['ASSIGNED_BY_ID']]+=1    
        except:
            managers.setdefault(deal['ASSIGNED_BY_ID'],1)
    pprint(managers)
    names, counts = prepare_dict_to_name_managers(managers)
    #create_pie(names,counts)
    create_histogram(names,counts)
    photo1 = InputFile('test.png')
    state = dp.current_state(user=msg.from_user.id)
    await state.finish()
    await bot.send_photo(chat_id= msg.chat.id, photo=photo1)

@dp.message_handler(commands=['start'])
async def process_start_command(msg: types.Message):
    await msg.reply("Пришлите дату в формате начало/конец (2022-06-22/2022-07-22)",reply_markup=markup_first)
    state = dp.current_state(user=msg.from_user.id)
    await state.set_state('date')

@dp.message_handler(content_types=ContentType.ANY)
@logger.catch
async def echo_message(msg: types.Message):
    message = msg.text.lower()
    user_id = msg.from_user.id
    state = dp.current_state(user=msg.from_user.id)

    if message == 'получить отчет':
        await process_start_command(msg)

@logger.catch
def main():
    deals = get_deal(date)
    managers={}

    for deal in deals:
        try:
            managers[deal['ASSIGNED_BY_ID']]+=1    
        except:
            managers.setdefault(deal['ASSIGNED_BY_ID'],1)
    pprint(managers)
    names, counts = prepare_dict_to_name_managers(managers)
    #create_pie(names,counts)
    create_histogram(names,counts)
    


    #print(len(a))

if __name__ == '__main__':
    art = text2art('Statistic deal', 'rand')
    print(art)
    executor.start_polling(dp)
    #b = bit.callMethod('crm.deal.get', ID=6155)
    #pprint(b)
 #   main()
