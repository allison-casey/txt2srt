from pathlib import Path
from txt2srt import convert

def test_convert():
    input_file = Path("tests/io/input.txt")
    output_gold = Path("tests/io/output.srt").read_text()

    txt = convert(input_file.read_text())
    assert output_gold == txt
