import os
import unittest

from main import check_input_directory, check_output_directory, check_working_directory, create_directory


class TestCliOptions(unittest.TestCase):
    def setUp(self):
        self.test_directory_name = 'TestCliOptions/new-directory'

    def test_check_input_directory(self):
        self.assertFalse(check_input_directory('TestCliOptions/does-not-exist'))
        self.assertTrue(check_input_directory('TestCliOptions/input-directory'))

    def test_check_output_directory(self):
        self.assertFalse(check_output_directory('TestCliOptions/does-not-exist'))
        self.assertTrue(check_output_directory('TestCliOptions/output-directory'))

    def test_check_working_directory(self):
        self.assertFalse(check_working_directory('TestCliOptions/does-not-exist'))
        self.assertTrue(check_working_directory('TestCliOptions/working-directory'))

    def test_create_directory(self):
        self.assertFalse(check_working_directory(self.test_directory_name))
        self.assertTrue(create_directory(self.test_directory_name))
        self.assertTrue(check_working_directory(self.test_directory_name))

    def tearDown(self):
        # remove test directories
        os.rmdir(self.test_directory_name)
