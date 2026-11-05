"""Original neutral motion example. No creator style, portrait, voice or third-party assets."""
import math
from PIL import Image, ImageDraw, ImageFont


def render_frame(t, width, height, context):
    style = context['style']
    colors = style.get('colors', ['#241C35', '#FFB454', '#B8E0D2'])
    im = Image.new('RGB', (width, height), colors[0]); d = ImageDraw.Draw(im)
    scale = width / 720
    floor = height * .68
    phase = t % 5
    # Quadratic fall; impact at1.2s, damped bounce afterwards, same event clock as audio.
    if phase < 1.2:
        y = height * .28 + (floor - height * .28) * (phase / 1.2) ** 2
    else:
        dt = phase - 1.2; y = floor - abs(math.sin(dt * 8)) * math.exp(-dt * 1.7) * height * .12
    squash = max(0, 1 - abs(phase - 1.2) / .16)
    rx, ry = 58 * scale * (1 + .22 * squash), 58 * scale * (1 - .18 * squash)
    x = width * .5 + math.sin(t * .7) * width * .12
    d.line((width * .16, floor + 62 * scale, width * .84, floor + 62 * scale), fill=colors[2], width=max(2, round(3 * scale)))
    d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=colors[1])
    for k in range(5):
        px = width * (.2 + .15 * k); py = height * .18 + math.sin(t * 1.2 + k) * 8 * scale
        d.rectangle((px - 4 * scale, py - 4 * scale, px + 4 * scale, py + 4 * scale), fill=colors[2])
    return im
