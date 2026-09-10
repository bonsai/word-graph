# word-graph

疎結合な共通Graph基盤。専門repoの知識・計算をNode / Edge / Provenanceとして接続する。

## Architecture

```text
rhyme-finder ─┐
SEED ─────────┤ JSON / OpenAPI → word-graph → query → consumer
RAG ──────────┤
rhyme-yamanote┘
```

CoreはRust。外部repositoryの実装言語は問わない。

## Model

- `Node`: id / type / label / reading / metadata
- `Edge`: source / target / type / score / metadata / provenance
- `Provenance`: source / method / version / timestamp

## Example

`日暮里 → しっぽり` は `phonetic` edgeとして表現できる。

```json
{
  "source": "station:nippori",
  "target": "word:shippori",
  "type": "phonetic",
  "score": 0.92
}
```

## Development

```bash
cargo test
```

## Design

詳細なADRはGitHub Issuesを参照。

- ADR #1: 疎結合な共通グラフ基盤
- Issue #2: Node / Edge / Provenance schema
- Issue #3: OpenAPI contract
- Issue #4: 専門repo接続
- ADR #5: Rust基盤実装
