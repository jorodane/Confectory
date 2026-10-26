# v536 등록 함수의 소유 복사본 본문 저장

기준 게시 `8cd62189a4f219f6d30e511ba0c1f16f83cca7b1` 및 저장소 v536 `196c605`다. 고정 7행에서 정보 화면 모듈의 **등록 함수를 구현하는 단독 로컬 복사본**만 다룬다. 함수 계약과 원본/부모/외부 파일은 그대로 유지한다.

기존 `직접 작성 → 구현 선택 → target 선택`은 이미 외부 구현의 복사 생성·배정·첫 저장/Confirm을 지원했다. 기존 모듈 `편집`으로 확정 복사본의 본문을 다시 저장하는 정상 경로도 동작했다. `BlueprintCopyAbi`의 같은 namespace 제한은 그 별도 ABI receipt의 경계이며 이 본문 화면 전체의 미연결 근거가 아니었다. 이를 일괄 미구현으로 보고한 과거 잔여를 바로잡는다.

실제 결함은 재편집 본문의 저장 파일 쓰기 실패였다. 원래 경로는 본문을 live draft에 적용하고 화면 입력을 먼저 지운 뒤 `saveDraft`를 호출했다. checkpoint가 쓰기 실패로 바뀌지 않아도 원래 입력은 사라졌다. 단독 소유 schema의 직접 배정·고정 copy provenance·root를 확인한 source/intent/implementation-description 편집만 기존 `authorBatch`에 연결한다. 같은 검증 후보·원본 source closure·checkpoint CAS·receipt 안에서 전체 저장하며 성공 후에만 입력을 정리한다. 구조/계약 편집, 다른 소유자의 공유 구현, donor 쓰기 권한은 늘리지 않는다. ABI guard나 `InformationFunctionCopies`의 계약을 완화하지 않는다.

fixture의 모듈과 함수는 `Source.Module`, 소유 정보와 복사 ID는 `Owned.Elements`다. 외부 함수/구현/common 및 windows 원문을 전부 바이트 비교하고, CRLF donor·한글/이모지·9223372036854775806 원문과 9223372036854775804 정보 값을 보존한다. HTML textarea의 사용자가 편집한 텍스트는 LF로 정규화되며 변경하지 않는 donor는 CRLF 그대로다.

집중10흐름과 영향4흐름, 총14흐름 59확인을 통과했다([실제 기록](evidence/v536-information-external-copy/focused-verification.json)). 기본/독립 창, 미확정/확정 copy, C#/기존 직렬 Blueprint, source editor Undo/Redo·취소, 저장 전후 재시작, 쓰기 실패/live 미적용/재시도, 실제 저장 경합, 저장·조회 응답 유실 뒤 receipt 조회/중복 방지, peer 입력과 프로젝트 전환, Review 취소/명시 compiler Confirm을 확인했다. target 불일치 정상 거절은 별도로 세며 Windows 실행 통과로 합산하지 않는다. 독립 checkout과 새 교차 패키지는 다음 결과 기록에서 구분한다.

전역 Review는 다른 창의 미적용 입력이 남아 있으면 기존 정책대로 차단한다. copy Save/cold가 peer 입력을 보존한 것을 확인한 뒤, 그 창의 명시 취소만 입력을 해제하고 compiler Confirm으로 진행했다. 다른 창 입력을 자동 폐기하거나 전역 검토 권한을 넓히지 않았다.

Windows 본문만 선택한 copy를 Linux/portable만 선언한 fixture의 Linux Review로 Confirm할 수 없는 것은 정상 target 보호다. 선택창·Save·cold·본문 재편집과 invalid Review의 초안 보존을 검사하며 Windows 실행 성공으로 세지 않는다. target 전체 자동 복제는 기존 선택창의 요구가 아니므로 새 필수 범위로 만들지 않는다.

이번 단위 밖의 실제 다음 조작은 외부 함수를 구현하는 copy 내부의 호출 래퍼에서 `원본 계약 갱신`을 누를 때 필요한 외부 root 함수의 읽기 전용 receipt다. 현재 같은 namespace `BlueprintCopyAbi` 경계로 해당 명시적 ABI 갱신은 제한된다. import/alias 자체 변경 및 기존 serial copy whitelist 밖 graph의 원래 지원 문맥은 각각 별도로 남는다. 오버라이드 원계약의 타입/핀 수/역할/반환 구조를 독립적으로 바꾸는 새 계약 복제는 필수 제외이며 정상 거절이다.

8행의 다른 계약/body/private/whole/wrapper closure 결합, 9행 함수 고급 타입·표시명, I6 기호/이모지/사용자 로컬 이미지, B2 실제 작업자 배지 및 A4~A6/M4/M11/M12는 별도 후속이다. 전체 UI·실제 Windows/WebView2·모바일 기기·Library 전달은 미완료/미검증이다. 사용자 프로젝트·유료 AI를 호출하지 않는다. 기존 자료를 정리하지 않고 이번 검사의 소유 복사본만 증거를 보관한 뒤 승인된 수명관리로 정리한다.
