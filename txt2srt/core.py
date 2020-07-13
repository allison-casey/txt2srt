# written by deciMae, minorly edited by glumbaron

import re
import sys
from dataclasses import dataclass
from functools import reduce


def srt_time(hour: int, min: int, sec: int, milli: int) -> str:
    return f"{hour:02}:{min:02}:{sec:02},{milli:03}"


def srt_time_range(
    start_hour: int,
    start_min: int,
    start_sec: int,
    start_milli: int,
    end_hour: int,
    end_min: int,
    end_sec: int,
    end_milli: int,
) -> str:
    start_time = srt_time(start_hour, start_min, start_sec, start_milli)
    end_time = srt_time(end_hour, end_min, end_sec, end_milli)
    return f"{start_time} --> {end_time}"


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

    capture_sequence: int
    text: str

    def __repr__(self):
        time_range = srt_time_range(
            self.start_hour,
            self.start_min,
            self.start_sec,
            self.start_milli,
            self.end_hour,
            self.end_min,
            self.end_sec,
            self.end_milli,
        )

        return str.join("\n", [str(self.capture_sequence), time_range, self.text])


def parse(capture_sequence: int, text: str, time_delta: int) -> Section:
    time = capture_sequence * time_delta
    nexttime = (capture_sequence + 1) * time_delta
    hour = time // 3600
    min = time // 60 % 60
    sec = int(time) % 60
    next_hour = nexttime // 3600
    next_min = nexttime // 60 % 60
    next_sec = int(nexttime) % 60

    return Section(
        hour, min, sec, 0, next_hour, next_min, next_sec, 0, capture_sequence + 1, text
    )


def convert(
    src_txt: str, time_delta: int = 5, split_on_empty_lines: bool = False
) -> str:
    if split_on_empty_lines:
        chunks = re.split(r"(?:\r?\n){2,}", src_txt.strip())
    else:
        chunks = (line for line in src_txt.splitlines() if line)

    sections = (str(parse(i, text, time_delta)) for i, text in enumerate(chunks))

    return str.join("\n\n", sections)
