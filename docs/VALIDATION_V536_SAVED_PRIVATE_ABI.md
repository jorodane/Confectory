# v536 저장된 copy의 private callee ABI 갱신

기준은 저장소 `196c605`의 내부 흐름 진입·기존 편집/원본 계약 갱신 버튼과 고정 7행이다. 미확정 copy의 완료 단위를 반복 구현하지 않고, **이미 저장·직접 배정된 단일 target copy의 private frame 안에 있는 기존 execution-enum 호출 하나를 ref→값으로 갱신**하는 단위다. 기존 이름·타입·핀 수/순서·출력/반환과 공개 override 계약을 유지한다. 독립 계약 복제·새 공개 ID·자동 C# 재작성·새 UI/레이아웃은 추가하지 않는다.

## 연결과 보호

- 기존 CopyAbiBinding의 단독 배정 owner·public/module 계약·target/locator·copy provenance·객체 closure를 재사용한다. 선택된 privatePath/privateGraph만 server가 추가해 기존 root와 혼동하지 않는다. 원래 typed import와 수동 wrapper/본문/helpers·실행선·정확한 값은 보존한다.
- 기존 pure BlueprintCallAbi의 qualified selector를 사용한다. 같은 callee의 다른 frame/import 사용이나 opaque 전체 본문 문맥은 추측해 고치지 않는다. 이 단위 밖의 서명 변경을 새 영구 UX 금지로 정하지 않는다.
- 공개 함수는 읽기 evidence다. 소유 owner/implementation/physical graph와 원래 records/그룹을 같은 후보·atomicEditGroup·checkpoint CAS에 묶는다. 부모·donor·등록 원본이나 공개 함수 선언은 쓰지 않는다. source closure·기존 coordination·receipt를 건너뛰지 않는다.
- 독립 정보 창은 기존 nonce·project/owner 문맥과 같은 source proof를 요구한다. 정확한 private copy 계획 하나만 기존 authorBatch로 처리한다. 다른 owner/창, 누락·위조 binding, 일반 ABI 우회와 혼합 요청은 전체 거절한다.
- 실패/취소/실제 source·checkpoint 충돌은 입력·원문과 이전 기록을 보존한다. 응답 유실은 기존 attempt의 결과를 먼저 조회하고 같은 receipt로 중복 적용을 막는다. 자동 확정하지 않고 Review/Confirm을 유지한다.

초기 화면에서 root 모듈 카드가 private frame의 갱신 가능 호출을 보지 못해 기존 편집 버튼을 숨겼다. 같은 bounded pure validator의 읽기 전용 하위 preview로 원래 편집 진입을 복원했다. 그다음 기존 requiresCoupledCopy 가드가 정확한 private ABI 계획까지 막는 저장 연결 누락을 확인해, server binding이 일치하는 wrapper 하나만 기존 후보 저장/복구 경로로 보냈다. 물리 source 변경 회귀에서 cached 원문만 검사하여 기존 본문 파일 변경을 checkpoint Save 전에 놓치는 결함도 재현했다. 기존 소유 파일 baseline·링크 경계를 private ABI의 적용/완료조회/재시도 기준 확인에도 재사용해, 실제 변경이면 전체 미적용과 원래 입력 보존으로 처리한다. 초기 실패 로그·fixture는 scratch에 보존하고 통과 수에 포함하지 않는다. 보호나 레이아웃을 완화하지 않는다.

## 검증 경계와 잔여

`v536_saved_copy_abi.py ... nested`의 기존 저장 copy fixture를 사용한다. 기본/독립 schema 창, 단독 소유 receipt 위조 10종, source/owner/path/nonce/target·혼합 거절, 실제 저장/실패/충돌/응답 유실, Undo·취소·cold·Review 취소·compiler Confirm과 원래 tree/정확한 int64/본문 바이트 보존을 확인한다. 독립 창은 다른 primary 문서를 유지하며 기존 정보 창의 권한을 확장하지 않는다. 확정 결과는 아래 후속 evidence로만 기록한다.

74개 리소스 중 기존 `feature-authoring.js`·`element-functions.js` 어댑터 두 항목과 descriptor만 갱신한다. HTML·CSS·나머지72개를 유지하고 원래 850×600 Blueprint·모듈 카드 배치를 사용한다. 현재 실행이 만든 fixture/임시 패키지는 로그·프로필·스크린샷/manifest 증거를 보존한 뒤 그 복사본만 정리한다. 원래 자료·보관 패키지/SDK/사용자 데이터는 지우지 않는다.

이번 단위는 private callee의 이름/타입/수/출력·반환을 유지한 ref→값 한 호출 경계다. 그 밖의 실제 기존 private ABI 조작은 별도 수용 증거가 필요하며 가능한 조합 전체를 새 필수로 늘리지 않는다. 여러 target/shared-copy·동일 callee 복수 사용을 자동으로 고치지 않는다. 공개 override 구조 변경 거절은 정상 보호이며 독립 계약 복제는 필수 제외다.

8행의 기존 경계 밖 공유 caller/계약 결합, 9행 정보·참조·외부 타입 함수 핀과 표시명/native 식별자 분리, I6 아이콘·B2 실제 배정 배지·A4~A6·M4/M11/M12는 별도 후속이다. 전체 UI·실제 Windows apphost/WebView2·모바일 기기/터치·Library 전달은 미완료/미검증이다. 이미지/협의/렌더 신규 backend나 Helper 작업 권한은 확대하지 않는다.

## 확정 집중 검사

최종 제품 소스 세대를 고정하여 실제 엔진/API·렌더러 12흐름 65확인을 통과했다. 각 저장 copy fixture의 순수 receipt 위조10종도 포함하며, 기본/독립 창·source/CP/nonce/path/owner 거절·물리 변경 전체 미적용·다른 frame 입력 보호·Undo/취소·쓰기 실패·응답 유실·cold·Review/컴파일 Confirm과 root/미확정 copy/모듈/enum 회귀를 확인했다. 초기 실패를 통과로 집계하지 않는다. 최종 independent checkout/교차 패키지 결과는 후속 evidence로 구분한다.

## 독립 checkout·교차 패키지

소스 체크포인트 `75ed5ef243cdb8a9c565a49772deef09c964f1a3`를 기존 독립 checkout에 정상 FF하여 10개 변경 Git blob·원래 autocrlf/clean을 확인했다. Native/CLI Release와 Linux 엔진, 독립 정보 창의 실제 UI/컴파일러 Confirm 및 기존 private enum 회귀 2흐름 13확인, 순수 private 후보 6확인이 통과했다. 집중 검사의 결과와 각 fixture의 순수 receipt 위조10종은 별도다.

restore·솔루션 Release·MCP Release·새 Windows x64 교차 패키지·package probe·패키지 자체 runtime의 독립 창 private ABI UI/컴파일러 11확인까지 6단계가 통과했다. manifest 2346개/전체 2347개 목록·SHA·링크 부재와 Core/Native DLL·검토 소스 바이트가 일치한다. manifest SHA `267b3ea6825e262a8fbd53ad08da2d040ebd84bb3de60e639b0c1d9e83e56158`, Native DLL `43c8007b28923a37679ae47235eaafbb367aebbe2bd700ff64295724861c2e74`다.

이번 패키지는 `/tmp` RAM 기반 검사 산출물이다. 전체 manifest와 fixture/로그/프로필·원본 증거를 보존한 뒤 이번 실행의 임시 패키지만 제거했다. 기존 보관 패키지/SDK/원본/사용자 자료는 지우지 않았다. 다운로드 가능한 새 보관 빌드나 Library 첨부 전달이 아니다. 최종 후속 커밋은 문서/evidence만 추가하며 위 소스 체크포인트의 실행 코드와 동일하다. 실제 Windows apphost/WebView2·모바일 기기/터치와 전체 UI 완료는 미검증/미완료로 유지한다.
