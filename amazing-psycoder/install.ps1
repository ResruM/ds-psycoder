# DeepSeek PsyCoder (ds-psycoder) — Windows 安装器包装脚本。
#
# 真正的安装 / 漂移检查逻辑在仓库根目录的 ds_psycoder.py 中实现：它跨平台、
# 只依赖 Python 标准库，并把 7 个 skill 安装到 DeepSeek Harness 的 skill 根目录。
# 本脚本只负责参数转写和查找可用的 Python 解释器，不再支持 Claude Code、
# Codex、Hermes 或 OpenClaw。
#
# 用法:
#   powershell -ExecutionPolicy Bypass -File install.ps1
#   powershell -ExecutionPolicy Bypass -File install.ps1 -Check
#   powershell -ExecutionPolicy Bypass -File install.ps1 -Scope project -ProjectDir .\my-study
#   powershell -ExecutionPolicy Bypass -File install.ps1 -Target "$env:USERPROFILE\.dsh\skills"

[CmdletBinding()]
param(
    [Parameter(Position = 0)][string]$Platform,
    [switch]$Check,
    [ValidateSet('user', 'project')][string]$Scope = 'user',
    [string]$ProjectDir = (Get-Location).Path,
    [string]$Target,
    [string]$PythonBin = $env:PYTHON_BIN,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

function Show-Usage {
    Write-Host @'
用法:
  install.ps1 [deepseek] [-Check] [-Scope user|project] [-ProjectDir PATH] [-Target PATH]

说明:
  默认安装到 DeepSeek Harness 的用户级 skill 根目录 %DSH_HOME%\skills
  （DSH_HOME 未设置时为 %USERPROFILE%\.dsh\skills）。
  -Scope project 时安装到 <ProjectDir>\.dsh\skills。

示例:
  install.ps1
  install.ps1 -Check
  install.ps1 -Scope project -ProjectDir .\my-study
  install.ps1 -Target "$env:USERPROFILE\.dsh\skills"
'@
}

if ($Help) { Show-Usage; exit 0 }

if ($Platform -and $Platform -notin @('deepseek', 'dsh')) {
    if (Test-Path -LiteralPath $Platform) {
        if ($Target) { Write-Error '-Target 与位置参数不能同时使用'; exit 1 }
        $Target = (Resolve-Path -LiteralPath $Platform).Path
    }
    else {
        Write-Error "未知平台: $Platform（本仓库只支持 DeepSeek Harness: deepseek / dsh，或传入已有安装目录的绝对路径）"
        exit 1
    }
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$cli = Join-Path $repoRoot 'ds_psycoder.py'
if (-not (Test-Path -LiteralPath $cli)) {
    $cli = Join-Path $scriptDir 'ds_psycoder.py'
}
if (-not (Test-Path -LiteralPath $cli)) {
    Write-Error '未找到 ds_psycoder.py；请在仓库 checkout 中运行本脚本。'
    exit 1
}

function Resolve-Python {
    if ($PythonBin) {
        $command = Get-Command $PythonBin -ErrorAction SilentlyContinue
        if ($command) { return $command.Source }
    }
    foreach ($name in @('python', 'python3', 'py')) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) { return $command.Source }
    }
    return $null
}

$python = Resolve-Python
if (-not $python) {
    Write-Error '未找到 Python 解释器。请安装 Python 3.8+，或用 -PythonBin 指定路径。'
    exit 1
}

$arguments = @($cli, 'install', '--scope', $Scope, '--project-dir', $ProjectDir)
if ($Target) { $arguments += @('--target', $Target) }
if ($Check) { $arguments += '--check' }

& $python @arguments
exit $LASTEXITCODE
