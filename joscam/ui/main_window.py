import cv2
import pyvirtualcam

from dataclasses import asdict

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)

from joscam.camera import Camera
from joscam.pipeline import EffectPipeline
from joscam.presets import PRESETS
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

        self.sliders = {}
        self.slider_scales = {}

        self.virtual_camera = pyvirtualcam.Camera(
            width=WIDTH,
            height=HEIGHT,
            fps=FPS,
            fmt=pyvirtualcam.PixelFormat.BGR,
        )

        self.preview = QLabel()
        self.preview.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.preview.setMinimumSize(640, 360)

        layout = QVBoxLayout()

        layout.addWidget(self.preview, stretch=1)

        # Presets
        layout.addLayout(
            self.create_preset_controls()
        )

        # Tabs
        layout.addWidget(
            self.create_control_tabs()
        )

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        # Default state
        self.apply_preset("Neutral")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // FPS)

    def create_preset_controls(self):
        layout = QHBoxLayout()

        label = QLabel("Preset")

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(
            PRESETS.keys()
        )

        self.preset_combo.currentTextChanged.connect(
            self.apply_preset
        )

        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(
            self.reset_settings
        )

        layout.addWidget(label)
        layout.addWidget(self.preset_combo)
        layout.addWidget(reset_button)

        return layout

    def create_control_tabs(self):
        tabs = QTabWidget()

        tabs.addTab(
            self.create_basic_tab(), "Basic"
        )
        tabs.addTab(
            self.create_light_tab(), "Light"
        )
        tabs.addTab(
            self.create_color_tab(), "Color"
        )
        tabs.addTab(
            self.create_detail_tab(), "Detail"
        )
        tabs.addTab(
            self.create_film_tab(), "Film"
        )

        return tabs

    def create_basic_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(
            self.create_slider(
                key="brightness",
                label="Brightness",
                minimum=-100,
                maximum=100,
                scale=1,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="contrast",
                label="Contrast",
                minimum=50,
                maximum=200,
                scale=100,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="gamma",
                label="Gamma",
                minimum=50,
                maximum=150,
                scale=100,
            )
        )

        return container

    def create_light_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(
            self.create_slider(
                key="exposure",
                label="Exposure",
                minimum=-100,
                maximum=100,
                scale=100,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="highlights",
                label="Highlights",
                minimum=-100,
                maximum=100,
                scale=100,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="shadows",
                label="Shadows",
                minimum=-100,
                maximum=100,
                scale=100,
            )
        )

        return container

    def create_color_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(
            self.create_slider(
                key="saturation",
                label="Saturation",
                minimum=0,
                maximum=200,
                scale=100,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="temperature",
                label="Temperature",
                minimum=-30,
                maximum=30,
                scale=100,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="tint",
                label="Tint",
                minimum=-30,
                maximum=30,
                scale=100,
            )
        )

        return container

    def create_detail_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(
            self.create_slider(
                key="skin_smoothing",
                label="Skin Smoothing",
                minimum=0,
                maximum=100,
                scale=100,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="blur",
                label="Blur",
                minimum=0,
                maximum=100,
                scale=100,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="clarity",
                label="Clarity",
                minimum=-50,
                maximum=50,
                scale=100,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="sharpness",
                label="Sharpness",
                minimum=0,
                maximum=50,
                scale=100,
            )
        )

        return container

    def create_film_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(
            self.create_slider(
                key="fade",
                label="Fade",
                minimum=0,
                maximum=50,
                scale=100,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="vignette",
                label="Vignette",
                minimum=0,
                maximum=70,
                scale=100,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="grain",
                label="Film Grain",
                minimum=0,
                maximum=10,
                scale=100,
            )
        )

        return container

    def create_slider(
        self,
        key,
        label,
        minimum,
        maximum,
        scale,
    ):
        container = QWidget()
        layout = QVBoxLayout(container)

        value_label = QLabel()

        slider = QSlider(
            Qt.Orientation.Horizontal
        )

        slider.setMinimum(minimum)
        slider.setMaximum(maximum)

        self.sliders[key] = slider
        self.slider_scales[key] = scale

        def value_changed(raw_value):
            value = raw_value / scale

            setattr(
                self.settings,
                key,
                value,
            )

            if scale == 1:
                display = f"{value:.0f}"
            else:
                display = f"{value:.2f}"

            value_label.setText(
                f"{label}: {display}"
            )

        slider.valueChanged.connect(
            value_changed
        )

        default_value = getattr(
            self.settings,
            key,
        )

        slider.setValue(
            round(default_value * scale)
        )

        value_changed(
            slider.value()
        )

        layout.addWidget(value_label)
        layout.addWidget(slider)

        return container

    def apply_preset(self, name):
        if name not in PRESETS:
            return

        preset = PRESETS[name]

        for key, value in asdict(preset).items():
            setattr(
                self.settings,
                key,
                value,
            )

            slider = self.sliders.get(key)

            if slider is None:
                continue

            scale = self.slider_scales[key]

            slider.setValue(
                round(value * scale)
            )

    def reset_settings(self):
        self.preset_combo.setCurrentText(
            "Neutral"
        )

        # Tetap apply walaupun combo
        # sudah berada di Neutral.
        self.apply_preset(
            "Neutral"
        )

    def update_frame(self):
        frame = self.camera.read()

        frame = cv2.resize(
            frame,
            (WIDTH, HEIGHT),
        )

        frame = self.pipeline.process(
            frame
        )

        self.virtual_camera.send(
            frame
        )

        self.show_preview(
            frame
        )

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

        pixmap = QPixmap.fromImage(
            image
        )

        pixmap = pixmap.scaled(
            self.preview.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.preview.setPixmap(
            pixmap
        )

    def closeEvent(self, event):
        self.timer.stop()

        self.camera.close()
        self.virtual_camera.close()

        event.accept()
