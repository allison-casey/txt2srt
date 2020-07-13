# written by deciMae, minorly edited by glumbaron

import re
import sys
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Union


def srt_time(hour: int, minute: int, sec: int, milli: int) -> str:
    return f"{hour:02}:{minute:02}:{sec:02},{milli:03}"


@dataclass
class Section:
    start_hour: int
    start_min: int
    start_sec: int
    start_milli: int

    end_hour: int
    end_min: int
    end_sec: int
    end_milli: int

    sequence_number: int
    text: str

    @property
    def start_time(self):
        return srt_time(
            self.start_hour, self.start_min, self.start_sec, self.start_milli
        )

    @property
    def end_time(self):
        return srt_time(self.end_hour, self.end_min, self.end_sec, self.end_milli)

    @property
    def time_range(self):
        return f"{self.start_time} --> {self.end_time}"

    def __repr__(self):
        return str.join("\n", [str(self.sequence_number), self.time_range, self.text])


def parse(sequence_number: int, text: str, time_delta: int) -> Section:
    time = sequence_number * time_delta
    nexttime = (sequence_number + 1) * time_delta
    hour = time // 3600
    min = time // 60 % 60
    sec = int(time) % 60
    next_hour = nexttime // 3600
    next_min = nexttime // 60 % 60
    next_sec = int(nexttime) % 60

    return Section(
        hour, min, sec, 0, next_hour, next_min, next_sec, 0, sequence_number + 1, text
    )


def convert(
    src_txt: str, time_delta: int = 5, split_on_empty_lines: bool = False
) -> str:
    """
    Converts a pre-formated text into valid SubRip Text (srt) file format.

    Args:
        src_txt: Source text to convert
        time_delta: Optional; Seconds each subtitle section should remain on
          screen. Defaults to 5 seconds.
        split_on_empty_lines: Optional; Defines what is considered a chunk of
          dialogue. If True, a chunk is separated by an empty line or lines only
          otherwise a chunk is created by every line break.

    Returns:
       The converted SRT text.
    """
    if split_on_empty_lines:
        chunks = re.split(r"(?:\r?\n){2,}", src_txt.strip())
    else:
        chunks = (line for line in src_txt.splitlines() if line)

    sections = (str(parse(i, text, time_delta)) for i, text in enumerate(chunks))

    return str.join("\n\n", sections)


def convert_file(src_file: Union[str, Path], output_file: Union[str, Path], **kwargs):
    """
    Converts a pre-formated text file into valid SubRip Text (srt) file format.

    Args:
        src_file: Path to the input text document.
        output_file: Path to the converted srt file.
        kwargs: See `convert` for available conversion options.
    """
    src_txt = Path(src_file).read_text()
    srt_txt = convert(src_txt, **kwargs)

    Path(output_file).write_text(srt_txt)
