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
