# 관측된 C# 노드 매개변수 타입 최종 검증

일반 C# 노드의 현재 frame 타입 선택·기존 타입 보존과 명시 매개변수/값/본문의 원자 저장을
`b63020847c70faa18a9e60f48fae812b5caeaf57`에서 고정했다. 제품4파일은 delta의 해시와 일치한다.
후속 결과 문서 커밋은 제품·테스트·실행 코드를 바꾸지 않는다.
[실제 지원 경계](V666_NATIVE_PARAMETERS.md)를 전체 고급 ABI 또는 전체 UI 완료로 합산하지 않는다.

최종 **46단계(신규41·동등 재사용5), 실패0**을 통과했다. 개발 증거를 최종 통과로 재사용하지 않았다.

| 구분 | 신규 실행·동등 재사용 |
|---|---:|
| LF 독립 checkout·빌드·새 UI/DOM/receipt·기존 회귀 | 신규15·동등4 |
| CRLF 독립 checkout·빌드·새 UI/DOM/receipt·기존 회귀 | 신규16·동등0 |
| 관리 IPC 수명 | 신규0·동등1 |
| 새 Windows 교차패키지 생성/구조 검사·제품 실행·전체 압축 복원·실패 수명관리 | 신규10·동등0 |

새 테스트는 실제 매개변수 편집 DOM, 원래 canvas/핀 타입 팝오버와 root·독립 소유 함수 private
frame이다. DOM 단독 검사는 작은 host fixture이며, 별도 UI 검사는 실제 editor engine·checkpoint·
compiler를 사용한다. 기존 receipt·whole-body API/UI·retained UI·primitive 매개변수/helpers/Task
회귀를 새로 실행했다. IPC와 LF 선언·헤더 아이콘·DOM·receipt5건의 엄격한 동등 재사용은 아래에 구별한다. 기존 테스트 코드 재사용과
과거 실행 증거 재사용을 구별한다. LF/CRLF 각각 독립 Git·NuGet/engine cache를 사용했다.

원래 UI에서 struct 입력 이름의 명시 대응, 새 같은 타입 입력과 root 값 연결, 수동 C# 본문을
저장했다. 기존 public 함수/호출자·helpers·private 부모와 정확한 local·ID/좌표/경로는 유지했고,
compiler Review/명시 Confirm 후 실제 결과는 **31 → 61**이다. Review 뒤 물리 code 원문이
공백만 달라져도 최종 CAS가 거절하며, 원문 복원과 새 Review 뒤에만 Confirm한다.
기존 등록 외부 함수의 저장 copy 안에서 핀 삭제·이름 대응·새 입력·수동 본문을 저장하고
재시작·명시 보완·compiler Confirm으로 원본/공개 계약을 보존하는 기존 회귀를 LF와 전체
복원본에서 추가 실행했다. 새 일반 노드 분류가 기존 소유 nested-copy 요청을 가로채지 않는다.
관측 enum/interface 타입 목록은 확인하지만 fixture의 interface 인자는 명시 `null!`이다.
provider 호출·모듈 async·살아 있는 참조 객체를 실행했다고 주장하지 않는다.

연결된 핀의 묵시 타입 변경 거절, 팝오버/C# 취소, 계약 Undo/Redo와 뒤늦은 독립 본문/바인딩을
덮는 Undo 거절, cold 재시작, 저장 실패·타입 원본 충돌 뒤 전체 입력 보존과 명시 재시도,
apply/조회 응답 유실 뒤 두 번째 apply 없는 receipt 복구, 응답 중 새 설명과 후속 Save를 검증했다.
패키지의 normal root 실제 실행과 전체 복원본의 private 실제 실행·storage/loss/late도 새로 실행했다.
공개/override/부모·외부 원본 편집권한을 추가하지 않았다.

개발 단계는 25회 실행 중8회 실패를 그대로 보관했다. 순차 적용 후 checkpoint
실패가 입력을 지우던 제품 결함은 한 후보/write-before-commit/receipt로 수정했다. 일반 노드
계약 편집의 snapshot Undo 누락도 수정했다. 나머지는 잘못된 selector/포커스, 필수 atomic
Review 그룹 누락, nullable interface fixture와 정보 슬롯 private 진입의 기존 거절 경계다.
정보 슬롯의 비복사 private 보호를 풀지 않고 실제 독립 소유 함수 private 경로를 검사했다.
수정된 검사를 다시 통과했으며 실패를 통과 또는 동등 재사용으로 세지 않았다.

| 기록 | evidence SHA256 |
|---|---|
| 최종46단계 | `e8de9cc6a154a35ba1961c73ee1a7f8bd3d6216a5975ba7d18b9d3f0c46eaa4b` |
| 분류 중복 코드 검토 후 경계에서 보관한 첫 최종 시도 | `880a43e7f051a06aa98e299072e9908640ca6a9a4ab1bf597313df8c2b393920` |
| copy CRLF assertion 실패·동등5건 출처 | `f142d9c0d6b8f2600ac8a32579c2e2c925293e8f2d69948697b8324f44388a50` |
| copy Confirm 뒤 leaf CRLF assertion 실패 | `60fe80bc02358ae87bda8bc3281367b60c34facc92bf17642fe86305e7ee94e3` |
| 개발 재현·진단·복구25회 | `d9006ca4312b50abb2ba743f4f41bbe352ff02af53cad0e12da65bb2807c494c` |

제품이 같은 `0e731803` 시도의 copy 재편집 검사는 입력 내용이 정확히 보존됐는데 LF 예상 문자열을
CRLF 실제 transport에 직접 포함 비교하여 실패했다. 보관 presentation에서 개행 정규화 후 C# 전체가
동일함을 확인했다. 후속 leaf 비교도 같은 개행 기대값 문제로 실패했고, 보관된 실제 Confirm 결과의 본문·helpers·
핀/값·공개 경로가 모두 정확함을 별도로 진단했다. 이 진단을 실패 검사의 통과로 대체하지 않았다.
fixture는 의도한 본문과 원래 leaf의 개행 정책까지 정확히 비교하고 Confirm 기대값에 실제 transport를
유지하도록 수정했다. 제품4파일은 byte-for-byte 동일하다. ZIP/manifest 전체 파일 해시, SDK/NuGet/
configuration/RID, 독립 LF checkout, 명령과 transitive import closure를 검사하여 이 fixture에
의존하지 않는 통과5건만 동등 재사용했다. 실패한 copy 검사·모든 빌드·새 패키지·전체 복원과
나머지 검사는 새로 실행했다. 실패를 통과로 세지 않았다.

최종 record `/workspace/artifacts/v536-verification-managed/runs/6313a80c9c43499abcad0ecdd4413252.json`. ZIP/manifest의 전체 파일 해시를 재확인했다.
첫 고정 코드의 새 분류가 기존 owner+private-frame 매개변수 요청에도 일치하는 중복을 코드
대조로 발견했다. 실행 중이던 충돌 검사의 completion(exit0·allChildrenReaped)을 확인한 뒤
후속 실행만 SIGINT로 멈췄다. 첫 시도의 기록된 13개 통과와 별도
완료 영수증을 보관했으며, 중단을 제품 실패나 최종 통과·재사용으로 세지 않았다.
수정 제품의 최종46단계에서 이 첫 시도의 통과는 재사용하지 않았다.
개발 원본·실패 로그·checkpoint·화면과 명령도 보존했다. 소유 관리 임시 산출물만 기존 규칙으로 정리했다.

| 세대 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | `b63020847c70faa18a9e60f48fae812b5caeaf57` | `5aefba4e38afafe7e96295cae19d7d4d7bf8a972979c1086b5d2c954cf830828` | 53979632 |
| rollback | `2afbe93143ecfea870c4f92192151019c971218d` | `b5a7d5a4a6431915d6381996bf04e198bafadb963548bddd458b10dc1f414605` | 53978888 |

이전 latest를 rollback으로 보관하고 이전 rollback 한 세대만 기존 승인된 관리 규칙으로 교체했다.
추가 메모리9GiB+여유1GiB·RAM 파일4GiB+여유512MiB·evidence512MiB·디스크 여유64MiB를
유지했다. SDK/seed·알려진 관리 archive의 읽기 FD cache advice만 사용했고 전역 cache나
과거 evidence·원래 checkout을 정리하지 않았다. 확인 시 디스크 여유 25,527,017,472B
(약23.77GiB), 관찰 cgroup peak 9,148,981,248B다.

저장 문법·receipt version1은 유지하며 이전 executor의 새 batch 지원을 보장하지 않는다.
이전 전체 executor/reader를 이번 단위에서 실행한 것은 아니다. 기존 nominal/enum 구 parser
비호환과 자동 migration 없음도 유지한다. 실제 Windows apphost/WebView2·모바일·실제 기기·
전체 UI는 미검증이다. 초기 빈 화면 원인은 미확정이다.

다른 기존 public/private/retained 고급 ABI 문맥, 살아 있는 참조 객체/접근자·수명, 모듈 async/공개
실행 결과의 계약-only closure/DLL 순환, multiple/함수 필드 native 생성은 같은9행의 유한 잔여다.
M11/M12/M4는 증거 없는 새 회귀로 다시 열지 않는다. 이번 단위에 추가 사용자 정책 결정은 없다.
