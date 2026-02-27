"""Tests for the shell_exec tool."""

from __future__ import annotations

import os

from openjarvis.tools.shell_exec import ShellExecTool


class TestShellExecTool:
    def test_spec(self):
        tool = ShellExecTool()
        assert tool.spec.name == "shell_exec"
        assert tool.spec.category == "system"
        assert tool.spec.requires_confirmation is True
        assert tool.spec.timeout_seconds == 60.0
        assert "code:execute" in tool.spec.required_capabilities
        assert "command" in tool.spec.parameters["properties"]
        assert "command" in tool.spec.parameters["required"]

    def test_no_command(self):
        tool = ShellExecTool()
        result = tool.execute(command="")
        assert result.success is False
        assert "No command" in result.content

    def test_no_command_param(self):
        tool = ShellExecTool()
        result = tool.execute()
        assert result.success is False
        assert "No command" in result.content

    def test_simple_echo(self):
        tool = ShellExecTool()
        result = tool.execute(command="echo hello")
        assert result.success is True
        assert "hello" in result.content
        assert "STDOUT" in result.content

    def test_capture_stderr(self):
        tool = ShellExecTool()
        result = tool.execute(command="echo error_msg >&2")
        assert "error_msg" in result.content
        assert "STDERR" in result.content

    def test_timeout_exceeded(self):
        tool = ShellExecTool()
        result = tool.execute(command="sleep 60", timeout=1)
        assert result.success is False
        assert "timed out" in result.content
        assert result.metadata["returncode"] == -1
        assert result.metadata["timeout_used"] == 1

    def test_timeout_capped_at_max(self):
        tool = ShellExecTool()
        # Request 999 seconds -- should be capped at 300
        result = tool.execute(command="echo ok", timeout=999)
        assert result.success is True
        assert result.metadata["timeout_used"] == 300

    def test_working_dir(self, tmp_path):
        tool = ShellExecTool()
        result = tool.execute(command="pwd", working_dir=str(tmp_path))
        assert result.success is True
        assert str(tmp_path) in result.content
        assert result.metadata["working_dir"] == str(tmp_path)

    def test_working_dir_not_exists(self):
        tool = ShellExecTool()
        result = tool.execute(command="echo hi", working_dir="/nonexistent/path")
        assert result.success is False
        assert "does not exist" in result.content

    def test_working_dir_not_directory(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("data", encoding="utf-8")
        tool = ShellExecTool()
        result = tool.execute(command="echo hi", working_dir=str(f))
        assert result.success is False
        assert "not a directory" in result.content

    def test_env_clearing(self):
        """Verify that arbitrary env vars are NOT passed through."""
        marker = "OPENJARVIS_TEST_SECRET_12345"
        os.environ[marker] = "leaked"
        try:
            tool = ShellExecTool()
            result = tool.execute(command=f"echo ${marker}")
            assert result.success is True
            # The echoed value should be empty (variable not set in child)
            assert "leaked" not in result.content
        finally:
            os.environ.pop(marker, None)

    def test_env_passthrough(self):
        """Verify that explicitly listed env vars ARE passed through."""
        marker = "OPENJARVIS_TEST_PASSTHROUGH_67890"
        os.environ[marker] = "allowed_value"
        try:
            tool = ShellExecTool()
            result = tool.execute(
                command=f"echo ${marker}",
                env_passthrough=[marker],
            )
            assert result.success is True
            assert "allowed_value" in result.content
        finally:
            os.environ.pop(marker, None)

    def test_returncode_in_metadata(self):
        tool = ShellExecTool()
        result = tool.execute(command="echo ok")
        assert result.success is True
        assert result.metadata["returncode"] == 0

    def test_nonzero_returncode(self):
        tool = ShellExecTool()
        result = tool.execute(command="exit 42")
        assert result.success is False
        assert result.metadata["returncode"] == 42

    def test_max_output_truncation(self, tmp_path):
        """Stdout exceeding 100 KB is truncated."""
        # Generate > 100 KB of output (each line ~101 chars, 1100 lines ~ 111 KB)
        tool = ShellExecTool()
        result = tool.execute(
            command="python3 -c \"print('A' * 200000)\"",
        )
        # Output should contain truncation marker
        assert "truncated" in result.content
        # Total content should be well under 200 KB
        assert len(result.content) < 200_000

    def test_no_output(self):
        tool = ShellExecTool()
        result = tool.execute(command="true")
        assert result.success is True
        assert result.content == "(no output)"

    def test_tool_id(self):
        tool = ShellExecTool()
        assert tool.tool_id == "shell_exec"

    def test_to_openai_function(self):
        tool = ShellExecTool()
        fn = tool.to_openai_function()
        assert fn["type"] == "function"
        assert fn["function"]["name"] == "shell_exec"
        assert "command" in fn["function"]["parameters"]["properties"]

    def test_default_timeout_metadata(self):
        tool = ShellExecTool()
        result = tool.execute(command="echo ok")
        assert result.metadata["timeout_used"] == 30
