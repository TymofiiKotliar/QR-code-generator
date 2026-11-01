import os
import requests
from flask import Flask, request, abort
import segno
import io
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from zoneinfo import ZoneInfo

PARAMS = {'error': 'Q', 'mask': 2, 'mode': 'numeric'}
SCALE, BORDER = 10, 4

TOKEN = os.environ["BOT_TOKEN"]
SECRET = os.environ["WEBHOOK_SECRET"]
ALLOWED = {int(x) for x in os.environ["ALLOWED_IDS"].split(",")}
API = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

@app.post("/webhook")
def webhook():
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != SECRET:
        abort(403)

    msg = (request.get_json(silent=True) or {}).get("message") or {}
    sender = msg.get("from", {}).get("id")
    text = msg.get("text", "")

    if sender in ALLOWED and text.startswith("/qr"):
        requests.post(
            f"{API}/sendPhoto",
            data={"chat_id": msg["chat"]["id"]},
            files={"photo": ("qr.png", generate_qr(), "image/png")},
            timeout=10,
        )
    return "ok"

def generate_qr(error="Q", version=1, mode="numeric", mask=2, boost_error=False) -> io.BytesIO:
    bytes_img = io.BytesIO()
    payload = datetime.now(ZoneInfo("Europe/Bratislava")).strftime("%Y%m%d")
    segno.make_qr(payload, error, version, mode, mask, boost_error=False).save(bytes_img, scale=SCALE, border=BORDER, kind='png')
    
    bytes_img.seek(0)
    img = Image.open(bytes_img)
    d = ImageDraw.Draw(img)
    
    
    x0 = y0 = (BORDER + 8) * SCALE
    x1 = y1 = x0 + 5 * SCALE
    d.rounded_rectangle([x0, y0, x1 - 1, y1 - 1], radius=4, fill="white")

    font = ImageFont.load_default(size=int(2 * SCALE))
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), "WC", fill="black", font=font, anchor="mm", stroke_width=1, stroke_fill="black")
    
    output = io.BytesIO()
    img.save(output, "PNG")
    output.seek(0)
    return output