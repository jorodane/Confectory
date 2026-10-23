# v536 요소 내부 Data 직접 편집 — 통합 검증 중

전체 v536 복원·Windows 실행·게시 완료가 아니다. 원본 `bindDataInputs`, `browserDataItems`, `data-property-detail` 동작을 다시 대조했다. 원본 상세 편집은 새 팝오버가 아니라 별도 요소 창을 열어 해당 경로를 펼치고 스크롤하는 동작이다. 기존 요소 편집기와 그 Save/Discard/Review/Confirm 계약을 재사용했다.

## 구현

- `TableCommand`의 `browser-element-edit`는 현재 열린 소유 프로젝트의 object 한 개와 Data에서 관측한 scalar column만 받는다. 표시된 source revision/textHash/viewHash를 모두 확인하고 기존 InstantTable의 버전·자료형·경로 검증과 EditBatch를 재사용한다. 임시 table은 작업 후 닫으며 사용자에게 표 구성 UI를 만들지 않는다. 최종 source/Save/Confirm은 실행하지 않는다.
- inherited compound 하위 값처럼 명시적 재정의가 필요한 경로는 직접 쓰기를 거절한다. 참조·다중 값은 기존 요소 상세 편집으로 연결한다. 다른 프로젝트/임의 필드/위조 버전 요청은 서버에서 거절한다.
- 클라이언트는 oninput 원문을 기존 창 metadata에 보관하고 Enter/값 변경 확정 시 해당 셀만 작업 초안에 적용한다. 같은 창의 알려진 자기 쓰기 결과만 다음 입력 proof에 대응시키며 다른 창의 입력은 갱신/삭제하지 않는다. 실패 시 입력과 원래 proof를 보존한다. 현재 구현의 저장 전 영수증 보관 결함은 아래에 별도로 기록한다.
- 상세 편집은 원본처럼 별도 소유 View를 열고 path 및 상위 경로의 접힘을 해제한다. 미적용 입력이 있는 숨겨진 기존 View는 새 상세 창으로 재사용하거나 슬롯 회수하지 않는다. 기존 3슬롯 제한을 유지한다.
- 같은 primary 창이 다른 요소로 전환되어도 Browser metadata를 요소별로 보관하도록 `elementBrowsers`를 추가했다. UI 레이아웃은 변경하지 않았다.
- 새 선언/등록 검토 진입의 `reviewGroup`에서 transport `stale_revision`을 재현했다. 같은 project/source/생성 ID 묶음과 입력 상태를 매번 확인할 때만 거절된 admission을 최대 3회 다시 시도한다. 내용이나 final token을 자동 승인하지 않는다.

## 실제 결과: 통과와 미완료

`v536_elements_data_write.py` 첫 실행은 격리된 새 Unit→Monster→Slime 프로젝트에서 **4건 통과 후 재시작 값 보관 결함에서 실패**했다.

1. Data HP200 쓰기가 실제 서버의 한 번 거절된 transport admission 뒤 적용됐다. parent Unit의 private111 및 다른 Monster View의 private150은 유지됐고 final source 바이트는 그대로였다.
2. 제출 전 201 입력을 Esc로 취소하면 실제 staged200을 다시 읽었고 쓰기 요청이 늘지 않았다.
3. 서버가 오래된 표시 proof, 다른 프로젝트 object, 명시적 parent override가 필요한 inherited compound child 쓰기를 거절했다.
4. int 필드의 2.5는 원문과 오류를 보존하며 거절했고, 사용자가 3으로 고친 명시적 재시도는 기존 type validation을 통과했다.

그 다음 nested long `9223372036854775805` 쓰기는 실제 서버 성공 결과로 확인했고, 원래 숫자를 Number로 변환하지 않았다. 그러나 **사용자가 Save하지 않은 staged 값을 처리한 뒤 Data metadata 입력을 삭제**했다. 프로세스를 종료/재시작하자 unsaved shared draft가 원본으로 돌아왔고, UI에도 영수증/보관 입력이 없어 `9223372036854775804`가 표시됐다. 같은 검사에서 아직 제출하지 않은 한글 metadata 입력은 복원됐다. 이는 저장 전 적용 영수증의 수명을 잘못 처리한 실제 결함이며 해결/검증 완료가 아니다.

기존 `v508` Source Save 계약을 자동 Save로 바꾸거나 새 버전으로 무조건 재적용해 통과시키지 않았다. 다음 작업은 applied-but-unsaved 입력/영수증을 보관하고, 실제 saved checkpoint와 구별하여 cold 시 자동 쓰기 없이 복원하는 것이다. 오래된/알 수 없는 외부 변경은 계속 막아야 한다. 새로운 내구성/장치 오류 범위를 추가하는 작업이 아니다.

증거: `/tmp/confectory-element-data-write-xy2kg6na/{progress.json,failure.json}` 및 `/workspace/scratch/v536-reference/elements-data-write-1.log`. 이후 array 상세 편집·다른 창 Save/Cancel 단계는 실행되지 않았다. 구현되어 있다는 이유로 실제 상세 Save 검증을 통과했다고 세지 않는다.

## 생성 그룹 검토

`v536_elements_creation_confirm.py` 네 번째 실행은 **새 FreshVariant와 ProjectManifest만 검토에 포함되고 취소 시 final 파일이 유지되는 실제 1건**을 통과했다. 별도로 staged Unit111은 그 묶음에 포함되지 않았다.

다음 최종 Confirm은 버튼 클릭 전에 다른 플로팅 요소 창의 resize handle이 pointer를 가로채 timeout됐다. 일반 focus 클릭만으로 해결되지 않는 layer 경계가 관측됐다. 아직 원본 host/layer 구조의 정확한 보정은 하지 않았고 force click으로 검사를 통과시키지 않았다. `confirmGroup` 요청은 보내지지 않았다. 새 FreshVariant final 파일은 없고, original manifest/Unit 파일은 보존된 상태다. 생성 그룹 compiler Confirm·cold·재편집은 **미완료**다.

증거: `/tmp/confectory-element-data-create-id7oxtwx/creation-confirm-failure.json`, `elements-creation-confirm-4.log`. 이 fixture는 old Fresh222와 registration/Unit111이 공유 초안에 있으므로 fresh 생성 fixture로 재사용하지 않는다. 이전 실행은 숨겨진/겹친 창을 잘못 누르는 fixture 및 첫 Data mode 선택을 가정한 검사에서 중단했다. 실제 original UI focus/표시 크기 선택을 거치도록 보완했다.

## 컴파일 및 한계

첫 cells build는 C# local `owned`/`applied` 이름이 기존 변수와 충돌해 실패했다. 이름을 고친 cells build2/3은 Linux compile exit0이었다. JS/Python 구문 및 canonical resource 62개/text53개 검사는 다시 확인했다. 미완료 상태를 게시하지 않았다.

actual rendered 상세 화면의 새 정확 비교는 위 두 실패 때문에 아직 완료하지 않았다. 다른 프로젝트/창 변경, 늦은 응답·취소·동일문구 새 입력, saved checkpoint/Confirm 후 영수증 정리, 상세 배열·참조·상속 재정의의 신규 진입 회귀도 잔여다. 기존 v508 typed editor 검증을 이번 신규 진입의 통과로 대신하지 않는다.

이름 변경·삭제·다중 선택·드래그·정밀 원본 대조와 모바일 Blueprint 제한·Helper 이미지/폼 삭제·전투 로그/신문고·창별 실행은 고정 잔여다. 전체 회귀/Windows 교차 패키지·checkout·normal push 및 실제 Windows/Android 검증은 완료하지 않았다. 실제 계정/토큰/유료 추론을 사용하지 않았고 main/Android/원본 ZIP/사용자 프로젝트는 변경하지 않았다.

## 2026-10-23 후속: 두 차단 결함 및 실제 상세 저장 완주

앞의 첫 실패는 이력이다. 현재 해당 두 결함을 수정하고 아래 경로를 실제 Linux 생성 엔진+Chromium에서 통과했다. v536 전체 복원/새 Windows 빌드/게시는 여전히 미완료다.

### 수정 경계

- 셀 적용 결과는 Save가 아니다. 적용 성공 시 원문과 ackRaw, 같은 창에서 관측한 bounded source revision/textHash/viewHash 이력을 metadata에 남긴다. cold 렌더는 입력만 복원하며 쓰기/Save를 재생하지 않는다. 사용자의 명시적 Enter는 현재 값이 정확한 기존 자기 관측 상태일 때만 새 CAS 요청을 만든다. 알 수 없는 원본/정의 상태는 재기준화하지 않는다. Esc는 새 사적 입력과 이미 접수된 입력을 구별하여 보관 의도를 잃지 않게 한다.
- 기존 owner-checked BrowserDrafts status의 저장 여부와 정확한 source hash/revision을 읽어 `checkpointSaved`를 투영한다. 저장된 현재 값과 일치하는 접수 영수증만 정리하며, 아직 다른 원문을 가진 입력·다른 창의 입력은 유지한다. 이 status 읽기는 자동 Save/Discard/Confirm을 하지 않는다.
- 원본 `app.js:3097 openReview`는 495×390 일반 창이며 중앙 모달이 아니다. 새 Review도 같은 크기의 플로팅 전면 창으로 연결했다. 실제 재오픈 실패는 retained 창을 무조건 world layer에 붙인 뒤, 이미 unplaced인 창의 배치를 다시 계산하지 않아 생겼다. retained 창도 기존 clamp/place 경로를 통과해 올바른 floating layer로 복귀한다. 모든 창의 pointer-events를 끄거나 force click으로 통과시키지 않았다.
- 별도 요소 View의 복합값 편집은 종전 `editObjectStructure`가 primary selection만 검사하여 실제 저장을 거절했다. 명시적 `editViewObjectStructure`를 기존 view/context/id 검사 및 기존 object-structure CAS로 연결했다. Save/Review/Confirm 권한을 추가하지 않았고, 3개 슬롯 및 다른 View의 입력 보존을 유지한다.
- Data의 blur 적용 중 행이 바뀌면 상세 버튼의 click이 소실되는 경우도 확인했다. 같은 원본 버튼이 pointerdown에서 입력 처리를 기다린 뒤 상세를 열며 키보드 click도 유지한다. 입력 오류를 단순 blur로 반복 제출하지 않으며 사용자가 변경/Enter로 명시적으로 재시도할 수 있다.
- 관련 Data 원문이 아직 실제 source 값과 다르면 Review/Confirm 진입을 거절한다. 검토 token이나 사용자의 명시적 확정은 자동 승인하지 않는다.

### 실제 검증 결과와 증거

각 숫자는 해당 실행에서 출력된 PASS 수이며 전체 회귀 통과율이 아니다. 중간 실패를 지우거나 전체 스크립트 통과로 합산하지 않았다.

- `elements-data-write-2.log`: 첫 **6 PASS**, 이후 상세 저장에서 중단. HP200/다른 창 HP150/부모111 분리, Esc201, stale/foreign/inherited readonly 거절, int2.5 거절·3 재시도, long `9223372036854775805`와 한글 원문 cold 복원, 자동 쓰기 없음, 명시적 HP/Speed/long 재적용을 실제 확인했다. 이후 발견한 상세 endpoint 결함은 위와 같이 수정했다.
- `elements-data-detail-1.log`: 첫 **3 PASS**, 이후 상세 첫 클릭 소실/숨긴 이전 View 선택에서 중단. 별도 세 번째 View에서 Counts 펼치기, 정확한 long 배열 저장 및 checkpointSaved 확인, 저장된 ack 영수증만 정리를 확인했다. parent111·다른 HP150·실패했던 두 번째 View 배열 원문은 보존됐다. 증거 `/tmp/confectory-element-data-write-k339i_m_/actual-data-and-array-detail.png`.
- `elements-data-followup-1.log`: 첫 **1 PASS**로 cold 후 unsaved201 영수증 Esc 취소 → saved200, rollback 쓰기 없음 확인. 이후 상세 클릭 소실은 수정했다.
- **최종 `elements-data-followup-2.log`: 3 PASS, exit0.** 실제 원본 상세 버튼으로 진입 후 다른 root archive의 invalid Data2.5 때문에 Review/Confirm 요청 자체가 나가지 않음, View의 다른 id/오래된 revision 거절, 실제 재시작 후 saved200/3/long5805와 부모111·HP150·기존 배열 사적 입력 보존을 확인했다. final source 바이트는 모두 원본이다. `detail-followup-evidence.json`, `saved-data-cold-restored.png`가 같은 fixture에 있다.
- `elements-creation-confirm-7.log`: 첫 **2 PASS**, 이후 cold fixture가 Data 모드와 새 플로팅 View를 명시적으로 선택하지 않아 중단. Review Cancel 후 파일 보존, 정상 클릭 가능한 Confirm 및 실제 compiler Confirm 성공을 확인했다. FreshVariant222+ProjectManifest만 최종 반영, Unit111은 별도 미확정 초안이고 Unit final은100이다. 이 fixture는 이제 **확정 완료** 상태이므로 생성/Confirm을 다시 실행하지 않는다. `review-layer.json`은 `clickable:true,layer:true`; `reachable-creation-review.png`를 실제 열어 확인했다.
- **최종 `elements-creation-cold-2.log`: 1 PASS, exit0.** 확정된 fixture를 실제 cold 시작 → 일반 Project Browser 재진입 → Data 선택 → 새 플로팅 View에서 private223 취소 →222 복원까지 확인했다. 원본 파일/부모 Unit111을 보존했다. 증거 `/tmp/confectory-element-data-create-id7oxtwx/creation-cold-evidence.json`.
- 최종 receipts build3 Linux compile exit0, 이전 receipts build1/2도 exit0. canonical resources62/text53 hash·size, 변경 JS/Python 구문, git diff --check를 확인했다. 렌더 이미지로 기존 Review495×390 및 요소 상세 배치를 확인했으며 새로운 디자인을 추가하지 않았다.

### 남은 범위

이 묶음은 Data 보관·상세 Save·생성 그룹 명시적 Confirm의 확인된 차단을 해결했다. 완전한 화면/입력 회귀나 전체 v536 완료를 뜻하지 않는다. 늦은 응답과 in-flight Esc/같은 원문 새 입력의 추가 조합, inherited/reference 상세 신규 진입 전체 조합은 후속 통합 회귀에 남긴다. 저장 장치/정전 내구성 범위를 추가하지 않는다.

다음 고정 Browser 잔여는 이름 변경·삭제·다중 선택·드래그·참조 hover·Category containment/생성과 정밀 원본 대조다. standalone Project Browser Data는 별도 어댑터라 아직 embedded Data와 같다고 주장하지 않는다. 기존 모바일 Blueprint 제한/이미지·삭제/전투 로그·실행창 및 전체 회귀·Windows 패키지·checkout·게시도 미완료다. 실제 Windows/Android 기기·OAuth·사용자 계정·유료 추론 검증은 하지 않았다. main/Android/원본 ZIP/실제 사용자 프로젝트는 보존했다.
