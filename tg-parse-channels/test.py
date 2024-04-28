

import re

def find_links(text):
    pattern = r'<a.*?href="(https?://t\.me/.*?)".*?>.*?</a>'
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    matches = re.findall(pattern, text)
    return matches









if __name__ == '__main__':

