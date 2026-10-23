# v536 전투 로그 — 실제 저장 작업 이력 연결

현재 work/current HEAD `cf2fcaef2788eab256e65f171b42e0579d7b1fbd` 뒤 미게시 작업이다. 전체 전투/협의 기능, 전체 v536 복원 또는 Windows 게시 완료가 아니다.

## 원본 의미와 기존 엔진의 경계

사용자 기준 main `196c605`의 v536 원본 `app.js` 2814–3098을 읽고 `v536-battle-log.png`를 실제로 열어 확인했다. 원본은 신문고의 충돌/격돌 사안에 참여자, 협의 대화, 체력·남은 턴, 승자 선택, 결과/Confirm 대기를 붙인 기록이다. `ensureDemoConflictExamples`는 샘플 사안을 넣고, 협의 메시지/승자 처리도 prototype local state와 custom worker-response 이벤트를 사용하는 구조다. 이를 실제 AI 협의/완료 결과로 가져오지 않는다. 기존 `EditWorkspace.Conflict`는 소스 CAS 비교이므로 이 협의 기록과 같은 것으로 취급하지 않았다.

현재 엔진에는 `WorkerTasks`의 실제 durable `tasks.json`/journal과 `ProjectAI.Adopt`의 `development-log.json`이 있다. 원본의 사안·협의 대화·승자 결정/체력/턴/신문고 처리 계약은 없다. **이번 연결은 원본 전투 로그 목록/상세 구조에 실제 저장 작업 기록을 읽기 전용으로 표시하는 범위다.** 카드 종류도 ‘작업 기록’으로 표시한다. 가짜 참여자 경쟁/협의 메시지/승자/자동 Confirm을 만들지 않는다.

## 서버와 화면 연결

- 새 `EditorHome.Model.BattleLog` 및 owner UI endpoint `battleLog`는 현재 manager context와 선택 manifest를 다시 확인한다. 입력은 list/read, record id와 page뿐이며 경로/다른 context/전송·쓰기 action을 받지 않는다. AI DevelopmentTools나 MCP 권한에 새 도구를 추가하지 않았다.
- 이미 로컬 소유권이 확인된 Helper 중 global 또는 현재 project membership만 후보로 삼고, 고정 `.confectory/ai-development[/helpers/<chief hash>]`를 읽는다. 저장 document의 project/owner/chief, task의 project/owning Helper를 검증한다. reparse/link 경로는 거부한다. 해당 프로젝트의 지난 작업을 읽는 것이며 미배치 Helper를 현재 참여자로 등록하거나 배치 권한을 복구하지 않는다.
- 실제 Task owner를 열거나 Agent를 poll/start/recover하지 않는다. `WorkerTasks.Open`의 interrupted 복구 쓰기도 하지 않는다. 실제 source/task/journal/계정/권한 변경이 없다. 파일4MiB/합계8MiB/32개 저장소 등의 경계와 부분 조회 경고를 둔다. 이벤트는 한 번 인덱싱하여 Task마다 전체 journal을 반복 순회하지 않는다.
- public projection은 작업 목표, Helper 표시 이름, 저장된 상태, 허용된 event kind/sequence 및 최소 채택 검증 metadata다. 요청 본문·detail·progress·checkpoint·goalEvidence·credentials/설정·원본 JSON을 내보내지 않는다. 실제 Task journal에 날짜가 없으므로 가짜 관측 시간을 넣지 않고 ‘기록 N’을 표시한다. 채택 기록도 협의 결과나 새 최종 반영 승인으로 표현하지 않는다.
- 저장된 running/dispatching에 현재 동일 Worker owner가 없으면 ‘현재 상태 확인 필요’로 표시한다. 기록 열기로 프로세스를 재개하거나 stored status를 바꾸지 않는다.
- 원본 `openConflictLog`/`conflictLogCardMarkup`/detail 구조와 원본 `.conflict-*` CSS를 재사용했다. CSS는 원본 브라우저 CSSOM에서 해당 selector와 관련 media rule만 추출했다. 원본 버튼이 `openContentTab`을 호출하는 것을 확인하고, 실제 문서 adapter의 허용 목록에 `conflict-log`/`conflict-detail`을 추가하여 기본 열기를 문서 탭에 연결했다. 임의의 새 레이아웃으로 대체하지 않았다.
- 필터/접힘·record id·읽음은 기존 프로젝트 presentation metadata에 보관한다. 상세를 **실제로 읽은 뒤** 읽음 표시를 남긴다. 실패한 조회는 읽음으로 올리지 않으며 현재 source/grant를 자동 승인하지 않는다. 재시작은 기존 정상 종료 presentation flush를 사용하며 임의 전원 단절 내구성을 추가로 주장하지 않는다.
- 실데이터 상세의 관련 요소 열기는 기존 `openDeclaration` guard로 연결했다. 이번 fixture는 related 없는 Task를 사용했으므로 그 클릭 경로를 새로 실검증했다고 세지 않는다.

## 재현·수정한 UI 경합

1. 프로젝트 채팅 입력 후 전투 로그 버튼 클릭이 사라졌다. 최초에는 창 복원 가능성을 조사했으나, ui-1/2/3의 실제 SDK trace에서는 **battleLog invoke가 없고**, chatDraft 저장만 있었다. blur가 `work`를 시작하여 pointer click 전에 버튼을 disabled로 바꿨다. 이 읽기 버튼으로 이동할 때는 기존 local presentation에 입력을 보관하여 클릭을 유지했다. main/project Helper 입력 경로에 한정한 처리이며 전송/계정/CAS 검사를 낮추지 않는다.
2. 목록과 상세가 함께 cold 복원될 때 한쪽이 loading에 남았다. 두 읽기가 동시에 idle을 통과한 뒤 한쪽 `work`가 busy로 거부되어 실행되지 않았다. 임의 sleep 대신 idle 이후 busy를 다시 확인하여 직렬 진입하고, 조회 실패는 다시 읽기 상태로 끝내도록 했다.
3. 화면 밖 창을 문서 가로폭 assertion이 발견하지 못했다. ui-6의 390px 캡처를 열어 일반 창의 오른쪽이 잘린 것을 확인했다. 원본의 기본 문서 탭 진입과 실제 adapter 지원 목록을 연결한 뒤 최종 ui-8에서는 **panel bounding box 자체**가 viewport 안인지 확인했다. 가로 문서 overflow 검사만으로 완료 처리하지 않았다.

실패 로그는 지우지 않았다. build1의 로컬 변수 request 이름 충돌은 battleQuery로 정리했다. ui-7은 테스트 문자열 치환이 `failed.locator`의 일부까지 바꿔 `faileclose_window` NameError가 난 검사 코드 오류였다. 보호 assertion을 제거하지 않고 실제 탭의 닫기 X를 사용하는 helper 이름을 바로잡았다.

## 실제 실행 결과

`tests/web/v536_battle_log.py`, `/workspace/scratch/v536-reference/battle-log-ui-8.log`, 세션78345 exit0, `/tmp/confectory-node-contract-engine-__y4u3g9`의 **실제 Linux 엔진 + Chromium 8건 통과**:

1. 빈 프로젝트 원본 제어/필터/빈 목록. Task/Agent/작업 저장소 생성 없음.
2. 실제 저장 형식의 Task fixture만 조회. 다른 Helper/project·symlink 저장소 제외, 원문 request/detail/progress/검증 evidence canary 비노출, 부분 경고 표시.
3. 3회 stale admission 실패 후 읽음 미표시, 명시적 다시 읽기로 복구. 실패 query를 성공/동의로 승격하지 않음.
4. 필터·상세·실제 event/채택 검증 표시, 협의/승자/Confirm 권한 없음, 기존 채팅 입력 보존.
5. 닫기/재진입의 읽음·선택 유지, stored running 자동 재개/저널 쓰기 없음.
6. 실제 프로세스 종료/재시작의 목록/상세/읽음/미저장 채팅 입력 복원, 저널 바이트 동일.
7. 임의 경로/협의 전송 위조 요청 서버 거부.
8. 동일 표시 이름의 다른 실제 프로젝트에서 원래 기록/입력/record id 접근 거부.

같은 최종 실행에서 390×844 More→전투 로그 실제 탭 열기, panel 경계와 문서 overflow, 캡처도 확인했다. 실제 터치/Android 검증이 아니다. `battle-log-desktop.png`와 `battle-log-mobile.png`를 직접 열었다. desktop 캡처의 stale_revision toast는 이 테스트의 의도적인 실패 주입에서 온 것으로, 자연 발생한 제공자 오류나 실제 협의 실패를 뜻하지 않는다.

최종 build7 세션27919 exit0. 리소스63개/canonical text54개의 해시·크기, 수정 JS/Python 구문, diff check 통과. 최종 fixture 프로젝트 원본은 base와 바이트 동일이며 저장 Task/development 파일도 열기/재시작/다른 프로젝트 시험 전후 동일을 검사했다. JS 오류/외부 요청 각0. 테스트는 새 /tmp profile/복사 프로젝트, 빈 credentialReference와 미실행 loopback Responses 등록으로만 수행했다. 저장 fixture 형식을 읽은 실제 엔진 검증이지 실제 Worker/유료 모델/계정/AI 협의 실행 성공이 아니다. 배포 엔진에 테스트 상태 주입 API를 만들지 않았다.

## 고정 미완료와 다음 순서

- 원본 협의 대화·사안 생성/연결·체력/턴·승자 결정·공유 Confirm, 신문고 대응/전송 계약은 미구현이다. Task 이벤트를 합의 결과로 바꾸지 않는다.
- 현재 한 프로젝트의 목록/상세 기본 key를 사용한다. 원본의 추가 독립 인스턴스/복제 및 일부 배치 drag는 미연결이다. UI 목록은 32개씩 읽고 필터/카운트는 현재 페이지 범위다. 32개 초과 전체 필터 의미·대량 이력·live status 갱신 및 관련 요소 클릭의 정밀 검증은 남긴다. 모든 과거 저장소/등록되지 않은 Helper를 열어 주는 기능이 아니다.
- 전체 pixel 비교, 실제 native Windows/WebView2/DPI/터치 및 실제 계정/Worker/provider 실행은 미검증이다. Windows 교차 패키지/checkout/commit/push도 이번에 하지 않았다.
- 다음은 원본 창별 실행창과 기존 project-execution/execution-comparison/RunHistory 계약 감사·연결이다. 이미 있는 신문고/Yogi 및 전투 로그 미지원 계약, 이미지 asset/history/provider 부재, Browser 일부 Data/ref/정밀 비교, 모바일 Blueprint 특수 계약·나머지 ABI/mixed Save는 전체 UI 고정 잔여에 유지한다. 전체 수용 후 회귀·Windows 교차 패키지·checkout·승인된 work/current 정상 게시로 이어간다. Helper의 에디터 작업 확장은 UI 완료 뒤 별도 감사다.
