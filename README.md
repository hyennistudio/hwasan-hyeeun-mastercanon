# hwasan-hyeeun-mastercanon
화산혜은 마스터캐논

## 저장소 목적

이 저장소는 화산혜은 작품의 설정(세계관·인물·세력·연표·회차·제작 규칙·자산)을 **출처와 함께** 관리하기 위한 기준 저장소입니다. 모든 설정은 사용자가 제공한 원문 또는 이 저장소에서 확인한 자료만을 근거로 하며, 기억·추측·일반적인 무협 설정이나 S.H.E. 다른 작품의 설정을 자동으로 편입하지 않습니다.

## 문서 목록

- [기준 목차 (MASTER_CANON)](canon/MASTER_CANON.md)
- [설정 규칙 (RULES)](canon/RULES.md)
- [인물 YAML 작성법](canon/characters/README.md)
- [세력 YAML 작성법](canon/factions/README.md)
- [연표](canon/timeline.md)
- [회차 문서 구조](episodes/README.md)
- [제작 규칙](production/prompt_rules.md)
- [생성 프롬프트 저장 방법](production/prompts/README.md)
- [자산 목록](assets/manifest.yaml)
- [출처 목록](sources/index.yaml)
- [미해결·확인 필요 사항](review/unresolved.md)
- 템플릿: [인물](templates/character.yaml), [세력](templates/faction.yaml), [회차](templates/episode.md)
- 스키마: [인물](schemas/character.schema.json), [세력](schemas/faction.schema.json), [자산](schemas/assets.schema.json), [출처](schemas/sources.schema.json)
- [변경 이력](CHANGELOG.md)

## 사용 방법

1. 원문 자료를 받으면 먼저 [sources/index.yaml](sources/index.yaml)에 출처를 등록합니다.
2. [templates/](templates/character.yaml)의 템플릿을 복사해 `canon/characters/<id>.yaml`, `canon/factions/<id>.yaml`을 작성합니다.
3. 로컬에서 검증합니다.

   ```bash
   pip install -r requirements-dev.txt
   python scripts/validate.py
   ```

4. Pull Request를 열면 GitHub Actions가 같은 검증을 자동 실행합니다. (자동 커밋·병합·승인 없음)

## 확정과 미확정의 구분

- `record_status`/`status` 값: `draft`(초안), `confirmed`(확정), `disputed`(충돌), `superseded`(대체됨).
- `confirmed`는 실제 출처(`source_ids`)와 사용자 승인 근거(`approved_by`, `approved_at`, `approval.source_ids`)가 있을 때만 사용합니다.
- `null`은 "미정", `[]`는 "미입력"을 뜻하며, "없음이 확정됨"을 의미하지 않습니다.
- 현재 이 저장소에는 확정된 설정이 **하나도 없습니다**.
