import os
from pathlib import Path
from detector import find_claude_dir

def test_find_claude_dir_none(monkeypatch, tmp_path):
    """Test that it returns None if no .claude directory is found."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()

    monkeypatch.setattr(Path, "home", lambda: fake_home)
    monkeypatch.setattr(os, "environ", {})

    assert find_claude_dir() is None

def test_find_claude_dir_in_home(monkeypatch, tmp_path):
    """Test that it finds .claude in the home directory."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    claude_dir = fake_home / ".claude"
    claude_dir.mkdir()

    monkeypatch.setattr(Path, "home", lambda: fake_home)
    monkeypatch.setattr(os, "environ", {})

    assert find_claude_dir() == claude_dir

def test_find_claude_dir_in_userprofile(monkeypatch, tmp_path):
    """Test that it finds .claude via USERPROFILE environment variable."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()

    fake_userprofile = tmp_path / "userprofile"
    fake_userprofile.mkdir()
    claude_dir = fake_userprofile / ".claude"
    claude_dir.mkdir()

    monkeypatch.setattr(Path, "home", lambda: fake_home)
    monkeypatch.setitem(os.environ, "USERPROFILE", str(fake_userprofile))
    monkeypatch.delitem(os.environ, "HOME", raising=False)

    assert find_claude_dir() == claude_dir

def test_find_claude_dir_in_home_env(monkeypatch, tmp_path):
    """Test that it finds .claude via HOME environment variable."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()

    fake_env_home = tmp_path / "env_home"
    fake_env_home.mkdir()
    claude_dir = fake_env_home / ".claude"
    claude_dir.mkdir()

    monkeypatch.setattr(Path, "home", lambda: fake_home)
    monkeypatch.delitem(os.environ, "USERPROFILE", raising=False)
    monkeypatch.setitem(os.environ, "HOME", str(fake_env_home))

    assert find_claude_dir() == claude_dir

def test_find_claude_dir_priority(monkeypatch, tmp_path):
    """Test the priority of candidates: Path.home() > USERPROFILE > HOME."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    home_claude = fake_home / ".claude"
    home_claude.mkdir()

    fake_userprofile = tmp_path / "userprofile"
    fake_userprofile.mkdir()
    up_claude = fake_userprofile / ".claude"
    up_claude.mkdir()

    fake_env_home = tmp_path / "env_home"
    fake_env_home.mkdir()
    env_home_claude = fake_env_home / ".claude"
    env_home_claude.mkdir()

    monkeypatch.setattr(Path, "home", lambda: fake_home)
    monkeypatch.setitem(os.environ, "USERPROFILE", str(fake_userprofile))
    monkeypatch.setitem(os.environ, "HOME", str(fake_env_home))

    # Should pick Path.home() one first
    assert find_claude_dir() == home_claude

    # Remove Path.home() one, should pick USERPROFILE
    home_claude.rmdir()
    assert find_claude_dir() == up_claude

    # Remove USERPROFILE one, should pick HOME
    up_claude.rmdir()
    assert find_claude_dir() == env_home_claude

    # Remove HOME one, should return None
    env_home_claude.rmdir()
    assert find_claude_dir() is None
