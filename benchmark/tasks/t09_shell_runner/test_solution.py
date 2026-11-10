from solution import count_files, run_command


def test_run_command():
    assert run_command("echo hi") == "hi"


def test_count_files(tmp_path):
    for name in ("a", "b", "c"):
        (tmp_path / name).write_text("x")
    assert count_files(str(tmp_path)) == 3
