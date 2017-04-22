from __future__ import print_function

import os
import time

from bs4 import BeautifulSoup
import requests


GAMEFAQS_ENCODING = 'ISO-8859-1'
DAY = 'mercs-day-1'

def find_max_page_num(page_content):
    html_parser = BeautifulSoup(page_content, 'html.parser')

    page_selector = html_parser.find('select', id='pagejump')
    if page_selector is not None:
        last_option_tag = page_selector('option')[-1]
        return int(last_option_tag['value']) + 1
    else:
        return 1

def save_page_to_disk(page_content, topic_name, page_number):
    parser = BeautifulSoup(page_content, "html.parser")

    page_name = 'page%s' % page_number

    # post_iter = parser.find_all.find_all("div", {'class': 'msg_infobox'})

    topic_folder = './{0}'.format(topic_name)
    if not os.path.exists(topic_folder):
        os.makedirs(topic_folder)

    topic_folder += '/'
    file_name = topic_folder + page_name + '.html'
    html_file = open(file_name, 'w', encoding=GAMEFAQS_ENCODING)

    with html_file:
        html_file.write(page_content)

def main():
    BOT_NAME = "mercscrawler"
    # User-Agent data, to identify my crawler to GameFAQs
    agent = 'Mozilla/5.0 (compatible; %s/1.0;)' % BOT_NAME
    headers = {'User-Agent': agent}
    url = 'https://www.gamefaqs.com/boards/8-gamefaqs-contests/75261000'
    response = requests.get(url=url, headers=headers)

    if response.status_code >= 300:
        print("Error! Failed to download initial page!", flush=True)
        print("Page code: %s" % response.status_code, flush=True)

    current_page = response.text

    max_page = find_max_page_num(response.text)
    save_page_to_disk(current_page, DAY, 1)

    for current_page_number in range(1, max_page+2):
        time.sleep(2)
        page_querystring = "?page=" + str(current_page_number)
        current_page_url = url + page_querystring
        current_page = requests.get(current_page_url, headers=headers)

        save_page_to_disk(current_page.text, DAY, current_page_number)


if __name__ == '__main__':
    main()