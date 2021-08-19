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
SLEEP_SCEONDS = 5


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
        else:
            send_msg(
                TG_USER_ID, f"[ERROR] ask {name} price got ({r.status_code}) {r.text}"
            )
    except Exception as e:
        send_msg(TG_USER_ID, f"[ERROR] ask {name} price got {e}")
        return -1


def send_msg(chat_id: str, text: str):
    bot = Bot(token=TG_BOT_TOKEN)
    bot.send_message(chat_id=chat_id, text=text)


def main():
    # send_msg(TG_USER_ID, f"FTX_KEY:{FTX_KEY}")
    # send_msg(TG_USER_ID, f"FTX_SECRET:{FTX_SECRET}")
    # send_msg(TG_USER_ID, f"TG_BOT_TOKEN:{TG_BOT_TOKEN}")
    # send_msg(TG_USER_ID, f"TG_GROUP_ID:{TG_GROUP_ID}")
    # send_msg(TG_USER_ID, f"TG_USER_ID:{TG_USER_ID}")
    # send_msg(TG_USER_ID, f"TG_USER_NAME:{TG_USER_NAME}")
    # send_msg(TG_USER_ID, f"LOW_RATE:{LOW_RATE}")
    # send_msg(TG_USER_ID, f"HIGH_RATE:{HIGH_RATE}")
    loop_range = int((60 * 60) / SLEEP_SCEONDS)  # 1 hour
    try:
        for _ in range(loop_range):
            cake, bnb, cakebnb = get_cakebnb()
            if cake != -1 and bnb != -1:
                if cakebnb >= HIGH_RATE:
                    send_msg(
                        TG_GROUP_ID,
                        f"CAKE/BNB 價格比到達 {cakebnb} ({cake}/{bnb})\r\n建議平倉\r\n{TG_USER_NAME}",
                    )
                    send_msg(
                        TG_USER_ID, f"CAKE/BNB 價格比到達 {cakebnb} ({cake}/{bnb})\r\n建議平倉"
                    )
                elif cakebnb <= LOW_RATE:
                    send_msg(
                        TG_GROUP_ID,
                        f"CAKE/BNB 價格比到達 {cakebnb} ({cake}/{bnb})\r\n建議加倉\r\n{TG_USER_NAME}",
                    )
                    send_msg(
                        TG_USER_ID, f"CAKE/BNB 價格比到達 {cakebnb} ({cake}/{bnb})\r\n建議加倉"
                    )
            time.sleep(5)
    except:
        pass


if __name__ == "__main__":
    main()
