# v536 연결 현황과 중간 빌드 준비 조건

2026-10-23, 게시된 `work/current` 기준 HEAD `c08d08f29f16c35e896097f5a62042f50c5ae242` 및 후속 Browser 검증. UI 기준은 사용자가 지정한 `origin/main` `196c605`의 원본 v536 ZIP이다. 첨부 ZIP과의 바이트 동일성은 미확인이다. 아래의 ‘검증 완료’는 명시한 묶음에 한정되며 전체 v536 복원, 전체 편집 문맥 또는 실제 Windows 통과를 뜻하지 않는다.

## 구현 및 해당 묶음 검증 완료

| 화면/기능 | 실제 연결과 확인 범위 | 한계/근거 |
| --- | --- | --- |
| 기존 Agent 연결·공통 사용 승낙·Helper 대화 | 게시된 CLI 로그인/시작 readiness 복구·계정 일치·Agent 등록 공통 승낙/철회·프로젝트 배치 범위·실제 CLI 경로를 보존한다. Enter/IME·초안/이력·일반 전송 개선도 보존한다 | 최근 작업의 추론 검사는 fixture이다. 실제 사용자 계정 성공/유료 호출을 새로 검증한 것이 아니다. 새 프로젝트/계정/도구 권한을 자동 허용하지 않는다 |
| 앱 상단바 | 원본 chrome, Windows host 제어 브리지와 신뢰 출처 검증 연결을 이전 게시 단계에서 완료 | Windows native 드래그/snap/DPI/IME는 실기기 수용 미완료. 웹에서 OS 기능을 가짜 성공 처리하지 않는다 |
| Workspace/Pack Manager/프로젝트 Helper 필터 | 이전 게시 단계에서 원본 고정 탭·메뉴·브라우저/줌과 배치된 Helper 표시, 전역 목록/배치 후보 구분을 연결 | Pack Manager 업데이트/설치해제는 기존 명시적 미지원 유지. 모든 원본 편집기 내부의 완료를 의미하지 않는다 |
| v536 Helper 기본 생성·설정/보관·복구 | 공용 폼, 전역/프로젝트 Helper 비파괴 보관·원래 소유권으로 가져오기·별도 배치 적용. 대화/기억과 Agent 공통 승낙 보존 | 이미지 영역은 아래 backend 부재 항목. 실제 사용자 Helper를 삭제한 검사가 아니다. `VALIDATION_V536_PROJECT_HELPER_RETIREMENT.md` |
| v536 프로젝트 생성/사이드바 Helper 드롭 | 실제 생성 영수증, 취소·재시도·배치/해제·재시작, 잔류 inert/오버레이 정리 | OS 폴더 선택/Windows native는 별도. `VALIDATION_V536_PROJECT_CREATION.md` 등 |
| 공통 모바일 셸/문서 분리·플로팅 | 브라우저 폭에 따른 작업자/목록/채팅·고정 탭, 독립 View 문서/Pack Manager 플로팅·일괄 닫기, A/B 프로젝트별 입력·문맥, 3-slot 소유 객체 View, Review/명시 compiler Confirm | 브라우저 폭/합성 입력 검사이다. 실제 Android/터치·Windows native 창 검사 아님. 독립 기능/모듈의 모든 문맥은 미수용. `VALIDATION_V536_DOCUMENT_PROJECTS.md` |
| 소유 개념/카테고리 이동 및 논리 삭제/복구 | 분류와 상속을 구별한 단일/복수/중첩/Root 이동, 원자적 그룹·Undo/Redo·취소·Save/cold·명시 Confirm, 참조된 대상 차단과 원본/초안 보관 | owned concept/category/유한 32개 그룹의 검증이다. 모든 source 종류·외부 namespace 재배치·문자열 참조 전체 분석은 아님. `V536_BROWSER_SUPPORT.md` |

## 부분 연결 또는 원본 수용 잔여

| 영역 | 현재 실제 동작 | 고정 잔여 |
| --- | --- | --- |
| 요소 정의/Browser Data | 상속/자기 속성·스칼라/복합/참조·배열의 검증된 편집, 부모/자손 탐색, embedded Data 셀·독립 View 상세·inline 바리에이션 생성, 그룹 Save/취소/명시 Confirm | 독립 소유 개념 Data9건/embedded7건, 상속 Hover·Shift 역참조 및 원본 Data11영역 대조 완료. 다른 소유 선언 6종의 공통 설명 Data·등록 직접 참조·문자 아이콘/표시 이름은 이번 고정 Browser 잔여로 연결하며 결과는 `VALIDATION_V536_BROWSER_REMAINDER.md`에 구분한다. 원본 작업자 배정 배지 backend·외부 runtime Data/구조 편집·이미지/OS 드래그와 전체 pixel equality·일반 receipt/check-path 수용은 완료가 아니다. `VALIDATION_V536_STANDALONE_DATA.md` 참조. 기존 자료 보존/CAS를 완화하지 않는다 |
| Blueprint 데스크톱/모바일 | 직렬 자연어 노드·검증된 값/핀/표현식/별칭·정수→실수 적응, root/function/implementation/graph 그룹 편집과 명시 Confirm, 일반 소유 기능 참조/모듈 가져오기·복사·원자 Save, 모바일 카드/상세/검색·기존 출력/새 정의 배치 | 공유/고정 반환 이름·잠정 빈 출력·영역/다중 선택·내부 흐름/async·일부 특수 핀/ABI/readonly, 나머지 원본 노드/지원 문맥·줌/검색/키보드·밀집 rail 정밀 수용. 속성+복사 혼합 Save는 기존 안전 차단을 유지한다 |
| 호출 ABI/공개 출력 | 공개는 호출 뒤 SourceContext에서 읽는 출력이다. 검증된 단일 소유 호출의 값↔ref 갱신과 생산자/소비자 검토·공동 명시 Confirm | 다른 호출 형태/소유 문맥·일반적인 임의 ABI 재연결까지 구현한 것이 아니다. 프로젝트/외부 공유 권한으로 해석하지 않는다 |
| 다중 구현/C# 변환 | 구현·실행 대상·출처 열거, 원본 C# preview/변환·정확한 source proof와 그룹 compiler Confirm의 서버 기반 및 이전 검증 | 실제 원본 UI의 모든 구현/대상 선택·전환·구현별 미저장 입력 격리/복원·Cancel/Save/실패/늦은 입력 수용은 전체 완료 아님. 첫 구현을 임의 선택하거나 원본을 덮어쓰지 않는다. `V508_UI_RESTORATION_SCOPE.md`의 마지막 서버 묶음과 v536 초기 실패 재검증 기록을 구분한다 |
| 전투 로그 | 원본 목록/상세/탭 구조로 실제 저장 Worker journal·채택 이력만 읽는다 | 기본 목록/상세 인스턴스·페이지 32개 필터에 한정. 추가 인스턴스·전 페이지 필터·대량/live·관련 요소 정밀 수용 잔여. 협의 backend 부재는 아래 표. `VALIDATION_V536_BATTLE_LOG.md` |
| 창별 실행/내보내기 | 창별 실제 process/lease, Play/Stop·협력적 Pause/Step·닫기/프로젝트 문맥, 원본 결과창과 실제 compiler/artifact 조회 연결 | Linux 실제 fixture 검사와 원본 치수 대조를 범위로 기록한다. 종료/재시도·내보내기 후속 결과는 `VALIDATION_V536_RUN_WINDOWS.md`에 별도 갱신. 내장 renderer/FPS·native Windows는 아래 제한 |
| 전체 화면 일치/통합 | 원본 HTML/CSS를 재사용하고 실제 캡처·일부 영역의 정밀 치수를 확인했다 | CSS 파일/특정 창 치수 일치가 전체 화면/상호작용 일치의 증거는 아니다. 누적 WIP 전체 수용·영향 회귀·Windows package/checkout/게시 미완료 |

## 실제 backend 부재로 미구현

- Helper 이미지 생성·자산 선택/교체·이미지 이력의 실제 제공자/자산 저장 계약. 원본 데모 이미지 순환을 사용자 이미지 생성으로 가져오지 않는다. 새 제공자·유료 호출·계정 권한을 만들지 않았다.
- 원본 전투 사안/협의 메시지·체력·차례·승자 결정·공유 Confirm 및 신문고 처리 계약. 저장된 작업 이력만 읽는 기능을 AI 협의/승자 결정으로 표시하지 않는다.
- 실행창 내장 프로젝트 렌더 표면과 렌더 FPS. 실제 프로세스와 협력적 frame 번호는 렌더 이미지/FPS가 아니다.
- 기존 Yogi 로컬 패키지/캡처와 별개인 실제 수신자 전달 등 아직 연결하지 않은 외부 동작. 데모 배포/전달 성공으로 대체하지 않는다.

이 항목은 단순 화면 배선만으로 완료할 수 없다. 원본 UI 잔여와 별도의 backend 기능 개발로 구분한다. 새 시각적 분기/루프·새 레이아웃·권한 확대를 도입하지 않는다.

## 검증 가능한 중간 빌드까지 필요한 일

1. 실행창의 현재 고정 묶음을 마치고, 위 표를 한 번 더 실제 결과와 대조한다. 미지원 기능은 명확히 비활성/오류 상태로 남긴다. 전체 UI 완료라는 이름으로 묶지 않는다.
2. 중간 빌드에 포함할 기존 연결 범위를 고정하고, 남은 **실제 결함**과 수용 미완료를 구분한다. Browser/Data·다중 구현/원본 특수 문맥 등 미수용 항목을 사용자에게 완료라고 표시하지 않는다. 새 backend 기능을 추가하며 중간 빌드를 무기한 미루지 않는다.
3. 누적 변경의 영향을 받는 통합 회귀를 실행한다. 우선 기존 Agent 공통 승낙/철회·프로젝트 소유권·Helper 전역/프로젝트 대화/입력·Browser/Blueprint Save/취소/Review/명시 Confirm·문서 전환과 실행 종료를 격리 fixture에서 확인한다. 실제 로그인/유료 추론이나 사용자 자료 실행은 필요하지 않다. 영향 없는 이전 전체 검사를 반복하는 단계는 아니다.
4. 정상 Windows 교차 빌드와 apphost exe/런타임 리소스·packs/UI 동반 패키지를 만든다. canonical resource 크기/hash, 일반 checkout의 참조/리소스 시작 검사, 테스트 전용 fault/provider API의 배포 노출 여부를 확인한다. 2026-10-23 로컬 Windows x64 중간 패키지와 구성/별도 cwd·SDK 없는 packaged 웹 시작 검증을 완료했다. 실제 Windows 실행과는 구별한다. 위치와 검사는 `VALIDATION_V536_LOCAL_INTERMEDIATE.md`를 따른다.
5. 검증 기록과 지원/미지원 목록을 함께 두고 승인된 `work/current`에 정상 커밋/푸시, remote SHA를 확인한다. main/Android/원본 ZIP·사용자 설정/자료를 보존하고 force push하지 않는다. 불확실한 외부 동작은 결과 확인 후 판단한다.
6. 산출물의 정확한 exe 경로와 .NET/WebView2 전제를 안내한다. 실제 Windows의 더블클릭/CWD·네이티브 제목 표시줄·DPI/IME 등은 별도 실제 호스트 수용으로 남기며 교차 빌드 성공과 혼동하지 않는다.

후속 ‘Helper가 에디터 작업을 수행하도록 확장’은 이 UI 상태 정리 후 **현재 제공하는 도구 목록과 실제 누락을 먼저 감사**하는 별도 작업이다. UI용 API가 존재한다는 이유로 Helper에 자동 노출하거나 최종 Confirm/프로젝트 실행/다른 프로젝트 권한을 부여하지 않는다. 이 문서는 새 기능이나 실제 계정 접근 동의를 생성하지 않는다.

2026-10-23 로컬 검증 갱신: 실행창 결합 전체8·핵심8·문서4·Data7·Agent fixture13과 Blueprint 전반10/집중 재개3을 확인했다. Windows 교차 패키지/구성/packaged 웹 시작은 통과했고 실제 native/전체 UI/게시/미게시 작업의 일반 commit checkout은 미완료다. 이번 요청은 커밋·푸시·업로드를 금지했으며 수행하지 않았다. 상세 실패/정정/검증 범위와 정확한 산출물은 [VALIDATION_V536_LOCAL_INTERMEDIATE.md](VALIDATION_V536_LOCAL_INTERMEDIATE.md)를 따른다.

후속 Browser 갱신: 독립 Data cold 재적용은 내용 지문과 최신 전체 CAS를 구분해 정상 복원을 허용하고 실제 타 소스/상속 스키마 변경은 차단했다. 이번 범위와 기존 c08d08f Windows ZIP의 Library 전달 실패(파일 ID 없음)는 `VALIDATION_V536_STANDALONE_DATA.md`에 구분했다. 이전 로컬 전용/미게시라는 아래 기록은 해당 시점의 이력이며 현재 게시 상태를 소급해 뜻하지 않는다.

Browser 후속 정리: 이번 유한 잔여와 이후 Blueprint 작업 단위는 `VALIDATION_V536_BROWSER_REMAINDER.md`, `V536_BLUEPRINT_REMAINDER.md`로 고정했다. 상단의 예전 로컬 전용/미게시 문구는 그 시점 이력이다. 최종 게시 여부와 새 Windows 교차 패키지는 해당 묶음의 검증 결과를 따른다.
