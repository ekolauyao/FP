#!/usr/bin/env python3
"""
sync_to_miniapp.py — 从 GitHub 同步 Celeb.md 到微信小程序后端

用法:
  python sync_to_miniapp.py <persona_name>           # 同步单个人物
  python sync_to_miniapp.py --all                     # 同步所有人物
  python sync_to_miniapp.py --list                    # 列出所有可用人物
"""

import os
import sys
import json
import shutil
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PERSONAS_DIR = REPO_ROOT / "personas"

# 小程序后端路径（根据实际部署修改）
MINIAPP_BACKEND = Path("E:/传世人物skill/engine/persona_data")


def list_personas():
    """列出所有可用人物"""
    if not PERSONAS_DIR.exists():
        print("❌ personas/ 目录不存在")
        return []

    personas = [d.name for d in PERSONAS_DIR.iterdir()
                if d.is_dir() and (d / "Celeb.md").exists()]
    return sorted(personas)


def compute_hash(filepath: Path) -> str:
    """计算文件的 MD5 hash"""
    return hashlib.md5(filepath.read_bytes()).hexdigest()


def sync_persona(name: str) -> bool:
    """同步单个人物到小程序后端"""
    src_dir = PERSONAS_DIR / name
    dst_dir = MINIAPP_BACKEND / name

    if not src_dir.exists():
        print(f"❌ 人物 '{name}' 不存在")
        return False

    if not (src_dir / "Celeb.md").exists():
        print(f"❌ 人物 '{name}' 缺少 Celeb.md")
        return False

    dst_dir.mkdir(parents=True, exist_ok=True)

    synced = []
    skipped = []

    # 同步 Celeb.md
    src_file = src_dir / "Celeb.md"
    dst_file = dst_dir / "Celeb.md"
    if not dst_file.exists() or compute_hash(src_file) != compute_hash(dst_file):
        shutil.copy2(src_file, dst_file)
        synced.append("Celeb.md")
    else:
        skipped.append("Celeb.md (未变化)")

    # 同步 metadata.json
    src_meta = src_dir / "metadata.json"
    dst_meta = dst_dir / "metadata.json"
    if src_meta.exists():
        if not dst_meta.exists() or compute_hash(src_meta) != compute_hash(dst_meta):
            shutil.copy2(src_meta, dst_meta)
            synced.append("metadata.json")
        else:
            skipped.append("metadata.json (未变化)")

    # 同步原著文本 (data/)
    src_data = src_dir / "data"
    dst_data = dst_dir / "data"
    if src_data.exists():
        dst_data.mkdir(exist_ok=True)
        for f in src_data.iterdir():
            if f.is_file():
                dst_file = dst_data / f.name
                if not dst_file.exists() or compute_hash(f) != compute_hash(dst_file):
                    shutil.copy2(f, dst_file)
                    synced.append(f"data/{f.name}")

    if synced:
        print(f"✅ {name}: 已同步 {', '.join(synced)}")
    if skipped:
        print(f"⏭ {name}: 跳过 {', '.join(skipped)}")

    return True


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    if sys.argv[1] == "--list":
        personas = list_personas()
        if personas:
            print(f"可用人物 ({len(personas)}):")
            for p in personas:
                print(f"  - {p}")
        else:
            print("没有找到任何人物")
        sys.exit(0)

    if sys.argv[1] == "--all":
        personas = list_personas()
        if not personas:
            print("没有找到任何人物")
            sys.exit(1)

        print(f"同步所有人物 ({len(personas)})...\n")
        failures = sum(1 for p in personas if not sync_persona(p))
        print(f"\n完成: {len(personas) - failures} 成功, {failures} 失败")
        sys.exit(failures)

    success = sync_persona(sys.argv[1])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
