# word-graph

**疎結合な共通Graph基盤**。専門repoの知識・計算を、Node / Edge / Provenanceとして接続する。

## Architecture

```text
rhyme-finder ─┐
SEED ─────────┤
RAG ──────────┤ JSON / OpenAPI → word-graph → query → consumer
rhyme-yamanote┘                    Rust
```

- **Core:** Rust
- **Boundary:** JSON / OpenAPI
- **Specialized knowledge:** 各repoに保持
- **Storage:** JSON / JSONLから開始

実装言語を統一するのではなく、**contractを統一する**。

## Model

### Node

`id` / `type` / `label` / `reading` / `metadata`

### Edge

`source` / `target` / `type` / `score` / `metadata` / `provenance`

### Provenance

`source` / `method` / `version` / `timestamp`

Edge typeは固定せず、`phonetic`, `rhyme`, `semantic`, `context`, `domain`, `association`などを拡張可能にする。

## Example

駅名から音韻的連想をGraphとして保持できる。

```json
{
  "source": "station:nippori",
  "target": "word:shippori",
  "type": "phonetic",
  "score": 0.92
}
```

```text
日暮里 ──phonetic──→ しっぽり
巣鴨   ──phonetic──→ 素顔
五反田 ──phonetic──→ 土壇場
```

## Loose Coupling

専門repoをword-graphへ直接importしない。

```text
specialized repo
      ↓
 JSON / OpenAPI contract
      ↓
 word-graph
      ↓
 query / traversal
      ↓
 consumer
```

- `rhyme-finder`: 音韻・押韻候補生成
- `SEED`: 初期知識・関連付け
- `RAG`: 文脈検索・補強
- `rhyme-yamanote`: 山手線ドメイン判断・ランキング
- `bqmlite-go`: 将来の学習済みscore/ranking

word-graphはこれらの専門知識を所有しない。

## Rust Design

```text
model      → Node / Edge / Provenance
   ↓
graph      → adjacency / traversal
   ↓
query      → typed query
   ↓
storage    → JSON / JSONL
   ↓
api / cli  → OpenAPI / local tooling
```

RustをCoreにする理由:

- 型安全なGraphモデル
- traversalの性能とメモリ効率
- CLI / HTTP API / WASMへの展開余地
- 外部engineとの境界を明確化

Rubyは排除せず、prototype / DSL / data preparation / adapterとして接続可能。

## Development

```bash
cargo test
```

## Design / ADR

設計判断はGitHub Issuesで管理する。

- ADR #1: 疎結合な共通グラフ基盤
- Issue #2: Node / Edge / Provenance schema
- Issue #3: OpenAPI contract
- Issue #4: 専門repo接続
- ADR #5: Rust基盤実装

## Principle

> **CoreはRust。境界はJSON/OpenAPI。専門知識は各repo。**
>
> **言語ではなくcontractとbenchmarkで競争する。**
