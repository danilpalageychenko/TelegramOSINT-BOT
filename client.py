import sys
import os
from telethon.tl.types import InputPhoneContact
from telethon.tl.functions.contacts import ImportContactsRequest
import pytz
import telebot
from dependency import token, api_id, api_hash, passwordFor2Factor
from telethon.sync import TelegramClient
from telethon import functions


bot = telebot.TeleBot(token)
client = TelegramClient('telegramOsint', api_id, api_hash)
client.start(password=passwordFor2Factor)
contact_phone_number = str(sys.argv[1])
chatId = sys.argv[2]
contact = InputPhoneContact(client_id=0, phone=contact_phone_number, first_name="", last_name="")
result = client(ImportContactsRequest(contacts=[contact]))
res = []
try:
    contact_info = client.get_entity(contact_phone_number)
    res.append(contact_info.phone)
    result = client(functions.contacts.DeleteContactsRequest(
        id=[contact_info.id]
    ))
    contact_info = result.users[0]
    res.append(contact_info.id)
    if contact_info.username is not None: res.append( "@" + contact_info.username)
    else: res.append(contact_info.username)
    res.append(contact_info.first_name)
    res.append(contact_info.last_name)
    res.append(contact_info.lang_code)
    if hasattr(contact_info.status, "was_online"):
        res.append(contact_info.status.was_online.astimezone(pytz.timezone('Europe/Kiev')))
    elif str(contact_info.status) == "UserStatusRecently()":
        res.append("Статус скрыт")
    else:
        res.append("Online")
    res.append(client.download_profile_photo(contact_info.id))
except Exception as err:
    print(err)
    bot.send_message(chatId, "Nomer nezaregan ili scrut")
    exit()

masName = ["*Number: *+", "*Telegram ID: *", "*Username: *", "*First_name: *", "*Last_name: *", "*language_code: *", "*Last_Online: *"]
resultString = ""
for i in range(len(masName)):
    if str(res[i]) == "None":
        continue
    resultString += str(masName[i]) + str(res[i]) + "\n"

keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
button = telebot.types.InlineKeyboardButton(text='Проверить WhatsApp', url='https://wa.me/%s'%res[0])
button1 = telebot.types.InlineKeyboardButton(text='Загуглить телефон', url='https://www.google.ru/search?q=+%s'%res[0])
keyboard.add(button, button1)
if res[2] != "None":
    keyboard.add(
        telebot.types.InlineKeyboardButton(text='Загуглить Username', url='https://www.google.ru/search?q=%a' % contact_info.username),
        telebot.types.InlineKeyboardButton(text='Поиск username в buzz.im', url='https://search.buzz.im/?param=query&search=%s' % contact_info.username),
        telebot.types.InlineKeyboardButton(text='Поиск username в Instagram', url='https://www.instagram.com/%s' %contact_info.username),
        telebot.types.InlineKeyboardButton(text='Поиск username в Facebook', url='https://www.facebook.com/%s' %contact_info.username),
        telebot.types.InlineKeyboardButton(text='Поиск username в Github', url='https://github.com/%s' %contact_info.username))

if res[7] != None:
    photo = open(res[7], "rb")
    bot.send_photo(chatId, photo, caption=resultString, parse_mode='Markdown', reply_markup=keyboard)
    photo.close()
    os.remove(res[7])
else:
    bot.send_message(chatId, resultString, parse_mode='Markdown', reply_markup=keyboard)
