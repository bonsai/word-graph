---
name: word-graph
description: >
  単語グラフ生成とゴール分解のスキル。wiki 内 md から頻出単語を集計してアスキーバー表示
  (generate_wordgraph.py) し、ゴール指向バージョン(generate_wordgraph_goal.py)では
  kanban の GOAL 分析・サブゴール分解・抽象化(LLM)を行う。WorkItem オントロジー参照付き。
  「単語グラフ」「wordgraph」「頻出単語」「ゴール分解」「decompose」「抽象化」「GOAL分析」
  「ワードグラフ」「kanban分析」などのキーワードで発動。
---

# 単語グラフ & ゴール分解

## 使い方

- 単語グラフ: `python3 generate_wordgraph.py` — `wiki/*.md` から上位50語を集計し、出現数バーを表示 (stopwords 除外)。
- ゴール拡張: `python3 generate_wordgraph_goal.py` で `MEGA/kanban/*.md` の `## GOAL` を分析。
  - goal: GOAL セクション抽出
  - decompose: ゴールをサブゴールに分解 (LLM)
  - abstract: 複数タスクを上位概念へ抽象化 (LLM)
- 分類モデル: `references/goal-ontology.md` のクラス階層 (PlannedWork/UnplannedWork, family resemblance 行列) を判定に使う。

## 主要ファイル

- `generate_wordgraph.py` — 頻出単語グラフ生成
- `generate_wordgraph_goal.py` — goal/decompose/abstract 拡張 (LLM)
- `references/goal-ontology.md` — WorkItem/Task/Todo/Issue/Ticket オントロジー

## 関連

- 分類文法の判定 Trees は `task-ontology` 参照