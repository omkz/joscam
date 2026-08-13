import logging
import time

import cv2
from PySide6.QtCore import QMutex, QMutexLocker, QObject, Signal

logger = logging.getLogger(__name__)


class CameraWorker(QObject):
    """Runs capture -> processing -> virtual camera output off the GUI thread.

    Preview frames are handed to the GUI via a plain notification signal
    plus a mutex-guarded "latest frame" slot, rather than emitting every
    frame as a signal argument. This way a busy GUI thread never builds up
    a backlog of stale frames to render -- it just reads whatever is
    current when it gets around to it.
    """

    preview_ready = Signal()
    error = Signal(str)

    def __init__(
        self,
        camera,
        pipeline,
        virtual_camera,
        width,
        height,
        preview_fps=15,
        stats_interval=5.0,
    ):
        super().__init__()

        self.camera = camera
        self.pipeline = pipeline
        self.virtual_camera = virtual_camera
        self.width = width
        self.height = height
        self.preview_interval = 1.0 / preview_fps
        self.stats_interval = stats_interval

        self._running = True
        self._mutex = QMutex()
        self._latest_preview = None

    def latest_preview_frame(self):
        with QMutexLocker(self._mutex):
            return self._latest_preview

    def stop(self):
        self._running = False

    def run(self):
        last_preview_emit = 0.0
        last_stats_time = time.perf_counter()
        frame_count = 0
        total_process_time = 0.0

        while self._running:
            try:
                frame = self.camera.read()
            except RuntimeError as exc:
                self.error.emit(str(exc))
                break

            if (
                frame.shape[1] != self.width
                or frame.shape[0] != self.height
            ):
                frame = cv2.resize(frame, (self.width, self.height))

            process_start = time.perf_counter()
            frame = self.pipeline.process(frame)
            total_process_time += time.perf_counter() - process_start

            self.virtual_camera.send(frame)

            now = time.perf_counter()

            if now - last_preview_emit >= self.preview_interval:
                last_preview_emit = now

                with QMutexLocker(self._mutex):
                    self._latest_preview = frame

                self.preview_ready.emit()

            frame_count += 1

            if now - last_stats_time >= self.stats_interval:
                elapsed = now - last_stats_time

                logger.info(
                    "capture=%.1ffps virtual=%.1ffps avg_process=%.2fms",
                    frame_count / elapsed,
                    self.virtual_camera.current_fps,
                    (total_process_time / frame_count) * 1000,
                )

                frame_count = 0
                total_process_time = 0.0
                last_stats_time = now

            self.virtual_camera.sleep_until_next_frame()
