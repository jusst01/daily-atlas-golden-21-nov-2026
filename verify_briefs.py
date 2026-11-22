
import os
from PIL import ImageFont

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
def _f(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

F = {
    "brief": _f("DejaVuSans.ttf", 10),
    "brief_b": _f("DejaVuSans-Bold.ttf", 10),
}

# Dummy draw object for text_w
class DummyDraw:
    def textbbox(self, xy, text, font, *args, **kwargs):
        return font.getbbox(text)

draw = DummyDraw()

def text_w(s, font):
    b = draw.textbbox((0, 0), s, font=font)
    return b[2] - b[0]

BRIEFS = [
    (16, "KRYVYI RIH", "Dozens hit", "EUROPE · REPORTED", (33.4, 47.9)),
    (17, "BRUSSELS", "Gen Z protest", "EUROPE · REPORTED", (4.6, 51.4)),
    (18, "LA", "Arson verdict", "AMERICAS · CONFIRMED", (-118.2, 34.1)),
    (19, "RIEMANN", "AI proof claim", "AMERICAS · CLAIM", (-122.4, 37.8)),
    (20, "TALLINN", "Border closed", "EUROPE · CONFIRMED", (24.7, 59.4)),
    (21, "PARIS", "Police laws pass", "EUROPE · OFFICIAL", (2.35, 48.9)),
    (22, "PARIS", "De Villepin run", "EUROPE · REPORTED", (2.6, 48.4)),
    (23, "SEOUL", "111 cheated", "ASIA · CONFIRMED", (127.0, 37.6)),
    (24, "PHILIPPINES", "Jet landed", "ASIA · REPORTED", (121.0, 14.6)),
    (25, "INDIA", "Alcohol kills", "ASIA · CONFIRMED", (78.0, 21.0)),
    (26, "NIGERIA", "Boat capsized", "AFRICA · REPORTED", (8.0, 10.0)),
    (27, "AFGHANISTAN", "Shell kills 4", "ASIA · REPORTED", (67.0, 34.5)),
    (28, "HAITI", "3 soldiers dead", "AMERICAS · REPORTED", (-72.3, 18.5)),
    (29, "SEATTLE", "2 arrested", "AMERICAS · REPORTED", (-122.3, 47.6)),
    (30, "BRUSSELS", "EU-Indo pact", "ASIA · OFFICIAL", (4.9, 50.5)),
    (31, "DC", "Trump eyes AI tax", "AMERICAS · CONFIRMED", (-77.4, 38.5)),
    (32, "CRYPTO", "BTC dips $55k", "GLOBAL · REPORTED", None),
    (33, "SIMALUNGUN", "Train kills driver", "ASIA · CONFIRMED", (99.0, 2.9)),
]

def line_h(font):
    a, d = font.getmetrics()
    return a + d
print(f"Line height: {line_h(F['brief'])}")

for n, place, text, tag, pin in BRIEFS:
    # Width estimate
    w = text_w(f"{n} {place} {text} {tag}", F["brief"])
    print(f"Brief {n}: {w}px {'OK' if w <= 264 else 'TOO LONG'}")
