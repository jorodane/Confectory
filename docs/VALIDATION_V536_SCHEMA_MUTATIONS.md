# v536 기존 속성 표시 이름·명시 삭제 — 첫 단위

`c8a678d` 이후 기본 요소 창의 직접 적용한 소유 schema root 속성 표시 이름과 삭제를 연결했다. 복합/중첩 정의 생성·수정, 독립 properties View 및 dirty raw source의 결합 Save는 **아직 미완료**다. 원본 HTML/CSS/버튼 배치·크기를 바꾸지 않는다.

## 원본 의미와 연결

저장소 `reference/site-ui/Confectory-Editor-Prototype-v536.zip`의 `app.js`는 `propertyKey(field)`에서 stable key를 사용하고 `renderObjectSchema`의 이름 변경은 `field.name`만 바꾼다. 삭제는 선택한 정의와 해당 로컬 값을 지운다. 원본의 타입 변경 중 기본값 초기화 동작을 이번 엔진에 추가하지 않는다.

- 이름은 native field ID/path를 rename하지 않는다. 기존 primitive metadata 문법인 `value editorFieldName_<nativeKey> = "표시 이름"`을 해당 schema에 저장한다. 기존 데이터 키·핀 경로·정확한 숫자·본문은 그대로다. schema가 공유되면 그 정의의 표시 이름도 공유된다. 빈 이름·60자 초과·제어 문자·같은 위치의 중복 이름은 전체 후보를 거절한다. 실제 source를 보관한 hash를 projection에 포함하며 저장할 때 최신 hash로 임의 치환하지 않는다.
- 삭제는 기존 root local 정의와 해당 owner 로컬 datum을 한 후보에 넣는다. 소스는 Confirm 전까지 바뀌지 않는다. 다른 객체/자손 값이 해당 필드를 쓰거나 Blueprint property 읽기/쓰기가 필요로 하면 전체 삭제를 거절한다. 다른 객체의 값이나 연결을 자동으로 지우지 않는다. 같은 필드의 미저장 값/타입/이름 입력이 있으면 먼저 명시 저장/취소하도록 막아 원문을 조용히 버리지 않는다.
- schema-name/schema-remove도 기존 SlotBatch/ApplySlots의 원래 소유권·schema hash·field contract·source closure와 checkpoint CAS, staged Blueprint 검증, 원자 Review 그룹을 사용한다. 새 접근 권한·자동 Confirm·유료 모델 호출은 없다.
- 화면은 기존 이름 input과 × 버튼을 사용한다. 입력은 즉시 private presentation에 보관하고 잘못된 이름도 실패 시 유지한다. Escape/기존 Ctrl+Z/변경 취소와 재시작 복원 경로를 사용한다. 상속/외부 정의를 local처럼 편집하거나 독립 View의 별도 소유권을 가로채지 않는다.

## 실제 발견한 결함

1. 표시 이름만 바꿔도 helper가 owner를 format해 객체 소스의 공백까지 바꿨다(`ui-rename1.log`). 원래/새 owner의 정규 형식이 같으면 원문을 반환해 label-only Confirm이 schema 파일만 바꾸게 했다. metadata 검사도 owner text 전체 일치를 요구한다.
2. owner 원문을 유지하자 schema만 dirty인 원자 그룹의 Confirm이 비활성화됐다(`ui-rename2.log`, `ui-storage3.log`, `ui-loss3.log`). BrowserDrafts 상태에 atomicEditGroup 전체를 포함하고 UI 상태 조회의 갱신 기준에 관찰한 schema hash를 포함했다. 저장 직후와 cold 후 모두 실제 Confirm 버튼 활성화를 검사한다.
3. Confirm은 실제 변경 schema만 반영했지만 저장 기록에서 clean owner/등록부 행을 남겨 다음 시작이 `Project workspace unavailable`로 막혔다. `Acknowledge`가 atomicEditGroup을 그룹 정리 대상으로 인식하지 않은 것이 원인이었다. SDK/PATH를 맞춘 별도 post-Confirm 읽기에서도 같은 실패가 재현되어 환경 원인으로 세지 않는다. 이제 완전한 saved 그룹의 **모든** 현재 text/kind/path가 clean·동일할 때만 지원 행까지 함께 정리한다. live 그룹도 모든 멤버가 clean/existing일 때만 정리한다. dirty/불완전/불확실한 기록은 자동 삭제하지 않는다. 기존에 이미 불완전해진 checkpoint의 무조건 삭제·자동 재적용은 이 수정에 포함하지 않는다.

## 격리 검증

모든 테스트는 임시 프로젝트/profile이다. 사용자 자료·계정·인증파일·실제 로그인·유료 추론·실제 프로젝트 실행을 사용하지 않았다. 숫자는 공통 준비를 포함한 PASS 묶음이며 독립 테스트 수로 합산하지 않는다. 로그는 `/workspace/scratch/v536-schema-mutations/`에 보존한다.

| 검사 | 실제 확인 범위 |
| --- | --- |
| `v536_schema_mutations_metadata.py` | 4 PASS(`metadata4.log`). 한글 표시 이름/native key/owner 원문 전체/raw64, 정확한 schema hash projection, 빈/중복 이름 거절, 이름+타입 계획 순서 독립, 명시 삭제의 sibling 값 보존, 자손/외부/오래된/겹친 입력 전체 거절. 파일 쓰기 없음 |
| `rename` 실제 엔진/Chromium | 잘못된 이름 Save 전체 거절→Escape→명시 재시도, 정확한 숫자·다른 필드, 저장 직후 Confirm 활성화, cold/Review 취소/실제 compiler Confirm, 확정 후 cold 및 그룹 정리 |
| `delete` 실제 화면 | ×→Ctrl+Z의 정의/raw64 복원, ×→한 후보 Save, cold/Review 취소/명시 Confirm, 확정 후 cold. schema와 owner 삭제 값만 변경 |
| `copy` 실제 화면 | 같은 표시 이름과 새 private copy의 C# 본문/wrapper를 함께 Save/cold/Review/Confirm. 원본/부모/다른 target 보존 |
| `storage` 실제 화면 | checkpoint 쓰기 거절은 전체 미적용/입력 보존, cold 명시 재시도·Review 취소·compiler Confirm까지 4 PASS(`ui-storage4.log`). 최종 그룹 정리 수정의 post-Confirm cold는 별도 최종 경로에서 검사 |
| `loss` 실제 화면 | 적용 응답과 결과 조회를 함께 유실, 원문/시도 보관, cold receipt 조회만으로 복구하며 새 applySlots가 없음을 검사. Review/Confirm 및 확정 후 cold |
| 취소·경합 | 각각2 PASS(`ui-cancel3.log`, `ui-conflict3.log`). 미적용 확인 후 명시 취소/cold, 실제 동료 저장 뒤 전체 차단·상대 checkpoint/입력 cold 보존 |
| 참조 보호 | renderer2 PASS(`ui-delete-reference1.log`): 자손의 데이터 사용 시 삭제 전체 거절·명시 취소/cold. 실제 API1 PASS(`ui-graph2.log`): 데이터가 없어도 property 읽기/Set graph가 사용하면 staged 검사에서 삭제 전체 거절. graph는 renderer 검사가 아님 |
| 기존 회귀 | 이전 primitive schema metadata4/adapter PASS. 기존 타입 거절→새 copy 혼합 Save→응답 유실/cold 복구→Review/Confirm 4 PASS(`type-copy-regression.log`). 공통 candidate formatter·그룹 상태 변경의 영향을 확인했다 |

테스트의 첫 저장 실패/응답 유실 보존 비교는 이전 journal이 새 journal의 previousAttempts로 보관되는 정상 정책을 반영하지 못했다(`ui-storage2.log`, `ui-loss2.log`). 현재 비교는 입력 전체와 이전 journal의 정확한 동등성/보관을 검사한다. assertion을 제거하거나 실패 기록을 지우지 않는다. 초기 metadata 문자열의 한글 escape 여부에 의존한 기대도 실제 파싱 값과 hash/원문 검사로 바꿨다. 초기 실패 로그는 남긴다.

## 정확한 잔여

- 이번 이름/삭제는 기본 요소 창의 직접 소유 root 정의 단위다. 복합/중첩 속성 정의 생성·변경, cardinality/kind 선택·아이콘 및 다른 source 종류의 정의 편집은 별도 미완료다.
- 독립 properties View/별도 Save, dirty raw source/선언, 기존 provider·saved-copy ABI·다중 target ABI·Set/property를 섞는 경로는 계속 차단한다. source ID/path/hash/version과 같은 후보/CAS로 결부하고 창별 입력·프로젝트 문맥·실패/응답 유실/취소/cold/Confirm을 수용한 뒤에만 해제한다.
- Browser 등의 native 경로 표시를 모두 표시 이름으로 바꾸는 작업과 미검증 ABI/모바일·최종 조작 수용은 전체 현황표에서 구분한다. 경로/저장 키를 표시 이름으로 바꾸지 않는다.
- 기존에 이미 불완전한 원자 checkpoint는 사용자 소스를 보존하고 fail-closed한다. 증거 없이 clean으로 간주해 자동 삭제하지 않는다.

## 패키지·게시 기록

최종 코드의 새 Windows 교차 패키지·깨끗한 checkout·resource 검사와 원격 SHA 결과는 아래 마무리 기록에 추가한다. 앞선 `/workspace/artifacts/Confectory-v536-schema-mutations/Windows-x64`는 마지막 그룹 정리 수정 전 중간본이다. 실제 Windows apphost/WebView2/DPI/IME 및 Android/touch는 실행하지 않았다. Library는 이전 tools/list 네트워크 실패 뒤 새 복구 근거가 없어 재호출/업로드하지 않았다. 전체 v536 UI 완료나 실제 파일 전달 완료가 아니다.

## 최종 실제 수용 결과

최종 생성 엔진은 `engine5.json`이며 경고0으로 완료했다. 실제 엔진/Chromium 최종 실행은 `ui-rename5.log` 4 PASS(`/tmp/confectory-wide-mixed-8ykwcb01`), `ui-delete5.log` 4 PASS, `ui-copy5.log` 4 PASS(`/tmp/confectory-wide-mixed-r9xcexiw`), `ui-loss5.log` 5 PASS(`/tmp/confectory-wide-mixed-y_8n9oje`)다. 모두 **명시 Confirm 뒤 한 번 더 프로세스를 재시작**해 창/값/표시명과 그룹의 완전한 저장 기록 정리를 확인했다. 현재값이 없는 지원 행을 무조건 dirty로 만들거나 원본 공백을 바꿔 통과시키지 않았다.

`/tmp/confectory-wide-mixed-8ykwcb01/schema-post-confirm-cold.png`를 실제 열어 원본 카드 배치에서 한글 표시명과 sibling 값을 확인했다. input 폭 때문에 긴 숫자는 이미지에서 일부만 보이며 전체 정확도는 실제 input value assertion으로 검사했다. 원본 레이아웃 전체의 pixel 동일성 검사는 아니다. delete5는 모든 assertion/exit0 뒤 Playwright driver 종료 중 pending route 경고를 남겼다. 테스트는 route callback 완료를 기다리고 browser를 명시 종료하도록 보완했으며 delete6 재검증도4 PASS/exit0으로 완료했고 종료 경고가 없어졌다(`ui-delete6.log`, `/tmp/confectory-wide-mixed-nhopav4j`). 보호 assertion은 유지했다.

최종 Windows 교차 패키지: `/workspace/artifacts/Confectory-v536-schema-mutations-final/Windows-x64/Confectory.exe` (폴더 전체 필요). 선언 파일 2313개+marker=2314개, 131,739,879 bytes. marker SHA-256 `a70d634bd87f14a3c5b678811c032201cef7a10b8bf495ad2b0b909a48e7294b`, checksum 목록 SHA-256 `a89ec0eaf2d5c8abb6dee0ffeae66cdec88336a56b4e1010431fe3f2e058302c`. package/root source 및 helper 일치, SDK 없는 격리 managed 웹 시작/구성·리소스 변조/누락 거절과 깨끗한 checkout의 재현 결과는 아래 게시 마무리에서 구분한다. 실제 Windows 네이티브 실행이나 Library 전달은 아니다.

최종 패키지 구성/checksum 및 SDK 없는 별도 cwd/profile의 실제 managed 웹 시작·70 resource·변조/누락 거절은 `package-probe2.log` PASS다. 변경17개는 구현12/테스트2/문서3으로 검토했고 생성물·로그·profile/사용자 데이터는 Git 후보에 없으며 비밀 패턴 발견0이다(모든 비밀 부재를 증명하는 검사는 아님). 실제 인증파일은 읽지 않았다. 원본 HTML/CSS·reference·Android 변경은 없다.

## 깨끗한 checkout 최종 기록

검증 코드 커밋 `f96a584ac4b2d0202b81a8d84dfae870e8380125`를 기존 격리 checkout에 정상 fast-forward했다. Release solution build 경고0/오류0(`checkout-build.log`), Linux 생성 엔진 경고0(`checkout-engine.json`), 실제 이전 CRLF checkout→attributes pull과 fresh LF 모두70 canonical/exact resource 읽기·내용/인코딩/BOM/binary/budget 거절·원래 byte 불변 PASS(`checkout-resources.log`)다. root/checkout의 구현12개 source는 정규화 byte가 일치하고 root/package 구현12개 및 helper DLL은 실제 byte가 일치했다.

이번 중간 환경 disconnect는 실제 명령이 불가능한 상태를 확인한 뒤 같은 저장소의 pwd/status/engine JSON 읽기로 복구를 확인했다. 그 이후 검증을 마쳤으며 다른 환경/저장소로 옮기지 않았다. 최종 문서 기록 커밋은 runtime 변경이 없다. 승인된 `https://github.com/jorodane/Confectory.git`의 `work/current`만 정상 게시하며 최종 원격 SHA/두 작업 트리 clean/main 보존은 체크포인트·최종 응답에 남긴다. 전체 UI 및 실제 Windows 실행 완료가 아니다.
