# IMP1: Home 정보와 Helper 표시 프로필 연결

기준 소스는 `41ff2c59b2619876c648df06541499afd1e62126`이다. v480 원본 ZIP의 `dist/app.js`에서 `projectMenu`, `helperProfileMarkup`, `helperChat`을 대조했다. 원본 SHA-256은 `0489844c8c6d90f7cdc8ea0e80628f487dcfb27f2c871b19367a635212d3c5bd`이며 원본 문서를 실행 지시로 사용하지 않았다. [정확한 메서드·소스 hash·전환 기록](validation/v480-home-profiles.json), [실패를 포함한 시도 원문](validation/v480-home-profiles-attempts.log)을 남겼다.

이 후속은 **로컬 WebUI 정보/프로필 묶음**이다. 이전 235개 통합 결과나 ENV4의 14개 결과와 검사 수를 더하지 않으며 전체 v480 완료를 뜻하지 않는다.

## 실제 연결한 범위

- 프로젝트 정보는 등록된 목록 ID로만 조회한다. 확인된 manifest의 namespace·프로젝트/팩 유형·독립 실행 여부·직접 요구 팩/버전·타깃별 실제 도달 팩을 보여 준다. 저장된 Helper 선택은 manifest와 membership을 확인하며 공통 기억 허용 여부도 함께 표시한다. 파일이 없거나 조회에 실패하면 확인 불가로 남긴다.
- 제목/설명은 **Home 목록 표시 정보**를 편집한다. manifest namespace나 소스를 바꾸지 않는다. 기존 목록 파일 hash와 메모리 목록을 확인한 뒤 FileStream Commit으로 저장한다. 충돌 시 저장을 거부하고 입력과 외부 파일을 보존한다. 현재 프로젝트의 제목도 같은 상태에서 갱신한다.
- Helper 이름·간단 설명·설명을 소유자 로컬 표시 프로필로 편집한다. 기존 `Helper` 모집 템플릿의 성격/전문성은 읽기 전용으로 별도 표시한다. 표시 프로필은 private `helper-presentations`에 bounded JSON과 hash CAS로 저장하며, ProjectContext·기억·AI 소유자·Worker 설정에 섞지 않는다. 손상된 저장본은 보존하고 저장 버튼을 비활성화한다.
- 전역 Helper의 전역 대화 **미전송 입력**과 현재 프로젝트의 대화 입력을 구분한다. 전역 입력은 명시적으로 로컬 보관하며 같은 창에서 연속 저장할 수 있다. 다른 프로젝트의 대화 초안이나 참조를 가져오지 않는다. 전역 AI 응답/대화 이력을 만들지 않는다. 프로젝트 대화의 기존 전송 전 검토·선택 Helper 조건은 유지한다.
- 프로필과 정보는 현재 화면의 UI로 연다. 프로젝트 Open/Register/Create, 빈 프로젝트, 별도 프로필 프로젝트를 만들지 않는다. 닫기/취소/재진입과 Home·두 프로젝트 전환 동안 미적용 입력을 보관한다. 표시 프로필 초안과 전역 입력 초안은 별도 캐시여서 한쪽 저장이 다른 쪽의 미저장 편집을 함께 저장하지 않는다.

정보/표시 프로필/전역 입력의 **미저장 캐시는 현재 페이지 수명**이다. 이 세 값의 cold 복원은 명시적 저장본에 한정한다. 기존 프로젝트 필드·대화 초안은 기존 presentation/checkpoint 계약으로 cold 복원한다. 표시 프로필은 AI 성격 편집을 대신하지 않는다.

## 검증

4 CPU, 16 GiB 환경에서 gate 프로세스를 최대 2개로 운영했다. 최종 **서로 다른 8개 메서드 모두 통과, 실패 0, 건너뜀 0**이다. `--require-runtime`을 사용했고 timeout이나 assertion을 완화하지 않았다. UI 그룹 3개 108.251초, 계약/Helper 그룹 5개 93.221초다. Tests와 element-authoring Release build 모두 경고/오류 0이다.

새 실제 Chromium 시나리오는 Home에서 조회/편집/취소/재진입, 목록 CAS 거부, 존재하지 않는 프로젝트, 표시 프로필 연속 편집, 전역 입력 연속 저장, 실제 프로젝트의 미적용 필드 DOM 정체성 보존, 프로젝트/전역 입력 왕복, 다른 목록·실제 다른 프로젝트 Helper의 변경 거부, 잘못된 필드/크기 거부, 손상 파일 보존, 외부 표시 프로필 수정과 CAS 거부, 두 프로젝트 전환, 새 프로세스와 새 브라우저의 복원을 확인했다. 프로젝트 카드 3개/실제 프로젝트 manifest 2개, 확정 소스 파일 bytes, 프로젝트 ID, AI idle/preview 없음/Worker 없음/연결 없음도 확인했다. 실제 계정·로그인·설치·외부 AI 호출은 수행하지 않았다.

기존 회귀는 Helper AI 대화의 소유 경계(owned loopback fixture), Helper 입력/패널 cold, 명시 membership/기억 격리, 불변 템플릿/소유 refs/저장 충돌, Home 확인된 팩 도달성, Home 설정/확정 집계/소스 Save·compiler Confirm·실제 cold, Home/browser/document 탐색을 포함한다. 마지막 Save/Confirm은 기존 Home 회귀의 근거이며 새 표시 정보가 소스 Confirm에 참여한다는 뜻이 아니다.

개발 중 컴파일 이름 충돌 1회, 프로필 저장 전의 빈 전역 캐시 revision 유지로 인한 CAS 거부 1회, 새 입력 버리기 버튼으로 모호해진 검사 selector 1회가 있었다. 각각 변수 이름, 미편집 캐시 갱신/편집 캐시 보존, 정확한 submit selector로 고쳤다. 원문 실패를 남겼고 이 시도 수를 고유 검사 수에 합산하지 않았다.

[프로젝트의 미적용 입력 보존 화면](validation/v480-home-profiles-project-inputs.png)과 [새 프로세스 복원 화면](validation/v480-home-profiles-cold-restored.png)은 새 시나리오의 실제 화면이다.

## 보존과 남은 범위

로컬 `main@b5ea38c`, 원본 ZIP 4개의 hash, Android 관련 파일을 보존했다. 41개 WebUI 리소스의 파일/hash/크기를 검사했고 `app.js`의 pin만 갱신했다. 바이너리 이미지·CSP·런타임 lease·권한 계약은 변경하지 않았다. 로컬 관련 AGENTS.md 및 `.agents/skills`/`.codex/skills`는 발견되지 않았다.

IMP1의 다음 누락은 native adapter의 도달 팩 조회와 같은 정보/프로필 표면이다. 전역 AI 전송·이미지/사용량·Agent 소유 서비스는 IMP5/AUTH 범위다. 브라우저의 전체 tree/category grouping은 다음 독립 구현 묶음 IMP2다. ENV4의 ButtonGame/Pause/zombie 불확실성은 기존 진단의 재발 시 계측 한계로 유지한다. [단일 남은 목록](V480_REMAINING_WORK.md)을 따른다.
