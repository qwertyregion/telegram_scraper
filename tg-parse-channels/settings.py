# Settings file.
tg_sec = {
    'api_id': ,
    'api_hash': '',
}

parser = {
    # If "True", the script will download ONLY photos from channels
    'only_photo': False,
    # If "True", the script will by download ONLY UNREAD messages from channels
    'only_unread': False
}

download_root = r'C:\Users\QWERTY\Desktop\telegram_scraper\download'

# Set list of channels for unread only parse method. See parser['only_unread'] mast be "True"
channels_unread_only = [
    -1001653475378,
]

# Set list of channels for parse not only unread method. See parser['only_unread'] mast be "False"
channels_all = [
    -1001653475378,

]
