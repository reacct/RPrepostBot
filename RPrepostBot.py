import sys
import asyncio
import telepot
import telepot.aio
from telepot.aio.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import vk_api
import requests, shutil, re
from database.database import engine, Base
from database import utils
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists, create_database, drop_database
from pprint import pprint

commands = ("/start",
            "/addchannel",
#            "/checkadmin",
#            "/addvktoken",
#            "/addvkgroup",
#            "/addvkalbum",
            "/help")
HELLO_FIRST_MSG = ("РУССКИЙ ЯЗЫК", "Hi new user!") #ИЗМЕНИТЬ
HELLO_MSG = ("РУССКИЙ ЯЗЫК", "Hi, {}! You are welcome!")
START_MSG = ("РУССКИЙ ЯЗЫК", "Start message!")
HELP_MSG = ("РУССКИЙ ЯЗЫК", "Help message!")
ADD_CHANNEL_MSG = ("РУССКИЙ ЯЗЫК", "Add channel message!")

CANCEL_BTN = ("Отмена", "Cancel")

def vk_poster(vk_token, vk_app, vk_group, text=None, bold=None, pics=None, urls=None):
    if not(text or pics):
        raise ValueError("Not Text or Pics")

    vk_session = vk_api.VkApi (token=vk_token, app_id=vk_app)
    vk = vk_session.get_api()

    attachs = []

    if pics:
        vk_response = vk.photos.getAlbums(owner_id=vk_group)
        album = vk_response['items'][0]['id']
        upload = vk_api.VkUpload(vk_session)
        for pic in pics:
            photo = upload.photo(pic, album_id=album, group_id=abs(vk_group))
            photo_url = "photo{}_{}".format(vk_group, photo[0]['id'])
            attachs.append(photo_url)


    if urls:
        attachs.append(urls[0])

    vk_response = vk.wall.post(owner_id=vk_group, from_group=1, message=text,
				attachments=",".join(attachs))

    post_id = vk_response['post_id']

    return post_id

def message_formater(text, bold=None, italic=None, code=None, pre=None, text_link=None):
    formated_text = text
    format_chars = {}
    sorted_format_chars = []

    if bold:
        for item in bold:
            if item[0] in format_chars:
                format_chars[item[0]] = "{}*".format(format_chars[item[0]])
            else:
                format_chars[item[0]] = "*"
            if item[1] in format_chars:
                format_chars[item[1]] = "*{}".format(format_chars[item[1]])
            else:
                format_chars[item[1]] = "*"
    if italic:
        for item in italic:
            if item[0] in format_chars:
                format_chars[item[0]] = "{}_".format(format_chars[item[0]])
            else:
                format_chars[item[0]] = "_"
            if item[1] in format_chars:
                format_chars[item[1]] = "_{}".format(format_chars[item[1]])
            else:
                format_chars[item[1]] = "_"
    if code:
        for item in code:
            if item[0] in format_chars:
                format_chars[item[0]] = "{}`".format(format_chars[item[0]])
            else:
                format_chars[item[0]] = "`"
            if item[1] in format_chars:
                format_chars[item[1]] = "`{}".format(format_chars[item[1]])
            else:
                format_chars[item[1]] = "`"
    if pre:
        for item in pre:
            if item[0] in format_chars:
                format_chars[item[0]] = "{}```".format(format_chars[item[0]])
            else:
                format_chars[item[0]] = "```"
            if item[1] in format_chars:
                format_chars[item[1]] = "```{}".format(format_chars[item[1]])
            else:
                format_chars[item[1]] = "```"
    if text_link:
        for item in text_link:
            if item[0] in format_chars:
                format_chars[item[0]] = "{}[".format(format_chars[item[0]])
            else:
                format_chars[item[0]] = "["
            if item[1] in format_chars:
                format_chars[item[1]] = "]({}){}".format(item[2],format_chars[item[1]])
            else:
                format_chars[item[1]] = "]({})".format(item[2])

    dic_keys = list(format_chars.keys())
    dic_keys.sort(reverse=True)
    for key in dic_keys:
        sorted_format_chars.append((key,format_chars[key]))

    for char in sorted_format_chars:
        formated_text = formated_text[:(char[0])] + char[1] + formated_text[(char[0]):]
    pprint(formated_text)
    return formated_text

async def start_cmd(msg, db_session, tg_user_id):
    print("Start command")

    keyboard = ReplyKeyboardMarkup(keyboard=[
                   [KeyboardButton(text='Справка'),
                    KeyboardButton(text='Добавить канал')],
               ], resize_keyboard=True, one_time_keyboard=True)
    sent = await bot.sendMessage(tg_user_id,START_MSG[1],parse_mode='Markdown',reply_markup=keyboard)

async def addchannel_cmd(msg, db_session, tg_user_id, answer=False):
    print("Add channel command")
    if answer:
        channel = 0
        chat = {}
        if "forward_from_chat" in msg:
            channel = msg['forward_from_chat']['id']
            try:
                chat = await bot.getChat(channel)
            except:
                print("Not id of channel")
        elif "text" in msg:
            match = ""
            if re.match(r"^@\w{3,}$", msg['text']):
                match = msg['text']
            elif re.match(r"^-\d{6,}$", msg['text']):
                match = int(msg['text'])
            if match:
                try:
                    chat = await bot.getChat(match)
                    channel = chat['id']
                except:
                    print("Unknown name")
        else:
            raise("Unknown type in place of waiting new channel id")

        if chat and chat['type'] == "channel":
            admins = {}
            try:
                admins = await bot.getChatAdministrators(channel)
                pprint(admins)
            except:
                sent = await bot.sendMessage(tg_user_id, "Bot is not an administartor of this channel") #В БОЛЬШУЮ ПЕРЕМЕННУЮ
            for admin in admins:
                if admin['user']['id'] == 548347944: #НОМЕР БОТА. УБРАТЬ!!!
                    if admin['can_delete_messages'] and admin['can_edit_messages'] and admin['can_invite_users'] and admin['can_post_messages']:
                        db_tg_user = utils.get_tg_user(db_session, tg_user_id)
                        channels = utils.get_channels(db_session, db_tg_user)
                        if not channel in channels:
                            print(channels)
                            utils.add_tg_channel(db_session, channel, db_tg_user)
                            sent = await bot.sendMessage(tg_user_id, "This channel has successfully been added") #В БОЛЬШУЮ ПЕРЕМЕННУЮ
                        else:
                            sent = await bot.sendMessage(tg_user_id, "This channel was already added") #В БОЛЬШУЮ ПЕРЕМЕННУЮ
                        return
                    else:
                        sent = await bot.sendMessage(tg_user_id, "Bot have not required permissions") #В БОЛЬШУЮ ПЕРЕМЕННУЮ
                    break

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text=CANCEL_BTN[0], callback_data='cancel_command')],
               ])

    sent = await bot.sendMessage(tg_user_id, ADD_CHANNEL_MSG[1], reply_markup=keyboard)
    DIALOG_STATE = "hard_addchannel" #ДОЛЖНО БЫТЬ В БАЗЕ

async def checkadmin_cmd(msg):
    print("checkadmin_cmd")

async def addvktoken_cmd(msg):
    print("addvktoken")

async def addvkgroup_cmd(msg):
    print("addvkgroup_cmd")

async def addvkalbum_cmd(msg):
    print("addvkalbum_cmd")

async def help_cmd(msg, db_session, tg_user_id):
    print("Help command")
    sent = await bot.sendMessage(tg_user_id,HELP_MSG[1],parse_mode='Markdown')

async def channel_handler(msg):
    print("channel handler")
    if not "text" in msg: return  #ПЕРЕСМОТРЕТЬ + сделать для фото

    channelusername = "@" + msg['chat']['username']
    channel_id = msg['chat']['id']
    ents = []				#entities of post
    text = ""				#text of post
    msg_id = msg['message_id']

    if "text" in msg:
        text = msg['text']
    if "entities" in msg:
        ents = msg['entities']

    urls = []
    bold = []
    italic = []
    code = []
    pre = []
    text_link = []
    pics = []
    if text and ents:
        for ent in ents:
            if ent['type'] == "text_link":
                urls.append(ent['url'])
                start_ch = ent['offset']
                end_ch = ent['offset'] + ent['length']
                text_link.append((start_ch,end_ch,ent['url']))
            elif ent['type'] == "bold":
                start_ch = ent['offset']
                end_ch = ent['offset'] + ent['length']
                bold.append((start_ch,end_ch))
            elif ent['type'] == "italic":
                start_ch = ent['offset']
                end_ch = ent['offset'] + ent['length']
                italic.append((start_ch,end_ch))
            elif ent['type'] == "code":
                start_ch = ent['offset']
                end_ch = ent['offset'] + ent['length']
                code.append((start_ch,end_ch))
            elif ent['type'] == "pre":
                start_ch = ent['offset']
                end_ch = ent['offset'] + ent['length']
                pre.append((start_ch,end_ch))
            elif ent['type'] == "url":
                start_ch = ent['offset']
                end_ch = ent['offset'] + ent['length']
                urls.append(text[start_ch:end_ch])

    for url_item in urls:
       if url_item.endswith('.jpg') or url_item.endswith('.jpeg') or url_item.endswith('.png') or url_item.endswith('.gif'):#оптимизировать списком граф.расширения
           picname_pos = url_item.rfind("/") + 1
           pic_item = "pics/" + url_item[picname_pos:]
           pics.append(pic_item)
           filereq = requests.get(url_item,stream = True)
           with open(pic_item,"wb") as receive:
               receive.write(filereq.content)
           del filereq

    post_id = vk_poster(VK_TOKEN, VK_APP_ID, VK_GRP_ID, text=text, bold=bold, pics=pics, urls=["https://t.me/{}".format(tg_channel)])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[	#Добавить счётчик переходов
                   [InlineKeyboardButton(text='VK', url='https://vk.com/wall{}_{}'.format(VK_GRP_ID, post_id)),
                    InlineKeyboardButton(text='FB', url='https://fb.com/'),
                    InlineKeyboardButton(text='Tw', url='https://twitter.com/')],
               ])
    try:
        sent = await bot.editMessageReplyMarkup((channel_id, msg_id),reply_markup=keyboard)
    except Exception as e:
        print("Exception of editing message", e)
        markdown_text = message_formater(text, bold, italic, code, pre, text_link)
        if markdown_text:
            sent = await bot.deleteMessage((channel_id, msg_id))
            sent = await bot.sendMessage(channel_id,markdown_text,parse_mode='Markdown',disable_notification=True,reply_markup=keyboard)

def group_handler(msg):
    print("group handler")

async def private_handler(msg, db_session):
    print("private handler")
    tg_user_id = None
    if not "text" in msg:
        return

    tg_user_id = msg['from']['id']
    tg_user_name = msg['from']['first_name']

    if not utils.get_tg_user(db_session, tg_user_id):
        sent = await bot.sendMessage(tg_user_id,HELLO_FIRST_MSG[1],parse_mode='Markdown')
        try:
            utils.add_tg_user(db_session, tg_user_id)
            #ДОБАВИТЬ В БАЗУ ИМЯ ПОЛЬЗОВАТЕЛЯ
        except:
            print("Problem with adding new tg user")
            return
        print("Added new user")
        return

    sent = await bot.sendMessage(tg_user_id,HELLO_MSG[1].format(tg_user_name),parse_mode='Markdown')

    dialog_state = DIALOG_STATE #database
    if dialog_state:
        if dialog_state == "hard_addchannel":
            await addchannel_cmd(msg, db_session, tg_user_id, answer=True)

    for command in commands:            #Возможно, стоит проверять по entities bot_command
        regex = re.compile("{}(\s+.*)*$".format(command)) #Регулярное выражение
        if re.match(regex, msg['text']):
            if command == "/start":
                await start_cmd(msg, db_session, tg_user_id)
            elif command == "/addchannel":
                await addchannel_cmd(msg, db_session, tg_user_id)
#            elif command == "/checkadmin":
#                await checkadmin_cmd(msg)
#            elif command == "/addvktoken":
#                await addvktoken_cmd(msg)
#            elif command == "/addvkgroup":
#                await addvkgroup_cmd(msg)
#            elif command == "/addvkalbum":
#                await addvkalbum_cmd(msg)
            elif command == "/help":
                await help_cmd(msg, db_session, tg_user_id)
            else:
                print("Command without function!")

    if msg['text'] == "Справка":
        await help_cmd(msg, db_session, tg_user_id)
    elif msg['text'] == "Добавить канал":
        await addchannel_cmd(msg, db_session, tg_user_id)

async def handle(msg):
    print("===================")
    DBSession = sessionmaker(bind=engine)
    db_session = DBSession()

    flance = telepot.flance(msg)
    print(flance)
    pprint(msg)

    if flance[0] == "chat":
        if flance[1][1] == "channel":
            await channel_handler(msg)
        elif flance[1][1] == "group":
            group_handler(msg)
        elif flance[1][1] == "private":
            await private_handler(msg, db_session)
    elif flance[0] == "callback_query":
        tg_user_id = msg['from']['id']
        callback_query = msg['data']
        msg_id = msg['message']['message_id']
        db_tg_user = utils.get_tg_user(db_session, tg_user_id)

        if callback_query == "cancel_command":
            DIALOG_STATE = "" #ДОЛЖНО БЫТЬ В БАЗЕ
            sent = await bot.deleteMessage((tg_user_id, msg_id))
    else:
        print("Not a 'chat'")




    try:
        db_session.close()
    except:
        print("Database session was not closed")
    print("///////////////////")

def reset_db():
    """
    Resets database
    :return: 1 if datebase has been renewed, 0 someelse
    """
    if "true" != input("Accepting hardreset DB type 'true': "):
        return 0

    if database_exists(engine.url):
        try:
            drop_database(engine.url)
        except:
            print('Problems with database drop')
        try:
            create_database(engine.url, encoding='utf8mb4')
        except:
            print('Problem with database creation')

    Base.metadata.create_all(engine)
    return 1

if "resetdb" in sys.argv:
    reset_db()

TG_TOKEN = sys.argv[1]  # get telegram token from command-line
VK_TOKEN = sys.argv[2]  # get vk token from command-line
VK_APP_ID = sys.argv[3]  # get app id from command-line
VK_GRP_ID = -162320418

DIALOG_STATE = "hard_addchannel" #ДОЛЖНО БЫТЬ В БАЗЕ

tg_channel = "q2w_test"

bot = telepot.aio.Bot(TG_TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(MessageLoop(bot, handle).run_forever())
print('Listening ...')

loop.run_forever()
