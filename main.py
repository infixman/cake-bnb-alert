import hmac
import os
import time

import requests
from telegram import Bot

FTX_KEY = os.getenv("FTX_KEY")
FTX_SECRET = os.getenv("FTX_SECRET")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_DEBUG_GROUP_ID = os.getenv("TG_DEBUG_GROUP_ID")
TG_GROUP_ID = os.getenv("TG_GROUP_ID")
TG_USER_ID = os.getenv("TG_USER_ID")
TG_USER_NAME = os.getenv("TG_USER_NAME")
EMERGENCY_RATE = float(os.getenv("EMERGENCY_RATE"))
LOW_RATE = float(os.getenv("LOW_RATE"))
HIGH_RATE = float(os.getenv("HIGH_RATE"))
SLEEP_SCEONDS = 5
SEND_ENV = False


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
            send_msg(
                TG_DEBUG_GROUP_ID,
                f"[ERROR] ask {name} price got ({r.status_code}) {r.text}",
            )
    except Exception as e:
        send_msg(TG_USER_ID, f"[ERROR] ask {name} price got {e}")
        send_msg(TG_DEBUG_GROUP_ID, f"[ERROR] ask {name} price got {e}")
        return -1


def send_msg(chat_id: str, text: str):
    bot = Bot(token=TG_BOT_TOKEN)
    bot.send_message(chat_id=chat_id, text=text)


def main():
    if SEND_ENV:
        send_msg(TG_USER_ID, f"FTX_KEY:{FTX_KEY}")
        send_msg(TG_USER_ID, f"FTX_SECRET:{FTX_SECRET}")
        send_msg(TG_USER_ID, f"TG_BOT_TOKEN:{TG_BOT_TOKEN}")
        send_msg(TG_USER_ID, f"TG_DEBUG_GROUP_ID:{TG_DEBUG_GROUP_ID}")
        send_msg(TG_USER_ID, f"TG_GROUP_ID:{TG_GROUP_ID}")
        send_msg(TG_USER_ID, f"TG_USER_ID:{TG_USER_ID}")
        send_msg(TG_USER_ID, f"TG_USER_NAME:{TG_USER_NAME}")
        send_msg(TG_USER_ID, f"EMERGENCY_RATE:{EMERGENCY_RATE}")
        send_msg(TG_USER_ID, f"LOW_RATE:{LOW_RATE}")
        send_msg(TG_USER_ID, f"HIGH_RATE:{HIGH_RATE}")

    try:
        # loop_range = int((60 * 60) / SLEEP_SCEONDS)  # 1 hour
        # for _ in range(loop_range):
        while True:
            cake, bnb, cakebnb = get_cakebnb()
            if cake != -1 and bnb != -1:
                msg = f"CAKE/BNB 價格比 {cakebnb} ({cake}/{bnb})"
                if cakebnb <= EMERGENCY_RATE:
                    msg = f"{msg}\r\n建議平倉止損"
                elif cakebnb <= LOW_RATE:
                    msg = f"{msg}\r\n建議加倉"
                elif cakebnb >= HIGH_RATE:
                    msg = f"{msg}\r\n建議平倉獲利"

                if cakebnb <= LOW_RATE or cakebnb >= HIGH_RATE:
                    send_msg(
                        TG_GROUP_ID,
                        f"{msg}\r\n{TG_USER_NAME}",
                    )
                    send_msg(TG_USER_ID, msg)
                send_msg(TG_DEBUG_GROUP_ID, msg)
            time.sleep(5)
    except Exception as e:
        send_msg(TG_USER_ID, f"[ERROR] main, {e}")


if __name__ == "__main__":
    main()
