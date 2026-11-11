# Goal Ontology — Task/Ticket/Issue Decomposition Model

## Class Hierarchy

```
WorkListItem (abstract)
├─ PlannedWork
│  ├─ Todo      — 軽い、「やるべきこと」リスト (daily.task.db)
│  └─ Task      — 完了条件＋推定規模
└─ UnplannedWork
   ├─ Issue     — 内部起点: bug/improvement (coding.task.db)
   └─ Ticket    — 外部起点: 報告/問い合わせ (coding.task.db)
```

## Family Resemblance Matrix

| Feature | Todo | Issue | Ticket |
|---------|------|-------|--------|
| 完了基準 | ✓ | ✓ | ✓ |
| 担当者必须 | ✗ | △ | ✓ |
| Sub-task | ✗ | ✓ | △ |
| Epic所属 | ✗ | ✓ | △ |
| 外部起点 | ✗ | ✗ | ✓ |
| 技術スタック | ✗ | ✓ | ✓ |
| ストーリーポイント | ✗ | ✓ | ✗ |
| MTGで扱う | ✗ | ✓ | ✓ |

## Generative Grammar

```
WorkListItem
  → if (source == "external") → Ticket
  → if (source == "internal" && type == "problem") → Issue
  → if (source == "internal" && type == "plan" && size == "atomic") → Todo
  → if (source == "internal" && type == "plan" && size == "complex") → Task
```

## Decompose Template (4-split)

```
Goal: "<goal text>"
  ├─ [ ] 条件定義 — 前提・制約・依存を明確化
  ├─ [ ] 手段列挙 — 実現方法を2-3案出す
  ├─ [ ] 検証基準設定 — 「できた」の判定条件
  └─ [ ] 完了条件確認 — 外部依存のクローズ基準
```

## Abstract Grouping (keyword-based)

| Group | Keywords |
|-------|----------|
| インフラ | server, deploy, infra, docker, ssl, dns |
| UI/UX | ui, ux, design, css, layout, component |
| データ | data, db, sql, migration, schema, export |
| 認証 | auth, login, token, session, oauth |
| テスト | test, spec, verify, check |
| ドキュメント | doc, readme, guide, manual |
| その他 | (no match) |

## DB Mapping

| Concept | DB | Table |
|---------|-----|-------|
| Todo | daily.task.db | `todo` |
| Issue | coding.task.db | `issue` (type='issue') |
| Ticket | coding.task.db | `issue` (type='ticket') |
| Epic | coding.task.db | `epic` |

## Sync Partners

| DB | External | Direction |
|----|----------|-----------|
| daily.task.db | Gmail drafts | bidirectional |
| coding.task.db | GitHub Issues | bidirectional |
