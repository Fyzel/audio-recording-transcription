import shutil
import unittest

from main import condition_input_files, create_directory


class AudioFileSplitting(unittest.TestCase):
    def setUp(self):
        self.input_directory_name = 'AudioFileSplitting'
        self.working_directory_name = 'AudioFileSplitting-working'
        create_directory(self.working_directory_name, verbose=True)

    def test_splitting(self):
        condition_input_files(input_path = self.input_directory_name,
                              working_path = self.working_directory_name,
                              max_file_size=5 * 1024,
                              max_segment_duration=60,
                              verbose=True)

        pass



    def tearDown(self):
        # remove test directories
        shutil.rmtree(self.working_directory_name)
