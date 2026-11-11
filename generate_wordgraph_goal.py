#!/usr/bin/env python3
"""
word-graph goal-extended
Goal追加・分解・抽象を提供するword-graph拡張

機能:
  goal   : DATA/kanban/*.md 内の GOAL セクションを分析/追加
  decompose : goalをサブゴールに分解 (LLM)
  abstract  : 複数タスクを上位概念に抽象化 (LLM)
"""
import argparse
import json
import re
import sys
from pathlib import Path
from collections import Counter

KANBAN = Path("/mnt/c/Users/dance/Documents/MEGA/kanban")
WIKI = Path("/mnt/c/Users/dance/Documents/MEGA/wiki")


def read_all_md(root: Path) -> list[tuple[Path, str]]:
    """全mdファイルを (path, text) で返す"""
    if not root.exists():
        return []
    return [(f, f.read_text(encoding="utf-8")) for f in sorted(root.glob("*.md"))]


def extract_goals(text: str) -> list[str]:
    """## GOAL 〜 セクションを抽出"""
    goals = []
    in_goal = False
    for line in text.split("\n"):
        if re.match(r"^#{1,3}\s*GOAL", line, re.IGNORECASE):
            in_goal = True
            continue
        if in_goal and line.startswith("#"):
            in_goal = False
        if in_goal and line.strip():
            goals.append(line.strip())
    return goals


def extract_tasks(text: str) -> list[str]:
    """- [ ] タスクを抽出"""
    return [m.group(1) for m in re.finditer(r"-\s*\[[ xX]\]\s*(.+)", text)]


def cmd_list(args):
    """kanban全mdのgoal・task + cards.jsonを列挙"""
    files = read_all_md(KANBAN) + read_all_md(WIKI)
    rows = []
    for path, text in files:
        goals = extract_goals(text)
        tasks = extract_tasks(text)
        if goals or tasks:
            rows.append((path.name, goals, tasks))

    # cards.json も読む
    cards_path = KANBAN / "cards.json"
    cards = []
    if cards_path.exists():
        try:
            cards = json.load(open(cards_path, encoding="utf-8"))
        except Exception:
            pass

    if not rows and not cards:
        print("No goals/tasks found.")
        return

    out = ["# Goal/Task Inventory\n"]
    for name, goals, tasks in rows:
        out.append(f"\n## {name}")
        if goals:
            out.append("### Goals")
            for g in goals:
                out.append(f"  - {g}")
        if tasks:
            out.append("### Tasks")
            for t in tasks:
                out.append(f"  - {t}")
    if cards:
        out.append(f"\n## cards.json ({len(cards)} items)")
        for c in cards:
            title = c.get("title", "")
            status = c.get("status", "open")
            project = c.get("project", "")
            out.append(f"  - [{status}] {title} ({project})" if project else f"  - [{status}] {title}")
    print("\n".join(out))


def cmd_add(args):
    """指定mdにgoalを追加"""
    target = KANBAN / args.file
    if not target.exists():
        target = WIKI / args.file
    if not target.exists():
        print(f"File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    text = target.read_text(encoding="utf-8")
    goal_block = f"\n## GOAL\n- {args.goal}\n"

    # 既存GOALセクションがあれば追記、なければ末尾に追加
    if re.search(r"^#{1,3}\s*GOAL", text, re.MULTILINE | re.IGNORECASE):
        # 既存GOALの最後に追加
        lines = text.split("\n")
        new_lines = []
        in_goal = False
        goal_end = len(lines)
        for i, line in enumerate(lines):
            if re.match(r"^#{1,3}\s*GOAL", line, re.IGNORECASE):
                in_goal = True
                new_lines.append(line)
                continue
            if in_goal and line.startswith("#") and not re.match(r"^#{1,3}\s*GOAL", line, re.IGNORECASE):
                goal_end = i
                in_goal = False
            new_lines.append(line)
        new_lines.insert(goal_end, f"- {args.goal}")
        text = "\n".join(new_lines)
    else:
        text += goal_block

    target.write_text(text, encoding="utf-8")
    print(f"Added goal to {target.name}: {args.goal}")


def cmd_wordgraph(args):
    """既存word-graphロジック（kanban全mdの頻度分析）"""
    STOPWORDS = {
        "する", "ある", "いる", "なる", "できる", "ない", "こと", "ため", "これ",
        "それ", "よう", "しまう", "いく", "れる", "られる", "せる", "いう",
        "その", "から", "まで", "より", "など", "という", "にて",
        "the", "is", "it", "to", "of", "in", "and", "for", "this", "that",
        "with", "from", "not", "are", "was", "be", "java", "a", "an"
    }

    files = read_all_md(KANBAN) + read_all_md(WIKI)
    all_text = " ".join(t for _, t in files)

    raw = re.findall(r'[\w\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]+', all_text)
    cnt = Counter(w for w in raw if len(w) > 1 and w.lower() not in STOPWORDS)

    top = cnt.most_common(args.top)
    if not top:
        print("No words found.")
        return

    max_count = top[0][1]
    print(f"=== Word Frequency (top {args.top}) ===\n")
    print(f"{'word':<20} {'count':>5}  bar")
    print("-" * 60)
    for word, count in top:
        bar_len = int(count / max_count * 30)
        bar = "#" * bar_len
        print(f"{word:<20} {count:>5}  {bar}")

    # 出現ページ
    print(f"\n=== Word → Pages ===")
    for word, count in top[:20]:
        sources = []
        for path, text in files:
            if word in text:
                sources.append(path.name)
        print(f"  {word} → {', '.join(sources[:5])}")


def cmd_decompose(args):
    """goalをサブゴールに分解（テンプレート出力）"""
    goal = args.goal
    print(f"# Decompose: {goal}\n")
    print("## Sub-goals")
    print(f"  - [ ] {goal} の条件定義")
    print(f"  - [ ] {goal} の手段列挙")
    print(f"  - [ ] {goal} の検証基準設定")
    print(f"  - [ ] {goal} の完了条件確認")
    print("\n## Abstract view")
    print(f"  → 「{goal}」は次の上位概念に属する:")
    print(f"    - 達成 (achievement)")
    print(f"    - 実行 (execution)")
    print(f"    - 検証 (validation)")


def cmd_abstract(args):
    """複数タスクを上位概念に抽象化"""
    tasks = args.tasks.split(",") if args.tasks else []
    if not tasks:
        # kanbanから全タスクを読む
        files = read_all_md(KANBAN) + read_all_md(WIKI)
        for path, text in files:
            tasks.extend(extract_tasks(text))

    print(f"# Abstract: {len(tasks)} tasks → upper concepts\n")
    # 簡易グルーピング（キーワードベース）
    groups: dict[str, list[str]] = {}
    keywords = {
        "インフラ": ["server", "deploy", "infra", "docker", "ssl", "dns"],
        "UI/UX": ["ui", "ux", "design", "css", "layout", "component"],
        "データ": ["data", "db", "sql", "migration", "schema", "export"],
        "認証": ["auth", "login", "token", "session", "oauth"],
        "テスト": ["test", "spec", "verify", "check"],
        "ドキュメント": ["doc", "readme", "guide", "manual"],
    }
    for task in tasks:
        task_lower = task.lower()
        matched = False
        for group, kws in keywords.items():
            if any(kw in task_lower for kw in kws):
                groups.setdefault(group, []).append(task)
                matched = True
                break
        if not matched:
            groups.setdefault("その他", []).append(task)

    for group, items in groups.items():
        print(f"\n## {group}")
        for t in items:
            print(f"  - {t}")


def main():
    p = argparse.ArgumentParser(description="word-graph goal-extended")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list", help="List all goals/tasks from kanban")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("add", help="Add a goal to a kanban md file")
    sp.add_argument("file", help="target md filename")
    sp.add_argument("goal", help="goal text")
    sp.set_defaults(func=cmd_add)

    sp = sub.add_parser("graph", help="Word frequency graph")
    sp.add_argument("--top", type=int, default=50)
    sp.set_defaults(func=cmd_wordgraph)

    sp = sub.add_parser("decompose", help="Decompose a goal into sub-goals")
    sp.add_argument("goal", help="goal to decompose")
    sp.set_defaults(func=cmd_decompose)

    sp = sub.add_parser("abstract", help="Abstract tasks into upper concepts")
    sp.add_argument("--tasks", help="comma-separated tasks (default: read from kanban)")
    sp.set_defaults(func=cmd_abstract)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
