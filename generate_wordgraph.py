import re, os
from collections import Counter
from pathlib import Path

WIKI = Path("wiki")
STOPWORDS = {"する", "ある", "いる", "なる", "できる", "ない", "こと", "ため", "これ",
             "それ", "よう", "しまう", "いく", "れる", "られる", "せる", "いう", "れる",
             "de", "la", "le", "the", "is", "it", "to", "of", "in", "and", "for",
             "this", "that", "with", "from", "not", "are", "was", "be", "java"}

texts = []
for f in sorted(WIKI.glob("*.md")):
    texts.append(f.read_text(encoding="utf-8"))

raw = re.findall(r'[\w\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]+', " ".join(texts))
cnt = Counter(w for w in raw if len(w) > 1 and w.lower() not in STOPWORDS)

top = cnt.most_common(50)

max_count = top[0][1] if top else 1

print("=== 単語グラフ ===\n")
print(f"{'単語':<16} {'出現数':>4}  グラフ")
print("-" * 50)
for word, count in top:
    bar_len = int(count / max_count * 40)
    bar = "#" * bar_len
    print(f"{word:<16} {count:>4}  {bar}")

print(f"\n全 {len(top)} 語表示")

# 出現場所も保存
results = []
for word, count in top:
    sources = []
    for f in sorted(WIKI.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        if word in text:
            page = f.stem
            for i, line in enumerate(text.split("\n"), 1):
                if word in line:
                    section = line.strip()[:60]
                    sources.append(f"{page}:{i}")
                    break
    results.append((word, count, sources))

print("\n\n=== 単語の出現ページ ===")
for word, count, sources in results:
    src_str = ", ".join(sources[:3])
    print(f"{word:<16} → {src_str}")
