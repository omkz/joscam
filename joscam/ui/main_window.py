import logging

import cv2
import pyvirtualcam

from dataclasses import asdict

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QColor, QImage, QPixmap
from PySide6.QtWidgets import (
    QColorDialog,
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
from joscam.filters import CATEGORIES
from joscam.frames import SHAPES, STYLE_NAMES
from joscam.pipeline import EffectPipeline
from joscam.presets import PRESETS
from joscam.settings import CameraSettings
from joscam.ui.worker import CameraWorker


logger = logging.getLogger(__name__)


WIDTH = 1280
HEIGHT = 720
FPS = 30


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Joscam")
        self.resize(1000, 800)

        self.camera = Camera(
            width=WIDTH,
            height=HEIGHT,
            fps=FPS,
        )

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

        # Capture, processing, and virtual camera output all run on a
        # worker thread so the GUI thread stays responsive.
        self.worker_thread = QThread(self)
        self.worker = CameraWorker(
            self.camera,
            self.pipeline,
            self.virtual_camera,
            WIDTH,
            HEIGHT,
        )
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.preview_ready.connect(self.on_preview_ready)
        self.worker.error.connect(self.on_worker_error)

        self.worker_thread.start()

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
            self.create_filter_tab(), "Filter"
        )
        tabs.addTab(
            self.create_film_tab(), "Film"
        )
        tabs.addTab(
            self.create_frame_tab(), "Frame"
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

    def create_filter_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        category_row = QHBoxLayout()
        category_row.addWidget(QLabel("Category"))

        self.category_combo = QComboBox()
        self.category_combo.addItems(CATEGORIES.keys())
        self.category_combo.currentTextChanged.connect(
            self.populate_filters
        )
        category_row.addWidget(self.category_combo)

        layout.addLayout(category_row)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter"))

        self.filter_combo = QComboBox()
        self.filter_combo.currentTextChanged.connect(
            self.select_filter
        )
        filter_row.addWidget(self.filter_combo)

        layout.addLayout(filter_row)

        self.populate_filters(
            self.category_combo.currentText()
        )

        layout.addWidget(
            self.create_slider(
                key="filter_intensity",
                label="Intensity",
                minimum=0,
                maximum=100,
                scale=100,
                on_change=self.set_filter_intensity,
                initial=self.pipeline.filter_intensity,
            )
        )

        return container

    def populate_filters(self, category):
        self.filter_combo.blockSignals(True)

        self.filter_combo.clear()
        self.filter_combo.addItems(
            ["None"] + CATEGORIES[category]
        )
        self.filter_combo.setCurrentText("None")

        self.filter_combo.blockSignals(False)

        self.select_filter(
            self.filter_combo.currentText()
        )

    def select_filter(self, name):
        self.pipeline.filter_name = name

    def set_filter_intensity(self, value):
        self.pipeline.filter_intensity = value

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

    def create_frame_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        frame_settings = self.pipeline.frame_settings

        style_row = QHBoxLayout()
        style_row.addWidget(QLabel("Frame Style"))

        self.frame_style_combo = QComboBox()
        self.frame_style_combo.addItems(STYLE_NAMES)
        self.frame_style_combo.setCurrentText(frame_settings.style)
        self.frame_style_combo.currentTextChanged.connect(
            self.set_frame_style
        )
        style_row.addWidget(self.frame_style_combo)

        layout.addLayout(style_row)

        shape_row = QHBoxLayout()
        shape_row.addWidget(QLabel("Shape"))

        self.frame_shape_combo = QComboBox()
        self.frame_shape_combo.addItems(SHAPES)
        self.frame_shape_combo.setCurrentText(frame_settings.shape)
        self.frame_shape_combo.currentTextChanged.connect(
            self.set_frame_shape
        )
        shape_row.addWidget(self.frame_shape_combo)

        layout.addLayout(shape_row)

        layout.addWidget(
            self.create_slider(
                key="frame_size",
                label="Size",
                minimum=10,
                maximum=100,
                scale=100,
                on_change=self.set_frame_size,
                initial=frame_settings.size,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="frame_feather",
                label="Feather",
                minimum=0,
                maximum=100,
                scale=1,
                on_change=self.set_frame_feather,
                initial=frame_settings.feather,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="frame_border_width",
                label="Border Width",
                minimum=0,
                maximum=40,
                scale=1,
                on_change=self.set_frame_border_width,
                initial=frame_settings.border_width,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="frame_position_x",
                label="Position X",
                minimum=-50,
                maximum=50,
                scale=100,
                on_change=self.set_frame_position_x,
                initial=frame_settings.position_x,
            )
        )

        layout.addWidget(
            self.create_slider(
                key="frame_position_y",
                label="Position Y",
                minimum=-50,
                maximum=50,
                scale=100,
                on_change=self.set_frame_position_y,
                initial=frame_settings.position_y,
            )
        )

        custom_row = QHBoxLayout()

        self.outside_color_button = QPushButton("Outside Color")
        self.outside_color_button.clicked.connect(
            self.pick_outside_color
        )
        self._set_color_button_swatch(
            self.outside_color_button,
            frame_settings.outside_color,
        )
        custom_row.addWidget(self.outside_color_button)

        self.border_color_button = QPushButton("Border Color")
        self.border_color_button.clicked.connect(
            self.pick_border_color
        )
        self._set_color_button_swatch(
            self.border_color_button,
            frame_settings.border_color,
        )
        custom_row.addWidget(self.border_color_button)

        layout.addLayout(custom_row)

        return container

    def set_frame_style(self, style):
        self.pipeline.frame_settings.style = style

    def set_frame_shape(self, shape):
        self.pipeline.frame_settings.shape = shape

    def set_frame_size(self, value):
        self.pipeline.frame_settings.size = value

    def set_frame_feather(self, value):
        self.pipeline.frame_settings.feather = value

    def set_frame_border_width(self, value):
        self.pipeline.frame_settings.border_width = value

    def set_frame_position_x(self, value):
        self.pipeline.frame_settings.position_x = value

    def set_frame_position_y(self, value):
        self.pipeline.frame_settings.position_y = value

    def pick_outside_color(self):
        frame_settings = self.pipeline.frame_settings

        color = QColorDialog.getColor(
            self._bgr_to_qcolor(frame_settings.outside_color),
            self,
            "Outside Color",
        )

        if not color.isValid():
            return

        frame_settings.outside_color = self._qcolor_to_bgr(color)
        self._set_color_button_swatch(
            self.outside_color_button,
            frame_settings.outside_color,
        )

    def pick_border_color(self):
        frame_settings = self.pipeline.frame_settings

        color = QColorDialog.getColor(
            self._bgr_to_qcolor(frame_settings.border_color),
            self,
            "Border Color",
        )

        if not color.isValid():
            return

        frame_settings.border_color = self._qcolor_to_bgr(color)
        self._set_color_button_swatch(
            self.border_color_button,
            frame_settings.border_color,
        )

    @staticmethod
    def _bgr_to_qcolor(bgr):
        b, g, r = bgr
        return QColor(r, g, b)

    @staticmethod
    def _qcolor_to_bgr(color):
        return (color.blue(), color.green(), color.red())

    @staticmethod
    def _set_color_button_swatch(button, bgr):
        b, g, r = bgr
        button.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b});"
        )

    def create_slider(
        self,
        key,
        label,
        minimum,
        maximum,
        scale,
        on_change=None,
        initial=None,
    ):
        container = QWidget()
        layout = QVBoxLayout(container)

        value_label = QLabel()

        slider = QSlider(
            Qt.Orientation.Horizontal
        )

        slider.setMinimum(minimum)
        slider.setMaximum(maximum)

        if on_change is None:
            self.sliders[key] = slider
            self.slider_scales[key] = scale

        def value_changed(raw_value):
            value = raw_value / scale

            if on_change is not None:
                on_change(value)
            else:
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

        if initial is not None:
            default_value = initial
        else:
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

    def on_preview_ready(self):
        frame = self.worker.latest_preview_frame()

        if frame is None:
            return

        self.show_preview(frame)

    def on_worker_error(self, message):
        logger.error("Camera worker error: %s", message)

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
        self.worker.stop()
        self.worker_thread.quit()
        self.worker_thread.wait()

        self.camera.close()
        self.virtual_camera.close()

        event.accept()
