# InStockNotifier

Simple python script to alert when Ryzen 5900x is in stock.
Webpage list in sites.json can be modified for use with any product (currently tested and functional for Amazon and Newegg products).

Use at your own risk. Some websites may IP ban you if they believe you are programmatically accessing their site.

## Optional Components
- Discord Notifications via Webhooks: [Discord Webhook guide here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)
- You can open `sites.json` in a text editor and modify the list of pages that get scanned.

## How to Run

By default, a browser window will open when an item is found to be in stock. If you wish to also receive discord notifications add your discord webhook to the .env file.

1. Clone or download the repository and navigate to the folder from the command prompt (make sure you have Python 3 installed).
2. From a conda environment with the necessary dependencies found in notifier.py installed, run the following:
```
python notifier.py
```

## Testing if Notifications Work

```
python notifier.py test
```
