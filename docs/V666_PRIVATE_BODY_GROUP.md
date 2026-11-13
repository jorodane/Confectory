# Private C# 본문·보조 함수와 일반 본문 공동 저장

고정 [7/8행](V536_I5_6_REMAINING.md)의 한 정보 창·한 Save를 qualified private
노드의 명시 본문 계획에 연결한다. [retained root 공동 저장](V666_RETAINED_BODY_GROUP.md)
다음의 한 사용자 흐름이다. 기존 단독 계획 검증과 private C# 경계 검증을 재사용한다.
정보별 struct·종류 enum·모듈 interface 및 명시 async 전환 전 sync caller 오류를 유지한다.

직접 소유 함수 안의 기존 private C# 본문·보조 함수와 다른 소유 함수의 일반 C# 본문을
편집한다. 공개 계약, 일반 Blueprint 상위 구현의 계약, private 프레임의 입출력·연결,
노드 자체 ABI와 graph/layout/locals를 그대로 둔다. private 노드의 매개변수 이름은
상위 구현과 같을 필요가 없다. 반대로 상위 구현의 매개변수 이름이 공개 계약과 다른
경우 기존 단독 처리의 정규화를 암묵적으로 합치지 않고 이 공동 경로에서 거절한다.
함수 2~8개·함수당 직접 소유 구현/target 하나·64-member/240-source 예산을 유지한다.
copy/상속/import와 실제 계약 변경은 해당 원래 명시 계획의 별도 범위다.

원래 UI는 일반 Blueprint에서 직접 소유 private C#만 있는 경우 C# 소스 선택창을
건너뛰었다. 이제 원래 readOwnerEdits가 그 함수 소유의 scoped-code-csharp를 확인하면
기존 구현 선택창으로 들어간다. 선택한 본문과 보조 함수는 기존 보호 영역에서 편집하고
취소·Undo/Redo·상세창 저장을 사용한다. 새 권한·저장 문법·타입 해석·레이아웃은 없다.
WebBundle의 해당 JS canonical 크기/hash도 함께 갱신한다.

WholeBodies는 qualified node identity와 노드 ABI를 상위 native ABI와 구분하며,
원래 단독 Contracts/Graphs가 전체 원본 hash/receipt·helpers 경계·assembled C#를
검증한다. 본문을 자동으로 바꾸거나 프레임/소비자 재연결을 추측하지 않는다.
기존 version3 nativeBodyContexts·readGuards를 사용하고, 후속 명시 저장은 원래
function/source/flow/read hash를 유지하며 사용자가 다시 쓴 text/helpers만 갱신한다.
별도 구조·계약 변경은 입력 보존 거절로 처리한다. metadata·cold·Review/Confirm·최종
CAS와 원래 독립 source 관측을 유지한다. 외부 경로를 새로 찾거나 권한을 넓히지 않는다.

종료 기준은 이 한 흐름의 원래 UI 편집·취소·Undo/Redo·한 Save·실패/재시도·cold·응답
유실·반복·독립 창·프로젝트 경계·늦은 입력·후속 명시 text/helpers 저장, Review 취소와
graph/선택 node/독립 source 경합이다. 원래 프로그램40과 직접 작성한 두 본문의 실행20,
선택 helpers·private/root graph bytes·정확한 local·독립 source bytes/mtime를 검사한다.
LF/CRLF 격리 restore/build, 새 package와 전체 추출본을 검증하고 개발 검사·최종 신규·
재사용 증거를 구분한다. 타입/문맥 조합을 끝없이 늘리지 않는다.

남은 유한 갈래는 독립 root code 노드 자체 명시 계획 결합과 실제 계약 변경 callee/import·
등록 외부 관측 결합이다. 이 private source-only 경로를 그 전체 완료로 표현하지 않는다.
직전 reader가 새 private pending scope를 수용한다고 보장하지 않으며 같은 게시 세대의
authoring/runtime을 사용한다. 자동 migration/downgrade와 구 Reference parser 변경은 없다.
Linux 실제 엔진/portable 실행·Chromium 자동화는 Windows/WebView2·물리 기기·IME/GPU/
오디오 및 전체 UI 검증과 구분한다. 과거 초기 빈 화면 원인은 미확정이다.
원본·latest/rollback·증거와 기존 정리 범위를 유지하고 main은 사용자 검토/merge에 남긴다.
