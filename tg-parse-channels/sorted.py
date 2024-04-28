

import os
import shutil

folder_track = r'C:/Users/QWERTY/Desktop/telegram_scraper'  # папка отслеживания
folder_move = r'C:/Users/QWERTY/Desktop/telegram_scraper/download'  # папка куда будет переноситься

# video_format = ['mp4', 'mpg', 'avi', 'mpeg', ]
# image_format = ['jpg', 'png', 'svg', ]
# text_format = ['txt', ]


def clean_sorted():
    files = os.listdir(folder_track)
    for item in files:
        extension = item.split(".")
        if len(extension) > 1:
            if not extension[0] == '':
                list_item = item.split("--")
                # list_item_time = list_item[3].split(".")
                old_path = os.path.join(folder_track, item, )
                new_path = os.path.join(folder_move, list_item[1], list_item[2], list_item[3], item, )
                shutil.move(old_path, new_path)


if __name__ == '__main__':
    clean_sorted()








        # if len(extension) > 1 and extension[1].lower() in video_format:
        #     old_path = os.path.join(folder_track, item, )
        #     new_path = os.path.join(folder_move, list_item[1], list_item[2], list_item[3], )
        #     shutil.move(old_path, new_path)
        # elif len(extension) > 1 and extension[1].lower() in text_format:
        #     old_path = os.path.join(folder_track, item, )
        #     new_path = os.path.join(folder_move, list_item[1], list_item[2], list_item[3], )
        #     shutil.move(old_path, new_path)




