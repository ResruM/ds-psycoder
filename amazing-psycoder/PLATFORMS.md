# DeepSeek Runtime Adapter Reference

Amazing PsyCoder keeps discovery frontmatter portable by using only `name` and `description`, following the currently supported subset documented by [agentskills.io](https://agentskills.io). Re-check host documentation before publishing because discovery paths, invocation syntax, and optional fields can change.

This edition is **DeepSeek-only**. It runs in one of two DeepSeek runtimes:

1. **DeepSeek Harness (`dsh`)** — the local agent host. The skills are discovered from the DSH skill roots and the agent may use the full DSH tool chain.
2. **`ds-psycoder` CLI (`--backend api`)** — a self-contained runner that calls the DeepSeek OpenAI-compatible Chat Completions API and drives a minimal file-tool loop.

Claude Code, Codex, Hermes, and OpenClaw are **not** supported and **not** required: this repository contains no install path for any of them.

Runtime notes were last checked on **2026-10-14** against DeepSeek Harness 0.2.0-rc.2 and the DeepSeek OpenAI-compatible API at `https://api.deepseek.com`.

---

## agentskills.io Standard (Baseline)

All runtimes below implement this common specification. Key rules:

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | 1-64 chars, `a-z` `0-9` `-` only. Must match directory name. No leading/trailing/consecutive hyphens. |
| `description` | Yes | 1-1024 chars. Must include trigger keywords for agent auto-discovery. |
| `license` | No | Short license name (e.g., `MIT`). |
| `compatibility` | No | 1-500 chars. Environment requirements (system packages, network, intended product). |
| `metadata` | No | String-to-string key-value map. Extension point for platform-specific data. |

### Progressive Disclosure (3-stage loading)

1. **Discovery** (~100 tokens): Only `name` + `description` loaded at startup
2. **Activation** (<5000 tokens): Full `SKILL.md` body loaded when the skill matches the task
3. **Execution** (on demand): `scripts/`, `references/`, `assets/` loaded only when needed

**Best practice:** Keep `SKILL.md` under 500 lines. Move detailed reference material to `references/`.

---

## Supported Runtimes

### DeepSeek Harness (`dsh`)

| Item | Detail |
|------|--------|
| User skill root | `${DSH_HOME:-$HOME/.dsh}/skills` |
| Project skill root | `<project>/.dsh/skills` (project = nearest ancestor containing `.git`, otherwise the current directory) |
| Shared agents root (compatibility) | `~/.agents/skills` |
| Discovery unit | a top-level directory bundle containing `SKILL.md`, or a flat `<name>.md` file |
| Required frontmatter | `name`, `description` |
| Install (Linux/macOS/Git Bash) | `./install.sh deepseek` |
| Install (Windows PowerShell) | `powershell -ExecutionPolicy Bypass -File install.ps1` |
| Project install | `./install.sh --scope project --project-dir <path>` |
| Drift check | `./install.sh --check` |
| Invoke | describe the task in a `dsh web` or `dsh tui` session; DSH matches the skill by `description` |
| Headless | `dsh headless "<request>"` |
| Reload | the skill roots are watched, so added, renamed, or edited skills appear without restarting |

Nested `**/SKILL.md` files are deliberately **not** discovered. That is why the installer places all seven skills at the top level of the skills root instead of copying the suite as one tree.

### ds-psycoder CLI (DeepSeek API)

| Item | Detail |
|------|--------|
| Install | `python ds_psycoder.py install` |
| Environment | `DEEPSEEK_API_KEY` (required for the API backend), `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL` |
| Default endpoint | `https://api.deepseek.com/chat/completions` |
| Default model | `deepseek-chat` |
| Run | `python ds_psycoder.py run --backend api --workdir ./study "<request>"` |
| Tools | `read_file`, `write_file`, `list_dir`, and `run_command` (only with `--allow-commands`) |
| Session record | `--transcript transcript.json` |
| Dry run | `--dry-run` prints the composed request and tool list without touching the network |
| Environment check | `python ds_psycoder.py doctor` |

---

## Tool Mapping

When a sub-skill references an action, use the capability actually exposed by the current runtime. The names below are examples, not an API guarantee:

| Action | DeepSeek Harness (`dsh`) | ds-psycoder (`--backend api`) |
|--------|---------------------------|--------------------------------|
| Shell command | `pwsh` / `bash` | `run_command` (requires `--allow-commands`) |
| Read file | `read` | `read_file` |
| Write file | `write` | `write_file` |
| Edit file | `edit` | rewrites the file through `write_file` |
| Sub-agent | `subagent`, `subagent_fork` | not available (single tool loop) |
| Ask user | `ask_user_question` | not available |
| Web search | `web_search` | not available |
| Web fetch | `web_fetch` | not available |

---

## Quick Install (Recommended)

```bash
git clone https://github.com/ResruM/ds-psycoder
cd ds-psycoder/amazing-psycoder
./install.sh                  # DeepSeek Harness, user scope
./install.sh deepseek         # same, runtime named explicitly
./install.sh --scope project --project-dir /path/to/study
./install.sh --check          # drift check only, no file changes
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
powershell -ExecutionPolicy Bypass -File install.ps1 -Check
```

Both wrappers delegate to `ds_psycoder.py`, so the same operations are available on any platform with Python 3.8 or newer:

```bash
python ds_psycoder.py install
python ds_psycoder.py check
python ds_psycoder.py doctor
```

## Manual Installation

Pass an absolute skills directory when the runtime uses a custom location:

```bash
./install.sh --target /absolute/path/to/skills
python ds_psycoder.py check --target /absolute/path/to/skills
```

The installer validates all seven manifests, stages the complete batch, and rolls the whole installation back if any replacement fails. Avoid copying only one sub-skill: the pipeline depends on sibling references and handoff contracts.

---

## Validation Scope and Evidence

Installation compatibility and generated-project runtime compatibility are different claims:

| Layer | Automated evidence in this repository | Still required on the target system |
|---|---|---|
| DeepSeek Harness / ds-psycoder installation | Temporary-directory install, rollback, drift, and path tests for the DeepSeek roots | Runtime discovery, invocation, reload behaviour, tool mapping, and one routed experiment/analysis smoke test |
| PsychoPy | Python parse plus experiment static-contract checks | PsychoPy dependency install, display/input launch, timing and device smoke tests |
| jsPsych 8.x | Node.js syntax plus experiment static-contract checks | Supported browser deployment, persistence, timing and device tests |
| Psychtoolbox | MATLAB-oriented static-contract checks | MATLAB/Octave `checkcode`, Psychtoolbox sync tests, display/input/audio calibration |
| Python analysis | Python AST/static-contract checks plus a clean paired-analysis fixture whose run/input/output/environment hashes are verified | Clean execution against the user's real schema/data, diagnostics and result review |
| R analysis | R static/parse checks plus a `renv`-restored paired-analysis fixture whose run/input/output/environment hashes are verified | Clean execution against the user's real schema/data, diagnostics and result review |

The installer uses the standard-library-only portable preflight, so installing the skills does not require Studio services or contributor test dependencies. Before an analysis Designer/Coder/Reviewer runs `validate_analysis.py`, use an isolated interpreter with the packaged validation dependencies; do not assume the host's default `python3` has PyYAML:

```bash
AMAZING_PSYCODER_ROOT="/absolute/path/to/amazing-psycoder"
python -m venv .venv-validation
. .venv-validation/bin/activate
python -m pip install -r "$AMAZING_PSYCODER_ROOT/requirements-dev.txt"
python -c "import yaml"
```

Release and contributor validation remains strict:

```bash
python amazing-psycoder/scripts/validate_skills.py
python -m unittest discover -s amazing-psycoder/tests -v
```

Static success is a gate to runtime testing. It is never evidence by itself for `ready_for_collection` or `ready_for_publication`.

---

## Runtime-Specific Caveats

| Runtime | Caveat |
|---------|--------|
| **DeepSeek Harness** | Skill roots are scanned at the top level only, and `name` must equal the directory name. Confirm the installed `dsh` version before relying on headless flags such as `--session-id` or `--json`. |
| **ds-psycoder (`--backend api`)** | The API backend exposes no sub-agent, web, or user-question tools. It saves artifacts with `write_file` and can only run local validators when `--allow-commands` is set. Long tasks are bounded by `--max-steps`. |

---

## Adding a New Runtime

1. Add a section to Supported Runtimes above with directory paths, install commands, and invocation methods
2. Add tool mappings to the Tool Mapping table
3. Add an `agents/<runtime>.yaml` manifest to every skill when the runtime needs UI metadata; the validator currently accepts the `host: deepseek` shape used by `agents/deepseek.yaml`
4. Document any runtime-specific frontmatter extensions or caveats
5. Update all `README.md` installation sections
6. If the runtime has a registry, publish the skill there
