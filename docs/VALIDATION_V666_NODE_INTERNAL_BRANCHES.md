# M11 실행 분기 선택기의 내부 흐름

## 원본과 지원 단위

기준은 저장소 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`이다. 원본 `dist/blueprint.js`의 `openInternal(node,false)`(838행 부근)는 선택한 동작의 정의를 복사해 내부 문맥으로 넘긴다. 개별 동작의 `data-flow-internal` 연결과 C# `Result` 실행 계약을 따른다. 정보 종류의 Enum/EnumValue 데이터 정의나 미정인 종류 C# 실행 표현을 이 계약과 섞지 않는다.

이번 지원은 저장된 직접 소유 Root/중첩 graph의 기존 switch-profile C# 선택기를 원문 보존 단일 코드로 감싸고 본문·helpers를 편집/저장하는 흐름이다. 기존 private/switch 지원 profile을 유지한다. copy/상속/참조·구형 profile을 자동 변환하거나 공개 override 계약을 바꾸지 않는다.

바깥 노드의 ID·control·입력/출력 signature·arguments·branchOwner·실행 enum의 primary/ID/이름/수치/순서와 바깥 edges를 그대로 둔다. graph의 `executionSource`는 기존 내부 local node `body`를 명시적으로 가리킨다. 원래 코드가 계산한 **정수 실행 선택값 자체**를 private 경계 밖으로 전달하므로 음수·미지정 수치, 명시적 빈 case, 원래 default/계속 경로도 재해석하지 않는다. 새 데이터 핀이나 공개 계약 ID, 종류 타입을 발급하지 않는다.

native compiler는 전달 선택기의 signature와 실행 enum이 경계와 정확히 같은지, 모든 도달 가능한 종료 전에 선택기가 실행되는지 검사한다. 누락/다른 종류의 선택기, 다른 enum·signature, 선택기를 우회하는 종료는 거절한다. 이 내부 매핑은 C# 본문을 파싱하거나 문자열로 치환하지 않는다. 원래 record 파일은 guard와 출처로 보존하고 새 leaf만 별도로 소유한다.

## 편집과 저장

전달 경계 안의 enum·매개변수 선언은 고정하고 본문/helpers만 기존 C# 창에서 편집한다. 사용자는 기존 `Result` 멤버를 본문에서 명시 선택할 수 있으며 바깥 연결의 의미는 유지된다. ref/out은 기존 native 저장소 규칙을 사용한다. 전환 전 ref/out 선택기의 기존 실행 계약 편집 정책을 넓히는 작업은 아니다.

Save는 기존 단일 `authorBatch` 후보, 원문 guard, 체크포인트 및 최종 파일 CAS를 재사용한다. 실제 소스/활성 구현 반영은 컴파일·Review→Confirm에서만 일어난다. 취소·Undo/Redo·컴파일 오류·쓰기 실패·충돌·응답 유실·cold·늦은 입력은 원문과 입력을 보존해야 한다.

고정 계약의 본문 저장은 구조 화면을 재생성하지 않아 진행 중인 요청의 화면 세대를 바꾸지 않는다. cold에서 이미 저장된 후보는 receipt를 검증한 뒤 회수한다. 늦은 전체 본문 입력은 현재 view의 증거나, 같은 key/노드/종류의 수락된 cell과 정확히 같은 원본 증거가 있을 때만 확인된 후보의 basis로 이어간다. 다른 원본 입력을 추정해 재배정하거나 수락 여부가 불확실한 요청을 중복 실행하지 않는다.

## 검사와 보관

새 `v666_node_internal_branch_fixture.py`는 실제 선택기·빈 primary case·다른 case·default·미지정 수치·메인 계속·out 출력과 반복 호출을 사용한다. API는 직접 Root, 중첩 frame, 다른 선택기가 소유한 case 안의 동작, ref/out 동일/별도 저장소, 반복 내부 진입을 확인한다. 본문/helpers에서 기존 Result를 명시 선택하는 편집도 실제 컴파일/호출로 확인한다. qualified probe는 컴파일만 하고 실행하지 않는다.

화면 검사는 원본 진입·Undo/Redo·enum/매개변수 고정·본문/helpers 취소/편집·Root Save·쓰기 실패/재시도·충돌·프로젝트 왕복·응답 유실·늦은 입력·cold receipt·Review 취소/Confirm을 확인한다. 실제 결함이던 전달 노드 표시 필터와 본문 편집의 불필요한 화면 재생성을 수정했다. 진단용으로 응답을 붙잡고 같은 응답의 flush를 기다리던 테스트 교착은 통과로 계산하지 않고 소유 프로세스만 종료해 증거를 보존했다. 응답을 잃은 뒤 정상적으로 보관한 새 입력을 재시작하는 흐름으로 복구 검사를 고정한다.

`tools/verify_desktop.py --suite node-internal-branches`는 독립 LF/CRLF checkout, native switch/중첩/whole-body/ref-out·소유 경계, 기존 고정 call/After compiler와 일반/whole-body/ref-out 내부 흐름의 영향 회귀, 새 교차 패키지와 전체 SHA/CRC/모드 복원 검증을 순차 수행한다. 오래된 compiler 검사도 현재 실행의 독립 SDK home/NuGet cache를 존중하고 전역 임시 cache를 새로 만들지 않는다. 최종 코드와 결과·최신/롤백·공간 실측은 검증 후 아래에 기록한다.

## 남은 원래 경계

M11 전체 완료는 아니다. 현재 bridge는 선언된 선택기의 결과를 전달한다. 원본 `branch-exit` 카드처럼 내부 graph의 서로 다른 종료점에서 실행 분기 ID를 직접 선택하는 편집은 이번 단위가 아니다. 기존 M11 분기 잔여의 구체적 사용자 조작으로 한 번만 집계하며 가능한 C# 조합마다 새 요구를 추가하지 않는다. 선택기 우회 거절은 현재 명시적 전달 경계의 보호이며 새 영구 UX 정책이 아니다.

legacy bool 경로를 새 enum으로 자동 변환하거나 숨긴 원본 UI를 새 필수 흐름으로 만들지 않는다. copy/상속/참조 전환과 private 미지원 profile은 별도 기존 잔여다. 생성된 private class 이름·stack/reflection까지 임의 C#의 완전 동등성을 주장하지 않는다. 원문 보존과 실제 검증한 입출력·실행 계약을 구분한다.

B2 다른 사용자/그룹 권한 backend, 종류 C# 표현/사용 중 삭제 대응, M4/M12 및 3D/권한 별도 팩도 기존 고정 잔여다. 3D 이동은 표시 연출이며 실행 조건이 아니다. 실제 Windows apphost/WebView2·모바일 기기·전체 UI·Library/Space 전달은 교차 패키지 검사와 구분한다. 새 executionSource를 사용하는 graph/초안을 이전 롤백 UI로 확정하는 호환성은 보장하지 않는다.

## 최종 코드의 검증 결과

실행 코드 commit은 `ce127d874a049cfb4460b5361086392ceffaa799`다. 새 독립 LF **27단계**, CRLF **22단계**, 새 교차 패키지·전체 압축 복원·실패 수명관리 **8단계**, 총 **57단계**가 모두 통과했다. 양쪽 checkout에서 native switch/중첩/whole-body/ref-out **28개**와 상속/소유 보호 **2개**가 각각 통과했고 실패/skip은 없다. 일반 Root·void·원문 보존·whole-body this/재귀/import·기존 ref/out 저장소와 공통 선언/아이콘, 고정 call/After compiler 영향 회귀도 새로 실행했다. 기존 검사 정의를 재사용했지만 이 57단계에 과거 실행 결과를 통과로 합산하지 않았다.

새 API는 Root·직접 소유 중첩·다른 분기가 소유한 case·반복 내부 진입, 음수/빈 primary case/default/미지정 수치·메인 계속·호출 횟수·반환·out을 확인했다. ref/out 동일/별도 저장소와 기존 Result의 명시적 선택 편집을 실제 컴파일/호출로 확인했다. 누락/다른 enum·signature·우회 종료 거절, 컴파일 오류·원문 guard·최종 CAS·cold·qualified 컴파일 probe도 통과했다. 화면은 진입·Undo/Redo·고정 선언·본문/helpers 취소/편집·Root Save·쓰기 실패·충돌·프로젝트 왕복·응답 유실 후 새 입력·늦은 ref/out 입력·재시작·Review 취소/Confirm을 확인했다.

새 생성 패키지와 전체 복원본의 Linux .NET 런타임에서 일반 Root 및 실행 분기 화면을 실행했다. 복원본에서는 ref/out 응답 유실 복구도 새로 확인했다. 집중 진단의 초기 제품/fixture 실패와 테스트 교착은 최종 통과에 합산하지 않고 수정 전후 로그·합성 입력을 별도로 보존했다. 교착 테스트는 관리된 자체 worker만 종료했고 같은 막힌 요청을 다시 실행하지 않았다.

- 최종 관리 record: `/workspace/artifacts/v536-verification-managed/runs/a11defaeb225426288f129f02cc20fb4.json` (cleaned).
- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/a11defaeb225426288f129f02cc20fb4.zip`, SHA-256 `2bd2bc405d17e6b2e7ffcd7286e0e13a40b7b3ce6c36c8a6323da1a5a0190a5d`.
- 집중 증거: `/workspace/artifacts/v536-verification-managed/runs/e9c85aff28eb45a2a245de216bdb3bf2.zip`, SHA-256 `dc8e3a9472b5efc9f31455a748f23dcffc5901c5fd61f089a0f721e417641e4e`.

| 보관본 | 실행 코드 commit | ZIP SHA-256 | bytes | manifest SHA-256 |
|---|---|---|---|---|
| 최신 | `ce127d874a049cfb4460b5361086392ceffaa799` | `ef92b8bb8338f1fa1ec65e79e8bb921ea4309954aba43f46ca2f536ed84edd1e` | 51,251,080 | `8537cf2e79d74106e93865f7e143219e4d7fbed3874e7f14c76beaf897660bf0` |
| 정상 롤백 | `383863158de6b4e4efe8b505699b1cac614bd8bc` | `931e6cd878e315a0387c46d3fdced726b029634dc0d3de9ad51aee1b4aad4c80` | 51,248,015 | `1c0ca5dedc75957363ce87dbadcfe843734a79e76380fe476eb8d918675a3008` |

보관 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신은 이번 코드로 새 생성·전체 파일 SHA/CRC/모드 복원과 복원본 실행을 검증했다. 롤백은 직전 정상본의 검증 결과를 재사용하고 ZIP SHA를 다시 확인했다. 최신 2510항목(2363파일/147디렉터리) / 롤백 2510항목(2363파일/147디렉터리).

최종 관리 실행의 디스크 여유는 2083.36 MiB → 정리 후 2078.31 MiB, 순증가 **5.05 MiB**다. 단계 샘플 최소 여유 2083.28 MiB, cgroup 메모리 피크 4618.30 MiB였다. 기존 144 MiB 추가 디스크 예산(64 MiB 안전 여유 포함)과 RAM/메모리 사전 검사를 유지했다. 집중/최종 소유 임시 root는 증거 보존 후 제거됐다. 승인된 관리 저장소의 최신/롤백 회전과 해당 실행의 자체 임시 정리만 적용했고 과거 비관리 자료는 추가 삭제하지 않았다. 이번 실측은 이후 단위당 순증가를 보장하지 않는다.

결과 기록 후 게시 HEAD와 위 패키지 실행 코드의 차이는 문서뿐임을 확인한다. 실행 source/리소스는 동일하고 보관 패키지는 위 코드 commit에서 생성한 바이트 그대로다. 보고서 commit에서 다시 빌드했다는 뜻은 아니다. 실제 Windows apphost/WebView2·모바일·전체 UI·Library/Space 전달 및 위 남은 원래 문맥은 완료로 집계하지 않는다.
