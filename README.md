# Tooools-cli

Single-entry CLI over the upstream `Tooools/file_process_tools` backend. Same logic — exposed as `tools <group> <action>` subcommands plus the legacy `-X` flags used by the existing zsh aliases.

## Layout

```
Tooools-cli/
├── tools                # bash wrapper → activates venv and runs tools.py
├── tools.py             # dispatcher: subcommands + legacy short flags
├── venv/                # local Python venv with required deps
└── toolscli/
    ├── upstream.py      # injects upstream backend onto sys.path
    ├── result.py        # uniform printing of backend api dicts
    └── commands/
        ├── name.py      # filename ops (extract-numbers, delete, prefix, suffix, revert, rename)
        ├── folder.py    # flatten / organize / encode / decode / iso
        ├── combine.py   # merge pdf|txt, epub→txt
        ├── pdf.py       # encode / decode / trim / repair / to-txt / to-image
        └── image.py     # to-pdf / compress
```

The backend lives at `/Users/doudouda/Downloads/Personal_doc/Study/Proj/Tooools/file_process_tools/backend`; this CLI imports its `modules/*.py` directly rather than copying code, so upstream fixes propagate automatically.

## Usage

```bash
# Subcommand style (preferred)
tools name extract-numbers
tools name delete "删"
tools name suffix _bak --dry-run
tools name rename folders

tools folder flatten
tools folder organize
tools folder encode --password 1111
tools folder iso

tools combine pdf --name merged
tools combine txt
tools combine epub

tools pdf encode --password 1234
tools pdf decode --password 1234
tools pdf trim --where f --num-pages 1
tools pdf trim --pages 1,3,5-7
tools pdf to-txt
tools pdf to-image --format jpg --dpi 200

tools image to-pdf --name combined
tools image compress
```

```bash
# Legacy short flags (used by existing zsh aliases tn / tf / tcp / ...)
tools -N                 # extract numeric sequence in filenames
tools -F                 # flatten subdirectories
tools -C p|t|e           # combine pdf | txt | epub→txt
tools -D PATTERN         # delete pattern from filenames
tools -V                 # revert last rename op
tools -B SUFFIX [--dry-run]
tools -A PREFIX
tools -R files|folders|both
tools -FO                # organize files by group
tools --encode-pdf PWD
tools --decode-pdf [PWD]
tools --encode-folder [--password PWD]
tools --decode-folder
```

All commands operate on `--dir` (default: cwd) and write to `--output-dir` (default: same as `--dir`).

## zsh aliases (already wired in `~/.zshrc`)

| alias | maps to |
|---|---|
| `tools` | this CLI |
| `tn` / `tf` / `tcp` / `tct` / `tce` / `td` / `tv` / `tb` | filename + flatten + combine + delete + revert + suffix |
| `tde` / `ten` | PDF decrypt / encrypt |
| `rfolder` / `rfile` | rename folders / files |
| `FO` | `tools -FO && rfolder` (organize then rename folders) |
| `tds` / `tdw` | derived from `td` (delete `删` / `我`) |
| `tt` / `tp` | commented out — original meaning lost |

`enfolder` / `defolder` keep pointing at their proven shell scripts, but the same operation is also available via `tools --encode-folder` / `--decode-folder` (or `tools folder encode` / `folder decode`).

## Dependencies

Installed in `./venv`: `tqdm pypinyin pikepdf ebooklib beautifulsoup4 PyMuPDF py7zr`.
