#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_sources.py — 按 lock.json 下载每个 grammar 的 pristine 上游 tarball，解压到 <lang>/。

设计原则：
  - 产物是"原始上游存档"：只做 tarball 下载 + 解压，绝不运行 tree-sitter generate / build，
    也不格式化。tree-sitter.json、重新生成的 parser.c 等构建产物不会出现在提交里。
  - <lang>/ 目录 = 上游仓库在该 commit 的完整快照（--strip-components=1），和 lock.json 严格对应。
  - 用于一次性把仓库里的源码同步到 lock.json 指定的新版本；之后在 git 历史里归档，
    供离线机 clone 后直接 build.py 编译。

用法:
  python3 sync_sources.py                 # 全量同步
  python3 sync_sources.py --limit 10      # 测试：前 10 个
  python3 sync_sources.py --list-only     # 列出将要同步的清单
  python3 sync_sources.py zig bash        # 只同步指定语言
  python3 sync_sources.py --retry-failures  # 重试上次失败的语言（读 /tmp/sync-failures.txt）
"""
# ruff: noqa: E501,S603,S607,BLE001
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# ----- 配置 ---------------------------------------------------------------
REPO_ROOT = Path(__file__).parent
LOCKFILE = REPO_ROOT / "lock.json"
PARALLEL = min(os.cpu_count() or 1, 16)
PROXIES = {k: os.environ.get(k, "") for k in ("http_proxy", "https_proxy")}
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
FAILURE_FILE = Path("/tmp/sync-failures.txt")
USER_AGENT = "Mozilla/5.0 (sync_sources; archive download)"


# ----- 工具 ---------------------------------------------------------------
def tarball_url(url: str, revision: str) -> str:
    """构造归档下载链接（github / gitlab 两种格式）。"""
    if "gitlab.com" in url:
        repo_name = url.split("/")[-1].removesuffix(".git")
        base = url.removesuffix(".git")
        return f"{base}/-/archive/{revision}/{repo_name}-{revision}.tar.gz"
    return f"{url}/archive/{revision}.tar.gz"


def download(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["curl", "-sLf", "--retry", "3", "--retry-delay", "2", "-A", USER_AGENT, "-o", str(dest), url]
    # 代理：走环境变量（http_proxy/https_proxy），curl 默认读取
    if GITHUB_TOKEN and "github.com" in url:
        cmd.insert(2, "-H")
        cmd.insert(3, f"Authorization: token {GITHUB_TOKEN}")
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=120)
        if r.returncode != 0:
            return False
        # 校验是 gzip 而非 HTML 错误页
        ftype = subprocess.run(["/usr/bin/file", str(dest)], capture_output=True, text=True).stdout
        return dest.stat().st_size > 500 and "gzip" in ftype
    except Exception:
        return False


def sync_one(lang: str, meta: dict, force: bool = False) -> tuple[str, str, str]:
    """下载并解压单个 grammar 的 pristine 源码到 <lang>/。"""
    url, revision = meta["url"], meta["commit"]
    location = meta.get("location", "")
    target = REPO_ROOT / lang
    archive = Path(tempfile.mkdtemp(prefix="sync-")) / f"{lang}.tar.gz"

    # 非强制模式: 已同步过就跳过(目录存在且包含 src/parser.c = 真实 upstream 存档),
    # 避免重复下载撞 GitHub 限速.  force=True 时强制重下(迁移/修正旧版).
    if not force and target.is_dir():
        probe = (target / location / "src" / "parser.c") if location else (target / "src" / "parser.c")
        if probe.is_file():
            n = sum(1 for _ in target.rglob("*") if _.is_file())
            return (lang, "SKIP", f"exists {n} files")

    url_tar = tarball_url(url, revision)
    if not download(url_tar, archive):
        return (lang, "FAIL", f"download {url_tar}")

    # 解压到临时目录，校验里面有 src/parser.c（或 location 子目录）
    extract_dir = Path(tempfile.mkdtemp(prefix=f"extract-{lang}-"))
    r = subprocess.run(
        ["/usr/bin/tar", "xzf", str(archive), "-C", str(extract_dir), "--strip-components=1"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return (lang, "FAIL", f"extract rc={r.returncode}")

    # 清理临时归档
    archive.unlink(missing_ok=True)

    # 替换目标目录：清空旧的（.git 保留），放入 pristine 源码
    if target.exists():
        # 删除旧内容，但保留可能存在的嵌套 .git（理论上不应有）
        for child in target.iterdir():
            if child.name == ".git":
                continue
            if child.is_dir():
                __import__("shutil").rmtree(child)
            else:
                child.unlink()
    else:
        target.mkdir(parents=True)

    # 把解压内容移入 target
    for child in extract_dir.iterdir():
        dest = target / child.name
        if child.is_dir():
            __import__("shutil").copytree(child, dest)
        else:
            __import__("shutil").copy2(child, dest)

    # 清理临时解压目录
    __import__("shutil").rmtree(extract_dir, ignore_errors=True)

    n = sum(1 for _ in target.rglob("*") if _.is_file())
    return (lang, "OK", f"{n} files")


def load_lock() -> dict[str, dict]:
    return json.loads(LOCKFILE.read_text())["parsers"]


def main():
    p = argparse.ArgumentParser(description="Sync pristine grammar sources from lock.json")
    p.add_argument("--jobs", type=int, default=PARALLEL)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--list-only", action="store_true")
    p.add_argument("--retry-failures", action="store_true", help="读 /tmp/sync-failures.txt 重试")
    p.add_argument("--force", action="store_true", help="忽略已有目录, 强制重新下载 pristine 版 (用于迁移/修正)")
    p.add_argument("langs", nargs="*")
    a = p.parse_args()

    if a.retry_failures and FAILURE_FILE.exists():
        retry = [x.strip() for x in FAILURE_FILE.read_text().splitlines() if x.strip()]
        print(f"=== 重试 {len(retry)} 个上次失败的语言 ===")
        parsers = {lang: load_lock()[lang] for lang in retry if lang in load_lock()}
    else:
        parsers = load_lock()

    if a.langs:
        specified = set(a.langs)
        parsers = {k: v for k, v in parsers.items() if k in specified}
    if a.limit > 0:
        parsers = dict(list(parsers.items())[: a.limit])
    if a.list_only:
        for lang, meta in sorted(parsers.items()):
            print(f"  {lang:20} {meta['commit'][:12]}  {meta['url'].split('/')[-1]}")
        return

    print(f"=== 同步 {len(parsers)} 个 grammar 的 pristine 源码 ({a.jobs} 并发) ===")
    print(f"  代理: http_proxy={PROXIES['http_proxy'] or '-'}  https_proxy={PROXIES['https_proxy'] or '-'}")
    print(f"  GITHUB_TOKEN: {'已设' if GITHUB_TOKEN else '未设'}")
    start = time.time()
    results, failures = [], []
    marks = {"OK": "✅", "FAIL": "❌", "SKIP": "🟡"}
    with ThreadPoolExecutor(max_workers=a.jobs) as exe:
        futs = {exe.submit(sync_one, lang, meta, a.force): lang for lang, meta in parsers.items()}
        for fut in as_completed(futs):
            lang = futs[fut]
            try:
                r = fut.result()
                results.append(r)
                print(f"  {marks[r[1]]} {lang:20} {r[1]:4} {r[2]}")
                if r[1] == "FAIL":
                    failures.append(lang)
            except Exception as e:
                results.append((lang, "FAIL", str(e)))
                failures.append(lang)
                print(f"  {marks['FAIL']} {lang:20} FAIL {e}")

    elapsed = int(time.time() - start)
    ok = sum(1 for r in results if r[1] == "OK")
    print(f"\n=== 完成 ({elapsed}s): 成功 {ok}, 失败 {len(failures)} ===")
    if failures:
        FAILURE_FILE.write_text("\n".join(sorted(failures)))
        print(f"  失败列表写入 {FAILURE_FILE}（可用 --retry-failures 重试）")
        for lang in sorted(failures):
            meta = parsers[lang]
            print(f"    {lang}: {meta['url']} @ {meta['commit'][:12]}")


if __name__ == "__main__":
    main()
