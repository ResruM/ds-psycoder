from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = REPO_ROOT / "amazing-psycoder"
CLI_PATH = REPO_ROOT / "ds_psycoder.py"
SHELL_INSTALLER = SKILL_ROOT / "install.sh"
POWERSHELL_INSTALLER = SKILL_ROOT / "install.ps1"
SKILL_NAMES = (
    "amazing-psycoder",
    "psy-exp-designer",
    "psy-exp-coder",
    "psy-exp-reviewer",
    "psy-ana-designer",
    "psy-ana-coder",
    "psy-ana-reviewer",
)

spec = importlib.util.spec_from_file_location("ds_psycoder", CLI_PATH)
ds_psycoder = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(ds_psycoder)


def bash_available() -> bool:
    executable = shutil.which("bash")
    if executable is None:
        return False
    probe = subprocess.run([executable, "-c", "exit 0"], capture_output=True, check=False)
    return probe.returncode == 0


def base_env() -> dict[str, str]:
    """Return an environment with a usable home directory for child processes."""
    env = os.environ.copy()
    home = env.get("USERPROFILE") or env.get("HOME") or tempfile.gettempdir()
    env["HOME"] = home
    env["USERPROFILE"] = home
    return env


def powershell_available() -> bool:
    if os.name != "nt":
        return False
    return shutil.which("powershell") is not None or shutil.which("pwsh") is not None


class DeepSeekInstallTests(unittest.TestCase):
    def run_cli(self, arguments: list[str], environment: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        env = base_env()
        env.update(environment or {})
        return subprocess.run(
            [sys.executable, str(CLI_PATH), *arguments],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_user_scope_installs_into_dsh_home(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            dsh_home = Path(directory) / "dsh-home"
            result = self.run_cli(["install", "--skip-validation"], {"DSH_HOME": str(dsh_home)})
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            skills = dsh_home / "skills"
            for name in SKILL_NAMES:
                self.assertTrue((skills / name / "SKILL.md").is_file(), name)
            check = self.run_cli(["check"], {"DSH_HOME": str(dsh_home)})
            self.assertEqual(0, check.returncode, check.stderr + check.stdout)
            self.assertIn("与工作区一致", check.stdout)

    def test_default_user_scope_is_home_dsh(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fake_home = Path(directory).resolve()
            environment = {key: value for key, value in os.environ.items() if key != "DSH_HOME"}
            environment["HOME"] = str(fake_home)
            environment["USERPROFILE"] = str(fake_home)
            with mock.patch.dict(os.environ, environment, clear=True):
                self.assertEqual(
                    fake_home / ".dsh" / "skills",
                    ds_psycoder.default_skills_dir("user", Path(".")),
                )

    def test_project_scope_uses_project_dsh_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "study"
            project.mkdir()
            result = self.run_cli(
                ["install", "--skip-validation", "--scope", "project", "--project-dir", str(project)]
            )
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            for name in SKILL_NAMES:
                self.assertTrue((project / ".dsh" / "skills" / name / "SKILL.md").is_file(), name)

    def test_explicit_target_overrides_scope(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "custom"
            result = self.run_cli(["install", "--skip-validation", "--target", str(target)])
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            self.assertTrue((target / "amazing-psycoder" / "SKILL.md").is_file())

    def test_check_reports_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "skills"
            self.assertEqual(0, self.run_cli(["install", "--skip-validation", "--target", str(target)]).returncode)
            (target / "psy-ana-coder" / "SKILL.md").write_text("# drifted\n", encoding="utf-8")
            (target / "psy-ana-reviewer" / "extra.md").write_text("extra\n", encoding="utf-8")
            result = self.run_cli(["check", "--target", str(target)])
            self.assertEqual(1, result.returncode)
            self.assertIn("psy-ana-coder", result.stdout)
            self.assertIn("psy-ana-reviewer", result.stdout)
            self.assertIn("漂移", result.stdout)

    def test_mid_batch_failure_rolls_back_every_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "skills"
            for name in SKILL_NAMES:
                (target / name / "old-marker").mkdir(parents=True)

            real_move = shutil.move

            def flaky_move(source: str, destination: str) -> str:
                if Path(source).parent.name == "stage" and Path(destination).name == "psy-ana-designer":
                    raise OSError("simulated mid-batch failure")
                return real_move(source, destination)

            with mock.patch("shutil.move", side_effect=flaky_move):
                with self.assertRaises(ds_psycoder.InstallError):
                    ds_psycoder.staged_install(ds_psycoder.skill_sources(), target)

            for name in SKILL_NAMES:
                self.assertTrue((target / name / "old-marker").is_dir(), name)
            self.assertEqual([], list(target.glob(".ds-psycoder.transaction.*")))

    def test_installer_rejects_hosts_that_are_no_longer_supported(self) -> None:
        if not bash_available():
            self.skipTest("bash is not available on this machine")
        for host in ("claude", "codex", "hermes", "openclaw"):
            with self.subTest(host=host):
                result = subprocess.run(
                    ["bash", str(SHELL_INSTALLER), host],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn("DeepSeek", result.stdout + result.stderr)

    def test_powershell_installer_rejects_unknown_host(self) -> None:
        if not powershell_available():
            self.skipTest("Windows PowerShell is not available on this machine")
        executable = shutil.which("powershell") or shutil.which("pwsh")
        result = subprocess.run(
            [str(executable), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(POWERSHELL_INSTALLER), "claude"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("DeepSeek", result.stdout + result.stderr)

    def test_shell_installer_help_mentions_deepseek_only(self) -> None:
        if not bash_available():
            self.skipTest("bash is not available on this machine")
        result = subprocess.run(
            ["bash", str(SHELL_INSTALLER), "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("deepseek", result.stdout)
        self.assertIn("DSH_HOME", result.stdout)
        for host in ("claude", "codex", "hermes", "openclaw"):
            self.assertNotIn(host, result.stdout.lower())


class DeepSeekRunnerTests(unittest.TestCase):
    def run_cli(self, arguments: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI_PATH), *arguments],
            cwd=REPO_ROOT,
            env=base_env(),
            capture_output=True,
            text=True,
            check=False,
        )

    def test_api_dry_run_composes_a_deepseek_request(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "skills"
            workdir = Path(directory) / "work"
            workdir.mkdir()
            install = self.run_cli(["install", "--skip-validation", "--target", str(target)])
            self.assertEqual(0, install.returncode, install.stderr + install.stdout)
            result = self.run_cli(
                [
                    "run",
                    "--backend",
                    "api",
                    "--target",
                    str(target),
                    "--workdir",
                    str(workdir),
                    "--dry-run",
                    "帮我做一个 Stroop 实验",
                ]
            )
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual("api", payload["backend"])
            self.assertEqual(str(workdir), payload["workdir"])
            self.assertEqual(str(target), payload["skills_dir"])
            self.assertEqual(["read_file", "write_file", "list_dir"], payload["tools"])
            self.assertIn("DeepSeek 运行时说明", payload["messages"][0]["content"])
            self.assertEqual("帮我做一个 Stroop 实验", payload["messages"][1]["content"])
            for name in SKILL_NAMES[1:]:
                self.assertIn(str(target / name / "SKILL.md"), payload["messages"][0]["content"])

    def test_api_backend_requires_a_key_before_any_network_call(self) -> None:
        environment = base_env()
        environment.pop("DEEPSEEK_API_KEY", None)
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "run", "--backend", "api", "hello"],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("DEEPSEEK_API_KEY", result.stderr)

    def test_write_file_tool_refuses_paths_outside_the_workdir(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workdir = Path(directory) / "work"
            workdir.mkdir()
            outside = Path(directory) / "outside.txt"
            output, failed = ds_psycoder.execute_tool(
                "write_file", {"path": str(outside), "content": "nope"}, workdir, False
            )
            self.assertTrue(failed)
            self.assertIn("拒绝写入", output)
            self.assertFalse(outside.exists())

    def test_read_file_tool_numbers_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workdir = Path(directory)
            (workdir / "sample.txt").write_text("alpha\nbeta\n", encoding="utf-8")
            output, failed = ds_psycoder.execute_tool("read_file", {"path": "sample.txt"}, workdir, False)
            self.assertFalse(failed)
            self.assertIn("alpha", output)
            self.assertIn("beta", output)

    def test_run_command_is_disabled_unless_requested(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output, failed = ds_psycoder.execute_tool(
                "run_command", {"command": "echo hi"}, Path(directory), False
            )
            self.assertTrue(failed)
            self.assertIn("--allow-commands", output)

    def test_shell_argv_wraps_windows_command_shims(self) -> None:
        if os.name != "nt":
            self.skipTest("Windows-only behaviour")
        argv = ds_psycoder.shell_argv(r"C:\tools\dsh.CMD", ["headless", "hi"])
        self.assertEqual(["headless", "hi"], argv[-2:])
        self.assertIn("/c", argv)

    def test_doctor_reports_environment(self) -> None:
        result = self.run_cli(["doctor"])
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("ds-psycoder", result.stdout)
        self.assertIn("DeepSeek Harness", result.stdout)


if __name__ == "__main__":
    unittest.main()
