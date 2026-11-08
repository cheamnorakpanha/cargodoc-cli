# CargoDoc

An interactive terminal tool for preparing folders for freelance taxation work.
It combines the export (`RE-001-2026`) and import (`IMP-001`) folder workflows
in one persistent prompt. Runs locally; no account or AI service is required.

## Install on Windows

Requires Python 3.10 or newer. From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\cargodoc.exe
```

To use the short `cargodoc` command in the current terminal, activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
cargodoc
```

If PowerShell blocks activation, use the executable path above. Activation is
optional. For a command available from any directory and new terminals, install
with [pipx](https://pipx.pypa.io/stable/installation/):

```powershell
pipx install .
pipx ensurepath
```

Open a new terminal after updating PATH, navigate to your intended destination,
then run `cargodoc`. To update an existing pipx installation after code changes,
run `pipx install --force .` from this repository.

## Interactive mode

```text
cargodoc > /export
Starting number: 001
Ending number:   010
Year:            2026
```

The tool previews the destination, first and last folder names, and requested
count, then asks before creating folders. The year defaults to the current year.
After each task it returns to the prompt.

The workspace uses a cyan-to-violet pixel wordmark with layered shadows, mint
success states, and slate borders. A destination panel sits above three task
cards for outbound, inbound, and workspace actions. The banner scales down in
smaller windows and uses plain text in terminals without block character support.
At widths below 88 columns, the cards become a compact command list. The
command area includes completion and shortcut hints. `/clear` redraws the
workspace with the latest task from this session. Colors respect your terminal's
background; redirected output stays readable without color.

| Command | Action |
| --- | --- |
| `/export` | Create `RE-NUMBER-YEAR` folders |
| `/import` | Create `IMP-NUMBER` folders |
| `/directory` | Choose an existing destination directory for this session |
| `/help` | Show available commands |
| `/clear` | Redraw the welcome screen and latest session activity |
| `/exit` | Quit |

Tab completes commands; Up/Down recalls commands from this session. Ctrl+C
cancels the current prompt; Ctrl+D exits. Command history stays in memory.
The starting number determines zero padding: `001` produces three-digit names.

## Direct commands

Direct commands execute immediately, making them suitable for scripts. Use
`--dry-run` to preview without creating anything:

```powershell
cargodoc export --start 001 --end 010 --year 2026 --dry-run
cargodoc export --start 001 --end 010 --year 2026
cargodoc import --start 001 --end 020 --directory "D:\Clients\November"
cargodoc --help
cargodoc export --help
```

The destination defaults to the current working directory and must already
exist. Ranges are inclusive, contain digits only, and allow at most 100,000
folders per task. Existing directories are skipped; files with the same names
are reported as failures. The summary counts created, existing, and failed
folders separately. Interrupted runs may leave folders already created;
rerunning skips them.

Exit codes: `0` success (including skipped directories and previews), `1` folder
creation failures, `2` invalid arguments or destination, `130` interrupted direct
command. Interactive mode requires a terminal; direct commands also work when
output is redirected.

## Development

```powershell
python -m unittest discover -s tests -v
python -m cargodoc --help
```

The package uses `prompt_toolkit` for input and completion, Rich for output,
and shared folder operations in `cargodoc/folders.py`.

## Original standalone executables

The original scripts and PyInstaller specs remain in `EXP` and `IMP`. They run
independently of CargoDoc, and the original export script still uses its fixed
2026 suffix. To rebuild them with PyInstaller installed:

```powershell
cd EXP
pyinstaller export.spec
cd ..\IMP
pyinstaller import.spec
```

Outputs are `EXP\dist\export.exe` and `IMP\dist\import.exe`.
