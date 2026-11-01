import unittest

import cv2
import numpy as np

from joscam.effects.beauty import FaceBeauty
from joscam.pipeline import EffectPipeline
from joscam.settings import CameraSettings


class BeautyTests(unittest.TestCase):
    def setUp(self):
        self.frame = np.random.default_rng(7).integers(
            60, 190, (120, 160, 3), dtype=np.uint8
        )
        self.beauty = FaceBeauty()

    def test_disabled_does_not_initialize_detector(self):
        self.assertIs(self.beauty.process(self.frame), self.frame)
        self.assertIsNone(self.beauty.detector)

    def test_missing_face_leaves_frame_unchanged(self):
        self.beauty._faces = lambda frame: []
        np.testing.assert_array_equal(
            self.beauty.process(self.frame, 1, 1), self.frame
        )

    def test_retouch_is_local_and_reduces_texture(self):
        self.beauty._faces = lambda frame: [(30, 10, 80, 100)]
        result = self.beauty.process(self.frame, 1)
        np.testing.assert_array_equal(result[:, :30], self.frame[:, :30])
        np.testing.assert_array_equal(result[:, 110:], self.frame[:, 110:])
        self.assertLess(result[60:75, 55:85].std(), self.frame[60:75, 55:85].std())
        self.assertEqual(result.dtype, np.uint8)
        self.assertEqual(result.shape, self.frame.shape)
        np.testing.assert_array_equal(
            result[49, 54], self.frame[49, 54]  # protected eye center
        )

    def test_face_leaving_does_not_leave_old_mask(self):
        self.beauty._faces = lambda frame: [(30, 10, 80, 100)]
        self.beauty.process(self.frame, 1, 1)
        self.beauty._faces = lambda frame: []
        np.testing.assert_array_equal(self.beauty.process(self.frame, 1, 1), self.frame)

    def test_light_preserves_white_and_lifts_midtones(self):
        self.beauty._faces = lambda frame: [(0, 0, 160, 120)]
        white = np.full_like(self.frame, 255)
        np.testing.assert_array_equal(self.beauty.process(white, 0, 1), white)
        gray = np.full_like(self.frame, 120)
        self.assertGreater(self.beauty.process(gray, 0, 1)[65, 80, 0], 120)

    def test_bundled_detector_loads_and_pipeline_remains_neutral(self):
        black = np.zeros_like(self.frame)
        np.testing.assert_array_equal(self.beauty.process(black, 1), black)
        self.assertFalse(self.beauty.detector.empty())
        np.testing.assert_array_equal(
            EffectPipeline(CameraSettings()).process(self.frame), self.frame
        )


if __name__ == '__main__':
    unittest.main()
