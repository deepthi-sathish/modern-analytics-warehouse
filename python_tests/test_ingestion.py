import pytest

from ingestion.load_bronze import count_csv_rows, validate_file


def make_csv(path, text):
    path.write_text(text, encoding="utf-8")
    return path


def test_count_rows_ignores_header(tmp_path):
    f = make_csv(tmp_path / "a.csv", "id,name\n1,a\n2,b\n")
    assert count_csv_rows(f) == 2


def test_validate_file_accepts_matching_header(tmp_path):
    f = make_csv(tmp_path / "a.csv", "id,name\n1,a\n")
    assert validate_file(f, ["id", "name"]) == 1


def test_validate_file_rejects_wrong_header(tmp_path):
    f = make_csv(tmp_path / "a.csv", "id,nme\n1,a\n")
    with pytest.raises(ValueError):
        validate_file(f, ["id", "name"])


def test_validate_file_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        validate_file(tmp_path / "nope.csv", ["id"])


def test_validate_file_rejects_empty_file(tmp_path):
    f = make_csv(tmp_path / "a.csv", "")
    with pytest.raises(ValueError):
        validate_file(f, ["id"])