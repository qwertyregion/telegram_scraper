import os
import re
import settings
import logging
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import PeerChannel
from telethon import functions, types
from telethon.utils import pack_bot_file_id
import requests
import time
import pdfkit
from bs4 import BeautifulSoup



api_id = settings.tg_sec['api_id']
api_hash = settings.tg_sec['api_hash']
client = TelegramClient('session',
                        api_id,
                        api_hash,
                        system_version='python',
                        device_model='pycharm',
                        app_version='1.01',
                        )

download_root = settings.download_root
logging.basicConfig(level=logging.INFO)

async def ParseOnlyUnread():
    """ function for collecting data from unread messages """
    channels_ids = settings.channels_unread_only
    channels_count = 1
    channels_total = len(channels_ids)
    for channel_id in channels_ids:
        channel_entity = await client.get_entity(PeerChannel(channel_id)) #PeerChannel
        download_root = r'c:\Users\QWERTY\Desktop\telegram_scraper\download'
        title_channel = channel_entity.title
        title_channel = re.sub(r"[><:/|\.?*]", "", title_channel)
        dialog = await client(functions.messages.GetPeerDialogsRequest(peers=[channel_id]))
        dialog = dialog.dialogs[0]
        unread_messages = []
        count = 1
        logging.info(f'One moment. Counting messages in the {channel_entity.title} channel')
        async for message in client.iter_messages(PeerChannel(channel_id)):
            if count > dialog.unread_count:
                break
            unread_messages.append(message)
            count += 1
        if len(unread_messages) == 0:
            logging.info(f'No read messages in {channel_entity.title} channel')
        # Is unread messages
        elif len(unread_messages) > 0:
            m_readed_count = 1
            m_total = len(unread_messages)
            os.chdir(r'C:\Users\QWERTY\Desktop\telegram_scraper')
            for msg in unread_messages[::-1]:
                await message_processing(msg=msg,
                                         title_channel=title_channel,
                                         channels_count=channels_count,
                                         channels_total=channels_total,
                                         m_readed_count=m_readed_count,
                                         m_total=m_total,
                                         )
                m_readed_count += 1
        channels_count += 1

async def ParseAll():
    """ function for collecting data from all available messages """
    channels_ids = settings.channels_all
    channels_count = 1
    channels_total = len(channels_ids)
    for channel_id in channels_ids:
        channel_entity = await client.get_entity(PeerChannel(channel_id))
        title_channel = channel_entity.title
        title_channel = re.sub(r"[><:/|.?*]", "", title_channel)
        dialog = await client(functions.messages.GetPeerDialogsRequest(peers=[channel_id]))
        dialog = dialog.dialogs[0]
        m_readed_count = 1
        m_total = 0
        logging.info(f'One moment. Counting messages in the {channel_entity.title} channel')
        os.chdir(r'C:\Users\QWERTY\Desktop\telegram_scraper')
        async for msg in client.iter_messages(channel_id):
            m_total += 1
            await message_processing(msg=msg,
                                     title_channel=title_channel,
                                     channels_count=channels_count,
                                     channels_total=channels_total,
                                     m_readed_count=m_readed_count,
                                     m_total=m_total,
                                     )
            m_readed_count += 1
        channels_count += 1

async def message_processing(msg, title_channel, channels_count, channels_total, m_readed_count, m_total, ):
    """ function of preparing a message for uploading text, media, HTML and PDF data """
    date_msg = msg.date
    time_msg = date_msg.strftime('%H_%M_%S')
    str_time_msg = time_zone_correction(time_msg)
    str_date_msg = date_msg.strftime('%Y_%m_%d')
    name_file = title_channel + '--' + str_date_msg + '--' + str_time_msg + '--'
    path_to_msg = os.path.join(download_root, title_channel, str_date_msg, str_time_msg, )
    if not os.path.isdir(path_to_msg):
        os.makedirs(path_to_msg)
        text_message_processing(msg=msg, name_file=name_file, path_to_msg=path_to_msg,)
        hyperlink_processing(msg=msg, hyperlink_template='https://telegra.ph', name_file=name_file,path_to_msg=path_to_msg,)
        await media_processing(msg=msg,
                               name_file=name_file,
                               path_to_msg=path_to_msg,
                               title_channel=title_channel,
                               channels_count=channels_count,
                               channels_total=channels_total,
                               m_readed_count=m_readed_count,
                               m_total=m_total,)
        await msg.mark_read()

async def media_processing(msg, name_file, path_to_msg, title_channel, channels_count, channels_total, m_readed_count, m_total):
    """ function for uploading media data """
    if msg.media is not None:
        path = None
        if getattr(msg.media, 'photo', None):
            filename_photo = 'photo--{}'.format(name_file)
            if not os.path.isfile(path_to_msg + '/' + filename_photo):
                path = await msg.download_media(path_to_msg + '/' + filename_photo, progress_callback=progress_callback, thumb=-1)
        # if only_photo is True, will download only photo, not documents(video, gifs, files)
        if getattr(msg.media, 'document', None) and settings.parser['only_photo'] == False:  # elif
            filename_document = 'document--{}'.format(name_file)
            if not os.path.isfile(path_to_msg + '/' + filename_document):
                path = await msg.download_media(path_to_msg + '/' + filename_document, progress_callback=progress_callback)
        # Log download event
        if not None == path:
            logging.info(
                f'[Channels: {channels_count}/{channels_total}] [Progress: {m_readed_count}/{m_total}] '
                f'[DOWNLOAD] media from {title_channel} to ' + path)


def text_message_processing(msg, name_file, path_to_msg):
    """ function for uploading text data """
    text_message = msg.message
    if text_message is not None:
        filename_text = 'text--{}.txt'.format(name_file)
        with open(path_to_msg + '/' + filename_text, "a", encoding="UTF-8") as fail_text:
            fail_text.write(text_message)
        logging.info(f'text file loaded')

def hyperlink_processing(msg, hyperlink_template, name_file, path_to_msg,):
    """ hyperlink processing function """
    index_linc = 1
    list_msg_linc = msg.entities
    if list_msg_linc is not None:
        for item_msg_linc in list_msg_linc:
            if hasattr(item_msg_linc, 'url'):
                msg_linc_url = item_msg_linc.url
                if (msg_linc_url is not None) and (hyperlink_template in msg_linc_url):
                    try:
                        headers = {'Connection': 'keep-alive',
                                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                   'Accept-Encoding': 'gzip,deflate,sdch',
                                   'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
                                   'Cache-Control': 'max-age=0',
                                   'Origin': 'http://site.ru',
                                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.0 Safari/537.36'}
                        response = requests.get(msg_linc_url, headers=headers, )
                        #content_encoding = "iso-8859-1"  response.headers['Content-Encoding']

                        time.sleep(0.25)
                        if response.status_code == 200:
                            html_code = response.text
                            сreation_html_and_pdf_file(index_linc=index_linc,
                                                       name_file=name_file,
                                                       path_to_msg=path_to_msg,
                                                       html_code=html_code,
                                                       msg_linc_url=msg_linc_url,
                                                       )
                            index_linc += 1
                        else:
                            logging.info(f'error when receiving page ----', response.status_code, )
                    except requests.exceptions.RequestException:
                        logging.info(f'---------------------- РАЗРЫВ СОЕДИНЕНИЯ -------------------------', )


def сreation_html_and_pdf_file(index_linc, name_file, path_to_msg, html_code, msg_linc_url, ):
    """ function for creating HTML and PDF files """
    filename_msg_linc = 'linc{}--{}.html'.format(index_linc, name_file)
    path_file_linc = path_to_msg + '/' + filename_msg_linc
    with open(path_file_linc, "w", encoding='utf-8') as file_linc:    #content_encoding
        file_linc.write(html_code)
        logging.info(f'------------------------HTML FILE CREATED--------------------')
    filename_msg_pdf = 'pdf{}--{}.pdf'.format(index_linc, name_file)
    path_file_pdf = path_to_msg + '/' + filename_msg_pdf
    try:
        config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe", )
        pdfkit.from_url(msg_linc_url, path_file_pdf, configuration=config, )
        logging.info(f'----------------------PDF FILE CREATED---------------------')
    except BaseException:
        logging.info(f'------------------------PDF NOT CREATED----------------------')


def progress_callback(current, total):
    """ displaying media file download progress """
    print('Downloaded progress', current, 'out of', total, 'bytes: {:.2%}'.format(current / total))

def pars_header_linc(html_code, ):
    """ function returning a string from the header tag in HTML code """
    soup = BeautifulSoup(html_code, 'html.parser')  #'lxml'    -----------------------
    if soup.find('header', ) is not None:
        header_object = soup.find('header', )
        header_linc = header_object.find('h1').text
        return header_linc

def time_zone_correction(old_time):
    """ time zone correction function """
    split = old_time.split('_')
    a = split[0]
    b = str(int(a) + 3)
    if int(b) >= 24:
        b = '0' + str(int(b) - 24)

    if len(b) == 1:
        b = '0' + b
        new_time = old_time.replace(a, b)
        return new_time
    else:
        new_time = old_time.replace(a, b)
        return new_time

async def pars_main():
    """ a function that determines the data collection method set in the settings """
    print('pars_main')
    if settings.parser['only_unread']:
        await ParseOnlyUnread()
    else:
        await ParseAll()

def start_script():
    """ function that initializes the script launch """
    print('start_script')
    with client:
        client.loop.run_until_complete(pars_main())

if __name__ == '__main__':
    start_script()

