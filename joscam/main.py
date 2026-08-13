import cv2
import pyvirtualcam

from joscam.camera import Camera
from joscam.effects.basic import (
    brightness,
    contrast,
    gamma,
    saturation,
)


WIDTH = 1280
HEIGHT = 720
FPS = 30


def main():
    camera = Camera()

    try:
        with pyvirtualcam.Camera(
            width=WIDTH,
            height=HEIGHT,
            fps=FPS,
            fmt=pyvirtualcam.PixelFormat.BGR,
        ) as virtual_camera:

            print(f"Virtual camera: {virtual_camera.device}")

            while True:
                frame = camera.read()

                frame = cv2.resize(
                    frame,
                    (WIDTH, HEIGHT),
                )

                frame = brightness(frame, 5)
                frame = contrast(frame, 1.08)
                frame = saturation(frame, 0.95)
                frame = gamma(frame, 1.03)

                virtual_camera.send(frame)
                virtual_camera.sleep_until_next_frame()

    finally:
        camera.close()


if __name__ == "__main__":
    main()
