import segno
import datetime
import io
from PIL import Image, ImageDraw, ImageFont

PARAMS = {'error': 'Q', 'mask': 2, 'mode': 'numeric'}
OUT = io.BytesIO()
SCALE, BORDER = 10, 4

def get_payload():
    payload = datetime.datetime.now()
    return f"{payload.year}{payload.month}{payload.day}"

def generate_and_save_qr(payload, error="Q", version=1, mode="numeric", mask=2, save=False, boost_error=False):
    segno.make_qr(payload, error, version, mode, mask, boost_error=False).save(OUT, scale=SCALE, border=BORDER, kind='png')
    
    OUT.seek(0)
    img = Image.open(OUT)
    d = ImageDraw.Draw(img)
    
    
    x0 = y0 = (BORDER + 8) * SCALE
    x1 = y1 = x0 + 5 * SCALE
    d.rounded_rectangle([x0, y0, x1 - 1, y1 - 1], radius=4, fill="white")

    font = ImageFont.load_default(size=int(2 * SCALE))
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), "WC", fill="black", font=font, anchor="mm", stroke_width=1, stroke_fill="black")
    
    img.save("QR_out/replica-qr.png")

generate_and_save_qr(payload=get_payload(), save=True)