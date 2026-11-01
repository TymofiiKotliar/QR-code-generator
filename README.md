# QR-code-generator

A personal Telegram bot that answers `/qr` with a QR code for today's date. I built it to
learn how QR codes work by reproducing one by hand, then wrapped the generator in a bot so I
can use it from my phone.

## What I learned about QR codes

**Structure of a version 1 code (21x21 = 441 modules)**
- 233 modules are *function* modules: three 7x7 finder patterns with separators (192), timing
  patterns (10), one always-dark module (1), and format information (30).
- The remaining 208 modules (26 bytes) hold the payload and error correction.
- Version 1 has no alignment pattern (that starts at version 2).

**Format information**
- 15 bits stored twice: 2 bits error correction (EC) level, 3 bits mask number, 10 BCH check bits.
- The whole value is XORed with `0x5412` before it is written, so an all-light area never occurs.
- Reading these bits from a code tells you its EC level and mask.

**The grid is not the message in binary**
- Dark = 1, light = 0, but only after undoing the mask. One of 8 XOR patterns is applied to the
  data area, chosen by a penalty score so the code stays easy to scan.
- Data is encoded in a *mode*. Digits use numeric mode: 3 digits in 10 bits. `20260929`
  fits easily in version 1, even at the highest EC level.
- Reed-Solomon bytes are added after the data. For version 1, the data/EC byte split is
  19/7 (L), 16/10 (M), 13/13 (Q), 9/17 (H).

**Error correction and the center label**
- Error correction works on bytes, not modules. A 5x5 patch drawn over the center damages a few
  codewords, and the code still scans because they are rebuilt.
- The label must avoid finders, timing patterns and format information, which are not protected
  by Reed-Solomon.

**Identifying the generator tool**
- It can't be done from the grid alone. Given the same payload, mode, EC level and mask, any
  conforming library produces the same modules. What differs between tools is the defaults
  (EC level, mask choice), border width, styling and rendering.
- Reproducing a code means pinning all of those: EC level, mode, version and mask.

## The project

```
You: /qr -> Telegram -> webhook (Flask) -> generate QR -> sendPhoto -> You
```

- **Generator:** `segno` builds a version 1, numeric-mode QR code with fixed EC level (Q) and
  mask (2). The payload is today's date, `YYYYMMDD`, in Europe/Bratislava time.
- **Label:** `Pillow` draws a rounded 5x5-module patch and a bold "WC" label in the center.
- **Bot:** a Flask webhook receives Telegram updates. A secret header and a user ID allow-list
  keep it private. The image is created in memory and sent as a photo.
- **Hosting:** PythonAnywhere free tier. Webhooks fit it, because a free web app only runs when
  a request arrives, while polling would need an always-on process.

## Configuration

Secrets are read from environment variables and never committed: `BOT_TOKEN`, `WEBHOOK_SECRET`,
`ALLOWED_IDS`.

## Stack

Python, Flask, segno, Pillow, requests, Telegram Bot API.