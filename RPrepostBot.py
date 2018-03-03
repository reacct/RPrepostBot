import sys
import asyncio
import telepot
import telepot.aio
from telepot.aio.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import vk_api
import requests, shutil
from pprint import pprint


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
    pprint(attachs)

    vk_response = vk.wall.post(owner_id=vk_group, from_group=1, message=text,
				attachments=",".join(attachs))
    pprint(vk_response)

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
async def channel_handler(msg):
    print("channel handler")
    if not "text" in msg: return  #ПЕРЕСМОТРЕТЬ + сделать для фото

    channelusername = "@" + msg['chat']['username']
    print(channelusername)
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

    post_id = vk_poster(VK_TOKEN, VK_APP_ID, VK_GRP_ID, text=text, bold=bold, pics=pics, urls=["https://t.me/{}/{}".format(tg_channel, msg_id)])
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

def private_handler(msg):
async def private_handler(msg):
    print("private handler")
    #


async def handle(msg):
    print("===================")
    flavor = telepot.flavor(msg)

    summary = telepot.glance(msg, flavor=flavor)
    print(flavor, summary)
    pprint(msg)

    if flavor == "chat":   #написать обработчик [/] команд
    if flavor == "chat":
        if summary[1] == "channel":
            await channel_handler(msg)
        elif summary[1] == "group":
            group_handler(msg)
        elif summary[1] == "private":
            private_handler(msg)
            await private_handler(msg)
    else:
        print("Not a 'chat'")





    print("///////////////////")



TG_TOKEN = sys.argv[1]  # get telegram token from command-line
VK_TOKEN = sys.argv[2]  # get vk token from command-line
VK_APP_ID = sys.argv[3]  # get app id from command-line
VK_GRP_ID = -162320418

tg_channel = "q2w_test"

bot = telepot.aio.Bot(TG_TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(MessageLoop(bot, handle).run_forever())
print('Listening ...')

loop.run_forever()
