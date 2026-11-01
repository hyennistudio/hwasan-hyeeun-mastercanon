# 인물 YAML 작성 방법

- 파일 위치: `canon/characters/<id>.yaml` (한 인물당 한 파일)
- [templates/character.yaml](../../templates/character.yaml)을 복사해 작성합니다.
- 스키마: [schemas/character.schema.json](../../schemas/character.schema.json)
- `id`, `name_ko`는 필수입니다.
- `profile.affiliations`는 등록된 세력 ID, `appearance.reference_asset_ids`는 [assets/manifest.yaml](../../assets/manifest.yaml)의 ID, `relationships[].target_id`는 인물 ID, 모든 `source_ids`는 [sources/index.yaml](../../sources/index.yaml)의 ID를 참조해야 합니다.
- `facts[]`: `field`, `value`, `status`, `source_ids`. `confirmed` 사실은 유효한 출처가 1개 이상 필요합니다.
- 회차별 위치·부상·생존 상태는 프로필에 덮어쓰지 않고 [회차 문서](../../episodes/README.md)에서 관리합니다.
- 규칙: [RULES.md](../RULES.md)
