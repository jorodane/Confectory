# 등록된 외부 helper와 소유 C# 본문 공동 저장

고정 8행의 기존 정보 한 창·한 Save를 [기존 로컬 import](V666_NATIVE_BODY_IMPORTS.md)의
다음 실제 원본 의존성에 연결한다. v666 원본의 openOwnFunctionPopover·본문 편집·정보
Save를 유지한다. 게시 `5f4cca78525dc3e5389d9e14cb555564dcebc508`에서 기존 등록
helper를 호출하는 소유 함수 두 개는 각각 명시 본문 후보가 유효하고 원래 프로그램은
46을 반환하지만, 함께 저장하면 그룹 guard만 거절하는 것을 순수 후보와 원래 UI로 재현했다.

범위는 직접 소유 함수 2~8개의 계약 불변 native C# 본문, 이미 등록된 읽기 전용 함수
import와 부모 선언이다. 실제 검사 흐름은 두 소유 본문이 같은 등록 helper를 호출하며,
그 helper는 등록 부모 계약을 상속한다. 원래 native/public 서명·별칭·핀·공유 caller·
외부 계약·provider 원문과 권한을 보존한다. 새 등록·provider 선택·외부 쓰기·암묵 변환이나
본문 재작성은 없다. 표시 이름과 계약 이름 변경을 혼동하지 않는다.

원래 InformationFunctionDependencies의 직접 등록 조회·receipt·부모/경로/hash·바이트
예산을 재사용한다. 각 명시 계획을 완전한 원래 관측에서 독립 검증하고 내부 overlay로만
결합한다. 외부 선언은 readonly 계약 사전에만 넣으며 소유 units/write group에 넣지 않는다.
행 순서를 바꿔도 결과와 원래 hash가 같아야 한다. 직접 작성한 두 본문만 덧셈에서 뺄셈으로
바꾸면 실제 실행은 26이다. provider 구현/본문을 등록 계약 조회가 새로 읽지 않는다.

기존 version3 slotSaveReceipt의 선택적 `nativeBodyDependencies`와
`nativeBodyDependencyReads`에 완전한 원래 등록 proof와 절대 경로 관측을 보관한다.
원래 선언에 동일한 완전한 proof가 남아 있는 첫 후보에서는 중복 보관 필드 하나의 부재가
원본 재수락은 아니다. 논리적 proof 전체의 누락, 원래 읽기 목록/hash의 누락·추가·변경,
unknown 경로와 외부 write member 주장은 거절한다. 한 후보의 기존 전체 source/read 240
한도를 유지하며 기존 local-only/단일 typed receipt에 새 registry I/O를 요구하지 않는다.

후속 설명·함수 표시 Save와 cold는 캡처한 proof/read set을 그대로 이어받는다. 원래 소유
headers/manifest를 기준으로 기존 등록 조회를 다시 검증하되 현재 외부 원본을 새 기준으로
수락하지 않는다. Review 전 검증뿐 아니라 기존 ConfirmReviewed의 readonly 최종 source
lease로 절대 관측을 전달한다. Save 전과 Review 후 등록 manifest·함수·부모의 변경은 전체
거절하고 peer·checkpoint·입력을 보존해야 한다. 정확한 원문 복원 뒤 명시 새 Review로만
계속한다. 소유 원본은 기존 readGuards·CAS를 그대로 유지한다.

완료 조건은 위 한 원본 사용자 흐름의 순수/실제 UI 정상·잘못된 마지막 본문/receipt·
취소·Undo/Redo·checkpoint 실패/재시도·cold·응답/조회 유실·반복·프로젝트 전환·늦은
설명 입력/후속 Save 및 외부 원본의 Review 후 충돌 검증이다. LF/CRLF 격리 restore/build,
새 교차 package와 전체 ZIP 추출본도 검사한다. 기존 local import/guard·native 계약·
새 소유 자식·단일 whole-body 저장은 별도 회귀로 포함하고 개발 실패/신규/재사용을 구분한다.

같은 게시 세대의 authoring/runtime을 사용한다. 새 등록형 공동 저장의 미확정 receipt를
이전 실행기가 검증한다고 보장하지 않으며 자동 migration/downgrade는 없다. 기존 구
Reference parser 제약도 바꾸지 않는다. 외부 provider 본문을 임의로 감시하는 기능이나
새 권한을 추가하지 않는다. 실제 Windows/WebView2·물리 기기·IME·GPU/audio와 전체 UI
전수는 Linux 엔진/Chromium 자동화와 구별하며 초기 빈 화면 원인은 미확정이다.

남은 고정 갈래는 opaque/private의 명시 본문 계획 결합과 실제 계약 변경 callee/import
closure다. 이번 계약 불변 등록 읽기를 그 전체 완료로 세지 않는다. 타입/문맥의 가능한
조합을 새 의무로 늘리지 않으며 M11/M12/M4는 회귀 없이 다시 열지 않는다. 정보별 struct·
종류 enum·모듈 interface, 명시 async 전환 전 sync caller 오류·override 계약·authored 배치·
권한·Review/Confirm을 유지하고 main은 사용자 검토/merge에 남긴다.

## 기존 단일 타입 전환 영수증의 guard 분리

집중 회귀에서 기존 단일 whole-body 타입 전환의 cold Review가 거절되는 잠복 결함도
발견했다. 직전 보관 runtime `7dbe6d3f`에서도 동일했다. 원래 타입 guard는 전체 proof/read를
유효하게 검증했지만 일반 본문 그룹 guard가 공통 readGuards만 보고 node/caller 멤버를
잘못 주장했다. 하나의 직접 소유 함수·완전한 `$function:` 타입 proof/read·일치하는
atomic 멤버·graph node라는 정확한 기존 모양만 원래 타입 guard에 남긴다. 일반 본문
계획이나 새 nativeBody 보관 필드가 있는 그룹은 이 분리로 우회하지 않는다. 타입 guard·
Review/Confirm·원래 최종 read lease와 C# 변환 의미는 유지한다. 새 opaque/private 그룹
기능의 완료가 아니라 이미 제공한 단일 흐름의 회복이며, 이 수정 뒤 최종 검사는 전부 다시 수행한다.
