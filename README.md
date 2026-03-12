# Repo Skill Creator

既存のリポジトリを、再利用可能な Codex スキルへ変換するための実践的な
スキルパックです。

このリポジトリは、`repo-skill-creator` スキルを GitHub 上で共有できる形に
パッケージしたものです。実際のスキル本体は `skills/repo-skill-creator/`
配下に置き、人間向けの説明資料はリポジトリ直下に分離しています。

## できること

このスキルを使うと、Codex は次の作業を進めやすくなります。

- 実在するリポジトリを調査してからスキル設計に入る
- repo 固有の文脈を含むスキルのひな形を生成する
- frontmatter の基本検証だけで終わらない品質レビューを行う
- trigger、機能、性能の観点を含むテスト計画を生成する
- zip とインストール説明を含む配布 bundle を作成する

現在の実装は、Codex のローカル skill ディレクトリに配置して使う運用を
前提にしています。必要に応じてインストール先や補助スクリプトの呼び出し
パスは各環境に合わせて調整してください。

## リポジトリ構成

```text
repo-skill-creator/
├── README.md
├── AGENTS.md
├── HANDOFF.md
├── .agent/memory/MEMORY.md
└── skills/
    └── repo-skill-creator/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── scripts/
        └── references/
```

## インストール

スキルフォルダを Codex の skills ディレクトリへコピーします。

```bash
cp -R skills/repo-skill-creator ~/.codex/skills/
```

インストール前に内容を確認するなら、まず次を読むのがわかりやすいです。

- `skills/repo-skill-creator/SKILL.md`
- `skills/repo-skill-creator/references/skill-creation-checklist.md`

## 検証

基本バリデーター:

```bash
python3 /path/to/quick_validate.py \
  skills/repo-skill-creator
```

詳細レビュー:

```bash
python3 skills/repo-skill-creator/scripts/review_skill.py skills/repo-skill-creator
```

## 使用例

リポジトリを解析する:

```bash
python3 skills/repo-skill-creator/scripts/analyze_repo.py /path/to/repo
```

repo 由来のスキルをひな形生成する:

```bash
python3 skills/repo-skill-creator/scripts/init_repo_skill.py /path/to/repo my-skill
```

完成したスキルの配布 bundle を作成する:

```bash
python3 skills/repo-skill-creator/scripts/create_distribution_bundle.py \
  skills/repo-skill-creator \
  --output-dir /tmp/repo-skill-creator-dist
```

## ライセンス

MIT
