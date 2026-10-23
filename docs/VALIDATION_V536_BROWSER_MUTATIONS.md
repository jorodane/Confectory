# v536 요소 Browser 이름·선택·드래그 — 첫 묶음

전체 복원, 삭제 기능, Windows 검증이나 게시 완료 보고가 아니다. 기준 ZIP은 `origin/main 196c605`의 v536 원본이며 수정하지 않았다. 현재 로컬 HEAD는 `cf2fcae`, 기존 미게시 엔진/UI 변경을 보존했다.

## 원본과 연결

원본 `app.js` 1438–1468의 선택 로직, 1864의 inline 이름 변경, 1235의 복수 객체 drag payload, 3313–3348의 Browser 부모 이동을 구분해 읽었다. 이름 변경은 stable ID 변경이 아닌 표시 이름 편집이다. 기존 `DeclarationAuthoring.properties.displayName` → local `editorName`과 relations-map title 투영을 재사용했다. 임의 새 이름 저장 형식을 만들거나 참조 ID를 치환하지 않았다.

- embedded Browser에 Ctrl/Meta toggle, Shift 범위, Ctrl+A, Escape, 화살표/Home/End, F2 및 원본 inline 입력 클래스를 연결했다. 선택은 창의 private metadata이며 source 변경이 아니다. 선택창의 Delete 메뉴는 아직 삭제 계약으로 연결하지 않았으며 성공처럼 표시하지 않는다.
- 표시 이름은 기존 source revision/hash와 소유 프로젝트 검사, 기존 declaration 편집을 통과해 stage만 한다. 다른 primary 선택은 복구하고 부모/다른 창의 입력은 적용하거나 삭제하지 않는다. 같은 형제 표시 이름은 UI에서 거절한다. 일반 declaration API가 label uniqueness를 전역 강제하는 것은 아니다.
- 저장되지 않은 이름 원문과 적용 영수증을 per-Browser metadata에 보관한다. cold 시 자동 source write 없이 입력으로 복원한다. 명시적 재시도만 이전 자기 원본으로 돌아간 경우 같은 source CAS를 사용하며, 알 수 없는 원본 상태는 보존 후 차단한다. 체크된 saved source와 일치하는 닫힌 영수증만 정리하고 편집 중 새 원문은 지우지 않는다. 숨긴 창의 이름 입력도 슬롯 회수 금지 대상이다.
- 관련 이름 원문이 실제 metadata와 다르면 기존 Review/Confirm 입력 검사의 대상이다. 최종 검토 token이나 확정 권한을 자동으로 만들지 않는다. 이 새 이름 경로의 Save/Review/Confirm·saved receipt 정리는 아직 실제 UI 완주 검증 전이다.
- 복수 drag는 같은 프로젝트 owner와 stable IDs를 가진 원본 HTML transfer 형태를 유지하며 실제 독립 요소 View에 연결했다. 필드 편집이 아니라 Workspace 배치다. 기존 3-slot 제한과 다른 View의 입력을 유지한다. 창 사이 상태 조회가 진행되면 기다린 뒤 다음 창을 연다. 일반 미구현 Run/신문고 drag handler를 일괄 켜지 않고 소유 요소 전용 drop 수신기를 추가했다.
- Browser 내부 drop은 아직 부모 이동으로 연결하지 않았다. 이를 Workspace 배치로 오인해 창을 만들지 않도록 거절한다. 다른 프로젝트 owner의 오래된 drag도 거절한다. 실제 부모 이동·다중 구조 변경의 원자적 계약은 다음 묶음이다.

## 실행 결과

검사는 `/tmp` fixture만 사용했고 실제 계정·토큰·OAuth·유료 추론이나 사용자 프로젝트를 사용하지 않았다.

- `elements-browser-mutations-1.log`: 실제 생성 엔진+Chromium에서 **2 PASS**(Ctrl/Shift/Ctrl+A/Esc 선택, F2/Esc 취소). 그 다음 이름 stage 자체는 성공했으나 오래된 renderer를 갱신해 inline 입력이 남는 실패를 확인했다. 현재 살아 있는 Browser renderer를 갱신하도록 수정했다.
- `elements-browser-mutations-2.log` 및 `-3.log`: 각각 첫 **1 PASS**로 cold 원문 보관·중복 거절·명시적 한글 rename·live inline 종료/부모111 보존을 확인했다. 이어 복수 배치 수신기 누락, 그다음 첫 창 상태 조회와 둘째 창 열기 경합을 각각 재현해 수정했다. 전체 실행 통과로 부풀리지 않는다.
- `elements-browser-placement-1.log`: cold 이름 재시도 시 background 상태 조회가 시작되면 work가 미실행된 채 반환하는 실패를 확인했다. 이름 API도 busy가 끝난 뒤 실행하도록 고쳤다.
- **최종 `elements-browser-placement-2.log`: 실제 엔진 1 PASS, exit0.** 보관된 한글 이름을 명시적으로 재적용한 뒤, 합성 HTML drag/drop으로 Monster/Other 두 stable IDs의 실제 owned 요소 View 두 개를 배치했다. 부모 private111 및 모든 final source 바이트가 보존됐다. 합성 drag 입력을 native Windows 드래그 검증이라고 하지 않는다.
- **`elements-browser-drop-boundary.log`: 통제 renderer 3개 경계 참**, exit0. Browser 내부 drop 거절, project owner 불일치 거절, 같은 owner의 빈 Workspace drop만 host callback 전달을 확인했다. 이는 backend 권한/실제 사용자 계정 검증을 대체하지 않는다.
- **`elements-browser-lifetime-current.log`: 통제 renderer 3 PASS**, exit0. retired project/window/분리된 section 콜백이 다른 프로젝트 열기·검색 저장을 하지 않는 기존 경계를 확인했다.
- 최종 actions build9 Linux compile exit0. canonical resource62/text53 hash·size, 관련 JS/Python 구문과 diff 검사를 확인했다. 새 Windows 패키지/네이티브 실행은 하지 않았다.

실제 fixture: `/tmp/confectory-element-mutation-uj3cgnj5`. 원본 Unit→Monster→Slime에 테스트 전용 Other를 격리 복사본의 manifest에 등록했다. 실제 final source는 snapshot과 동일하다. 현재 Monster 이름은 `몬스터 A`로 stage된 상태, 부모 Unit private HP111, Monster/Other View 2개가 배치되어 있다. 아직 이 표시 이름을 source Confirm하지 않았다. 프로세스는 종료됐다. 다음 검사는 이 상태를 보존하고 원인 없이 fixture를 reset하지 않는다.

## 원본 정밀 화면 비교

원본 ZIP의 실제 JavaScript/CSS를 로컬 격리 브라우저에서 열고 1480×1050, 동일한 460px 요소 창, Unit→Monster→Slime 구조로 embedded Compact 이름 편집을 렌더했다. 데모 화면은 동작/기하 비교용이며 backend 성공 증거가 아니다.

첫 비교의 현재 input은290px, 원본은326px였다. 원인은 접힌 hierarchy에서 원본의 `browser-simple` body class가 빠져 36px resizer가 남은 것이었다. 기존 원본 클래스 적용을 복원했으며 새 CSS/레이아웃을 설계하지 않았다. 최종 측정은 양쪽 모두:

| 측정 | 원본 v536 | 현재 |
| --- | --- | --- |
| inline 입력 | 326×27px | 326×27px |
| Compact 행 | 394×41px | 394×41px |
| 글꼴 / padding / radius | 14px / 3px 5px / 7px | 동일 |
| 행 icon / expand | 22px / 20px | 동일 |

원본 `original-embedded-browser-inline-name.png`, 실제 엔진 `current-inline-name.png`는 직접 열어 대조했다. 전자는 최종 hierarchy fixture로 갱신됐고 후자는 수정 전290px 이미지이므로 완전한 최종 pixel-diff라고 주장하지 않는다. 최종 DOM geometry는 `current-inline-children.json`에326px로 기록됐다. 최종 배치 화면은 `browser-selection-and-placement.png`다. 내용/위치/프로필 및 다른 source 데이터에 따른 전체 창 차이는 이 작은 기하 일치로 완료 처리하지 않는다.

## 정확한 잔여

1. 이름 변경의 상세 Save/취소/saved cold/Review·명시적 compiler Confirm 및 다른 이름/동시 source 변경 경계 실제 UI 완주.
2. **삭제 미구현.** 원본 데모는 객체를 즉시 배열에서 제거하고 자손 parent/inherits를 지우지만, 현재 엔진의 Changes/Export/Restore/Confirm은 source 문자열 쓰기만 표현하고 제거 tombstone/복구를 표현하지 않는다. `file-stream.Commit`도 hash+text 쓰기만 수행한다. 빈 문자열/sentinel/File.Delete로 우회하지 않는다. 소유 제거+manifest 등록 변경, CAS/원자적 batch, Save/취소/cold/검토확정, 참조 존재시 안전 거절, 복구와 실제 final 파일 처리 계약을 먼저 연결해야 한다.
3. Browser 내부 object/Category 부모 이동, containment와 상속 구분, 범위/타입/CAS·다중 변경 검증 미완료. 원본이 하는 이름 자동 변경·자손 이동을 조용히 복제하지 않는다.
4. 다중 창의 반복/실패/프로젝트 전환/재시작 전체 조합, Context 메뉴의 table/tab 경로, reference hover, standalone Data 및 전체 정밀 화면 비교 잔여.
5. 기존 고정 목록인 모바일 Blueprint 제한, Helper 이미지/삭제, 전투·신문고/Yogi 실제 계약, 창별 Run, 전체 회귀·Windows 패키지·checkout·게시도 미완료. UI 완료 후 Helper 편집 기능 확장 순서를 유지한다.
