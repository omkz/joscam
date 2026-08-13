import cv2
import pyvirtualcam

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from joscam.camera import Camera
from joscam.pipeline import EffectPipeline
from joscam.settings import CameraSettings


WIDTH = 1280
HEIGHT = 720
FPS = 30


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Joscam")
        self.resize(1000, 800)

        self.camera = Camera()

        self.settings = CameraSettings()
        self.pipeline = EffectPipeline(self.settings)

        self.virtual_camera = pyvirtualcam.Camera(
            width=WIDTH,
            height=HEIGHT,
            fps=FPS,
            fmt=pyvirtualcam.PixelFormat.BGR,
        )

        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(640, 360)

        layout = QVBoxLayout()

        layout.addWidget(self.preview)

        layout.addWidget(
            self.create_slider(
                "Brightness",
                -100,
                100,
                0,
                lambda value: setattr(
                    self.settings,
                    "brightness",
                    float(value),
                ),
            )
        )

        layout.addWidget(
            self.create_slider(
                "Contrast",
                50,
                200,
                100,
                lambda value: setattr(
                    self.settings,
                    "contrast",
                    value / 100,
                ),
            )
        )

        layout.addWidget(
            self.create_slider(
                "Saturation",
                0,
                200,
                100,
                lambda value: setattr(
                    self.settings,
                    "saturation",
                    value / 100,
                ),
            )
        )

        layout.addWidget(
            self.create_slider(
                "Gamma",
                50,
                150,
                100,
                lambda value: setattr(
                    self.settings,
                    "gamma",
                    value / 100,
                ),
            )
        )

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // FPS)

    def create_slider(
        self,
        name,
        minimum,
        maximum,
        default,
        callback,
    ):
        container = QWidget()
        layout = QVBoxLayout(container)

        label = QLabel()

        slider = QSlider(Qt.Orientation.Horizontal)

        slider.setMinimum(minimum)
        slider.setMaximum(maximum)
        slider.setValue(default)

        def value_changed(value):
            callback(value)

            if name == "Brightness":
                display_value = str(value)
            else:
                display_value = f"{value / 100:.2f}"

            label.setText(
                f"{name}: {display_value}"
            )

        slider.valueChanged.connect(value_changed)

        value_changed(default)

        layout.addWidget(label)
        layout.addWidget(slider)

        return container

    def update_frame(self):
        frame = self.camera.read()

        frame = cv2.resize(
            frame,
            (WIDTH, HEIGHT),
        )

        frame = self.pipeline.process(frame)

        self.virtual_camera.send(frame)

        self.show_preview(frame)

    def show_preview(self, frame):
        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        height, width, channels = rgb.shape

        image = QImage(
            rgb.data,
            width,
            height,
            channels * width,
            QImage.Format.Format_RGB888,
        )

        pixmap = QPixmap.fromImage(image)

        pixmap = pixmap.scaled(
            self.preview.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.preview.setPixmap(pixmap)

    def closeEvent(self, event):
        self.timer.stop()

        self.camera.close()
        self.virtual_camera.close()

        event.accept()
