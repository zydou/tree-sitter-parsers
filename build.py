#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build.py — 并行编译 treesitter parsers (.so).

依赖:
  - tree-sitter CLI v0.24.7  (ABI 14, nvim v0.10.x 兼容)
  - curl
  - neovim
  - gcc / g++ / cc
  - $GITHUB_TOKEN 环境变量 (绕过 rate limit)

用法:
  JOBS=16 python3 build.py                 # 全量编译
  JOBS=8  python3 build.py --limit 10      # 测试: 只跑前 10 个
  JOBS=8  python3 build.py --list-only     # 列出所有 parser

产物:
  ./dist/<lang>.so
"""

# ruff: noqa: RUF002,RUF003,S603,BLE001,PLR0911, PLR0912,PLR0915,PLW1510
import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Literal

# ----- 配置 ---------------------------------------------------------------
TARGET = str(Path(__file__).parent / "dist")
CLI = str(Path.home() / ".local/bin/tree-sitter")  # tree-sitter CLI v0.24.7
NVIM = str(Path.home() / ".local/neovim/bin/nvim")
CXX = shutil.which("g++") or shutil.which("cc") or ""
CC = shutil.which("cc") or ""
ABI_VERSION = 14
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
JOBS = min(os.cpu_count() or 1, 16)  # 默认等于CPU个数，最多 16 个并发
LOCKFILE = str(Path(__file__).parent / "lock.json")
WORKDIR = Path(tempfile.mkdtemp(prefix="ntbuild-"))


# ----- 主流程 -------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="Build treesitter parsers (tree-sitter v0.24.7)")
    p.add_argument("--jobs", type=int, default=JOBS)
    p.add_argument("--limit", type=int, default=0, help="只处理前 N 个")
    p.add_argument("--list-only", action="store_true", help="只列出 parser")
    p.add_argument("langs", nargs="*", help="只编译指定语言 (可多个, 空格分隔)")
    args = p.parse_args()

    # 0. 工具链检查
    tools = "=== 工具链检查 ==="
    tools += f"\n  CLI             : {tool_version(CLI)}"
    tools += f"\n  Neovim          : {tool_version(NVIM, allow_missing=True)}"
    tools += f"\n  CXX compiler    : {tool_version(CXX)}"
    tools += f"\n  C compiler      : {tool_version(CC)}"
    tools += f"\n  $GITHUB_TOKEN   : {'已设' if GITHUB_TOKEN else '未设'}"
    tools += f"\n  ABI 版本        : {ABI_VERSION}"
    tools += f"\n  并发数          : {args.jobs}"
    print(tools)
    if "缺失" in tools:
        print("  [ERROR] 缺失必要的工具链")
        return

    # 1. 清单
    print("\n=== 获取 parser 清单 ===")
    logdir = WORKDIR / "log"
    logdir.mkdir(parents=True, exist_ok=True)

    parsers = get_parsers(LOCKFILE)
    print(f"  共 {len(parsers)} 个 parser")
    if args.langs:
        # 过滤指定语言
        specified = set(args.langs)
        parsers = {lang: meta for lang, meta in parsers.items() if lang in specified}
        missing = specified - set(parsers.keys())
        if missing:
            print(f"  [WARN] 未找到: {', '.join(sorted(missing))}")
        print(f"  指定语言: {len(parsers)} 个")
    if args.limit > 0:
        parsers = dict(list(parsers.items())[: args.limit])
        print(f"  --limit {args.limit}: 只处理前 {len(parsers)} 个")

    if args.list_only:
        print()
        for lang, meta in sorted(parsers.items()):
            repo = meta["url"].split("/")[-1]
            print(f"  {lang:20} {meta['revision'][:12]} {repo}")
        return

    # 2. 并行编译
    (WORKDIR / "archive").mkdir(parents=True, exist_ok=True)
    print(f"\n=== 启动并行编译 ({args.jobs} 并发) ===")
    print(f"  输出目录: {TARGET}")
    print(f"  工作目录: {WORKDIR}")
    Path(TARGET).mkdir(parents=True, exist_ok=True)

    start = time.time()
    results = []
    marks = {"OK": "✅", "FAIL": "❌", "SKIP": "🟡"}

    with ThreadPoolExecutor(max_workers=args.jobs) as exe:
        futures = {exe.submit(compile_one, lang, meta, logdir): lang for lang, meta in parsers.items()}
        for fut in as_completed(futures):
            lang = futures[fut]
            try:
                result = fut.result()
                results.append(result)
                mark = marks[result[1]]
                print(f"  {mark} {lang:20} {result[1]:4} {result[2]}")
            except Exception as e:
                results.append((lang, "FAIL", str(e)))
                print(f"  {marks['FAIL']} {lang:16} FAIL {e}")

    # 3. 汇总
    elapsed = int(time.time() - start)
    ok_list = [r for r in results if r[1] == "OK"]
    skip_list = [r for r in results if r[1] == "SKIP"]
    fail_list = [r for r in results if r[1] not in ("OK", "SKIP")]

    print(f"\n=== 完成 ({elapsed}s) ===")
    print(f"  {marks['OK']}成功: {len(ok_list)}")
    print(f"  {marks['FAIL']}失败: {len(fail_list)}")
    print(f"  {marks['SKIP']}跳过: {len(skip_list)}")

    if fail_list:
        print("\n--- 失败列表 ---")
        for lang, status, detail in sorted(fail_list, key=lambda x: x[2]):
            print(f"  {lang:16} {status}: {detail}")

    # 清理中间产物
    if len(fail_list) == 0:
        rmrf(WORKDIR)
    else:
        print(f"  编译日志: {logdir}/")


# ----- 工具函数 -----------------------------------------------------------
def tool_version(bin_path: str, *, allow_missing: bool = False) -> str:
    if Path(bin_path).is_file():
        v = subprocess.run([bin_path, "--version"], capture_output=True, text=True)
        return f"{v.stdout.split(chr(10))[0].strip()}"
    if allow_missing:
        return "🟡跳过"
    return "❌缺失"


def download(url: str, dest: Path) -> bool:
    """Curl 下载, 带 github token auth + 重试."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["curl", "-sL", "--retry", "3", "--retry-delay", "2"]
    if GITHUB_TOKEN:
        cmd += ["-H", f"Authorization: token {GITHUB_TOKEN}"]
    cmd += ["-o", str(dest), url]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=90)
        return r.returncode == 0 and dest.stat().st_size > 100
    except Exception:
        return False


def compile_one(lang: str, meta: dict[str, str], logdir: Path) -> tuple[str, Literal["OK", "FAIL", "SKIP"], str]:
    """编译 + 验证 单个 parser（已存在 .so 则跳过）.

    设计: 把提交的 <lang>/ 当作只读 pristine 存档, 绝不修改.
    所有 generate / build 都在临时工作目录 (WORKDIR/<lang>/) 里进行,
    这样离线机 clone 仓库后源码保持原始存档不变.

    Returns:
        (str, str, str): (lang, status, note)
    """
    Path(logdir).mkdir(parents=True, exist_ok=True)
    out_so = Path(TARGET) / f"{lang}.so"
    if out_so.exists():
        return (lang, "SKIP", f"exists {out_so.stat().st_size // 1024}K")

    revision = meta["revision"]
    url = meta["url"]
    location = meta.get("location", "")
    logfile = logdir / f"{lang}.log"
    srcdir = Path(__file__).parent / lang  # 只读 pristine 存档
    workdir = WORKDIR / lang  # 临时工作目录(可任意修改)
    build_dir = workdir / location if location else workdir
    archive_file = WORKDIR / "archive" / f"{lang}.tar.gz"

    def log(msg):
        with logfile.open("a") as f:
            f.write(msg + "\n")

    # --- 准备工作目录: 优先从已提交的 pristine 存档复制, 否则在线下载 ---
    if srcdir.is_dir():
        # 离线/已提交: 复制只读存档到工作目录 (不修改原存档)
        log(f"copy pristine src {srcdir} -> {workdir}")
        shutil.copytree(srcdir, workdir)
    else:
        # 在线懒加载 (源码未提交时): 直接下载解压到工作目录
        workdir.mkdir(parents=True, exist_ok=True)
        archive_file.parent.mkdir(parents=True, exist_ok=True)
        # Gitlab archive name strips the ".git" suffix: repo-<rev>.tar.gz (NOT repo.git-<rev>.tar.gz)
        repo_name = url.split("/")[-1]
        archive_url = f"{url.removesuffix('.git')}/-/archive/{revision}/{repo_name.removesuffix('.git')}-{revision}.tar.gz" if "gitlab.com" in url else f"{url}/archive/{revision}.tar.gz"
        log(f"download: {archive_url}")
        ok = download(archive_url, archive_file)
        if not ok:
            return (lang, "FAIL", "download")
        if "gzip" not in subprocess.run(["/usr/bin/file", str(archive_file)], capture_output=True, text=True).stdout:
            return (lang, "FAIL", "not-gzip")
        log(f"extract to {workdir}")
        r = subprocess.run(["/usr/bin/tar", "xzf", str(archive_file), "-C", str(workdir), "--strip-components=1"], capture_output=True, text=True)
        if r.returncode != 0:
            log(f"extract err: {r.stderr}")
            return (lang, "FAIL", f"extract rc={r.returncode}")

    if not build_dir.is_dir():
        return (lang, "FAIL", f"no-dir {build_dir}")

    # 4. generate
    # ABI 13 和 14 都能在 nvim 0.10.4 加载,其他 ABI (如 15) 必须 regenerate
    need_gen = False
    parser_c = build_dir / "src" / "parser.c"
    if not parser_c.exists():
        need_gen = True
    else:
        content = parser_c.read_text(errors="replace")
        m = re.search(r"#define LANGUAGE_VERSION\s+(\d+)", content)
        abi_val = int(m.group(1)) if m else 0
        if abi_val not in (13, 14):
            need_gen = True
            log(f"prebuilt ABI={abi_val} not in (13,14), regenerate")
            print(f"[{lang}] prebuilt ABI={abi_val} not in (13,14), regenerate")
    if need_gen:
        log(f"tree-sitter generate --abi {ABI_VERSION}")
        print(f"[{lang}] tree-sitter generate --abi {ABI_VERSION}")
        rmrf(parser_c)
        r = subprocess.run([CLI, "generate", "--abi", str(ABI_VERSION)], cwd=build_dir, capture_output=True, text=True, timeout=600)
        log(r.stdout + r.stderr)
        if r.returncode != 0:
            return (lang, "FAIL", f"generate rc={r.returncode}")

    # 5. tree-sitter build (自动链接 parser.c + scanner.cc)
    out_so.unlink(missing_ok=True)
    log("tree-sitter build ...")
    r = subprocess.run([CLI, "build", "-o", str(out_so), "."], cwd=build_dir, capture_output=True, text=True, timeout=600)
    log(r.stdout + r.stderr)
    if r.returncode != 0 or not out_so.exists():
        # 备选: 手动 cc (可能 external scanner 有 g++ 链接问题)
        log("build failed, try manual cc")
        src_files = []
        pd = build_dir / "src"
        if (pd / "parser.c").exists():
            src_files.append(pd / "parser.c")
        if (pd / "scanner.c").exists():
            src_files.append(pd / "scanner.c")
        if (pd / "scanner.cc").exists():
            src_files.append(pd / "scanner.cc")
        if not src_files:
            return (lang, "FAIL", "no-src")
        includes = ["-I", str(pd)]
        if (pd / "scanner.cc").exists():
            cmd = [CXX, "-shared", "-fPIC", "-std=c++14", "-o", str(out_so), *[str(s) for s in src_files], *includes]
        else:
            cmd = [CC, "-shared", "-fPIC", "-std=c11", "-o", str(out_so), *[str(s) for s in src_files], *includes]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=build_dir)
        (logdir / f"{lang}-cc.log").write_text(r.stdout + r.stderr)
        if r.returncode != 0 or not out_so.exists():
            return (lang, "FAIL", f"compile rc={r.returncode}:{(r.stderr or '')[:80]}")

    # 6. 验证 .so
    # macOS 的 file 输出 "Mach-O ... dynamically shared library", Linux 输出 "ELF ... shared object"
    fc = subprocess.run(["/usr/bin/file", str(out_so)], capture_output=True, text=True)
    is_dso = "shared" in fc.stdout.lower() and ("object" in fc.stdout.lower() or "library" in fc.stdout.lower())
    if not is_dso:
        out_so.unlink(missing_ok=True)
        return (lang, "FAIL", "not-so")

    # 7. nvim 验证
    vfy = nvim_verify(lang, out_so)
    if vfy == "PARSE_OK":
        size = out_so.stat().st_size
        rmrf(archive_file)
        rmrf(logfile)
        return (lang, "OK", f"{size // 1024}K")
    out_so.unlink(missing_ok=True)
    return (lang, "FAIL", f"verify:{vfy}")


def nvim_verify(lang: str, so_path: Path) -> str:
    """Nvim 原生 API 验证, 直接指定 lang (不设 filetype).

    并行 verify 时需要隔离 ShaDa 写入路径 (-i <tmpfile>),避免 16 个 nvim 同时写
    ~/.local/state/nvim/shada/main.shada 互相踩踏 E138 错误。
    """
    if not Path(NVIM).is_file():
        return "PARSE_OK"
    # 用 NamedTemporaryFile(delete=False) 替代不安全的 mktemp: mktemp 只返回路径而不创建文件,
    # 存在 TOCTOU 竞争. 这里用 mkstemp 语义安全地创建临时文件供 nvim -i 写入 shada.
    with tempfile.NamedTemporaryFile(prefix="nvim-shada-", suffix=".tmp", delete=False) as shada_fh:
        shada_tmp = shada_fh.name
    shada_parent = Path(shada_tmp).parent
    lua_code = (
        f'local so="{so_path}"; '
        f'pcall(function() vim.treesitter.language.add("{lang}",{{path=so}}) end); '
        f"local buf=vim.api.nvim_create_buf(false,true); "
        f'vim.api.nvim_buf_set_lines(buf,0,-1,false,{{"x"}}); '
        f'local ok,p=pcall(vim.treesitter.get_parser,buf,"{lang}"); '
        f'if ok and p then local t,_=pcall(function()return p:parse()[1]end); print(t and "PARSE_OK" or "PARSE_FAIL") else print("LOAD_FAIL") end'
    )
    # +S 让退出时把 shada 写入 -i 指定的临时文件,不与其他进程冲突
    cmd = [str(NVIM), "--headless", "-i", shada_tmp, "-c", f"lua {lua_code}", "-c", "qa!"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        out = r.stderr.strip() or r.stdout.strip() or "NO_RESULT"
        return out.split("\n")[-1].strip()
    except Exception:
        return "NO_RESULT"
    finally:
        # +S 可能还会生成 .tmp.bak / .tmp.shada 等伴随文件, 一并清理
        for sibling in shada_parent.glob(Path(shada_tmp).name + "*"):
            sibling.unlink(missing_ok=True)


def rmrf(path: Path | str):
    if Path(path).is_dir():
        shutil.rmtree(Path(path), ignore_errors=True)
    elif Path(path).is_file():
        Path(path).unlink(missing_ok=True)


def get_parsers(path: Path | str) -> dict[str, dict[str, str]]:
    """从 lock.json 加载 parser 清单.

    lock.json 字段: owner/repo/host/commit/location/url/source。

    Returns:
        {lang: {revision, url, location}}
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = raw["parsers"]
    out: dict[str, dict[str, str]] = {}
    for lang, e in entries.items():
        meta: dict[str, str] = {
            "revision": e["commit"],
            "url": e["url"],
            "location": e.get("location", ""),
        }
        out[lang] = meta
    return out


if __name__ == "__main__":
    main()
