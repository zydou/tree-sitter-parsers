# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A centralized build farm that compiles [tree-sitter](https://tree-sitter.github.io) language parsers from 326 upstream repositories into prebuilt `.so` shared objects, pinned at reproducible commits.
Output lands in `dist/<lang>.so`.
Target ABI is **14** (Neovim v0.10.x compatible).

The only first-party code is `build.py`, `lock.json`, and `.github/workflows/build.yaml`.
Every other top-level directory (`ada/`, `rust/`, `typescript/`, …) is an extracted upstream tree-sitter grammar sourced from its `source` URL — treat them as read-only build inputs,
not project source.

## Build Commands

```bash
# Full build (all 326 parsers). JOBS caps at min(cpu_count, 16).
JOBS=16 python3 build.py

# Smoke test — build only the first N parsers.
JOBS=8 python3 build.py --limit 10

# Build specific langs by name (matches lock.json keys).
python3 build.py rust cpp zig

# List what would be built, with pinned revision + upstream repo.
python3 build.py --list-only
```

Required on `PATH` or at the hardcoded location:

- `tree-sitter` CLI **v0.24.7** at `~/.local/bin/tree-sitter`
- `nvim` at `~/.local/neovim/bin/nvim` (used for verify step)
- a C compiler (`cc`) and C++ compiler (`g++`/`cc`)
- `curl` (downloads tarballs)
- `$GITHUB_TOKEN` — strongly recommended to avoid GitHub rate limits

Skipping logic: `dist/<lang>.so` that already exists is skipped (status `SKIP`).
On full success the temp workdir is removed; on any failure the per-lang logs under the temp dir are preserved and printed.

## Architecture

`build.py` is a single-file parallel build pipeline.
Per parser (`compile_one`):

1. **Skip** if `dist/<lang>.so` exists.
2. **Fetch** — if `<lang>/` dir is absent, download `source` tarball from `lock.json`
   (GitHub `archive/{commit}.tar.gz` or GitLab `/-/archive/...`) and extract with `--strip-components=1` into `<lang>/`.
3. **Locate** — `build_dir = <lang>/<location>` when `lock.json` has a non-empty `location` (monorepo grammars like `csv`, `dtd`, `ebnf`, `fsharp`), else `<lang>/` itself.
4. **Generate** — inspect `src/parser.c` for `#define LANGUAGE_VERSION`.
   If it's missing or not `13`/`14`, run `tree-sitter generate --abi 14` (upstream prebuilt ABI 15+ must be regenerated for nvim 0.10).
5. **Build** — `tree-sitter build -o dist/<lang>.so .`.
   Falls back to an explicit `cc`/`g++` invocation (handling `scanner.cc` link issues) if that fails.
6. **Verify** — `file` checks it's a shared object, then a headless nvim loads the `.so` via `vim.treesitter.language.add` and parses a one-line buffer (`PARSE_OK`).
   Each nvim runs with an isolated `-i <tmp>` shada file to avoid E138 contention under parallelism.

### lock.json schema

Top-level `{ "description", "parsers": { <lang>: { owner, repo, host, commit, location, url, source } } }`.
`commit` is the pinned revision, `source` is the resolvable tarball URL, `location` is the optional subdirectory within the extracted archive.
`get_parsers()` normalizes this to `{ lang: { revision, url, location } }`.

### CI

`.github/workflows/build.yaml` runs on push to `main`: it fethes the pinned `tree-sitter` CLI + Neovim v0.10.4 releases, runs `python3 build.py`,
then uploads every `dist/*.so` to the `parsers` GitHub release (create-or-edit + clobber upload).
