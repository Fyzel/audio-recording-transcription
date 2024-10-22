# README

Generate speech to text transcription using OpenAI's general purpose speech recognition model [Whisper](https://github.com/openai/whisper).

## Description

From command line, specify the input, working, and output directories. [Whisper](https://github.com/openai/whisper) requires the input files to be constrained to a maximum file size. This utility will pre-process the files in the input directory to split the files into multiple parts if they exceed the maximum input size restriction.


## Installation

1. Requires Python version 3.12 or previous

2. Install python-ffmpeg

```bash
pip3 install python-ffmpeg
```

3. Install whisper

```bash
pip3 install git+https://github.com/openai/whisper.git
```

