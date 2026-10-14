#!/usr/bin/env python3
"""ds-psycoder — DeepSeek 驱动的 PsyCoder 技能套件入口。

一个命令即可完成四件事：

* install 把 7 个 PsyCoder skill 安装到 DeepSeek Harness (dsh) 的 skill 根目录；
* check   检查已安装 skill 是否与仓库工作区一致（漂移检查）；
* doctor  报告本机 DeepSeek 运行环境；
* run     用一个 DeepSeek 模型执行一项研究任务，可选两种后端：

  - dsh：调用本机 DeepSeek Harness 的 "dsh headless"（完整工具链）；
  - api：直接调用 DeepSeek 的 OpenAI 兼容 Chat Completions 接口，并自带一个
    最小文件工具循环，因此不需要安装 Claude Code、Codex、Hermes 或 OpenClaw
    等任何第三方 Agent 宿主。

本文件只依赖 Python 标准库。
"""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parent
SKILL_SOURCE_ROOT = REPO_ROOT / "amazing-psycoder"
VALIDATOR = SKILL_SOURCE_ROOT / "scripts" / "validate_skills.py"
ENTRY_SKILL = "amazing-psycoder"
SPECIALIST_SKILLS = (
    "psy-exp-designer",
    "psy-exp-coder",
    "psy-exp-reviewer",
    "psy-ana-designer",
    "psy-ana-coder",
    "psy-ana-reviewer",
)
SKILL_NAMES = (ENTRY_SKILL, *SPECIALIST_SKILLS)

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_MAX_STEPS = 24
DEFAULT_TIMEOUT_SECONDS = 600
MAX_TOOL_OUTPUT_CHARS = 20000


# --------------------------------------------------------------------------- #
# 安装位置
# --------------------------------------------------------------------------- #
def skill_sources() -> dict[str, Path]:
    """返回 7 个 skill 名称到源目录的映射。"""
    sources = {ENTRY_SKILL: SKILL_SOURCE_ROOT}
    for name in SPECIALIST_SKILLS:
        sources[name] = SKILL_SOURCE_ROOT / name
    return sources


def dsh_home() -> Path:
    """DeepSeek Harness 配置根目录：DSH_HOME 或 ~/.dsh。"""
    configured = os.environ.get("DSH_HOME")
    if configured:
        return Path(configured).expanduser()
    try:
        home = Path.home()
    except RuntimeError as exc:
        raise InstallError(
            "无法确定用户主目录（HOME / USERPROFILE 未设置）；请设置 DSH_HOME 或使用 --target 指定安装目录。"
        ) from exc
    return home / ".dsh"


def default_skills_dir(scope: str, project_dir: Path) -> Path:
    """按 scope 返回 dsh 的 skill 根目录。

    user 对应 DSH_HOME/skills，project 对应 <project>/.dsh/skills；
    两者都是 dsh-skill-filesystem 提供方的默认扫描根。
    """
    if scope == "project":
        return project_dir.resolve() / ".dsh" / "skills"
    return dsh_home() / "skills"


def resolve_target(args: argparse.Namespace) -> Path:
    if getattr(args, "target", None):
        return Path(args.target).expanduser().resolve()
    return default_skills_dir(args.scope, Path(args.project_dir))


# --------------------------------------------------------------------------- #
# 安装事务
# --------------------------------------------------------------------------- #
class InstallError(RuntimeError):
    """安装失败；调用方负责回滚。"""


def validate_sources(quiet: bool = False) -> None:
    """运行仓库自带的安装前校验（仅标准库）。"""
    if not VALIDATOR.is_file():
        raise InstallError(f"校验脚本不存在：{VALIDATOR}")
    if not quiet:
        print("验证源 skill ...")
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--portable"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise InstallError("源 skill 校验失败：\n" + (result.stdout + result.stderr).strip())
    if not quiet:
        print(result.stdout.strip())


def staged_install(sources: dict[str, Path], destination: Path) -> None:
    """在同一文件系统内暂存并原子替换 7 个 skill，任一失败则整批回滚。"""
    destination.mkdir(parents=True, exist_ok=True)
    transaction = Path(tempfile.mkdtemp(prefix=".ds-psycoder.transaction.", dir=str(destination)))
    stage = transaction / "stage"
    backup = transaction / "backup"
    stage.mkdir()
    backup.mkdir()
    committed: list[str] = []
    try:
        for name, source in sources.items():
            if not (source / "SKILL.md").is_file():
                raise InstallError(f"源目录缺少 SKILL.md：{source}")
            shutil.copytree(source, stage / name)

        for name in sources:
            target = destination / name
            previous = backup / name
            if target.exists() or target.is_symlink():
                shutil.move(str(target), str(previous))
            try:
                shutil.move(str(stage / name), str(target))
            except OSError as exc:
                # 该 skill 替换失败：先恢复它自己的备份，再让外层整批回滚。
                if previous.exists() or previous.is_symlink():
                    shutil.move(str(previous), str(target))
                raise InstallError(f"安装失败：{name}（{exc}）") from exc
            committed.append(name)
            print(f"  OK  {name}")
    except BaseException:
        for name in reversed(committed):
            target = destination / name
            previous = backup / name
            if target.exists() or target.is_symlink():
                shutil.rmtree(target, ignore_errors=True)
            if previous.exists() or previous.is_symlink():
                shutil.move(str(previous), str(target))
        raise
    finally:
        shutil.rmtree(transaction, ignore_errors=True)


def directory_diff(source: Path, target: Path) -> list[str]:
    """递归比较两个 skill 目录，返回人类可读的差异列表。"""
    problems: list[str] = []

    def walk(left: Path, right: Path, prefix: str) -> None:
        comparison = filecmp.dircmp(str(left), str(right))
        for name in comparison.left_only:
            problems.append(f"缺少 {prefix}{name}")
        for name in comparison.right_only:
            problems.append(f"多出 {prefix}{name}")
        for name in comparison.diff_files:
            problems.append(f"内容不同 {prefix}{name}")
        for name in comparison.funny_files:
            problems.append(f"无法比较 {prefix}{name}")
        for name in comparison.common_dirs:
            walk(left / name, right / name, f"{prefix}{name}/")

    walk(source, target, "")
    return problems


def check_install(sources: dict[str, Path], destination: Path) -> int:
    print(f"检查目录：{destination}")
    status = 0
    for name, source in sources.items():
        target = destination / name
        if not (target / "SKILL.md").is_file():
            print(f"  --  未安装 {name}")
            status = 1
            continue
        problems = directory_diff(source, target)
        if problems:
            status = 1
            print(f"  !!  {name} 已漂移或版本落后")
            for problem in problems[:10]:
                print(f"        {problem}")
        else:
            print(f"  OK  {name} 与工作区一致")
    if status == 0:
        print("全部已安装 skill 与工作区一致。")
    else:
        print("检测到安装漂移；确认后重新运行 install 以同步。")
    return status


def command_install(args: argparse.Namespace) -> int:
    sources = skill_sources()
    destination = resolve_target(args)
    if args.check:
        if not destination.is_dir():
            print(f"未安装：目录不存在 {destination}")
            return 1
        return check_install(sources, destination)

    if not args.skip_validation:
        validate_sources()
    print(f"范围: {args.scope}")
    print(f"目录: {destination}")
    print("安装 DeepSeek PsyCoder ...")
    staged_install(sources, destination)
    print("")
    print("完成。7 个 skill 已就绪：")
    for name in SKILL_NAMES:
        print(f"  - {name}")
    print("")
    print("接下来：")
    print("  DeepSeek Harness : dsh web    # 在会话中直接描述任务")
    print('  DeepSeek CLI     : python ds_psycoder.py run "帮我做一个 Stroop 实验"')
    print("  环境自检         : python ds_psycoder.py doctor")
    return 0


def command_check(args: argparse.Namespace) -> int:
    destination = resolve_target(args)
    if not destination.is_dir():
        print(f"未安装：目录不存在 {destination}")
        return 1
    return check_install(skill_sources(), destination)


# --------------------------------------------------------------------------- #
# 环境自检
# --------------------------------------------------------------------------- #
def which_dsh() -> str | None:
    return shutil.which("dsh")


def describe_dsh() -> tuple[bool, str]:
    executable = which_dsh()
    if executable is None:
        return False, "未找到 dsh（安装 DeepSeek Harness 后可用）"
    try:
        result = subprocess.run(
            [executable, "--version"], capture_output=True, text=True, check=False, timeout=60
        )
        version = (result.stdout + result.stderr).strip().splitlines()
        return True, f"{executable} ({version[0] if version else 'unknown'})"
    except OSError as exc:
        return False, f"无法执行 dsh：{exc}"


def command_doctor(args: argparse.Namespace) -> int:
    print("ds-psycoder 环境自检")
    print(f"  Python           : {sys.version.split()[0]} ({sys.executable})")
    available, detail = describe_dsh()
    print(f"  DeepSeek Harness : {'OK   ' + detail if available else '--   ' + detail}")
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    print("  DeepSeek API Key : " + ("OK   已设置 DEEPSEEK_API_KEY" if api_key else "--   未设置 DEEPSEEK_API_KEY（api 后端需要）"))
    print(f"  API Base URL     : {os.environ.get('DEEPSEEK_BASE_URL', DEFAULT_BASE_URL)}")
    print(f"  API Model        : {os.environ.get('DEEPSEEK_MODEL', DEFAULT_MODEL)}")
    destination = resolve_target(args)
    print(f"  Skill 目录       : {destination}")
    installed = [name for name in SKILL_NAMES if (destination / name / "SKILL.md").is_file()]
    print(f"  已安装 Skill     : {len(installed)}/{len(SKILL_NAMES)}")
    if len(installed) == len(SKILL_NAMES):
        drifted = [
            name
            for name, source in skill_sources().items()
            if directory_diff(source, destination / name)
        ]
        print("  漂移检查         : " + ("全部一致" if not drifted else "漂移：" + ", ".join(drifted)))
    else:
        missing = [name for name in SKILL_NAMES if name not in installed]
        print("  漂移检查         : 未安装完整套件，跳过")
        print(f"  缺失             : {', '.join(missing)}")
    return 0


# --------------------------------------------------------------------------- #
# dsh 后端
# --------------------------------------------------------------------------- #
def shell_argv(executable: str, arguments: Sequence[str]) -> list[str]:
    """Windows 下 .cmd/.bat 需要经 cmd.exe 启动。"""
    if os.name == "nt" and Path(executable).suffix.lower() in {".cmd", ".bat"}:
        return [os.environ.get("COMSPEC", "cmd.exe"), "/c", executable, *arguments]
    return [executable, *arguments]


def command_run_dsh(args: argparse.Namespace) -> int:
    executable = which_dsh()
    if executable is None:
        print("未找到 dsh。请安装 DeepSeek Harness，或改用 --backend api。", file=sys.stderr)
        return 2
    arguments = ["headless"]
    if args.session_id:
        arguments += ["--session-id", args.session_id]
    if args.json:
        arguments.append("--json")
    arguments.append(args.request)
    if args.dry_run:
        print(" ".join(shell_argv(executable, arguments)))
        return 0
    print("DeepSeek Harness (dsh headless) 正在处理请求 ...", file=sys.stderr)
    return subprocess.call(
        shell_argv(executable, arguments), cwd=str(Path(args.workdir).resolve())
    )


# --------------------------------------------------------------------------- #
# DeepSeek API 后端
# --------------------------------------------------------------------------- #
class DeepSeekError(RuntimeError):
    """DeepSeek API 调用失败。"""


class DeepSeekClient:
    """最小 DeepSeek Chat Completions 客户端（OpenAI 兼容）。"""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def chat(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"model": self.model, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:2000]
            raise DeepSeekError(f"DeepSeek API 返回 {exc.code}：{detail}") from exc
        except urllib.error.URLError as exc:
            raise DeepSeekError(f"无法连接 DeepSeek API：{exc.reason}") from exc
        choices = body.get("choices") or []
        if not choices:
            raise DeepSeekError(
                "DeepSeek API 响应缺少 choices：" + json.dumps(body, ensure_ascii=False)[:1000]
            )
        return choices[0].get("message", {})


TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取一个文本文件，返回带行号的内容。用于加载 skill 参考文档、配置或代码。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "绝对路径或相对工作目录的路径"},
                    "offset": {"type": "integer", "description": "起始行，1 起算"},
                    "limit": {"type": "integer", "description": "最多返回行数，默认 400"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "在工作目录内写入或整体覆盖一个 UTF-8 文本文件；请把交付物保存到磁盘。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "相对工作目录的文件路径"},
                    "content": {"type": "string", "description": "完整文件内容"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "列出目录中的文件与子目录。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "绝对路径或相对工作目录的路径，默认工作目录"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "在工作目录中运行一条校验命令（例如仓库自带的 scripts/validate_experiment.py）。仅当 --allow-commands 时可用。",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string", "description": "要执行的命令行"}},
                "required": ["command"],
            },
        },
    },
]


def resolve_path(raw: str, workdir: Path) -> Path:
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = workdir / candidate
    return candidate.resolve()


def clip(text: str, limit: int = MAX_TOOL_OUTPUT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n...（已截断，共 {len(text)} 字符）"


def execute_tool(
    name: str, arguments: dict[str, Any], workdir: Path, allow_commands: bool
) -> tuple[str, bool]:
    """执行一次工具调用，返回（输出文本，是否失败）。"""
    if name == "read_file":
        path = resolve_path(str(arguments.get("path", "")), workdir)
        if not path.is_file():
            return f"文件不存在：{path}", True
        offset = max(1, int(arguments.get("offset") or 1))
        limit = max(1, int(arguments.get("limit") or 400))
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            return f"读取失败：{exc}", True
        window = lines[offset - 1 : offset - 1 + limit]
        numbered = "\n".join(f"{offset + index:>5}: {line}" for index, line in enumerate(window))
        return (
            clip(f"{path}（共 {len(lines)} 行，显示 {offset}-{offset + len(window) - 1}）\n{numbered}"),
            False,
        )

    if name == "write_file":
        path = resolve_path(str(arguments.get("path", "")), workdir)
        try:
            path.relative_to(workdir)
        except ValueError:
            return f"拒绝写入工作目录之外：{path}", True
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(arguments.get("content", "")), encoding="utf-8")
        except OSError as exc:
            return f"写入失败：{exc}", True
        return f"已写入 {path}（{path.stat().st_size} 字节）", False

    if name == "list_dir":
        path = resolve_path(str(arguments.get("path") or "."), workdir)
        if not path.is_dir():
            return f"目录不存在：{path}", True
        entries = sorted(path.iterdir(), key=lambda item: (item.is_file(), item.name.lower()))
        listing = "\n".join(f"{'d' if entry.is_dir() else 'f'} {entry.name}" for entry in entries[:400])
        return clip(f"{path}\n{listing or '（空目录）'}"), False

    if name == "run_command":
        if not allow_commands:
            return "run_command 未启用：请用 --allow-commands 重新运行。", True
        command = str(arguments.get("command", ""))
        try:
            result = subprocess.run(
                command,
                cwd=str(workdir),
                shell=True,
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return f"命令执行失败：{exc}", True
        output = (result.stdout or "") + (result.stderr or "")
        return clip(f"退出码 {result.returncode}\n{output}"), result.returncode != 0

    return f"未知工具：{name}", True


def build_system_prompt(installed_dir: Path | None) -> str:
    """把总入口 skill 与运行时说明组装成 system prompt。"""
    entry = SKILL_SOURCE_ROOT / "SKILL.md"
    body = entry.read_text(encoding="utf-8") if entry.is_file() else "# DeepSeek PsyCoder\n"
    root = installed_dir if installed_dir is not None else SKILL_SOURCE_ROOT
    specialists = "\n".join(
        f"- {name}: {root / name / 'SKILL.md'}" for name in SPECIALIST_SKILLS
    )
    runtime = (
        "\n\n---\n\n"
        "## DeepSeek 运行时说明\n\n"
        "你正通过 ds-psycoder 的 DeepSeek API 后端运行，没有 Claude Code、Codex、\n"
        "Hermes 或 OpenClaw 宿主。请用下列工具自行完成工作：\n\n"
        "- read_file：读取下面的专业 skill、references/、methods/、paradigms/ 或用户数据；\n"
        "- write_file：把确认后的 config、条件表、生成代码与报告保存到工作目录；\n"
        "- list_dir：查看工作目录或 skill 目录；\n"
        "- run_command（若已启用）：运行仓库自带的 scripts/validate_*.py 校验。\n\n"
        "专业 skill 文件：\n"
        f"{specialists}\n\n"
        "规则：按总入口的路由规则先确认设计再生成代码；产物必须落盘并报告路径；\n"
        "不得把未执行的校验说成通过。\n"
    )
    return body + runtime


def command_run_api(args: argparse.Namespace) -> int:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key and not args.dry_run:
        print("缺少 DEEPSEEK_API_KEY。请先设置环境变量，或改用 --backend dsh。", file=sys.stderr)
        return 2
    workdir = Path(args.workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)

    installed_dir = resolve_target(args)
    installed = all((installed_dir / name / "SKILL.md").is_file() for name in SKILL_NAMES)
    model = args.model or os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL)
    base_url = args.base_url or os.environ.get("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL)

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": build_system_prompt(installed_dir if installed else None)},
        {"role": "user", "content": args.request},
    ]
    tools = [
        tool
        for tool in TOOL_SCHEMAS
        if tool["function"]["name"] != "run_command" or args.allow_commands
    ]

    if args.dry_run:
        print(
            json.dumps(
                {
                    "backend": "api",
                    "model": model,
                    "base_url": base_url,
                    "workdir": str(workdir),
                    "skills_dir": str(installed_dir if installed else SKILL_SOURCE_ROOT),
                    "tools": [tool["function"]["name"] for tool in tools],
                    "messages": messages,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    client = DeepSeekClient(api_key, base_url, model, args.timeout)
    print(f"DeepSeek ({model}) 正在处理请求 ...", file=sys.stderr)
    for step in range(1, max(1, args.max_steps) + 1):
        message = client.chat(messages, tools=tools)
        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            content = message.get("content") or ""
            print(content)
            if args.transcript:
                write_transcript(
                    Path(args.transcript), messages + [{"role": "assistant", "content": content}]
                )
            return 0
        messages.append(
            {
                "role": "assistant",
                "content": message.get("content") or "",
                "tool_calls": tool_calls,
            }
        )
        for call in tool_calls:
            function = call.get("function") or {}
            name = function.get("name", "")
            try:
                arguments = json.loads(function.get("arguments") or "{}")
            except json.JSONDecodeError:
                arguments = {}
            summary = ", ".join(f"{key}={value!r}"[:60] for key, value in arguments.items())
            print(f"  [{step}] {name}({summary})", file=sys.stderr)
            output, failed = execute_tool(name, arguments, workdir, args.allow_commands)
            if failed:
                print("       -> 失败", file=sys.stderr)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id", ""),
                    "name": name,
                    "content": output,
                }
            )
    print(f"已达到最大步数 {args.max_steps}，任务未收敛。", file=sys.stderr)
    if args.transcript:
        write_transcript(Path(args.transcript), messages)
    return 1


def write_transcript(path: Path, messages: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(list(messages), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"会话记录已保存：{path}", file=sys.stderr)


def command_run(args: argparse.Namespace) -> int:
    if args.backend == "dsh":
        return command_run_dsh(args)
    return command_run_api(args)


# --------------------------------------------------------------------------- #
# 命令行
# --------------------------------------------------------------------------- #
def add_target_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--scope",
        choices=("user", "project"),
        default="user",
        help="user=DSH_HOME/skills（默认）；project=<project>/.dsh/skills",
    )
    parser.add_argument("--project-dir", default=".", help="--scope project 时使用的项目目录")
    parser.add_argument("--target", help="直接指定 skill 安装目录（覆盖 scope 推导）")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ds-psycoder",
        description="DeepSeek 驱动的 PsyCoder 技能套件安装与运行入口。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  python ds_psycoder.py install\n"
            "  python ds_psycoder.py install --scope project --project-dir ./my-study\n"
            "  python ds_psycoder.py check\n"
            "  python ds_psycoder.py doctor\n"
            '  python ds_psycoder.py run "我要做一个 Stroop 任务"\n'
            '  python ds_psycoder.py run --backend api --workdir ./study "分析这份数据"\n'
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    install = subparsers.add_parser("install", help="安装 7 个 skill 到 DeepSeek Harness")
    add_target_arguments(install)
    install.add_argument("--check", action="store_true", help="只做漂移检查，不修改文件")
    install.add_argument("--skip-validation", action="store_true", help="跳过安装前的源校验")
    install.set_defaults(handler=command_install)

    check = subparsers.add_parser("check", help="检查已安装 skill 与工作区是否一致")
    add_target_arguments(check)
    check.set_defaults(handler=command_check)

    doctor = subparsers.add_parser("doctor", help="报告 DeepSeek 运行环境")
    add_target_arguments(doctor)
    doctor.set_defaults(handler=command_doctor)

    run = subparsers.add_parser("run", help="用 DeepSeek 执行一项研究任务")
    run.add_argument("request", help="任务描述")
    run.add_argument(
        "--backend",
        choices=("dsh", "api"),
        default="dsh",
        help="dsh=本机 DeepSeek Harness（默认）；api=DeepSeek Chat Completions",
    )
    run.add_argument("--workdir", default=".", help="工作目录；产物保存于此")
    run.add_argument("--model", help=f"覆盖模型，默认 DEEPSEEK_MODEL 或 {DEFAULT_MODEL}")
    run.add_argument("--base-url", help=f"覆盖 API 地址，默认 DEEPSEEK_BASE_URL 或 {DEFAULT_BASE_URL}")
    run.add_argument("--max-steps", type=int, default=DEFAULT_MAX_STEPS, help="api 后端的最大工具步数")
    run.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS, help="单次 API 请求超时秒数")
    run.add_argument("--allow-commands", action="store_true", help="允许 api 后端运行本地校验命令")
    run.add_argument("--session-id", help="dsh 后端：继续一个已存在的会话")
    run.add_argument("--json", action="store_true", help="dsh 后端：输出机器可读事件")
    run.add_argument("--transcript", help="api 后端：把完整会话写入该 JSON 文件")
    run.add_argument("--dry-run", action="store_true", help="只打印将要执行的内容，不访问网络")
    add_target_arguments(run)
    run.set_defaults(handler=command_run)
    return parser


def configure_console() -> None:
    """避免在非 UTF-8 的 Windows 控制台上因个别符号直接抛 UnicodeEncodeError。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def main(argv: Sequence[str] | None = None) -> int:
    configure_console()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except InstallError as exc:
        print(f"安装失败：{exc}", file=sys.stderr)
        return 1
    except DeepSeekError as exc:
        print(f"DeepSeek 调用失败：{exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("已中断。", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
