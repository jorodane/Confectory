# v536 Helper 이미지 조사와 삭제 첫 묶음

후속 프로젝트 전용 복구/실행·경합 결과는 `VALIDATION_V536_PROJECT_HELPER_RETIREMENT.md`가 최신이다. 아래는 첫 묶음 당시 범위/실패 이력이다.

현재 `work/current` HEAD `cf2fcaef2788eab256e65f171b42e0579d7b1fbd` 이후 미게시 변경이다. 전체 v536 UI 완료나 Windows 게시 결과가 아니다. 기존 Browser 일부 Data·참조·정밀 시각 대조 제한은 `V536_BROWSER_SUPPORT.md`에 그대로 남는다.

## 원본과 실제 계약

확인한 사용자 기준은 main `196c605`의 v536 ZIP이다. 원본 `app.js` 3184–3198의 이미지 생성은 `lumi/tori/vex` 샘플 assets를 회전하고 `imageHistory`를 저장하는 데모다. 현재 엔진 `HelperPresentation`은 표시 텍스트와 전역 초안만 저장하며, 실제 Helper 이미지 생성/asset 저장/선택 이력 API는 없다. Yogi capture 조회는 Helper 이미지 생성이 아니다. 따라서 샘플 이미지를 사용자 생성 결과로 넣거나 기존 CLI/Agent 동의에 이미지 생성 권한을 추가하지 않았다. 세 이미지 영역과 비활성 생성 제어를 보존한다. **실제 이미지 선택·보관·이력·취소·재시작 연결은 미완료다.** 원본에 없는 로컬 업로드 메뉴도 임의로 추가하지 않았다.

원본 `removeHelper`는 화면 자료와 prototype 대화를 지우지만 실제 Helper 저장소는 immutable 모집 템플릿/기억을 보관하며 영구 삭제 API가 없다. 엔진의 기존 명시적 Helper 가져오기 경로에 맞춰 안전한 논리 삭제를 연결했다. 원본 생성/설정 공용 모달의 삭제 버튼과 중첩 확인창 위치/CSS를 사용한다. 확인 문구는 실제 의미인 대화·기억·채팅 초안 보관, 프로젝트 배치 재선택을 안내한다. 기본 Agent 등록 동의에는 영향을 주지 않는다.

## 연결한 삭제 경계

- 글로벌 membership Helper만 지원한다. 프로젝트 안에서 만들었더라도 실제 membership이 global인 일반 Helper는 포함한다. 과거 project 전용 membership의 삭제·UI 복구는 미완료이며 버튼/서버가 차단한다.
- `HelperAgents archive-plan`은 현재 모집 소유권, Agent assignment, 전 프로젝트 배치 저장본/메모리 일치와 진행 중 대화/worker를 검사하고 5분 토큰을 만든다. 새 검토로 대체된 토큰은 무효다.
- `archive`는 토큰/기한/registry 및 배치 revision을 다시 검사한다. 해당 Helper의 scoped 사용권을 철회하고 registry assignment, 전 프로젝트 배치 정리, 복구 영수증을 기존 FileStream 다중 파일 CAS로 한 번 저장한다. Agent 공통 grant/다른 Helper/계정/프로젝트 소스/모집·기억·프로필·대화 파일을 삭제하지 않는다. 최종 원본 Confirm 권한도 추가하지 않는다.
- 기존 main Helper를 제거한 배치에서는 남은 순서의 첫 Helper를 선택하며, 남은 사람이 없으면 해당 배치만 제거한다. 기존 다른 roster 항목/기억 선택은 유지한다.
- 철회는 fail closed다. 철회 뒤 디스크 CAS가 실패하면 데이터와 입력은 남고 해당 Helper의 scoped grant는 철회될 수 있다. 성공으로 처리하거나 자동 재허용하지 않는다.
- 진행 중 owner 정리는 파일 반영 전에 수행한다. global 채팅 초안과 창 입력 보관을 먼저 flush한다. 성공 시 해당 Helper의 열린/고정 카드만 닫는다. 취소 시 설정 입력/카드를 보존한다.
- main Helper 변경은 정상적인 transport scope 변경이므로 결과가 불확실할 때 같은 삭제를 다시 실행하지 않는다. `archive-status`가 정확한 helper/token 영수증과 assignment 해제를 읽어 확인한다. 일치하지 않으면 실패로 남긴다. 동일 토큰의 이미 적용된 요청도 같은 영수증만 확인한다.
- 실제 복구는 기존 명시적 `Helper 가져오기`를 사용한다. 원래 대화·기억·표시 프로필을 유지하되 프로젝트 배치/도구권한은 자동 복구하지 않는다. 실제 영구 파일 삭제나 새 로그인/권한 승격은 없다.

## 실제 실행 결과

`tests/web/v536_helper_retirement.py` 최종 `/workspace/scratch/v536-reference/helper-retirement-ui-6.log`, 세션 `55622` exit0, 자료 `/tmp/confectory-node-contract-engine-d1c0w8ia`의 **실제 Linux 엔진 + Chromium 7건 통과**:

1. 원본 설정창 삭제 버튼·중첩 취소·미저장 설정 입력/inert 보존.
2. 위조 삭제 토큰 차단, 저장본 불변.
3. 두 Helper 배치에서 해당 항목만 해제, main 이관, 기억/대화/다른 프로필/Agent 보존.
4. 삭제된 Helper의 global prepare/프로젝트 대화 선택 서버 차단, 모델 호출 없음.
5. 실제 프로세스 cold 재시작으로 삭제 유지, 원래 가져오기 UI로 복구, 프로젝트 재배치/권한 자동 복구 없음.
6. 600 너비 확인창의 취소/Escape/모달 정리.
7. 새 검토 후 이전 토큰 거부와 다른 Helper 보존.

모집 템플릿·기억 및 미리 심은 fixture 대화 파일은 삭제/복구 전후 바이트 동일을 검사했다. fixture 프로젝트 원본 전체도 base와 바이트 동일이다. 시험용 Responses 등록은 loopback 미실행 endpoint/빈 credentialReference이며 실제 계정/추론/공통 사용 grant를 만들지 않는다. 외부 요청·JS 오류 각 0. 테스트를 위해 새 엔진 API나 권한 우회를 추가하지 않았다.

기존 `v536_helper_forms.py`는 `/workspace/scratch/v536-reference/helper-forms-regression.log`, 세션 `55419`, 자료 `/tmp/confectory-node-contract-engine-_mqxaqs3`에서 **6건 통과**했다. 생성/설정·취소/미저장 입력·프로필 저장·재시작·600/900 너비·실제 디스크 CAS 거부를 유지한다.

실패 이력도 보존했다. 초기 retirement-ui-1은 테스트가 허용되지 않은 `host.open-file` endpoint를 호출해 admission에서 차단됐다. ui-2는 roster 반영으로 helper scope가 정상 변경된 후 테스트가 옛 view에서 결과만 기다렸다. 실제 배치는 적용됐으며 이를 재시도한 성공으로 꾸미지 않고 scope 변경 뒤 실제 state를 확인하도록 검사 보완했다. ui-3은 프로젝트 Helper+를 전역 생성/가져오기 버튼으로 잘못 기대했다. 실제 Home으로 이동해 기존 가져오기 UI를 사용하도록 고쳤다. ui-4에서 기본 6건 통과 후, ui-5의 project 전용 fixture 생성은 legacy `helperRecruit` UI 매퍼가 Agent 입력을 전달하지 않아 거부됐다. 테스트를 위해 매퍼/권한을 넓히지 않고 project 전용 삭제는 안전하게 미지원으로 남겼다. 최종 ui-6의 7건은 지원하는 global membership 범위다. project 전용 삭제/복구가 실제 검증됐다는 의미가 아니다.

## 원본 비교·빌드와 남은 범위

원본 실제 렌더 캡처: `/workspace/scratch/v536-reference/helper-reference/original-settings.png`, `original-delete.png`, 원본 modal rectangle 760×459 at 1280×900. 처음 캡처는 startup transition 중이라 무효였고, home transition/유한 animation 완료 뒤 재촬영하여 실제 이미지를 열어 확인했다. 실제 삭제 캡처는 최종 fixture `helper-delete-desktop.png`, `helper-delete-600.png`. 공용 모달·삭제 버튼·중첩 확인창은 원본 CSS/배치를 사용한다. 샘플 이미지 유무/명시적 복구 문구가 다르므로 전체 pixel 일치를 주장하지 않는다.

최종 생성 Linux 엔진 `helper-archive-build-4.log`/세션 `72959` exit0. 리소스 62개, canonical text 53개 해시/크기 일치. 수정 JS/Python 구문과 diff check 통과. Windows 패키징/checkout/commit/push는 하지 않았다. 실제 Windows/WebView2/native touch/사용자 계정은 미검증이다.

남은 Helper 묶음: 실제 이미지 provider/capability와 asset·선택 이력·저장/취소/재시작 연결; project 전용 Helper의 UI 복구 가능한 삭제 계약; 실행 중 worker/삭제 중 외부 CAS·오류 재시도/queued request 경계의 추가 집중 검사. 현재 코드에는 보수적 차단과 CAS를 넣었지만 이 조합들을 실제 통과라고 세지 않는다. 추가 내구성 범위를 만들지 않는다. 이후 고정 순서는 전투 로그·신문고/Yogi → 창별 Run → 전체 고정 잔여 수용/집중 회귀/Windows 교차 패키지/checkout/승인된 work/current 게시다. Helper 에디터 작업 확장은 UI 완료 후 별도 감사다.
