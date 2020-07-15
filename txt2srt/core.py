# written by deciMae, minorly edited by glumbaron

import re
import sys
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Union, Generator, List


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


def parse_chunk(sequence_number: int, text: str, time_delta: int) -> Section:
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


def split_by_score(text: str, base_width: int = 10, best_length: int = 80) -> List[str]:
    num_chars = len(text)
    scores = [[0, 0] for i in range(num_chars + 3)]
    for i in reversed(range(num_chars - 2)):
        listmin = i + 1
        listmax = min(int(round(i + best_length + 3 * base_width)), num_chars - 1)
        ideal = i + best_length

        for j in range(listmin, min(listmax + 1, num_chars - 1)):
            if text[j] == text[j + 1] and text[j] == "\n":
                listmax = j
                break

        scoreopts = [[k, 100] for k in range(listmin, listmax + 1)]

        def score(k, preference):
            return preference + ((k - ideal) / base_width) ** 2 + scores[k + 1][1]

        for k in range(listmin, listmax + 1):
            if text[k] in "\n.!":
                scoreopts[k - listmin] = [k, score(k, 0.001)]
            elif text[k] == ",;:":
                scoreopts[k - listmin] = [k, score(k, 1.001)]
            elif text[k] == " ":
                scoreopts[k - listmin] = [k, score(k, 2.001)]

        scores[i] = min(scoreopts, key=lambda pair: pair[1])

    out = []
    start = 0
    while scores[start][0] != 0:
        end = scores[start][0] + 1
        chunk = text[start:end].strip()
        start = end

        out.append(chunk)
    return out


def convert(src_txt: str, time_delta: int = 5, split_type: str = "linebreak") -> str:
    """
    Converts a pre-formated text into valid SubRip Text (srt) file format.

    Args:
        src_txt: Source text to convert
        time_delta: Optional; Seconds each subtitle section should remain on
          screen. Defaults to 5 seconds.
        split_type: Optional; Defines what is considered a chunk of
          dialogue. Can be one of three options `linebreak`, `emptyline`, `score`.

    Returns:
       The converted SRT text.
    """
    if split_type == "linebreak":
        chunks = (line for line in src_txt.splitlines() if line)
    elif split_type == "emptyline":
        chunks = re.split(r"(?:\r?\n){2,}", src_txt.strip())
    elif split_type == "score":
        chunks = split_by_score(src_txt)
    else:
        raise ValueError(f"Undefined split type: {split_type}")

    sections = (str(parse_chunk(i, text, time_delta)) for i, text in enumerate(chunks))

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
