# 세력 YAML 작성 방법

- 파일 위치: `canon/factions/<id>.yaml` (한 세력당 한 파일)
- [templates/faction.yaml](../../templates/faction.yaml)을 복사해 작성합니다.
- 스키마: [schemas/faction.schema.json](../../schemas/faction.schema.json)
- `id`, `name_ko`는 필수입니다.
- `leader_ids`, `member_ids`는 인물 ID, `flag_asset_ids`는 자산 ID, `source_ids`는 출처 ID를 참조해야 합니다.
- 규칙: [RULES.md](../RULES.md)
