#!/usr/bin/env bash
set -euo pipefail

# DeepSeek PsyCoder (ds-psycoder) — 安装器包装脚本。
#
# 真正的安装 / 漂移检查逻辑在仓库根目录的 ds_psycoder.py 中实现：它跨平台、
# 只依赖 Python 标准库，并把 7 个 skill 安装到 DeepSeek Harness 的 skill 根目录。
# 本脚本只负责参数转写和查找可用的 Python 解释器，不再支持 Claude Code、
# Codex、Hermes 或 OpenClaw。

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
    cat <<EOF
用法:
  ./install.sh [--check] [--scope user|project] [--project-dir PATH] [deepseek]
  ./install.sh [--check] --target /absolute/path/to/skills

说明:
  默认安装到 DeepSeek Harness 的用户级 skill 根目录 ${DSH_HOME:-~/.dsh}/skills
  （DSH_HOME 未设置时为 ~/.dsh/skills）。
  --scope project 时安装到 <project>/.dsh/skills。

示例:
  ./install.sh                              # 用户级安装
  ./install.sh deepseek                     # 同上，显式指定平台
  ./install.sh --scope project --project-dir /path/to/study
  ./install.sh --check                      # 只检查漂移，不修改文件
  ./install.sh --target ~/.dsh/skills       # 自定义安装目录

环境变量:
  DSH_HOME      DeepSeek Harness 配置根目录（默认 ~/.dsh）
  PYTHON_BIN    指定 Python 解释器
EOF
}

find_cli() {
    local candidate
    for candidate in "$REPO_ROOT/ds_psycoder.py" "${SCRIPT_DIR}/ds_psycoder.py"; do
        if [[ -f "$candidate" ]]; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

# 逐个候选解释器实际执行一次版本探测：Windows 上 python3 可能只是应用商店占位符。
find_python() {
    local candidate
    for candidate in "${PYTHON_BIN:-}" python3 python py; do
        [[ -n "$candidate" ]] || continue
        command -v "$candidate" >/dev/null 2>&1 || continue
        if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

CHECK=0
SCOPE="user"
PROJECT_DIR="$(pwd)"
TARGET=""
PLATFORM=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --check) CHECK=1; shift ;;
        --scope)
            [[ $# -ge 2 ]] || { echo "--scope 需要 user 或 project"; exit 1; }
            SCOPE="$2"; shift 2 ;;
        --project-dir)
            [[ $# -ge 2 ]] || { echo "--project-dir 需要路径"; exit 1; }
            PROJECT_DIR="$2"; shift 2 ;;
        --target)
            [[ $# -ge 2 ]] || { echo "--target 需要路径"; exit 1; }
            TARGET="$2"; shift 2 ;;
        --help|-h) usage; exit 0 ;;
        --*)
            echo "未知参数: $1"; usage; exit 1 ;;
        *)
            [[ -z "$PLATFORM" ]] || { echo "只能指定一个平台或安装路径"; exit 1; }
            PLATFORM="$1"; shift ;;
    esac
done

if [[ "$SCOPE" != "user" && "$SCOPE" != "project" ]]; then
    echo "未知 scope: $SCOPE（仅支持 user 或 project）"
    exit 1
fi

if [[ -n "$TARGET" && -n "$PLATFORM" ]]; then
    echo "--target 与位置参数不能同时使用"
    exit 1
fi

if [[ -n "$PLATFORM" && "$PLATFORM" != "deepseek" && "$PLATFORM" != "dsh" ]]; then
    case "$PLATFORM" in
        /*|[A-Za-z]:[/\]*) TARGET="$PLATFORM" ;;
        *)
            echo "未知平台: $PLATFORM"
            echo "本仓库只支持 DeepSeek Harness (deepseek / dsh)，或直接传入安装目录的绝对路径。"
            exit 1
            ;;
    esac
fi

CLI="$(find_cli)" || {
    echo "未找到 ds_psycoder.py；请在仓库 checkout 中运行本脚本。"
    exit 1
}

PYTHON="$(find_python)" || {
    echo "未找到 Python 解释器。请安装 Python 3.8+，或用 PYTHON_BIN 指定路径。"
    exit 1
}

ARGS=(install --scope "$SCOPE" --project-dir "$PROJECT_DIR")
[[ -n "$TARGET" ]] && ARGS+=(--target "$TARGET")
[[ "$CHECK" == "1" ]] && ARGS+=(--check)

exec "$PYTHON" "$CLI" "${ARGS[@]}"
