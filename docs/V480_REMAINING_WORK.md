# v480 남은 범위: 단일 우선순위 목록

현재 구현은 [화면/행동 지도](EDITOR_V480_STATUS.md), 최종 실행 근거는 [통합 검증](V480_INTEGRATED_VALIDATION.md)을 따른다. 아래가 **현재 남은 항목의 단일 목록**이다. 완료한 Data 비교/원자적 채우기, 명시적 선언 탐색, Home 저장/팩 수/편집 receipt, private Workspace 링크/삭제 Undo, 로컬 frame 제어/비권한 실행 기록, typed Set, 제한된 실제 field ref는 이 목록에 다시 넣지 않는다. 행 순서는 후속 작업의 기본 순서이며 P2/P3를 이번 작업의 승인 요청이나 구현 지시로 해석하지 않는다.

IMP1의 로컬 WebUI 및 native 정보/표시 프로필 연결은 [후속 검증](V480_NATIVE_HOME_PROFILES.md) 범위로 완료했다. Linux GTK/X11 실제 입력 결과, Windows managed compile, Android/browser metadata fixture를 구분하며 미실행 장치·전체 OS 조합은 기존 ENV 항목에 남긴다.

분류는 **구현 누락**, **설계 결정**, **권한 승인**, **환경 미검증**이다. 하나의 항목에 다른 원인이 섞이면 행을 나눈다. 예를 들어 협업 서비스 자체의 부재는 구현 누락이고, 나중에 실제 계정으로 검증하는 허용 여부는 권한 승인이다. 내부 파일 형식이나 저장소 구현 선택은 사용자 답변 대기로 돌리지 않는다.

| 순서 · ID | 분류 | 실제 남은 범위 | 후속 완료 기준 · 현재 의존성 |
|---|---|---|---|
| P1 · IMP2 | 구현 누락 | 브라우저 전체 tree/category grouping UI, 현재 명시적 parent/schema 탐색 밖의 분류·임의 깊이 탐색 | 실제 선언 ID·소유/등록 경계를 유지한 조회/탐색·독립 창·검색/cold 검사. prototype Category를 CELEM category/concept와 동일시하는 부분은 DEC1을 먼저 결정 |
| P1 · IMP3 | 구현 누락 | 자동 전체 필드 합집합/표시, 사용자 계산 열, 일반 선택 범위 확장 | 기존 명시적 쓰기 대상·field/source/schema CAS를 보존하고 조회·정확한 값·선택/cold/오류를 검사. 계산 실행 의미가 필요하면 DEC3/DEC4 선행; 현재 Data/채우기 완료와 분리 |
| P1 · IMP4 | 구현 누락 | 객체/함수 화면의 원클릭 밸런스·테스트 실행 등 prototype 보조 행동 | 실제 실행/결과/실패와 소유 범위를 연결하고 UI 및 compiler/runtime 근거 마련. 화면의 성공 표시로 대체하지 않음 |
| P1 · IMP7 | 구현 누락 | Workspace의 일반 이동/연결 Undo, native reparent 이전의 전체 문서 Undo 이력 | private 문서/보기 정체성·미적용 입력을 보존한 역변경 명세와 cold/redo/분기 검사. 이미 지원하는 private 삭제 Undo와 구분. 소스 집합 변경은 DEC2 밖에서 추가하지 않음 |
| P1 · ENV4 | 환경 미검증 | [측정된 부하/검사 한계와 잔여 불확실성](V480_ENV4_DIAGNOSIS.md) | 두 graph timeout은 4 CPU/6 gate에서 작업 진행 중 재현됐고 같은 source의 2 gate에서 원래 deadline 내 통과. native Engine의 미관측 lease 순서와 Home 조회 PID 오판은 검사 보정 후 같은 부하 통과. 최초 native ButtonGame wait phase는 재현하지 못했으며, 추가 Pause 1회·cache/시작 이력·PID 1의 zombie 잔류 영향은 미확정. 환경 원인으로 일괄 단정하지 않음. 새 사용자 결정 불필요 |
| P2 · IMP6 | 구현 누락 | Run 창의 실제 render surface embedding, 비참여 runtime/Android/browser의 frame 제어 연결 | surface/수명/입력·협력적 frame 프로토콜을 구현한 뒤 실제 플랫폼으로 검사. 현재 Linux 별도 프로세스 Run/Stop과 managed compile로 완료 처리하지 않음. 영속 권한 인계는 DEC5 별도 |
| P2 · IMP5 | 구현 누락 | 실제 inbox 사건/actor/membership/co-worker 요청·수락·차단·채팅/news·room/recipient/ack, Yogi 수신/중복/실패, Helper 이미지/사용량·전송, 온라인 market/catalog/publisher/install 서비스 | 각 서비스 소유/식별·권한·멱등성·실패/단절·ack·복구를 실제 구현하고 먼저 owned fixture로 검증. 기존 로컬 scope/journal/snapshot은 전체 서비스 구현이 아님. 실계정 검증은 AUTH1/2 별도 |
| P2 · DEC1 | 설계 결정 | prototype Category/개념 분류와 CELEM category/concept의 전체 제품 의미 | 분류와 실제 선언 parent/contain/schema의 대응·편집 수명을 확정. 현재 명시적 관계 투영은 계속 유효; 일반 폴더로 임의 치환하지 않음 |
| P2 · DEC2 | 설계 결정 | 선언 소스 삭제/참조 치환, 소유 집합 생성/삭제 전체 Undo | 참조 무결성·manifest 등록·원자적 역변경·외부 변경/CAS/충돌 의미를 먼저 확정. 현재 graph 노드 제거/private 보기 삭제의 지원을 소스 삭제 승인으로 확대하지 않음. 이번 작업 범위 밖 |
| P2 · DEC3 | 설계 결정 | 제약 field mutable ref·array/reference ref, compound/function live property, enum/Vector3/일반 사용자 타입 ABI | null/finite/schema 제약·실제 storage/alias·호환 profile/instance 버전·validator/lowering/CLR 의미를 확정. 현재 general 단일 bool/int/long ref와 general/reference Set만 유지. 이번 작업에서 확장하지 않음 |
| P2 · DEC4 | 설계 결정 | 계산식 int/long overflow의 오류/wrap 의미 | 계산식 실행 기능에 착수할 때 사용자 정책을 확정하고 실제 compiler/runtime 경계 검사. enum int32 항목 범위 검사와 별개. 기존 C# 연산을 유지하며 이번 통합 검증의 차단 아님 |
| P2 · DEC5 | 설계 결정 | 새 호스트의 durable 실행 소유권 인계·프로세스 채택 | 인증·권한/세션 수명·재연결/중복·자동 재실행 금지를 포함한 별도 설계. 현재 cold 기록은 owner-unavailable이며 권한이 없음. 이번 작업에서 인계하지 않음 |
| P3 · AUTH1 | 권한 승인 | 실제 Agent/provider 계정 로그인·유료 모델/이미지·협업 서비스 실제 호출 | 대상·계정·비용·허용 행위를 특정한 승인 후 진행. 이번 작업은 owned fixture만 사용하며 새 승인 요청이 필요하지 않음 |
| P3 · AUTH2 | 권한 승인 | 사용자 PC 실제 설치, 실기기 서명/배포·시장 게시/설치 | 설치 대상·파일·서명/배포 효과를 구체화한 승인 후 진행. 현재 코드/관리 프로필 검사와 별개; 지금 설치하지 않음 |
| P3 · ENV1 | 환경 미검증 | Windows native 창·입력/접근성, Linux의 모든 실제 desktop/접근성 조합 | 해당 OS에서 실제 창/입력/문서/복구/접근성 행렬 실행. 현재 Linux X11 dummy의 소유 Engine/Button 검사는 해당 장면의 증거이며 전체 OS 검증 아님 |
| P3 · ENV2 | 환경 미검증 | 실제 Android 기기·서명/내보내기/설치, browser 배포 및 embedded surface | 필요한 실제 환경과 AUTH2 확보 후 compiler 성공과 장치 성공을 나누어 기록. 기존 Android 설정을 이번 작업에서 수정하지 않음 |
| P3 · ENV3 | 환경 미검증 | 실제 외부 Agent/협업/시장 서비스의 연결·장애/복구 | 해당 서비스 구현(IMP5) 및 AUTH1/2 후 실제 환경에서 검사. simulated transport·공식 metadata 조회·설치 안내를 실계정 성공으로 계산하지 않음 |

이번 통합 범위를 마치는 데 사용자의 새 결정은 필요하지 않다. DEC 항목은 다음 기능 범위를 넓힐 때 필요한 결정이고, AUTH 항목은 실제 외부 작업을 시작할 때의 권한 경계다. main·ZIP·Android 설정 보존과 새 ABI/제약 ref/overflow/소스 삭제·치환/영속 권한/CSP/실계정 설치 제외 조건을 유지한다.
