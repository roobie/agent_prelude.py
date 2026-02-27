import sys
import os
import json
import tempfile
from datetime import datetime
import subprocess
import pytest

import agent_prelude as ap


def test_read_write_json_and_text(tmp_path):
    p = tmp_path / "data.json"
    ap.write(str(p), {"a": 1})
    assert p.exists()
    data = ap.read(str(p))
    assert isinstance(data, dict) and data["a"] == 1

    txt = tmp_path / "t.txt"
    ap.write(str(txt), "hello", format="text")
    assert ap.read(str(txt)) == "hello"


def test_append_and_exists(tmp_path):
    f = tmp_path / "log.txt"
    ap.append(str(f), "line1")
    ap.append(str(f), "line2")
    content = ap.read(str(f))
    assert "line1" in content and "line2" in content
    assert ap.exists(str(f))


def test_ls_find_mkdir(tmp_path):
    d = tmp_path / "dir/sub"
    ap.mkdir(str(d))
    assert ap.exists(str(d))
    p1 = d / "a.py"
    p2 = d / "b.txt"
    ap.write(str(p1), "print(1)")
    ap.write(str(p2), "x")
    all_py = ap.find("*.py", str(tmp_path))
    assert any(str(p1) in x for x in all_py)
    listed = ap.ls(str(d), "*")
    assert any("a.py" in x for x in listed)


def test_grep(tmp_path, capsys):
    d = tmp_path / "g"
    d.mkdir()
    f1 = d / "one.txt"
    f2 = d / "two.txt"
    ap.write(str(f1), "apple\nbanana\ncarrot")
    ap.write(str(f2), "durian\napple\n")
    results = ap.grep(r"apple", str(d))
    files = {r["file"] for r in results}
    assert any(str(f1) in f for f in files) and any(str(f2) in f for f in files)
    # grep should not raise on directories
    # create a directory entry; grep will attempt to read and log a WARN
    ap.mkdir(str(d / "subdir"))
    # call grep again to exercise the IsADirectoryError path
    res2 = ap.grep(r"nope", str(d))
    assert isinstance(res2, list)


class DummyResp:
    def __init__(self, status=200, json_data=None, text_data="", content=b""):
        self.status_code = status
        self._json = json_data
        self.text = text_data
        self.content = content

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        if self._json is None:
            raise ValueError("no json")
        return self._json


def test_get_post_download_monkeypatch(monkeypatch, tmp_path):
    # monkeypatch requests.get and requests.post on the agent_prelude module
    def fake_get(url, timeout=30, **kwargs):
        return DummyResp(status=200, json_data={"ok": True}, text_data="ok", content=b"bytes")

    def fake_get_binary(url, timeout=30, stream=True, **kwargs):
        return DummyResp(status=200, content=b"filedata")

    def fake_post(url, json=None, timeout=30, **kwargs):
        return DummyResp(status=201, json_data={"posted": json})

    monkeypatch.setattr(ap, "requests", ap.requests)
    monkeypatch.setattr(ap.requests, "get", fake_get)
    monkeypatch.setattr(ap.requests, "post", fake_post)

    r = ap.get("http://example.com")
    assert isinstance(r, dict) and r["ok"]

    r2 = ap.post("http://example.com", data={"x": 1})
    assert isinstance(r2, dict) and r2.get("posted") is not None

    # test download writes bytes
    monkeypatch.setattr(ap.requests, "get", fake_get_binary)
    out = tmp_path / "dl.bin"
    ap.download(str("http://nx"), str(out))
    assert out.exists() and out.read_bytes() == b"filedata"


def test_sh_and_run_and_check(monkeypatch):
    # sh simple command
    out = ap.sh(f"{sys.executable} -c \"print('ok')\"")
    assert "ok" in out

    # run with args list
    res = ap.run([sys.executable, "-c", "print('hello')"]) 
    assert "hello" in res

    # check raising for non-zero
    with pytest.raises(subprocess.CalledProcessError):
        ap.run([sys.executable, "-c", "import sys; sys.exit(2)"], check=True)

    with pytest.raises(subprocess.CalledProcessError):
        # sh with check True should raise on non-zero
        ap.sh(f"{sys.executable} -c \"import sys; sys.exit(3)\"", check=True)


def test_log_and_now(capsys):
    ap.log("testing log", level="DEBUG")
    # log prints to stderr
    captured = capsys.readouterr()
    assert "testing log" in captured.err
    assert isinstance(ap.now(), datetime)
