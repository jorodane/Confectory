# 정보 자체 함수의 상속 C# 복사 편집 검증

[고정 7행 지원 경계](V536_I5_6_INHERITED_COPY_SCOPE.md)에 따라 정보 자체 함수의 상속 구현에서 기존 복사 선택창·private C# 편집·원자 저장·Review/Confirm으로 이어지는 경로를 연결했다. 부모나 외부 원본을 편집 대상으로 바꾸지 않는다. 공개 ABI는 그대로 유지하는 본문 편집 단위다.

## 변경과 보호

기존 복사 진입은 module requirement만 받아 직접 포함한 정보 함수에서 거절됐다. 이제 서버가 확인한 직접 origin·writable 함수에 한해서 같은 copy 거래를 사용할 수 있다. 기존 module requirements와 private scope 계산은 바꾸지 않았고, 이전 게시 엔진/호스트가 보관한 실제 모듈 copy seed를 새 엔진에서 재시작해 원래 hash·content fingerprint·snapshot으로 저장되는 것을 확인했다. UI에 모듈이나 새 메뉴를 추가하지 않는다.

provider metadata는 자식 구현의 직접 부모와 실제 body origin을 구분한다. 정보 함수의 편집 버튼은 부모가 있으면 기존 copy 선택창을 연다. private snapshot은 실제 registry 경로로 읽은 자식/부모 header와 본문 관측을 보관한다. 복사 후에도 구현 ID·출처·본문 부모를 혼동하지 않는다.

저장한 copy 재편집에서 미사용 상속 선언 때문에 입력 선택기 전체가 거절되던 결함도 수정했다. 읽기 목록에 상속 저장소를 편집 가능한 것으로 올리지 않으며, 쓰기는 공개 ABI가 정확히 같고 선택하지 않은 상속 정의만 그대로 둘 수 있다. 부모 header/body를 바꾸는 후보는 별도로 거절한다. 따라서 이 예외가 위조 요청의 부모 쓰기 권한으로 사용되지 않는다. 공개 ABI 변경과 다른 상속/외부 함수는 기존 차단을 유지한다.

## 실제 검증

격리된 C# 부모/자식 구현과 직접 소유 정보 함수를 사용했다. 부모 본문에 CRLF·한글·64비트 정수 원문을 두고 실제 Metadata/API/렌더러/컴파일러를 호출했다. 집중 **25 check**와 기존 saved-copy 영향 회귀 **5 check**를 통과했다([기록](evidence/v536-information-inherited-copy/focused-checks.json)). 반복 재실행이나 기본/독립 창의 공통 확인을 새 기능 수로 주장하지 않는다.

- 원본 출처 metadata·header/body receipt와 private snapshot 보존.
- 잘못된 노드 선택의 전체 미적용, 원자 Save·cold·명시 Confirm, saved copy 본문 재편집.
- 위조된 부모 본문 계획, 지원 후보 없는 공개 ABI 변경, 직접 소유하지 않은 상속 함수의 진입 거절.
- 이전 게시 엔진/호스트의 모듈 copy seed를 새 엔진에서 보존·저장.
- 기본/독립 정보 창의 기존 선택창·선택 취소·C# Undo/Redo·재시작·저장·Review 취소/재검토·명시 Confirm.
- 실제 checkpoint 쓰기 실패/재시도, 부모 header 경합과 cold 후 재거절, private copy 전체 취소.
- 적용/완료 조회 응답을 모두 유실시킨 뒤 cold 복구: 정확한 완료 조회와 저장 본문을 확인하고 같은 복사 ID를 다시 적용하지 않음.

초기 독립 창 검사에서는 원본의 floating 정보 창이 Blueprint 닫기 버튼을 가렸다. 사용자의 정상 제목 드래그로 창을 옆에 옮겨 검사했고 force click이나 레이아웃 변경은 하지 않았다. 실패 검사도 사용자 입력과 별도 저장 journal을 구분하고, 저장 전 거절과 저장 중 거절의 기록 차이를 확인했다. cold에서 이미 완료 조회를 검증한 결과가 복구될 수 있으므로 무조건 모든 입력이 남아 있어야 한다고 보지 않고, 확인된 완료 조회·저장 본문·중복 요청 부재를 함께 검증했다. 실패 기록을 지워서 통과시키지 않았다.

[기존 선택창](evidence/v536-information-inherited-copy/copy-picker.png)과 [C# 편집창](evidence/v536-information-inherited-copy/copy-script.png)을 실제 렌더로 확인했다. 정보 카드 폭 460px와 기존 HTML/CSS 네 파일의 이전 게시 대비 바이트 불변을 확인했다([근거](evidence/v536-information-inherited-copy/layout-evidence.json)). 모든 화면의 pixel equality를 주장하지 않는다. Native Release 경고/오류 0건, Linux 빌드 stderr 0이다.

전체 7행/I5-6/v536 UI 복원 완료가 아니다. 상속 정의를 유지한 공개 계약 동시 변경과 일반 Blueprint 부모의 정보 창 수용, 기존 미확정/외부 함수 ID/여러 target copy 계약 편집은 [고정 잔여](V536_I5_6_INHERITED_COPY_SCOPE.md)에 남는다. 8행 공유 caller·9행 고급 타입/표시명은 별도 후속이다. 실제 Windows/WebView2·모바일 기기·계정/유료 추론·사용자 프로젝트 실행·Library 전달은 미검증이다.
