# v536 독립 속성 창의 원자 Save

`dc2d9b2` 뒤의 한정 단위다. 원본의 **새 창으로 열기**로 연 properties View에서 설명·기존 속성 값·기존 owner 편집 후보를 같은 SlotBatch/ApplySlots 검증 후보와 checkpoint CAS로 보관한다. 원본 HTML/CSS·메뉴·창 크기·배치는 변경하지 않았다. 복합/중첩 **정의** 편집과 dirty raw source 결합을 완료한 것이 아니다.

## 확인한 문제와 연결

이전 독립 창은 설명/값/구조를 순서대로 native draft에 적용한 뒤 Save했다. checkpoint 쓰기가 거절되면 디스크는 그대로여도 앞 단계의 공유 메모리 draft가 바뀔 수 있었다. 이제 frontend가 창별 입력을 포착하고, 기존 서버 후보 검증 및 한 번의 CAS 저장이 끝나기 전에는 live draft를 바꾸지 않는다. 실제 readonly fixture checkpoint 검사로 공유 draft와 디스크가 모두 불변임을 확인했다.

- 기존 `blueprint` endpoint에 서버가 결부한 properties View 슬롯(1~3)·project/context·owner를 사용한다. 이 경로는 `readOwnerEdits`, owner-only `applySlots rows:[]`, `settledSlots`만 허용한다. source View·다른 owner·copy intent·클라이언트가 위조한 surface는 거절한다. 새로운 사용자/프로젝트 권한은 없다.
- 결과 receipt는 `uiSurface`에 결부된다. 다른 창이 같은 내용의 receipt를 자기 저장 성공으로 승격하지 않는다. 기존 primary receipt의 surface 누락은 빈 primary 값으로 호환한다. 새 frontend journal은 프로젝트/슬롯/owner별이며 원문·시도·이전 실패 기록을 보관한다.
- 응답 유실은 receipt 조회로 먼저 확인한다. 미적용 및 원래 기준 불변을 확인한 경우만 새 명시 저장을 허용한다. 불명 결과·실제 경합은 입력을 보관하고 차단한다. 늦게 들어온 동일 계약의 값은 기존 receipt proof로 기준을 갱신하며 조용히 지우지 않는다. 이번 fixture가 늦은 입력의 모든 조합을 수용했다는 뜻은 아니다.
- 각 창의 변경 취소는 그 창의 private 입력만 취소한다. 다른 편집자의 공유 미저장 draft를 되돌리지 않는다. 결과 불명 journal이 남은 닫힌 창 슬롯은 다른 객체에 재활용하지 않는다. View Review 중 primary raw source가 dirty면 자동 Apply하지 않고 막는다.
- 상태 조회도 bound View의 자기 owner만 읽는다. 모델의 일반 View refresh가 일회성 변경 상태 결과를 덮는 결함은 해당 View 행에 상태 결과를 따로 보관하여 수정했다. 공유 취소/Save를 상태 endpoint에 허용하지 않는다.

## 격리 검증

로그는 `/workspace/scratch/v536-view-save/`에 보관한다. 아래 숫자는 공통 준비를 포함한 PASS 묶음이며 독립 테스트 수로 합산하지 않는다. 실제 엔진과 Chromium을 사용하며 사용자 프로젝트·인증파일·로그인·유료 추론은 사용하지 않았다. 생성 엔진은 `engine2.json`(경고0)이다.

| 검사 | 실제 결과 |
| --- | --- |
| `v536_view_owner_api.py` | `api1.log` 5 PASS. 마지막 복합 값 타입 오류에 앞 설명도 전체 미적용, 정상 저장과 창별 receipt, 두 번째 창의 오래된 basis CAS 거절, 위조 surface/slot/mode/id/copy·공유 취소 거절, 재시작 조회와 다른 객체 슬롯 재사용 차단. API 검사이며 renderer 아님 |
| `v536_view_owner_ui.py normal` | `ui-normal1.log` 4 PASS. 원본 메뉴 두 창, 서로 다른 한글/raw64 입력, 한 후보 Save/cold, peer stale 거절, Review 취소·실제 compiler Confirm·확정 후 cold |
| 같은 검사 `storage` | `ui-storage1.log` 5 PASS. 격리 checkpoint 쓰기 실패 시 메모리/디스크 전체 미적용과 두 창 원문 보존, cold 명시 재시도·Review/Confirm·확정 후 cold |
| 같은 검사 `cancel` | `ui-cancel1.log` 2 PASS. 다른 편집자의 공유 미저장 변경과 peer private 입력을 보존하는 명시 취소·cold |
| 같은 검사 `loss` | `ui-loss2.log` 5 PASS. 실제 적용 응답과 조회 응답 유실, journal/입력 보존, cold receipt 조회만으로 복구하고 새 applySlots 없음, peer 경합·Review/Confirm·확정 후 cold |
| `v536_view_owner_projects.py` | `projects1.log` 4 PASS. namespace/id/slot이 같은 별도 실제 프로젝트 A/B의 Home 전환, 은퇴한 A 저장 콜백은 B 요청 없음, A Save가 B native/private 입력을 보존, 프로세스 재시작 및 양방향 재진입 |
| 기존 primary 혼합 Save 회귀 | `root-regression1.log` 4 PASS. 기존 타입 거절→Undo→새 copy 결합→응답/조회 유실→cold·Review 취소·compiler Confirm. primary receipt 호환과 priorOwner 내부 재조회 경로를 확인 |

초기 `ui-loss1.log`는 테스트 route를 닫는 중 `Route is already handled!`가 났다. `unroute_all(behavior='wait')`로 pending callback을 정리한 뒤 loss2를 실행했다. 제품 실패를 통과로 바꾸거나 보호 assertion을 제거하지 않았고 초기 로그를 보존한다. 종료된 프로젝트/primary 검사 세션50342/37134의 결과는 로그의 최종 JSON으로 확인했다. 새로 중복 실행하지 않았다.

`/tmp/confectory-wide-mixed-074v4mla/view-owner-final.png`를 실제 열어 원래 두 창의 부모/속성 카드·정확한 raw64·한글 설명을 확인했다. 창 위치는 테스트에서 사용자 드래그로 바꾼 것이다. 원본 전체 pixel equality나 모든 viewport 수용을 주장하지 않는다. renderer 오류/외부 요청은 없었다.

## 원본 복합 정의와 정확한 잔여

원본 v536 `app.js`는 primitive 선택 목록에 새 ‘복합’을 추가하지 않고 기존 inline compound를 **복합 (기존)**으로 구별한다. `정보`는 이름 있는 재사용 정의로 선택하며, 객체에서 linked 정보의 자식 정의를 직접 바꾸지 않는다. 원본의 Info 기본값과 현재 native schema의 타입 정의·객체 datum 저장을 어떻게 결부할지 남아 있다. native compound/reference 타입 backend 자체는 이미 존재하므로 전체 backend 부재로 세지 않는다. 임의 복합 버튼/새 저장 언어로 대체하지 않았다.

- **다음 구현 가능한 연결:** 원본 정보 picker/정의·기본값 계약에 맞춘 복합/중첩 정의, 독립 raw source와 owner/schema의 결합 후보, provider/saved-copy ABI·다중 target ABI·Set/property와 다른 계획의 혼합. 해당 조합은 아직 차단/미수용이다. 이번 properties View는 copy 편집을 허용하지 않는다.
- **기존 고정 UI 수용 잔여:** opaque/상속/copy-alltarget·whole-body context·같은 callee 여러 호출·등록 all-target의 ABI closure, 공유/고정 출력 이름·잠정 빈 출력, 나머지 특수/readonly 핀·영역/다중 선택·내부 흐름/async, 모바일/줌/검색/키보드/IME의 남은 문맥과 정밀 대조, Browser의 외부 runtime/전체 source 이동·배지 제한. 이미 통과한 문맥을 다시 미구현으로 세지 않는다.
- **별도 backend 부재:** 이미지 제공자/자산/이력, 실제 협의·승자·공유 Confirm, 내장 renderer/FPS 및 일부 외부 전달. Pack Manager 업데이트/설치해제는 명시적 미지원이다.
- **플랫폼:** 실제 Windows apphost/WebView2/snap/DPI/IME 및 Android/touch는 미검증이다. 기존 불완전 checkpoint를 자동 삭제하지 않는다. Library 전달은 이전 tools/list 네트워크 장애 이후 새 복구 근거가 없어 시도하지 않았다.

교차 패키지·깨끗한 checkout·게시 결과는 아래 마무리 기록에 추가한다. 전체 v536 복원 완료가 아니다.

## 교차 패키지와 게시 후보 검토

새 Windows 교차 패키지는 `/workspace/artifacts/Confectory-v536-view-save/Windows-x64/Confectory.exe`이며 폴더 전체가 필요하다. marker 제외2314개/포함2315개, 131,752,770 bytes다. marker SHA-256 `d780e5122464cb9dae88ef7c5c6c3c568d0b1f97544840b89e5cb0fdd1274dfd`, checksum 목록 SHA-256 `f53ee034eddfc34dea240c2f8251b22e8272790e6ac61f10fb28aa6eef4b1df5`다.

`package-probe.log`는 PASS다. SDK 없는 격리 runtime·별도 cwd/profile의 실제 managed 웹 기동/71 resource·기존 fixture profile 보존·패키지 변조/의존성 누락 거절을 검사했다. 실제 Windows apphost/WebView2 실행은 아니다. 구현10개 source는 package/content와 실제 byte가 일치했다. 후보17개(구현10·테스트3·문서4)를 검토했고 생성물/로그/사용자 자료는 후보에 없으며 비밀 패턴 발견0이다. 이는 모든 비밀의 부재를 증명하는 전수 검사는 아니며 실제 인증파일을 읽지 않았다.
