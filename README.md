# tree-sitter-parsers

Build farm for 326 [tree-sitter](https://tree-sitter.github.io) language parsers, compiled from pinned upstream sources into prebuilt `.so` shared objects for **Neovim v0.10.x** (ABI 14).

## Output

Every language in [`lock.json`](lock.json) becomes `dist/<lang>.so`.
The lockfile pins each grammar to a specific commit and tarball URL for reproducible builds.

## Build

Dependencies:

- `tree-sitter` CLI **v0.24.7** (`~/.local/bin/tree-sitter`)
- Neovim (`~/.local/neovim/bin/nvim`, used to verify each parser)
- `cc` and a C++ compiler
- `curl`
- `GITHUB_TOKEN` set in the environment (avoids GitHub rate limits)

```bash
# Build all parsers (parallel, JOBS = min(CPUs, 16))
JOBS=16 python3 build.py

# Build just a few
python3 build.py rust cpp zig

# Dry run / list what would build
python3 build.py --list-only

# Limit to first N (quick smoke test)
JOBS=8 python3 build.py --limit 10
```

Already-built `dist/<lang>.so` files are skipped on re-run.
Grammars whose upstream ships a prebuilt `parser.c` targeting ABI 15+ are regenerated with `tree-sitter generate --abi 14`.

## Layout

- **`build.py`** — the build pipeline (fetch → generate → build → verify).
  See its header comment for the algorithm.
- **`lock.json`** — 326 pinned parser sources (`owner/repo/commit/location/url/source`).
- **`dist/`** — compiled `.so` outputs.
- **`<lang>/`** directories — extracted upstream grammar sources (read-only build inputs, re-downloaded if missing).
- **`.github/workflows/build.yaml`** — CI that builds on push to `main` and uploads `dist/*` to the `parsers` release.
