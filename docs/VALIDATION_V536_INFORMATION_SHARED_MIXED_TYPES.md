# v536 공유 함수의 서로 다른 scalar 편집 종류 — 2026-10-25

같은 정보 창에서 A의 값 입력 타입만, B의 일반 out 타입만 바꾸고 기존 임시 저장을
한 번 누르는 단위다. 수정 전 격리 fixture에서 두 단일 closure가 각각 유효하지만
그룹은 모든 함수의 입력/out 동시 변경을 요구하여 거절함을 재현했다. 기존 v536
UI·레이아웃·리소스·함수/계약 ID·C# 원문·권한은 변경하지 않는다.

## 종료 조건과 구현

직접 소유 함수 2~8개의 입력 전용·out 전용·입력/out 동시 scalar 타입 편집을
함수별로 구별한다. 이 혼합 그룹에는 전체에서 최소 한 입력 타입 변경과 한 out 타입
변경이 있다. out을 유지한 채 모든 함수의 입력만 바꾸는 그룹은 이 단위에 추가하지
않았다. 이름·수·위치·역할·반환, 직렬 code/export callee·call/export
caller와 이미 검증한 고정 로컬 import 경계는 유지한다. bool/int/long/float/double/
string의 기존 exact 타입 검사를 사용한다.

입력이 바뀐 함수에만 원래 사용처/새 값/해제 증거를 요구하고, 출력이 바뀐 함수에만
writer/호환 소비 출력 선택을 요구한다. 입력 전용 함수의 출력 계획 및 출력 전용
함수의 입력 대체를 허용하지 않는다. 각 closure를 원래 스냅샷에서 먼저 검증한 뒤
기존 내부 overlay에 합친다. 원래 source 관측·최종 hash·단일 checkpoint CAS 및
receipt/Review/Confirm은 그대로이며 중간 결과는 저장하지 않는다.

## 실제 fixture와 검사

원래 A.count(long)→B.amount(long), B.count(long)→Caller 반환 연결이다.
A.amount만 string으로 바꾸고 명시 한글/emoji 값과 원래 연결 해제를 선택한다.
C# 노드의 기존 long amount 사용처에는 정확한 `9223372036854775800`을 명시한다.
B.count만 double로 바꾸고 writer는 real(double), 기존 long 소비는 B.return(long)을
선택한다. A.count→B.amount와 A의 writer, B의 code 인자 및 두 C# 본문은 보존한다.
기존 Power `9223372036854775806`, 실행 순서와 intent도 유지한다.

`tests/web/v536_information_shared_mixed_types_{fixture,native}.py`와 기존 API/UI
harness를 사용한다. API/UI는 `CONFECTORY_SHARED_MIXED_TYPES=1`로 선택하며 기존
`CONFECTORY_SHARED_IO`/local-import/기본 반환 경로는 유지한다. 기본/독립 창의
각 함수에 실제로 바꾼 타입만 조작하고 필요한 원래 remap 패널을 모두 확인한다.
순수 후보 역순·원래 hash, 마지막 계획 오류 전체 미적용, 실제 source/CAS 경합,
취소·Undo/Redo·거절 후 Undo 재시도·저장 실패·응답 유실 결과 조회·프로젝트 전환·
미저장/저장 재시작·Review 취소/Confirm과 최종 파일을 확인한다.

기존 입력/out 동시 검사에서 혼합 종류를 거절하던 음성 사례는 이번에 지원되는
경계다. 이를 새 양성 검사로 옮기고, 기존 음성 사례는 여전히 지원하지 않는
타입 변경+이름 변경으로 고정했다. 새 검사에는 입력 전용+출력 전용뿐 아니라
각각과 입력/out 동시 편집을 섞은 양방향 순서도 포함한다. 잘못된 해제 증거·
writer/타입·source/CAS의 거절 검사는 유지한다.

집중 수용 11흐름/28확인(추가 혼합 양성 사례를 포함한 최종 순수 검사 5확인),
기존 8개 공유 scope 영향 회귀 31확인, 이전 입력/out 동시 화면 회귀 2확인이
모두 통과했다. 원래 460px 기본/독립 창과 서로 다른 실제 remap 패널을 확인했다.
UI 파일·고정 리소스 74개의 해시/크기는 이전 게시본과 같다. Native Release는
warning/error 0이다. 상세 기록은 [집중 검사 증거](evidence/v536-information-shared-mixed-types/focused-verification.json)에 둔다.

clean checkout·새 교차 패키지 결과는 완료 후 별도 기록한다.

## 고정 잔여

8행은 미완료다. out이 있는 함수들의 입력 타입만 변경하는 그룹, 더 넓은
입력/out/반환/정의 변경 결합, 값 입력 수/ref/역할/순서,
수동 C#/native·혼합 target, nested/private/whole/postCall 및 copy/상속/등록/정보
속성 혼합은 별도다. 현재 scalar 밖 선택 타입도 남는다. 안전한 거절은 완료로
표시하지 않는다. 기존 단일 함수 지원과 이번 여러 함수 결합을 구분한다.

7행의 새 독립 copy 계약/ID/기능/호출 재지정 정책은 답변 대기이며 사용하지 않는다.
9행 named 정보/참조/외부 함수 타입 및 표시명/native ID 분리, I6/B2·A4~A6·M4/
M11/M12, Helper 실제 편집 도구는 후속이다. 전체 UI·Windows/WebView2·모바일 기기
실행 및 Library 전달은 완료가 아니다. 사용자 프로젝트/계정/유료 추론은 사용하지 않는다.
