import json
import platform
import random
import webbrowser
from datetime import datetime, time
from os import path, getenv, system
from time import sleep
from urllib.request import urlopen, Request
import sys
import requests
from dotenv import load_dotenv

platform = platform.system()
PLT_WIN = "Windows"
PLT_LIN = "Linux"
PLT_MAC = "Darwin"

# Set up environment variables and constants. Do not modify this unless you know what you are doing!
load_dotenv()
USE_DISCORD_HOOK = False
USE_TELEGRAM = False
DISCORD_WEBHOOK_URL = getenv('DISCORD_WEBHOOK_URL')
TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT = getenv('TELEGRAM_CHAT')
ALERT_DELAY = int(getenv('ALERT_DELAY'))
MIN_DELAY = int(getenv('MIN_DELAY'))
MAX_DELAY = int(getenv('MAX_DELAY'))
OPEN_WEB_BROWSER = getenv('OPEN_WEB_BROWSER') == 'true'

with open('sites.json', 'r') as f:
    sites = json.load(f)

# Discord Setup
if DISCORD_WEBHOOK_URL:
    USE_DISCORD_HOOK = True
    print('Enabled Discord Web Hook.')

# Telegram Setup
if TELEGRAM_TOKEN:
    USE_TELEGRAM = True
    print('Enabled Telegram API.')
    
# Platform specific settings
print("Running on {}".format(platform))
if platform == PLT_WIN:
    from win10toast import ToastNotifier
    toast = ToastNotifier()


def alert(site):
    product = site.get('name')
    print("{} IN STOCK".format(product))
    print(site.get('url'))
    if OPEN_WEB_BROWSER:
        webbrowser.open(site.get('url'), new=1)
    os_notification("{} IN STOCK".format(product), site.get('url'))
    discord_notification(product, site.get('url'))
    telegram_notification(product, site.get('url'))
    sleep(ALERT_DELAY)


def os_notification(title, text):
    if platform == PLT_MAC:
        system("""
                  osascript -e 'display notification "{}" with title "{}"'
                  """.format(text, title))
        system('afplay /System/Library/Sounds/Glass.aiff')
        system('say "{}"'.format(title))
    elif platform == PLT_WIN:
        toast.show_toast(title, text, duration=5)
    elif platform == PLT_LIN:
        # libnotify is installed by default on ubuntu and other distros
        # it can otherwise be easily installed
        import subprocess
        subprocess.Popen(["notify-send", "-i", "face-cool", title, text], shell=False)

def discord_notification(product, url):
    if USE_DISCORD_HOOK:
        data = {
            "content": "{} in stock at {}".format(product, url),
            "username": "In Stock Alert!"
        }
        result = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(data), headers={"Content-Type": "application/json"})
        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))
            
def telegram_notification(product, url):
    if USE_TELEGRAM: 
        TELEGRAM_URL = "https://api.telegram.org/bot{}/sendMessage".format(TELEGRAM_TOKEN)
        data = {
            "text": "{} in stock at {}".format(product, url),
            "chat_id": TELEGRAM_CHAT
        }
        result = requests.post(TELEGRAM_URL, data=json.dumps(data), headers={"Content-Type": "application/json"})
        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))

def urllib_get(url):
    # for regular sites
    # Fake a Firefox client
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(request, timeout=30)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    return html


def is_test():
    try:
        if sys.argv[1] == 'test':
            alert(sites[2])
            print("Test complete, if you received notification, you're good to go.")
            return True
    except:
        return False


def main():
    search_count = 0

    exit() if is_test() else False

    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Starting search {} at {}".format(search_count, current_time))
        search_count += 1
        for site in sites:
            if site.get('enabled'):
                print("\tChecking {}...".format(site.get('name')))

                try:
                    html = urllib_get(site.get('url'))
                    
                except Exception as e:
                    print("\t\tConnection failed...")
                    print("\t\t{}".format(e))
                    continue
                keyword = site.get('keyword')
                alert_on_found = site.get('alert')
                index = html.upper().find(keyword.upper())
                if alert_on_found and index != -1:
                    alert(site)
                elif not alert_on_found and index == -1:
                    alert(site)

                base_sleep = 1
                total_sleep = base_sleep + random.uniform(MIN_DELAY, MAX_DELAY)
                sleep(total_sleep)


if __name__ == '__main__':
    main()
