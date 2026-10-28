# v536 미확정 copy의 private callee ABI 갱신

기준은 저장소 `196c605`의 v536 내부 흐름 진입과 기존 “원본 계약 갱신” 버튼, `V536_I5_6_REMAINING.md`의 고정 7행이다. 공개 override의 매개변수·출력 계약을 유지하면서 구현 내부에서 호출하는 다른 함수의 현재 계약을 사용자가 명시적으로 채택한다. 독립 계약 복제·새 공개 ID·새 메뉴·레이아웃·실행 권한은 추가하지 않는다.

이번 최소 단위는 **미확정 same-contract copy의 private frame 안에 있는 기존 execution-enum 호출 하나의 ref→값 갱신**이다. 호출의 이름·타입·개수·순서·출력·반환과 부모 private/public 계약은 유지한다. 기존 수동 wrapper/본문/helpers·실행선·원래 입력 바인딩을 보존하고, qualified 경로의 선택된 호출과 해당 구현의 기존 typed import만 같은 후보에서 갱신한다. 이것은 구현 경계이며 다른 기존 함수 편집을 영구 금지하는 새 정책이 아니다.

- 원래 private snapshot·소유 ID·출처와 현재 callee 관측/receipt를 분리한다. 명시적 버튼을 누른 계획만 저장할 수 있고 재시작으로 원래 기준을 자동 변경하지 않는다.
- private 정의 조회에도 기존 `inspectStalePostCalls`를 전달한다. 이 옵션은 정의 조회에서만 작동하며 실제 Describe/컴파일/저장은 최신 계약과 모든 source record를 엄격히 검사한다.
- 같은 callee의 다른 frame/call/import 사용이나 opaque 전체 본문 문맥이 있으면 후보를 거절한다. 타 사용처를 추측해 고치거나 연결을 버리지 않는다.
- wrapper의 qualified private path·seed·현재 source hash/guard·typed import를 검증한다. 원래 본문·선언/정확한 값과 복사본을 기존 한 후보/CAS로 저장하며 실패/충돌은 전체 미적용이다. 응답 유실은 기존 receipt 조회 경로를 사용한다.
- 저장된 copy의 private callee ABI 갱신은 이번 단위에 포함하지 않는다. 일반 root의 기존 ABI 갱신은 유지한다.

## 검사 경계

`v536_general_private_abi_metadata.py ... nested`와 `v536_general_private_abi_ui.py ... MODE nested`의 격리 fixture를 사용한다. source-ready 원본에서 명시 복사하고, 별도 fixture 작업으로 donor/callee를 갱신한 후 원래 snapshot·미저장 본문으로 재시작하여 기존 버튼을 누른다. donor의 새 본문을 copy 입력으로 바꾸지 않는다. 저장·Undo/Redo·취소·실패·실제 경합·응답 유실·cold·Review 취소/명시 Confirm과 다른 target/부모 원본 보존을 확인한다. 확정 결과는 후속 기록/evidence에만 적는다.

초기 순수 검사의 private 정의 조회 실패는 stale 조회 옵션이 자식 요청에 빠진 실제 연결 결함이었다. 첫 화면 fixture는 private 삽입 과정에서 원래 root의 out/반환 export 노드를 빠뜨려 거절됐다. 원래 노드·실행선을 유지하는 유효 fixture로 수정하며, 제품의 계약 검사를 완화하지 않는다. 재시작 검사의 private 이동 위치는 저장 완료를 기다린 뒤 종료하고, 겹친 원래 창은 제목을 눌러 활성화한다. force click이나 레이아웃 변경으로 검사를 통과시키지 않는다. 빌드 보고서 생성 전에 실행되어 JSON을 읽지 못한 초기 실행도 실패 기록으로 보존하고 통과 수에서 제외한다.

## 고정 잔여

7행의 저장된 copy private callee ABI 및 현재 최소 경계 밖의 실제 기존 조작은 별도 수용 증거가 필요하다. 가능한 타입/핀/그래프 조합을 전부 새 필수 항목으로 만들지 않는다. override 계약 위반 거절은 정상 보호이며 독립 계약 복제는 요구에서 제외한다.

8행 공유 caller의 남은 실제 문맥/계약 결합, 9행 정보·참조·외부 타입 함수 핀과 표시명/native 식별자 분리, I6 기호/이모지/사용자 로컬 이미지 아이콘, B2 실제 배정 배지, A4~A6 및 M4/M11/M12는 별도 후속이다. 전체 UI, 실제 Windows apphost/WebView2·모바일 기기·Library 전달은 미완료/미검증이다. 이미지 생성/협의/렌더 신규 backend나 Helper 권한은 확대하지 않는다.

## 확정 검사

Native/CLI Release 0 warning/error, 순수 후보 10확인(새 private 6·기존 root 4), 실제 엔진/렌더러 12흐름 62확인을 통과했다. 기본/독립 정보 창, 저장 실패·전체 미적용·cold 재시도, 실제 callee/owner 경합, 성공 응답 유실/늦은 입력, 명시 취소, Undo/Redo, Review 취소/컴파일러 Confirm과 기존 root/모듈 nonce/enum/프로젝트 전환/override 보호 회귀를 포함한다. 모든 결과는 격리 fixture이며 원래 seed·원문·정확한 long·부모/다른 target을 보존한다. 독립 창 검사는 기존 schema 정보 창/nonce 경계를 사용하고 객체 창 권한을 넓히지 않는다.

74개 리소스 canonical 크기/SHA가 일치하고 JS 어댑터 한 항목 외 73개·HTML·CSS는 동일하다. 실제 화면의 원래 850×600 Blueprint와 기존 내부 흐름/갱신 버튼을 사용한다. 이번 검사의 fixture는 로그·프로필·스크린샷 증거를 ZIP/manifest로 보존한 뒤 이 실행이 만든 복사본만 정리했다. 원래 자료/보관 빌드 삭제는 없다.

## 독립 checkout·교차 패키지

소스 체크포인트 `6e877cd7c97ca539750dd66492bf06f7ae3e5a02`를 기존 독립 checkout에 정상 FF하여 10개 변경 Git blob·원래 autocrlf/clean을 확인했다. Native/CLI Release와 Linux 엔진, 독립 정보 창의 실제 UI/컴파일러 Confirm 및 기존 private enum 회귀 2흐름 9확인, 순수 private 후보 6확인이 통과했다. 집중 12흐름 62확인/순수10은 별도다.

restore·솔루션 Release·MCP Release·새 Windows x64 교차 패키지·package probe·패키지 자체 runtime의 독립 창 private ABI UI/컴파일러 7확인까지 6단계가 통과했다. manifest 2346개/전체 2347개 목록·SHA·링크 부재와 Core/Native DLL·검토 소스 바이트가 일치한다. manifest SHA `4d13057c5ada4af9d6b9c1e701bd194d070022ac26284648b30d991db407fad3`, Native DLL `8d6fd73a3c71cad423313a2d648049543e4c48eabf722a2fd0c0159a6f6b7d01`다.

이번 패키지는 `/tmp` RAM 기반 검사 산출물이다. 전체 manifest와 fixture/로그/프로필·원본 증거를 보존한 뒤 이번 실행의 임시 패키지만 제거했다. 기존 보관 패키지/SDK/원본/사용자 자료는 지우지 않았다. 다운로드 가능한 새 보관 빌드나 Library 첨부 전달이 아니다. 최종 후속 커밋은 문서/evidence만 추가하며 위 소스 체크포인트의 실행 코드와 동일하다. 실제 Windows apphost/WebView2·모바일 기기/터치와 전체 UI 완료는 미검증/미완료로 유지한다.

패키지의 6단계와 UI7확인은 처음 실행에서 모두 통과했다. 후속 바이트 증거 수집만 Core 소스 파일이 배포된다는 잘못된 기대 때문에 실패했다. 기존 `DesktopPackage.cs`의 배포 목록을 확인해 소스 대신 이미 배포된 Core DLL 7개와 root Release DLL의 SHA를 대조했다. 동일한 패키지/성공 로그를 재사용해 목록·바이트·증거 보관을 복구했으며, 패키지/화면 검사를 새로 중복 실행하거나 배포 구성을 바꾸지 않았다. 초기 실패 stderr도 보존한다.
