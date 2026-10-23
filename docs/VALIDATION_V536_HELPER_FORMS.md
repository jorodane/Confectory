# v536 첫 연결: Helper 생성·설정 기본 폼

기준은 `V536_UI_RESTORATION_SCOPE.md`의 저장소 v536이다. 전체 UI 적용, 전체 Helper 기능 완성이나 게시 완료를 의미하지 않는다. 동일한 작업 환경의 `work/current`, HEAD `cf2fcaef2788eab256e65f171b42e0579d7b1fbd`에 기존 미게시 변경을 보존했다.

## 구현

- `v508-views.js`의 기존 실제 Helper 생성/프로필 API 어댑터를 그대로 사용한다. v536 원본 `addParticipant`의 변경과 동일하게 편집에서도 artwork를 form 밖으로 이동하고 생성·편집에 중앙 모달을 사용한다. Helper ID·현재 프로필·Agent 소속으로 실제 대상을 지정하며 데모 객체를 만들지 않는다.
- `style.css`에서 v536 원본의 해당 form 경계 규칙만 반영했다(`padding:6px;margin:-6px`). 나머지 전역 화면의 CSS는 일괄 교체하지 않았다. 기존 닫기·focus·inert 복구 및 원래 입력/버튼 배치를 유지한다.
- 기존 Helper 표시 저장 API와 서버 revision 검사는 그대로다. 표시 이름·간단 설명·설명을 저장하며, 템플릿 성격/특기·기억·Agent 권한이나 대화 초안을 임의로 수정하지 않는다. 새 모달/계약서·상시 진단 패널은 추가하지 않았다.
- 저장 실패 시 기존 toast에 Helper 설정을 저장하지 못했으며 입력을 보존했다는 동작별 안내를 제공한다. 연결 작업 wrapper의 기본 동작은 유지하고 내부 호출의 `failureMessage` 옵션을 전달한다. 상세 원인 없는 일반 오류를 특정 계정/저장 충돌로 단정하지 않는다.
- 참조의 실제 이미지/생성 이력은 사용자 데이터가 아니다. 엔진에 이미지 생성 기능과 이미지 프로필 저장 계약이 없는 상태를 성공으로 표시하지 않는다. 생성 버튼은 기존처럼 비활성화했다. 폼 내부 삭제와 이미지 변경/이력까지 완성했다고 보고하지 않는다.

## 실제 엔진 검사

`tests/web/v536_helper_forms.py` **6건 통과**. 생성 Linux 엔진과 Chromium, 새 임시 프로필을 사용했다. 폐쇄된 loopback 주소를 지정한 Responses 설정만 등록했으며 실제 계정·로그인·자격 증명·추론·Codex 사용 승낙/권한은 만들지 않았다. 메시지 전송은 하지 않았다.

1. v536 중앙 생성 모달과 바깥 artwork에서 실제 Helper 2개 생성, 종료/inert 정리.
2. 설정의 같은 폼 재사용, 취소로 저장본/다른 Helper/대화 초안을 변경하지 않음, 다시 열어 미저장 설정 입력 유지.
3. 명시적 저장이 선택 Helper의 표시 필드만 갱신함. 다른 Helper·성격/특기·Agent 소속과 한글 전역 대화 초안 보존.
4. 실제 프로세스 재시작 후 같은 프로필 복구, 중복 Helper 생성 없음.
5. 900×760 및 600×800에서 모달/저장·닫기 제어가 화면 안에 있고 문서 가로 넘침 없음. 전체 v536 모바일 shell/390px 카드 편집 검증과는 별개다.
6. 격리 프로필 파일의 동시 변경 후 오래된 revision 저장 거부. 변경된 파일 바이트와 화면의 내 입력을 보존하고 정확한 저장 동작의 실패 안내를 표시함.

최종 세션 `69559` exit0, 로그 `/workspace/scratch/v536-reference/helper-forms-2.log`, 자료 `/tmp/confectory-node-contract-engine-24dw4p3f/evidence.json`. `pageerror`와 외부 요청은 0이다. desktop/600/900 PNG를 기록했고 desktop/600 화면을 실제로 열어 원본 v536 설정 캡처와 비교했다. 바깥 모달·필드·저장 배치는 유지되며 실제 이미지가 없는 상태와 지원되지 않는 생성은 그대로 보인다. 모든 화면의 픽셀 일치나 네이티브 Windows 실행 증거로 확대하지 않는다.

첫 실행의 충돌 검사는 서버가 노출하지 않는 `helper_profile_conflict` 문자열을 잘못 기대했다. 실제 저장 거부는 일어났으나 공통 오류가 소스 작업 문구로 표시됐다. 서버 검사를 약화하지 않고 동작별 실패 안내를 연결한 뒤, 화면 입력과 디스크 바이트 보존까지 검사했다.

## 이전 실패 3건

기존 실패 로그와 체크포인트를 보존한 상태에서 다음과 같이 재검증했다. 서로 다른 범위의 검사이므로 단일 고유 합계로 합치지 않는다.

- `v508_conversion_recovery_ui.py` **실제 엔진 3건 통과**, 세션 `58579`, `/workspace/scratch/v536-reference/conversion-recovery-1.log`, 자료 `/tmp/confectory-node-contract-engine-h3a82kgc`. 실제 저장 응답 유실 주입→cold 복구→같은 전환 확인/중복 방지→저장 중 새 입력 보존→후속 Save→실제 compiler Review/명시적 Confirm 완주. 원본 C#·다른 구현·다른 target 보존. cold에서 이미 확인한 proof 맵을 후속 입력 재바인딩에 누락한 결함을 수정했다. 실제 원본이 바뀐 proof를 임의 승인하지 않는다.
- `v508_module_slot_renderer.py` **통제 provider 렌더러 8건 통과**, 세션 `59646`, `/workspace/scratch/v536-reference/v508_module_slot_renderer-1.log`, 자료 `/tmp/confectory-slot-editor-renderer-ostqmld2`. 구현/target/슬롯별 입력 분리·복원, 정확한 source hash에 한한 옛 입력 이관, 알 수 없는 문맥 차단, 다른 6개 입력 보존 및 정확한 argument payload 검사. 마지막 실패는 `[None]`을 빈 배열로 기대한 검사 오류였다. `text` 필드 부재와 정확한 `valueJson`을 각각 검사한다. 실제 엔진 다중 창 전환 검증으로 확대하지 않는다.
- `v508_feature_serial_canvas.py` **통제 provider 렌더러 15건 통과**, 세션 `52693`, `/workspace/scratch/v536-reference/v508_feature_serial_canvas-3.log`, 자료 `/tmp/confectory-feature-serial-renderer-z9b90s4w`. root sidebar의 자료형 컨트롤 뒤를 강제로 클릭하지 않고 원본 값 선택 메뉴로 같은 입력 연결을 검증한다. 불일치 native 타입 후보 제외·쓰기 없음, Save의 정확한 argument 요청, 종료 값/원래 캔버스·메뉴/수명·입력 보존을 유지한다. 실패 assertion을 지워 통과시킨 것이 아니며 실제 원본 컨트롤 역할을 확인해 검사 경로를 수정했다.

## 빌드·정적 및 한계

생성 Linux 엔진 빌드 `46628`, 최종 `80024`는 exit0. UI 어댑터와 source proof 재바인딩 외 Core/SDK API 변경은 없어 이전 SDK 컴파일 결과를 유지한다. 최종 코드의 리소스 59개와 정규 텍스트 해시·크기 일치, 변경 JS/Python 구문 및 `git diff --check` 통과. 원본 v536 ZIP SHA-256은 `b53156e73fdbbe1f6b8b36a0829cdbfdaec002352304da0060fa53026314bd22`이며 사용자 main의 blob을 그대로 복사했다. v508 원본 ZIP은 변경하지 않았다.

아직 미완료: 프로젝트 생성 새 본문/고정 제어·사이드바 드롭, 모바일 shell/카드/터치, 탭·플로팅 다중 창과 프로젝트별 저장, 전투 로그/신문고/Yogi/실제 창별 실행 계약, 요소/Blueprint 고정 잔여 항목·전체 회귀·정밀 시각 대조·Windows 교차 패키지·checkout·게시. 실제 Windows/WebView2/DPI/IME/EXE 및 사용자 계정/실제 모델 검증은 하지 않았다. main/Android·기존 사용자 데이터·동의/계정/소유권/CAS/최종 Confirm 보호는 유지했다.
