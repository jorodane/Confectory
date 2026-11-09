# V6 원본 자료 Data 보기

고정 v666 ZIP `Confectory-v666/dist/app.js::renderResourceItems`의 Data 행이 기준이다.
`browser-data-identity`의 이름 버튼, `browser-data-fields`의 종류·크기·설명과
`browser-data-edit`의 명시 열기를 연결한다. 기존 원본 CSS와 Compact/Preview는 유지한다.
게시 eda49871의 실제 Data 보기에는 설명 입력만 있고 이 구조/컨트롤이 없음을 재현했다.

종류·크기는 현재 소유 프로젝트의 native metadata를 읽기 전용으로 표시한다. 폴더 크기는
원본처럼 `—`다. 값 선택/복사와 일반 입력의 기본 동작을 지키고 선택 변경·파일 열기·내부
자료 drag로 해석하지 않는다. 명시 열기는 기존 소유 ID/hash 관측의 미리보기 또는 폴더
진입을 재사용하며 선택을 바꾸지 않는다. 새 형식 renderer나 OS 파일 경로는 추가하지 않는다.

이름 버튼의 첫 클릭은 선택, 단일 선택된 이름의 다음 클릭은 원본260ms 지연 뒤 기존
인라인 이름 편집을 연다. modifier는 기존 다중 선택을 사용한다. double-click 열기는 지연
이름 편집을 취소한다. 새 입력·검색/종류/순서/밀도/선택·native revision·닫기/프로젝트 전환,
편집 중 focus와 폐기된 DOM은 오래된 activation을 적용하지 않는다. 지연 요청 자체는
보관/재생하지 않으며 실제 열린 인라인 초안은 기존 private 복원 계약을 사용한다.

설명·이름/구조·import 미확정 중 새 버튼/읽기 전용 필드를 클릭해 입력을 blur/제출하지
않는다. 명시 이름 Save는 기존 atomic alias·command/revision·CAS를 사용한다. 쓰기 실패,
응답 미확정의 동일 요청 확인·cold·동료 충돌·입력만 취소와 현재 설명의 보호를 보존한다.
원본 bytes/ID·권한·Review/Confirm·최종 CAS·공개/override 계약과 저장 문법은 바꾸지 않는다.

이 원본 Data 행과 영향 회귀를 유한한 완료 단위로 삼는다. LF/CRLF·새 패키지/전체 복원·
실패 수명·최신/롤백 보관에서 마감하며, 더 큰 보관/실제 신원 권한 backend·기존 종류 정책과
실제 기기/전체 UI·초기 빈 화면 원인 미확정은 별도로 남긴다. M11/M12/M4를 다시 열거나
핀 ID/타입·문맥 조합의 새로운 필수 목록을 만들지 않는다.

첫 최종 실행의 LF/CRLF와 생성본 Data 검사는 통과했으나, 복원본의 공통 Agent 화면
probe가 비동기 connectionSetup 중 기본5초 기대에서 멈췄다. Data 제품/Agent 코드는
바꾸지 않고 원래5초 관측·요청 완료 시각/오류를 보존하며30초 안에 실제 로그인 버튼과
선택 작업의 완료를 요구하도록 probe를 보강했다. 로그인/추론은 실행하지 않는다. 일시
지연의 원인과 기존 초기 빈 화면의 원인은 아직 확정하지 않는다. 동일한 Data/검사·SDK·
NuGet의 검증된 소스32개만 엄격한 source-bound 근거로 재사용하고, 빌드·경계·패키지·
실패한 probe·전체 복원은 신규 실행한다. 기존 실패 증거는 삭제하지 않는다.
