from pathlib import Path
from txt2srt import convert

def test_convert():
    input_file = Path("tests/io/input.txt")
    output_gold = Path("tests/io/output.srt").read_text()

    txt = convert(input_file.read_text())
    assert output_gold == txt


def test_split_empty_lines():
    input_file = Path("tests/io/input.txt")
    output_gold = Path("tests/io/output_split_empty.srt").read_text()

    txt = convert(input_file.read_text(), split_type='emptyline')
    assert output_gold == txt


def test_split_score():
    input_file = Path("tests/io/input.txt")
    output_gold = Path("tests/io/output_split_score.srt").read_text()

    txt = convert(input_file.read_text(), time_delta=10, split_type='score')
    assert output_gold == txt
