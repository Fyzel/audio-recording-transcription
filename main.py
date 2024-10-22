import io
import os
import shutil
from argparse import ArgumentParser

import magic
import whisper
from pydub import AudioSegment
from pydub.utils import mediainfo


def configure_command_line_parser(parser):
    """
    Configure the command line parser
    :param parser: argument parser
    :return:parser arguments
    """
    # parse input arguments
    parser.add_argument(
        '-i', '--input',
        type=str,
        help='Input directory containing audio files',
        required=True)
    parser.add_argument(
        '-t', '--temp',
        type=str,
        default='working',
        help='Temporary directory to save intermediate files',
        required=True)
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='output',
        help='Output directory to save transcriptions',
        required=True)
    parser.add_argument(
        '-v', '--verbose',
        help='Configure verbose output',
        action="store_true")
    # parser.add_argument(
    #     '-m', '--max-file-size',
    #     help='Maximum file size before file is split',
    #     type=int,
    #     action="store_const",
    #     const=25 * 1024 * 1024,
    #     required=False)
    return parser.parse_args()


def check_input_directory(path: str, verbose=False) -> bool:
    """
    Check if input directory exists
    :param path: input directory path
    :param verbose: verbose output
    :return: True if input directory exists, False otherwise
    """
    # check if input directory exists
    if not os.path.exists(path):
        if verbose:
            print('Input directory does not exist')
        return False

    if verbose:
        print(f'Input directory \'{path}\' exist')
    return True


def check_output_directory(path: str, verbose=False) -> bool:
    """
    Check if output directory exists
    :param path: output directory path
    :param verbose: verbose output
    :return: True if output directory exists, False otherwise
    """
    # check if input directory exists
    if not os.path.exists(path):
        if verbose:
            print(f'Output directory \'{path}\' does not exist')
        return False

    if verbose:
        print(f'Output directory \'{path}\' exist')
    return True


def check_working_directory(path: str, verbose=False) -> bool:
    """
    Check if working directory exists
    :param path: Working directory path
    :param verbose: verbose output
    :return: True if working directory exists, False otherwise
    """
    # check if directory exists
    if not os.path.exists(path):
        if verbose:
            print('Working directory does not exist')
        return False

    if verbose:
        print(f'Working directory \'{path}\' exist')
    return True


def create_directory(path: str, verbose=False) -> bool:
    """
    Create directory if it does not exist
    :param path: path to the directory
    :param verbose: verbose output
    :return: True if directory is created, False otherwise
    """
    if not os.path.exists(path):
        os.mkdir(path)
        if verbose:
            print(f'Created directory \'{path}\'')
        return True
    else:
        if verbose:
            print(f'Directory \'{path}\' already exists')
        return False


def condition_input_files(input_path: str,
                          working_path: str,
                          max_file_size: int,
                          max_segment_duration: int,
                          verbose: bool):
    """
    Condition the input files to be the correct size in the working directory
    :param input_path: Input directory path
    :param working_path: Working directory path
    :param max_file_size: Maximum file size
    ":param max_segment_duration: Maximum segment duration in seconds
    :param verbose: verbose output
    """
    for root, dirs, files in os.walk(input_path):
        for file in files:
            file_path = os.path.join(root, file)

            file_type = magic.from_file(file_path, mime=True)

            if file_type == 'audio/mpeg' or file_type == 'application/octet-stream':
                if os.path.getsize(file_path) <= max_file_size:
                    # file size is less than max file size
                    if verbose:
                        print(f'File \'{file_path}\' is less than {max_file_size} bytes')
                    shutil.copy(file_path, os.path.join(working_path, file))
                else:
                    # split the file into smaller files within the working directory\
                    if verbose:
                        print(f'File \'{file_path}\' is larger than {max_file_size} bytes')

                    audio = AudioSegment.from_mp3(file_path)
                    original_bitrate = mediainfo(file_path)['bit_rate']

                    # split the file into smaller files of max_segment_duration
                    segments = audio[::max_segment_duration * 1000]

                    for i, segment in enumerate(segments):
                        out = segment.export(os.path.join(working_path, f'{file}_{i:0>4}.mp3'),
                                             format='mp3',
                                             bitrate=original_bitrate)
                        out.close()
            else:
                if verbose:
                    print(f'File \'{file_path}\' is not an audio file')


def process_audio_files_in_working_directory(working_path: str,
                                             output_path: str,
                                             verbose: bool):
    """
    Process audio files in the working directory
    :param working_path: Working directory path
    :param output_path: Output directory path for transcripts
    :param verbose: verbose output
    """
    for root, dirs, files in os.walk(working_path):
        model = whisper.load_model(name="large", device="cuda")

        for file in files:
            input_file_path = os.path.join(root, file)
            output_file_path = os.path.join(output_path, f'{file}.txt')

            file_type = magic.from_file(input_file_path, mime=True)

            if file_type == 'audio/mpeg' or file_type == 'application/octet-stream':
                if verbose:
                    print(f'Processing file 🔊: \'{input_file_path}\'')

                transcript = model.transcribe(input_file_path, verbose=True, language="en")

                with io.open(output_file_path, "w", encoding="UTF-8") as my_file:
                    for (key, value) in transcript.items():
                        my_string = u"{key}: {value}".format(key=key, value=value)
                        my_file.write(my_string)


def main():
    """

    :return:
    """
    max_file_size = 25 * 1024 * 1024

    # parse the command line inputs
    parser = ArgumentParser(
        prog='symak-audio-recording-transcription',
        description='Convert audio recording to text transcription')

    args = configure_command_line_parser(parser)

    if not check_input_directory(args.input, args.verbose):
        print(f'Input directory \'{args.input}\' does not exist')
        parser.print_help()
        exit(-1)

    if not check_output_directory(args.output, args.verbose):
        create_directory(args.output, args.verbose)

    if not check_working_directory(args.temp, args.verbose):
        create_directory(args.temp, args.verbose)

    condition_input_files(input_path=args.input,
                          working_path=args.temp,
                          max_file_size=max_file_size,
                          max_segment_duration=20 * 60,  # 20 minutes or roughly 20 MB
                          verbose=args.verbose)

    process_audio_files_in_working_directory(working_path=args.temp,
                                             output_path=args.output,
                                             verbose=args.verbose)


if __name__ == '__main__':
    main()
