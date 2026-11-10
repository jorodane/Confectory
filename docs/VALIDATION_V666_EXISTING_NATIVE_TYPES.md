# v666 기존 정보 기능의 native 타입 전환 검증

최종 runtime source: `0d693a09f79c781c805ecc2a09f1de913775fa50`. [지원 경계](V666_EXISTING_NATIVE_TYPES.md)와
[제품 파일별 해시](v666-existing-native-types-delta.json)를 기준으로 고정했다.
원본 v666 레이아웃/CSS, 소유/등록 외부 원본, 함수 ID와 기존 C# 본문을 유지한다.

## 최종 검증

신규 **45단계, 재사용 0**: LF17, CRLF18, 소유 IPC1, package/전체 복원/실패 수명 관리9.
개발 기록은 최종 검증 결과로 재사용하지 않았다. 각 독립 checkout은 빈 엔진 cache에서 빌드한다.

- 실제 Linux engine + Chromium: 원본 460px 카드/420px 상세창, 지원 struct/enum/interface와
  배열의 입력/out/반환 선택, 검색, 비활성 경계, 취소, Undo/Redo, 별도 창, 반복 Save,
  저장 전후 cold 복원과 명시적 compiler Review/Confirm.
- 실제 checkpoint 쓰기 거절, 원본 변경에 의한 저장 준비 거절, 응답과 정산 조회 유실,
  늦은 이름 입력과 후속 Save. 원문/선택 증거/checkpoint를 보존하고 중복 저장을 발행하지 않는다.
- 없거나 변조된 사용처 부재 증거, 신규 요구 계약, Review 뒤 사용처 변경은 전체 후보를
  거절한다. 정확한 복원 뒤 새 Review/Confirm만 수락한다. Confirm 전 첫 구현 작성은 차단한다.
- nominal→기본형 되돌리기와 Confirm 후 같은 세션의 새 이름 Save를 실제로 확인했다.
  새 함수 생성, 기본형 편집, struct/enum/interface의 실제 native 실행을 회귀 검사했다.
- 현재 receipt adapter의 정확한 선택/늦은 입력 보존과 게시된 이전 UI adapter의 거절을
  실제 Node 실행으로 확인했다. 이전 전체 reader/compiler 바이너리 실행은 하지 않았다.
  보호 초안 v2 및 generated nominal/enum의 구 parser 제한을 숨기거나 migration하지 않는다.

## 개발 중 실패와 복구

개발24단계의4개 fixture 실패와 로그를 보존했다. 기존 Required 함수를 바꿔 다른 모듈 계약까지
깨뜨린 시험 데이터를 독립 Consumer 요구 계약으로 분리했고, 물리 원본 변경 후 살아 있는
SlotContext의 정상 거절은 fresh metadata projection에서 구분했다. 나머지는 `elements/`
경로가 빠진 기대값과 저장 준비 거절을 무시하고 applySlots 응답만 기다리던 검사 대기 조건이었다.
마지막 충돌 재실행은 준비 단계의 실제 거절과 applySlots 미발행, 입력/checkpoint 보존,
원상 복구 후 cold 재시도·Review/Confirm까지 통과했다. 제품을 약화해 검사를 통과시키지 않았다.

별도로 게시본의 Confirm 직후 같은 세션 저장 거절을 먼저 재현했다. 수락 후에도 남은 receipt가
과거 manifest 읽기 증거를 상속하던 제품 결함이었다. 활성 atomicEditGroup이 있을 때만
증거를 상속하도록 수정했고 신규/기존 함수 양쪽에서 최종 LF/CRLF 회귀를 통과했다.

| 기록 | evidence SHA256 |
|---|---|
| 최종45단계 | `19f344e44933d8a642e685a50fbfde199910d6b8decefd24e6d47cc886aef208` |
| 개발24단계와 baseline 재현 | `306801fdc64e045ac5f0297350010102ed7d0328a471869ec2286bb045a745ad` |

최종 기록: `/workspace/artifacts/v536-verification-managed/runs/a0ce0282796b44bdb48b90406002ed9e.json`. evidence ZIP 전체 파일 해시와 manifest를 다시 확인했다.
정상 실행 중 검사를 중단하거나 중복하지 않았으며 owned RAM workspace는 증거 보관 후 정리했다.

## 패키지와 공간

| 세대 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | `0d693a09f79c781c805ecc2a09f1de913775fa50` | `3ffac7b765dcec0181e721ed90b5900fda33288547071ad63dc2668beebadde3` | 53972299 |
| rollback | `3990e5dfb96fe85a753f19e846b6f93b4fd4d0e9` | `7a79f5978ba0284e94c401a8f253959d49d6d4e158cb12ee80fc34e867ca078a` | 53966845 |

새 Windows 교차 package 생성·구조/무결성 probe, 그 안의 실제 Linux engine UI,
전체 압축 복원본의 API/storage/lost-response/late-input와 실패 수명 관리를 새로 확인했다.
실제 Windows 실행을 뜻하지 않는다. 검증 뒤 이전 latest를 rollback으로 유지했으며,
기존 rollback ZIP 한 세대만 승인된 관리 규칙으로 교체했다. 과거 evidence는 보존했다.
SDK/seed와 알려진 관리 archive의 읽기 FD cache advice만 사용했다. 전역 cache 정리는 없다.
추가 메모리9GiB+여유1GiB, RAM 파일4GiB+여유512MiB, evidence512MiB·디스크 여유64MiB의
기준을 유지했다. 디스크 25,611,493,376B에서 25,606,606,848B
(약 23.85GiB), 관찰 cgroup peak 8,822,874,112B다.

## 잔여와 검증 한계

연결된 함수의 고급 nominal ABI 대응, 살아 있는 reference의 객체/접근자 연결과 수명,
module async/공개 실행 요구 및 기존9행의 multiple/함수 필드·고급 Blueprint 대응이 남는다.
모듈 고급 계약은 기존 Task/실행 결과 ABI와 계약 DLL 의존성을 함께 연결해야 한다.
동기 호출자는 명시적 async 전환 전 오류로 표시한다는 확정 정책을 유지하며 자동 대기/전환은 없다.
M11/M12/M4 완료 범위를 다시 열거나 조합별 선택적 migration을 필수로 늘리지 않는다.
초기 빈 화면 원인은 미확정이다. 실제 Windows/모바일 기기 및 전체 UI는 검증하지 않았다.
