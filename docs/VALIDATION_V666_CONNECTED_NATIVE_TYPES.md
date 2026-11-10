# v666 C# 연결 함수의 고급 타입 전환 검증

최종 runtime source: `50d07f3be05f39a80de79fcd0e15985a9c1ae507`. [지원 경계](V666_CONNECTED_NATIVE_TYPES.md)와
[제품 파일별 canonical 해시](v666-connected-native-types-delta.json)를 기준으로 고정했다.
원본 레이아웃/CSS·함수 ID·공개 override 계약·권한을 유지한다. 선택한 타입 계약과 사용자가
명시한 C# 계획만 바꾸며 원문을 자동 변환하지 않는다.

## 최종 신규 검증

신규 **45단계, 재사용 0**: LF17, CRLF18, owned IPC1, package/전체 복원/실패 수명 관리9.
개발 기록을 최종 통과 결과로 재사용하지 않았다. 독립 LF/CRLF checkout은 빈 엔진 cache에서
빌드하며, 각 runtime source와 실제 패키지/압축 복원본을 구별한다.

- 순수 후보는 원래 함수/구현/직접 C# 호출자의 정확한 계약과 두 명시 본문, 등록 외부 타입의
  읽기 observations를 보존하고 외부 쓰기나 provider 실행을 추가하지 않는다.
- 잘못된 C#, 빠진 호출자 계획, 변조/누락된 타입 증거와 본문 hash는 전체 Save를 거절한다.
  임시 저장·cold·compiler Review 후 호출자 원문 변경도 최종 CAS로 거절한다. 정확한 복원과
  새 Review/Confirm은 오직 명시한 함수/구현/호출자만 반영하며 실제 native 실행31을 확인한다.
- 확정 뒤 같은 계약의 C# 편집도 등록 타입을 새로 관찰하고 실제 실행32를 확인한다. 호출자
  바이트와 mtime는 유지한다. 기본형 편집, 선언 전용 타입 전환과 기존 native module 실행을
  같은 최종 코드에서 회귀 검사했다.
- 실제 Linux engine + Chromium: 원본 460px 카드/420px 상세창, struct/enum/interface 배열의
  입력/out/반환 선택, 기존 C# 구현 선택과 보호된 본문 입력, 취소·Undo/Redo·별도 창·재시작,
  원자 Save·반복 Save 차단·명시 Review/Confirm.
- checkpoint 쓰기 거절, 원본 변경에 의한 저장 준비 거절, 응답/정산 조회 유실과 cold 복구,
  늦은 이름·후속 Save·재시작을 확인한다. 타입/본문 계획을 잃거나 중복 저장하지 않는다.
- 수락한 mapping과 서명이 같은 경우에만 늦은 이름에서 수락한 본문 계획을 제거한다.
  다른 mapping은 유지한다. 현재 receipt adapter와 게시된 이전 UI adapter의 거절을 실제
  Node 실행으로 확인했다. 이전 전체 reader/compiler 바이너리 실행으로 주장하지 않는다.

## 개발 중 진단과 복구

게시본에서 원래 C# 함수와 호출자가 실제30을 실행하지만 고급 타입 선택은 거절됨을 먼저
확인했다. 개발에서 선택한 등록 외부 타입이 후보 컴파일러 사전에 빠지는 제품 누락을
재현했다. 검증된 선택 증거의 정확한 header만 읽기 전용으로 전달하고 source observations와
같은 최종 lease로 보호하도록 수정했다. 외부 원본을 쓰기 대상으로 승격하지 않았다.

개발 실패와 모든 원문/로그를 보존했다. copy2의 보존 시각 때문에 이전 authoring DLL이
재사용된 경우는 실제 바이너리에 새 profile이 없음을 증명한 뒤 명시 Rebuild했다. 바꾸는
C#은 readGuards가 아니라 쓰기 baseline/sources로 보호되는 기대값을 수정했다. 시험 호출자의
null 배열은 전체 nullable 컴파일에서 정상 거절됐으므로 명시적 빈 배열로 고쳤다. 그 이전의
미반영 결과만으로 CAS 통과를 확정하지 않고 유효한 코드로 최종 검증을 새로 수행했다.
진단 host의 잘못된 profile 선택, 보호된 편집기 전체 fill로 본문이 바뀌지 않은 시험 조작,
이전 엔진 경로를 재사용해 정상 리소스 무결성 거절이 난 실행 보고서도 각각 구분했다.
보호된 본문 구간에 실제 입력하고 이미 완료된 새 엔진 산출물을 회수했으며 제품의 검사나
컴파일 규칙을 약화하지 않았다. 최종45단계는 이 수정 후 모두 새로 실행했다.

최종 실행 중 동일 환경 연결 전환으로 출력 pipe가 닫혀 LF Release 통과 직후 `Broken pipe`가
발생했다. 진행 중 검사는 없었고 완료5단계 기록과 evidence
`dbe58fd82f0c2d4936ae394be35849cb25e513a5a14a15cd7c2962c630fb4382`를 보존했다. 관리 실패 정리로 임시 컴파일 산출물이 없어
검증을 이어갈 재생성이 필요했다. 같은 환경/SDK/모델과 고정 코드를 유지하고 stdout을
owned 파일로 남기는 방식으로 복구했다. 해당5단계는 최종45 통과로 재사용하지 않았다.


| 기록 | evidence SHA256 |
|---|---|
| 최종45단계 | `c7826e63a318f3f4f92f1c1f7a86d27081e8e1969254e729c7218b7fac18f81c` |
| 개발·baseline 재현/실패·복구 | `da3d63e7894d14da56b2287e85b9f458b2ee92ea300293ed4ac76993e2a3efd7` |

최종 기록: `/workspace/artifacts/v536-verification-managed/runs/4dde0563a29d45b8b72d8fdd277ece56.json`. 보관 evidence ZIP의 전 파일 해시와 manifest를 재검사했다.
정상 검사를 중단하거나 중복하지 않았다. owned RAM workspace는 증거 보관 후 정리했다.

## 패키지·보관·공간

| 세대 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | `50d07f3be05f39a80de79fcd0e15985a9c1ae507` | `d35fef4392874e683f36f6a207a9d651e68094b340d2967b5b85df78665014e5` | 53973789 |
| rollback | `0d693a09f79c781c805ecc2a09f1de913775fa50` | `3ffac7b765dcec0181e721ed90b5900fda33288547071ad63dc2668beebadde3` | 53972299 |

새 Windows 교차 package 생성·구조/무결성 probe, 그 안의 실제 Linux engine UI,
전체 압축 복원본의 API/storage/lost-response/late-input 및 실패 수명 관리를 새로 확인했다.
실제 Windows 실행은 아니다. 검증 후 이전 latest를 rollback으로 유지했고 이전 rollback ZIP
한 세대만 승인된 관리 규칙으로 교체했다. 과거 evidence와 원래 checkout은 보존했다.
SDK/seed와 알려진 관리 archive의 읽기 FD cache advice만 사용했고 전역 cache는 건드리지 않았다.
추가 메모리9GiB+여유1GiB, RAM 파일4GiB+여유512MiB, evidence512MiB·디스크 여유64MiB를
유지했다. 디스크 25,600,008,192B에서 25,595,162,624B
(약 23.84GiB), 관찰 cgroup peak 8,994,828,288B다.

## 유한 잔여와 실제 한계

고급 Blueprint ABI 대응, 살아 있는 reference의 실제 객체/접근자 연결, module async/공개
실행 요구와 기존9행의 multiple/함수 필드 native 생성이 남는다. 모듈 결과형은 기존 함수
계약 DLL과 정보 DLL의 의존성 순환을 해결해야 하며 원래 결과 ABI를 복제/변환하지 않는다.
동기 호출자는 명시적 async 전환 전 오류라는 확정 정책을 유지한다. 선언 data/default나
객체 ID를 살아 있는 참조의 값 snapshot으로 쓰지 않는다. M11/M12/M4 완료 범위를 새 회귀
없이 재개하거나 선택적 조합·migration을 필수로 늘리지 않는다.
이전 reader의 연결 scope 거절과 구 nominal/enum parser 제한을 유지한다. 실제 Windows/모바일
기기·전체 UI는 미검증이며 초기 빈 화면의 원인은 미확정이다.
