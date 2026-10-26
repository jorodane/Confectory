# v536 값 입력 타입·출력 정의 결합 — 2026-10-26

정보 창의 기존 함수 상세창에서 값 입력 타입과 출력 추가·삭제·void 반환 전환을
편집하고 창의 임시 저장을 한 번 누르는 동작이다. 함수 간·같은 함수·양방향 void
전환에서 원래 단일 후보는 유효하지만 그룹만 거절하는 것을 수정 전에 재현했다.

## 지원 경계와 보존

직접 소유 일반 Blueprint 함수 2~8개, code/export leaf callee·call/export 직렬
caller 및 고정 로컬 import 경계다. 값 입력 타입 전용과 출력 정의 편집을 함수
간에 결합하거나 같은 함수 안에서 함께 편집한다. 기존 유지 scalar out/비void
반환 타입 계획도 기존 writer 검증으로 함께 처리한다.

입력 타입 교체는 원래 이름·수·역할·상대 순서를 유지하고 기존 null 대응,
모든 callee 사용처의 명시 대체, caller의 명시 값/기존 바인딩·해제가 필요하다.
타입이 같은 핀의 기존 이름 대응은 유지한다. 유지 출력은 이름·역할·상대 순서와
명시 scalar 타입 계획을 검증한다. 입력 추가·삭제는 이 단위에서 허용하지 않는다.

기존 outputGraphs의 모든 원래 writer/exit 삭제, 새 배치의 값·삽입 위치·다음
경로, 공개 범위와 호환 소비를 검증한다. 새 출력은 자동 공개하지 않는다.
입력 타입 전용 행에는 출력 재선택을 허용하지 않으며 출력 전용 행에는 입력
재선택을 허용하지 않는다. 입력 사용처 계획은 입력 타입이 실제 바뀐 행에만
허용한다. 기존 C# 매개변수·본문·정확한 값·설명·함수/구현/기존 노드 ID는 보존한다.

각 closure를 원래 스냅샷에서 먼저 검증하고 내부 overlay에서만 결합한다.
앞선 출력 대응으로 옮겨진 뒤 caller 해제 바인딩도 기존 투영기로 원래 증거와
현재 내부 그래프를 대조한다. 출력이 바뀐 행만 출력 투영에 등록한다. 입력 타입
전용 행에 출력 계획을 만들거나 현재 live 소스로 동의를 재기준화하지 않는다.
원래 사용자 hash·물리 파일 관측·한 후보/CAS·receipt·Review/Confirm은 유지한다.
실패 시 앞선 함수나 caller도 부분 저장하지 않는다.

새 UI·레이아웃·권한·계약 ID·기본값 추정·자동 연결 삭제·C# 소스 재작성은 없다.
오버라이드는 원래 매개변수·출력 계약을 유지하며 독립 계약 복제는 필수 복원에서
제외한다. 원본/부모/외부 소스와 main·사용자 자료는 변경하지 않는다.

## 실제 fixture

원래 두 함수는 `(long amount,double real,out long count,out long stable)`이며
공유 caller의 A.count→B.amount와 B.count→caller 반환이 연결된다. count에는
실제로 두 writer가 있다. amount의 string 교체, count 전체 배치 삭제와 fresh
추가, 유지 출력/반환 타입과 양방향 void 전환의 네 경우를 구별한다.

caller의 명시 string 값과 callee의 원래 long 사용처를 대체하는 리터럴 41을
따로 선택한다. fresh의 값 23과 정확한 9223372036854775806, 새 string 반환의
한글/이모지, 유지 writer의 double real은 기존 타입 규칙으로 검증한다.
원래 long 소비에는 fresh/stable 등 현재 호환 출력을 명시한다. 편집 역순도
같은 최종 후보와 원래 source hash를 유지해야 한다.

사용처·값·해제·writer 전체 집합·exit·삽입 경로·소비 대응 누락, 잘못된 타입·
입력 이름/추가/순서/역할·C# 본문 계획·실제 source 변경은 전체 미적용이어야 한다.
실제 화면과 엔진의 저장·취소·Undo·실패·충돌·응답 유실·재시작·Review/Confirm은
격리 fixture만 사용하며 실제 사용자 프로젝트·계정·유료 추론을 사용하지 않는다.

## 정확한 잔여

8행 전체 완료는 아니다. 입력 정의 추가·삭제와 출력 타입/정의/반환의 결합,
ref·역할·매개변수 순서, 수동 C#/혼합 native·중첩/private/whole/postCall,
같은 원래 계약의 copy/상속/등록/소유 정보 속성 혼합과 scalar 밖 함수 타입은
별도다. 이미 지원한 입력 이름/출력 정의와 입력/out/비void 반환 타입, 이번
입력 타입/출력 정의·void 전환을 다시 미완료로 분류하지 않는다.

9행 정보/참조/외부 함수 타입·표시명/native 식별자 분리와 I6/B2·A4~A6·
M4/M11/M12 및 Helper 실제 편집 도구는 후속이다. 전체 v536 UI나 실제
Windows/WebView2·모바일 기기·Library 전달 완료를 의미하지 않는다. 승인된
현재 검사 소유 복사본의 종료 cleanup 외 기존 자료는 추가로 지우지 않는다.

## 집중·영향 회귀 완료

Native Release 경고/오류 0이다. 수정 전 재현 4흐름·8확인과 이후 결과를 구분한다.
집중 18흐름·50확인에서 순수 후보/역순·원래 hash·누락/오류/물리 경합의 전체
거절, 네 형태의 실제 API/컴파일과 기본/독립 화면 편집·취소·Undo/Redo·미저장/
저장 재시작·Review 취소/Confirm이 통과했다. checkpoint 실패/재시도, 응답/조회
유실 receipt·중복 방지, peer/프로젝트 전환과 Undo 명시 재시도도 통과했다.

초기 독립 화면 검사는 출력 삭제 remove: 영역에서 amount 입력을 찾는 fixture
선택자 오류로 timeout했다. 원본 UI는 해당 영역의 args가 비어 있다. 모든 writer
삭제를 선택하는 기존 검사는 유지하고 입력 대체 루프에서만 삭제 영역을 제외했다.
제품/레이아웃을 수정하거나 검사를 약화하지 않았으며 실패 로그·ZIP을 보존했다.
수정한 실제 독립 창의 저장·재시작·Confirm은 통과했다.

기존 입력/out/반환·입력/out·이름/출력 정의·입력 정의/타입·오버라이드 보호·
출력 없는 기존 입력 전용의 영향 6흐름·21확인도 통과했다. UI 74리소스와
WebBundle은 82e2676와 바이트가 같으며 실제 460px 창·기존 매핑/삭제 영역을
렌더로 확인했다. 새 증거 ZIP 29개의 집합·권한·내용·해시를 재검증했다.
[집중·회귀 증거](evidence/v536-information-shared-input-output-definition-mix/focused-verification.json)에 실패/수정/통과를 구분한다.
독립 checkout·패키지는 이후 별도 기록한다.

## 독립 checkout·새 교차 패키지 완료

실행 소스는 `8a77ae72695fe712f038b22ce3231952e803c179`다. 기존 독립 checkout을 정상 fast-forward하고
9개 Git blob·기존 LF/CRLF 설정·clean 상태를 확인했다. Native Release 경고/오류 0,
기존 입력 전용·새 후보·실제 API·독립 UI·오버라이드 보호의 5흐름·13확인이 통과했다.
root solution과 별도 MCP Release도 경고/오류 0이다.

Windows x64 패키지를 새로 교차 빌드했다. manifest 2,343항목/marker 포함
2,344파일, 132,764,092바이트의 집합/전체 해시와 현재 제품 소스·
Native DLL 및 7개 Core DLL 일치를 확인했다. manifest SHA-256은
`7b99a3ffa7f8daeb2ddab31342f0422c36391e56e114f49723c5d189bbc8b248`,
Native DLL SHA-256은 `4a1c01dc2460ddbe248217c444115b9cb170a8fbd626fb4dd6e95a4a5eaef9a7`이다.

새 SDK 없는 소유 runtime에서 무관한 cwd의 실제 managed 엔진 웹 기동,
74리소스·synthetic profile/명시 override 보존·변조/DLL 누락 거절과 패키지
backend 후보 4확인이 통과했다. 검사 6단계 모두 성공했으며 대형 검사는 순차 실행했다.
실제 Windows apphost/WebView2·모바일 기기 실행과 구별한다.

36개 새 증거 ZIP의 파일 집합·권한·전체 바이트를 재검증하고 전체 manifest와
fixture 증거를 보존한 뒤 이번 임시 RAM 패키지만 정리했다. 기존 자료 삭제·
변환이나 새 배포 파일 보관·Library 전달은 하지 않았다. 패키지 단계 최저 디스크
여유는 2,028,744,704바이트이며 OOM/oom_kill 0이다. 후속 결과 문서 커밋은
실행 코드를 바꾸지 않는다.
[checkout·패키지 증거](evidence/v536-information-shared-input-output-definition-mix/package-clean-verification.json)에 소스·단계·해시·한계를 기록한다.
