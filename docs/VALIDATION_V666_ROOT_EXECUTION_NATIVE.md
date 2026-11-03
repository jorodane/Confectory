# M12 native whole-body 공개 실행 진입

기준은 저장소 v666의 공개 함수 실행 분기/반환/직접 call 흐름과 기존 M11의 명시적 whole-body lift 계약이다. 기존 `sync-acyclic-switch-v1` Root에서 native 문맥이 있다는 이유만으로 공개 분기 전체 거래를 거절하던 경계를 연결한다. profile 자동 승격이나 C# 의미 변환은 하지 않는다.

공개 실행 어댑터가 native `public Invoke`와 중복되지 않도록 기존 M11처럼 그래프의 ordinary 진입을 명시적 `IInvoke` 구현에 둔다. 원래 instance `Invoke`, `this`/재귀, `IImports`/scoped import, CLR receiver와 CallerFilePath/CallerMemberName·CRLF 원문 위치는 그대로다. `IExecutionInvoke`는 기존 out과 별도의 비void 반환 캡처를 발행한 뒤 공개 결과 분기를 전달한다. 원문에 결과 enum/tuple/새 인수를 삽입하지 않는다. 예외를 실패 분기로 치환하지 않는다.

import 함수와 그 소유 scope object 헤더를 변경 없는 관측 멤버로 같은 checkpoint/receipt/Review/최종 CAS에 포함한다. 경로·종류·소유 namespace·source proof와 기존 문맥/인수 저장소 검증은 유지한다. object scope가 외부이면 기존 등록·readonly receipt 경계가 필요하며 이번 단위에서 소유 쓰기로 가장하지 않는다.

이번 새 사용자 흐름은 직접 소유된 이미 저장된 branch-capable whole-body Root, 명시 직접 Blueprint caller의 공개 분기 정의/반환/저장/실행이다. M11 완료분·copy 반환 편집을 새 잔여로 다시 세지 않는다. 공개 override IO 변경·비소유 원본 쓰기·구형 profile 자동 migration은 지원 요구가 아니다. 전체 공개 계약 갱신의 copy/자식·등록 import 등 실제 잔여와 종료 조건은 [유한한 마감표](M12_CLOSURE.md)를 따른다. native ordinary IInvoke 소비자와 자체 postCall wrapper는 새 분기 의미로 자동 해석하지 않는다.

검증은 생성 경계의 동기 void/out·비void/out 실제 실행, native 문맥/서명/인수/위치 변조 거절, scope/import/원문 Save 전후 경합, receipt 누락/변조·cold 복원·응답 재조회, 부분 Review/최종 CAS, 반복 이름/순서·명시 caller 연결을 포함한다. UI는 기존 팝오버/배치·Review 취소/Confirm·Undo/Redo·저장 실패·중단/늦은 응답·재시작을 확인한다. 독립 LF/CRLF와 새 패키지·전체 압축 복원본은 최종 동결 코드에서 별도로 실행하며 결과를 아래에 기록한다.

실제 Windows apphost/WebView2·모바일·DPI/IME, 독립 창·프로젝트 왕복과 전체 UI/Space 전달은 이번 교차 패키지 검사로 완료를 주장하지 않는다. 기존 원본·권한·main·과거 산출물은 보존하며 승인된 자체 검사 임시물의 증거 보존 후 수명관리와 최신/롤백 승격만 사용한다.

## 최종 동결 검증 결과 — 2026-11-03

제품·검사 동결 source는 `e64dea66427b25d4413b5a52bb393a3977fc47f6`다. 독립 LF 19단계·CRLF 16단계·새 Windows 교차 패키지/전체 복원/실패 수명관리 6단계, 총 **41단계 모두 신규 통과**했다. 재사용 검사는 0단계다. 각 checkout의 공개 실행/반환 runtime 17개와 소유 경계 2개, 합계 38개의 실행 검사를 포함한다. LF/CRLF의 native API·해당 UI normal/cancel/storage/conflict/loss/late, 기존 M11 receiver/재귀/CRLF/scoped import의 nonvoid/out 및 ref 저장소 회귀, ordinary 비void 반환과 LF private caller·최종 readonly lease 회귀를 실행했다.

새 생성 패키지와 전체 압축 복원본에서 같은 native UI 흐름을 다시 실행했다. 전체 파일·디렉터리 모드·크기·SHA manifest와 복원 무결성을 확인한 뒤 승인된 두 세대 저장소에 승격했다. Windows용 내용은 Linux의 dotnet/Chromium에서 교차 검사했으며 실제 Windows apphost/WebView2 실행을 뜻하지 않는다.

- 최종 실행 기록: `/workspace/artifacts/v536-verification-managed/runs/825330ebcbee43318f645fdd1ecfa3b3.json`
- 최종 지속 증거: `/workspace/artifacts/v536-verification-managed/runs/825330ebcbee43318f645fdd1ecfa3b3.zip`, SHA-256 `9c336320cf5b5a2d5c470785d25d1e69b01761171f04f40ceb2d012eed7017a2`
- 집중 증거: `/workspace/artifacts/v536-verification-managed/runs/922ab176bebf4c2a84cbda94202fd445.zip`, SHA-256 `9a5a6c569a4f50eadf0b3f55f7e104ae5253e4c9d523889e4ef083c23d3dffc1`. 최종 성공한 native void/out·비void/out 실행, API 7개·응답 유실 UI 9개 확인과 5개의 진단 실패를 함께 보존했다. 진단은 기존 Core의 public/native 일괄 거절(수정), 새 테스트의 팩 의존성·중복 선언·cold 초기화 및 공통 fixture의 사용하지 않는 postCall 서명 불일치였다. 마지막 경우 실제 저장 검증은 올바르게 거절했으며 완화하지 않고 독립 manifest로 바로잡았다.
- 최신 패키지 source `e64dea66427b25d4413b5a52bb393a3977fc47f6`, archive/SHA `e27850905958a9397cf020c4de87deb9ccb275a318fe51c95979e6fabd834cd0`, 2370파일·147디렉터리, 51,345,875 bytes, manifest SHA `099051460d68279b4dba20a444deb301b707b8000e380d91309dfd89f85cd94b`.
- 정상 롤백 source `29e22100810cabe094777c389fa9d23b10ee8dda`, archive/SHA `74fbb8f6b4f5a91b1895b544dba79726b77dc7aa685d4744c88342358e786128`, manifest SHA `dd7967666126abdfb8516cc900c2058cace08c8e8615aed74b5dc384be5067cd`.

집중 및 최종 실행의 직접 생성 임시 작업공간은 자식 프로세스 종료·증거 ZIP 검증 후 모두 정리했다. 승인된 최신/롤백 승격 이외의 기존 자료는 삭제하지 않았다. 최종 실행 전 여유 1874.41MiB, 정리/승격 후 1870.51MiB, 최종 단계 표본 최소 1874.35MiB였다. 별도 RAM 작업공간 예산 3GiB+512MiB, 추가 메모리 7GiB+1GiB, 지속 공간 144MiB(안전 64MiB 포함)를 낮추지 않았다. 최종 cgroup 메모리의 측정 최고치는 4220.04MiB다. 집중 기록의 순증가는 0.92MiB, 최종 기록은 3.90MiB이며 코드/Git·보고 문서 기록은 이 실행별 기준과 구별한다.

모델 중단 뒤에는 같은 실행 기록의 완료 결과·보관 SHA를 회수했으며 완료한 검사나 패키징을 재실행하지 않았다. 단계별 디스크 표본 최소값은 보관/승격 중 모든 순간의 최고 사용량을 뜻하지 않으며, 그 구간은 별도 144MiB 추가 공간 예산과 안전 여유로 확인했다.

제품 코드 변경 없는 보고 문서 후속 커밋은 위 동결 코드/SDK/NuGet와 동일한 제품 트리를 유지한다. main은 변경하지 않으며 work/current 게시와 원격 SHA·clean은 게시 후 별도로 확인한다.
