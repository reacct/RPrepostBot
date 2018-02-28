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

async def channel_handler(msg):
    print("channel handler")
    if not "text" in msg: return  #ПЕРЕСМОТРЕТЬ + сделать для фото

    channelusername = "@" + msg['chat']['username']
    print(channelusername)
    ents = []				#entities of post
    text = ""				#text of post
    msg_id = msg['message_id']

    if "text" in msg:
        text = msg['text']
    if "entities" in msg:
        ents = msg['entities']

    urls = []
    bold = []
    pics = []
    if text and ents:
        for ent in ents:
            if ent['type'] == "text_link":
                urls.append(ent['url'])
            elif ent['type'] == "bold":
                star_ch = ent['offset']
                end_ch = ent['offset'] + ent['length']
                bold.append((star_ch,end_ch))

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

    keyboard = InlineKeyboardMarkup(inline_keyboard=[	#Добавить счётчик переходов
                   [InlineKeyboardButton(text='VK', url='https://vk.com/wall{}_{}'.format(VK_GRP_ID, post_id)),
                    InlineKeyboardButton(text='FB', url='https://fb.com/'),
                    InlineKeyboardButton(text='Tw', url='https://twitter.com/')],
               ])
    sent = await bot.sendMessage(channelusername, "For repost in social", 					reply_markup=keyboard)

def group_handler(msg):
    print("group handler")

def private_handler(msg):
    print("private handler")
    #


async def handle(msg):
    print("===================")
    flavor = telepot.flavor(msg)

    summary = telepot.glance(msg, flavor=flavor)
    print(flavor, summary)
    pprint(msg)

    if flavor == "chat":   #написать обработчик [/] команд
        if summary[1] == "channel":
            await channel_handler(msg)
        elif summary[1] == "group":
            group_handler(msg)
        elif summary[1] == "private":
            private_handler(msg)
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
