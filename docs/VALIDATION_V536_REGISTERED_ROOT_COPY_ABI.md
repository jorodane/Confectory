# v536 등록 함수 복사본 내부 호출 ABI 갱신

기준 게시 `21a53db609fbc98fd2f9d671daf156dd9b7e5a50`, 원본 UI는 저장소 v536 `196c605`다. 고정 7행에서 **등록 외부 함수를 구현하는 단독 소유 로컬 복사본 내부 호출의 명시적 ABI 갱신**만 다룬다. 구현하는 외부 함수의 매개변수·출력 계약은 그대로 유지한다. 독립 계약 복제·새 계약 ID 발급은 추가하지 않는다.

실제 재현에서는 내부 callee가 ref→값으로 바뀐 saved copy에 `postCallStale=true`였으나 `callAbiAvailable=false`여서 정보 모듈의 기존 편집 버튼이 나오지 않았다. 원인은 외부 root 함수를 owned source로 읽고 쓰기 그룹에 포함하려는 기존 local-root 경계였다. 본문 재편집 전체가 미지원인 것은 아니며 이전 단위의 source 저장 보호를 유지한다.

`BlueprintRegisteredCopyAbi`는 기존 직접 dependency/registry·함수 선언·부모 계약 조회의 읽기 전용 receipt와 관측 해시만 사용한다. 외부 본문은 읽지 않는다. 실제 typed 선언은 내부 호출로만 전달하고, legacy helper의 클라이언트 JSON으로 외부 소유 권한을 얻을 수 없다. 원래 소유자·직접 배정·단일 target·단독 사용·copy provenance·현재 module/provider 계약 검증은 유지한다.

독립 정보 창의 저장 어댑터에도 본문/설명 외의 단일 `rebindCopyAbi` 전달이 빠져 있었다. 실제 schema 창의 project/owner/authorBinding·ownerHash 검증을 유지한 채 해당 owner·graph의 등록 root copy 갱신만 기존 PackWorkspace 전체 후보 검증에 전달한다. 다른 binding/owner/일반 ABI/혼합 요청은 허용하지 않는다.

기존 `원본 계약 갱신` 조작은 선택된 내부 callee의 typed import·wrapper·graph를 명시적으로 준비한다. 외부 root는 검증 근거로만 사용하고 저장/Review 그룹에 쓰기 대상으로 넣지 않는다. 소유 slot·copy header·graph·기존 node record 및 이전 원자 그룹을 하나의 후보/CAS로 검증한다. 외부 root/registry나 callee 또는 checkpoint가 바뀌면 전체 거절하고 입력을 유지한다. 저장 성공과 명시적 compiler Confirm은 구별한다. 사용자 C#을 문자열 치환하거나 자동 재작성하지 않는다.

집중8흐름과 영향5흐름, 총13흐름 77확인을 통과했다([검증 기록](evidence/v536-registered-root-copy-abi/focused-verification.json)). 기본/독립 정보 창, owned/등록 callee, 명시 갱신 Undo/Redo·취소, 실제 checkpoint 쓰기 실패/재시도, peer CAS 경합, 외부 root 변경의 전체 거절, 저장/조회 응답 유실 뒤 receipt 조회/중복 방지, 저장 전후 cold 재시작, Review 취소 및 compiler Confirm을 확인했다. 기존 local root copy ABI·등록 callee·외부 copy 본문 독립 창·모듈 권한·오버라이드 보호를 영향 회귀로 확인했다. 독립 checkout/새 교차 패키지는 다음 결과 기록에서 구분한다.

검증 fixture는 이전 snapshot을 가진 saved copy이며 신규 copy 생성 지원을 입증하는 검사는 아니다. 외부 root `Root.Contracts::Calc`, 소유 schema/copy `Owned.Context`, 내부 callee는 owned 또는 별도 등록 `Lib::Native`다. 확인한 ABI 변화는 이름·수·타입·반환을 유지하는 `ref long`→`long`이다. 일반 ABI helper의 다른 조합 전체를 이번 완료로 합산하지 않는다. Confirm 후 변경 물리 파일은 `Copy.celem`, `Copy.graph.json`뿐이며 소유 정보·다른 객체·donor·외부 root/callee·원래 node C# 원문은 바이트 보존한다.

원본 UI의 기존 정보 창/독립 창·제목 드래그·Blueprint 탐색·래퍼 갱신·저장·검토·확정만 사용한다. UI 74개와 WebBundle 총75개 파일은 기준 게시와 바이트가 같다. 독립 창이 뒤의 Blueprint 탐색을 가리면 원래 제목 막대로 옮겨 조작하며 CSS 층위나 제품 배치를 바꾸지 않는다. 첫 fixture의 object 독립 창 문맥과 제목 선택자 실패는 실패 기록으로 남기고, 고정 I5의 정보(schema) 문맥과 실제 제목 드래그로 검사한다.

정상 보호: 외부/부모 원문 수정, 미배정·공유 copy의 단독 갱신, 임의 target 선택, 출처 위조, 오버라이드 구조 변경은 허용하지 않는다. 다중 소유·다중 target 전체를 자동 선택해 고치는 새 의미를 추가하지 않는다.

7행에서 import/alias 자체의 이름 변경 및 serial copy whitelist 밖 그래프의 기존 지원 문맥 연결은 이번 단위 밖이다. 8행 다른 계약/body/private/whole/wrapper closure 결합과 9행 함수 고급 타입·표시명, I6 기호/이모지/사용자 로컬 이미지, B2 실제 배정 작업자 배지, A4~A6/M4/M11/M12는 별도 후속이다. 이미지 생성·협의/승자·공유 Confirm·내장 렌더/FPS backend는 구현하지 않는다. 전체 UI·실제 Windows/WebView2·모바일 기기·Library 전달은 완료로 표시하지 않는다.

검사는 격리 fixture만 사용하고 사용자 프로젝트·유료 AI를 호출하지 않는다. 기존 자료/보관 빌드는 삭제하지 않으며 이번 검사 소유 복사본만 전체 증거 ZIP/무결성을 확인한 뒤 기존 승인 수명관리로 정리한다.
