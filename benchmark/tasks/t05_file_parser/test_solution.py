from solution import parse_number, read_lines


def test_parse_number():
    assert parse_number("42") == 42
    assert parse_number("3.5") == 3.5
    assert parse_number("not valid") is None


def test_read_lines(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("one\ntwo \n")
    assert read_lines(str(p)) == ["one", "two"]


def test_read_missing_file(tmp_path):
    assert read_lines(str(tmp_path / "missing.txt")) == []
