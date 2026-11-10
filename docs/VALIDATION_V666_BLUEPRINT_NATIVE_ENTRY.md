# Blueprint 구현의 고급 entry/반환 검증

Runtime source `a55bf720be4265505d0c1f2b67c38276baf1040d`를 고정했다. [지원 경계](V666_BLUEPRINT_NATIVE_ENTRY.md)와
[제품 canonical 해시](v666-blueprint-native-entry-delta.json)를 따른다.
최종 검증 기록 commit은 문서만 더하고 제품 바이트는 위 runtime source와 같다.

## 신규 검증

**신규45단계·재사용0**: LF17·CRLF18·owned IPC1·package/전체 복원/실패 수명관리9.
개발 결과를 최종 통과로 재사용하지 않았다. 빈 엔진 cache의 독립 LF/CRLF checkout에서
각각 빌드하고 API/UI/실제 source 컴파일·실행을 확인했다.

- 직접 소유한 일반 직렬 Blueprint의 int 입력/반환을 같은 정보 struct로 바꾼다.
  현재 root 입력을 원래 반환 writer/실제 연결된 exit에 명시 선택하고 C# 호출자 본문을
  직접 작성한다. 원래 함수/구현/노드/핀 ID·좌표·entry·실행선·반환 위치는 유지한다.
  일반 writer와 call 뒤 반환 exit를 각각 실제 실행30→31로 검증했다.
- 바꾸는 writer 하나라도 빠짐·잘못된 값/타입·누락 C# 계획·틀린 C#·오래된 graph/scope
  증거는 checkpoint/원본 쓰기 없이 전체 거절한다. copy·opaque code·async frame은
  새 타입 선택 권한으로 승격하지 않는다.
- 전체 후보의 cold 복원과 compiler Review를 확인했다. Review 뒤 의미가 같은 공백만
  추가한 graph도 최종 CAS로 거절하고 정확 복원·새 Review/Confirm만 반영한다.
  변하지 않는 C#·타입 정의·등록 외부 원본 bytes는 유지한다.
- Linux native engine + Chromium의 원래460px 카드/420px 상세창에서 입력·반환 타입 선택,
  원래 출력 대응 창의 정확한 source 선택, 보호된 C# 호출자 편집·취소, Undo/Redo·별도 창·
  재시작·원자 Save·명시 Review/Confirm을 확인했다. 확정 뒤 기존 Blueprint 편집기로
  수락한 nominal entry와 원래 export 노드를 열고 추가 source 생성/쓰기가 없음을 확인했다.
- checkpoint 쓰기 거절·원본 변경·명시 취소·apply/정산 조회 응답 유실과 cold 회수·늦은
  이름 및 후속 Save를 확인했다. 같은 계약/본문 계획을 중복 적용하거나 새 입력을 버리지 않는다.
- 현재 최종 코드에서 이전 일반 Blueprint 호출자의 구조체/enum/interface 배열 입력 전달,
  명시 C# 구현·source/CAS 보호·실제31을 다시 확인했다. 미사용 함수 전환, 기본형 정보 기능
  UI와 receipt adapter도 새로 회귀 검사했다. module async나 live reference 실행으로 세지 않는다.
- 새 Windows 교차 package 생성·구조/무결성 probe, 포함 Linux engine의 실제 UI와 전체
  압축 복원본 API/storage/lost-response/late-input·실패 수명 관리를 모두 새로 확인했다.

## 개발 진단과 이전 버전

개발12단계와 실패1개를 보존했다. 첫 exit fixture는 entry가 비어 있어 원래 실행선이
없고 기존 기본 반환0을 수행했다. 원래 no-op call에서 exit로 연결되는 실행선이 있는
fixture로 고쳐 baseline30과 전환31을 확인했다. Core의 생성/종료/반환 의미를 바꾸거나
없는 실행선을 제품이 자동 생성하도록 하지 않았다. 초기 잘못된 fixture를 제품 회귀로
단정하지 않았고 실패 원문·로그를 유지했다.

직전 package source `a3659c2445b736db6234ce097b1f64cfbd962bc7`의 ZIP/추출 authoring 파일
해시를 확인하고 이전 바이너리의 readonly metadata 질의를 실제 실행했다. 이전 scope는
Blueprint 구현 전환을 거절했다. provider 실행이나 source 쓰기는 하지 않았다. 이전 전체
workspace reader 실행으로 주장하지 않으며 기존 nominal/enum parser 제한·명시 거절과
자동 migration 없음은 유지한다.

| 기록 | evidence SHA256 |
|---|---|
| 최종45단계 | `6f83fc15422fa2b92f8456a5bf0c9309522b55d31a2dd55d4203c349caf83fcc` |
| 개발·원래 실행·exit fixture 진단/복구 | `74ac2f865d25f388a28ab42d703e6e31f0b0ba923c07b3a4b9812083b56e332c` |

최종 run record `/workspace/artifacts/v536-verification-managed/runs/390c62fd5d9f4c1a941ba3791162b8a5.json`. evidence ZIP의 manifest와 전 파일 해시를 재검사했다.
원본·증거를 보존하고 소유한 재생성 가능 임시 산출물만 기존 관리 규칙으로 정리했다.

## 보관·공간·잔여

| 세대 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | `a55bf720be4265505d0c1f2b67c38276baf1040d` | `5541e30476e3d6708c32592ea4d4a1f78f2e77253a95aafaa6cb66689a8ece5c` | 53976388 |
| rollback | `a3659c2445b736db6234ce097b1f64cfbd962bc7` | `e364458ab6499cb361f48073a16ac57a25d137bd87ecfe7db36895882645cd09` | 53975188 |

기존 latest를 rollback으로 유지하고 이전 rollback 한 세대만 승인된 관리 규칙으로 교체했다.
추가 메모리9GiB+여유1GiB·RAM 파일4GiB+여유512MiB·evidence512MiB·디스크 여유64MiB를
유지했다. SDK/seed와 알려진 관리 archive의 읽기 FD cache advice만 사용했으며 전역 cache·
과거 evidence·원래 checkout은 정리하지 않았다. 디스크 여유 25,575,600,128B
(약23.82GiB), 관찰 cgroup peak 9,050,873,856B다.

일반/opaque C# code 노드와 private Blueprint의 명시적 고급 ABI 대응, 살아 있는 reference의
실제 객체/접근자 연결, module async/공개 실행 결과의 계약-only closure/DLL 순환 처리와
기존9행 multiple/함수 필드 native 생성은 남는다. 선택 조합을 새 필수 행으로 늘리거나
M11/M12/M4를 새 회귀 없이 재개하지 않는다. 현재 입력/반환 연결에 미결정 정책은 없다.
실제 Windows/모바일·전체 UI는 미검증이며 초기 빈 화면 원인은 미확정이다.
