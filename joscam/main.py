import cv2
import pyvirtualcam

from joscam.camera import Camera
from joscam.pipeline import EffectPipeline
from joscam.settings import CameraSettings


WIDTH = 1280
HEIGHT = 720
FPS = 30


def main():
    camera = Camera()

    settings = CameraSettings(
        brightness=5,
        contrast=1.08,
        saturation=0.95,
        gamma=1.03,
    )

    pipeline = EffectPipeline(settings)

    try:
        with pyvirtualcam.Camera(
            width=WIDTH,
            height=HEIGHT,
            fps=FPS,
            fmt=pyvirtualcam.PixelFormat.BGR,
        ) as virtual_camera:
            print(
                f"Virtual camera: {virtual_camera.device}"
            )

            while True:
                frame = camera.read()

                frame = cv2.resize(
                    frame,
                    (WIDTH, HEIGHT),
                )

                frame = pipeline.process(frame)

                virtual_camera.send(frame)
                virtual_camera.sleep_until_next_frame()

    finally:
        camera.close()


if __name__ == "__main__":
    main()
