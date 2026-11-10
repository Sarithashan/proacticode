from solution import analyze_text


def test_basic_counts():
    s = analyze_text("Hello World 42!")
    assert s["words"] == 3
    assert s["vowels"] == 3
    assert s["consonants"] == 7
    assert s["digits"] == 2
    assert s["spaces"] == 2
    assert s["punctuation"] == 1
    assert s["upper"] == 2
    assert s["lower"] == 8


def test_words():
    s = analyze_text("a bbb cc")
    assert s["longest"] == "bbb"
    assert s["shortest"] == "a"
    assert s["avg_len"] == 2.0


def test_empty():
    s = analyze_text("")
    assert s["words"] == 0
    assert s["avg_len"] == 0
    assert s["longest"] == ""
    assert s["shortest"] == ""
