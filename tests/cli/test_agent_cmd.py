"""Tests for the ``jarvis agent`` CLI commands."""

from __future__ import annotations

from click.testing import CliRunner

from openjarvis.cli import cli


class TestAgentCmd:
    def test_agent_list_help(self) -> None:
        result = CliRunner().invoke(cli, ["agent", "list", "--help"])
        assert result.exit_code == 0

    def test_agent_info_help(self) -> None:
        result = CliRunner().invoke(cli, ["agent", "info", "--help"])
        assert result.exit_code == 0

    def test_agent_group_help(self) -> None:
        result = CliRunner().invoke(cli, ["agent", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "info" in result.output
