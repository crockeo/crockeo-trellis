import math
import time
from colorsys import hsv_to_rgb
from typing import Any
from typing import Callable
from typing import Tuple

import busio
from adafruit_neotrellis.neotrellis import NeoTrellis
from board import SCL, SDA

BUTTON_COUNT = 16

FRAME_RATE = 30
SLEEP_TIME = 30 / 1000.0

FloatColor = Tuple[float, float, float]
ByteColor = Tuple[int, int, int]


def float_to_byte_color(float_color: FloatColor) -> ByteColor:
    return (
        int(float_color[0] * 255),
        int(float_color[1] * 255),
        int(float_color[2] * 255),
    )


def sin_time(cadence: float) -> float:
    return (math.sin(time.time() * cadence) + 1.0) / 2.0


def cos_time(cadence: float) -> float:
    return (math.cos(time.time() * cadence) + 1.0) / 2.0


def button_callback(trellis: NeoTrellis, i: int) -> Callable[..., Any]:
    def _button_callback(event):
        if event.edge == NeoTrellis.EDGE_FALLING:
            trellis.pixels[event.number] = (0, 0, 0)
        elif event.edge == NeoTrellis.EDGE_RISING:
            trellis.pixels[event.number] = (255, 0, 127)
    return _button_callback


def button_target_color(i: int) -> ByteColor:
    OUTER_RING = {0, 1, 2, 3, 4, 7, 8, 11, 12, 13, 14, 15}
    INNER_RING = {5, 6, 9, 10}

    if i in OUTER_RING:
        float_color = hsv_to_rgb(sin_time(0.25), 0.8, 0.8)
    if i in INNER_RING:
        float_color = hsv_to_rgb(cos_time(0.25), 0.8, 0.8)

    return float_to_byte_color(float_color)


def main(trellis: NeoTrellis):
    for i in range(BUTTON_COUNT):
        trellis.activate_key(i, NeoTrellis.EDGE_RISING)
        trellis.activate_key(i, NeoTrellis.EDGE_FALLING)
        trellis.callbacks[i] = button_callback(trellis, i)

    while True:
        for i in range(BUTTON_COUNT):
            trellis.pixels[i] = button_target_color(i)

        trellis.sync()
        time.sleep(0.02)


if __name__ == "__main__":
    i2c = busio.I2C(SCL, SDA)
    trellis = NeoTrellis(i2c)
    try:
        main(trellis)
    except KeyboardInterrupt:
        for i in range(BUTTON_COUNT):
            trellis.pixels[i] = (0, 0, 0)
