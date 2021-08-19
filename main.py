import hmac
import os
import time

import requests
from telegram import Bot

FTX_KEY = os.getenv("FTX_KEY")
FTX_SECRET = os.getenv("FTX_SECRET")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_GROUP_ID = os.getenv("TG_GROUP_ID")
TG_USER_ID = os.getenv("TG_USER_ID")
TG_USER_NAME = os.getenv("TG_USER_NAME")
LOW_RATE = float(os.getenv("LOW_RATE"))
HIGH_RATE = float(os.getenv("HIGH_RATE"))


def get_cakebnb():
    bnb = round(get_ftx_price("BNB-PERP"), 3)
    cake = round(get_ftx_price("CAKE-PERP"), 3)
    cakebnb = round(cake / bnb, 4)
    return (cake, bnb, cakebnb)


def get_ftx_price(name: str):
    try:
        url = f"https://ftx.com/api/markets/{name}"
        ts = int(time.time() * 1000)
        signature_payload = f"{ts}GET{url}".encode()
        signature = hmac.new(
            FTX_SECRET.encode(), signature_payload, "sha256"
        ).hexdigest()
        headers = {"FTX-KEY": FTX_KEY, "FTX-SIGN": signature, "FTX-TS": str(ts)}
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            robj = r.json()
            if robj["success"]:
                return robj["result"]["price"]
            else:
                return -1
    except:
        return -1


def main():
    bot = Bot(token=TG_BOT_TOKEN)
    try:
        cake, bnb, cakebnb = get_cakebnb()
        if cakebnb >= HIGH_RATE:
            bot.send_message(
                text=f"CAKE/BNB 價格比到達 {cakebnb} ({cake}/{bnb})\r\n建議平倉\r\n{TG_USER_NAME}",
                chat_id=TG_GROUP_ID,
            )
            bot.send_message(
                text=f"CAKE/BNB 價格比到達 {cakebnb} ({cake}/{bnb})\r\n建議平倉",
                chat_id=TG_USER_ID,
            )
        elif cakebnb <= LOW_RATE:
            bot.send_message(
                text=f"CAKE/BNB 價格比到達 {cakebnb} ({cake}/{bnb})\r\n建議加倉\r\n{TG_USER_NAME}",
                chat_id=TG_GROUP_ID,
            )
            bot.send_message(
                text=f"CAKE/BNB 價格比到達 {cakebnb} ({cake}/{bnb})\r\n建議加倉",
                chat_id=TG_USER_ID,
            )
    except:
        pass


if __name__ == "__main__":
    main()
