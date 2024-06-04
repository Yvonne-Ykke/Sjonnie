import unittest
from unittest.mock import patch
import math

# Import the function being tested
from blind_spot import calculate_arm_angles

class TestCalculateArmAngles(unittest.TestCase):

    def test_calculate_arm_angles_origin(self):
        x, y = 0, 0
        arm_segment_length = 1
        shoulder_angle, elbow_angle = calculate_arm_angles(x, y, arm_segment_length)
        self.assertEqual(shoulder_angle, 0)
        self.assertEqual(elbow_angle, 0)

    def test_calculate_arm_angles_negative_coordinates(self):
        x, y = -1, -2
        arm_segment_length = 1
        shoulder_angle, elbow_angle = calculate_arm_angles(x, y, arm_segment_length)
        self.assertEqual(shoulder_angle, math.pi)
        self.assertEqual(elbow_angle, math.pi)

    def test_calculate_arm_angles_large_coordinates(self):
        x, y = 10, 20
        arm_segment_length = 1
        shoulder_angle, elbow_angle = calculate_arm_angles(x, y, arm_segment_length)
        self.assertAlmostEqual(shoulder_angle, math.atan2(y, x), places=6)
        self.assertAlmostEqual(elbow_angle, math.pi - 2 * math.atan2(y, x), places=6)

    def test_calculate_arm_angles_zero_length(self):
        x, y = 1, 2
        arm_segment_length = 0
        with self.assertRaises(ValueError):
            calculate_arm_angles(x, y, arm_segment_length)

    @patch('blind_spot.calculate_arm_angles')
    def test_calculate_arm_angles_mocked(self, mock_calculate_arm_angles):
        mock_calculate_arm_angles.return_value = (0.5, 1.0)
        x, y = 1, 2
        arm_segment_length = 1
        shoulder_angle, elbow_angle = calculate_arm_angles(x, y, arm_segment_length)
        self.assertEqual(shoulder_angle, 0.5)
        self.assertEqual(elbow_angle, 1.0)

if __name__ == '__main__':
    unittest.main()
