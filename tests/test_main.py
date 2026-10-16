"""Tests for the SweetyAI launcher entry point (main.py)."""

import os

import main


def test_sweety_cli_exists():
    assert os.path.exists(main.SWEETY_CLI)


def test_build_command_default():
    cmd = main.build_command([])
    assert len(cmd) == 2
    assert cmd[1].endswith("sweety.py")


def test_build_command_passthrough():
    cmd = main.build_command(["legal", "bail", "--type", "482"])
    assert cmd[2:] == ["legal", "bail", "--type", "482"]
