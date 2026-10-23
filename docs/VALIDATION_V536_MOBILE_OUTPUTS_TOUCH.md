# v536 모바일 출력 정의·선택과 터치 기본 동작

2026-10-23. 최초 v536 원본의 출력 inspector/정의 목록/위치 선택과 Graph의 기본 터치·보기·찾기만 이번 묶음의 기준으로 삼았다. UI를 재설계하거나 새 실행/분기 언어를 추가하지 않았다. 전체 Blueprint·전체 UI 수용/배포 완료를 의미하지 않는다.

## 고정 완료 기준과 결과

| 원본 경로 | 이번 결과 | 남는 제한 |
| --- | --- | --- |
| 출력 inspector의 이름·기존 출력 선택·자료형 | 원본 label/input/select/type button 배치, 이름 draft/취소·기존 선택·자료형 변경 보호 연결 | 공유 출력 이름의 분리/고정 반환 이름 변경·미정의 빈 출력의 최종 저장은 지원하지 않으며 raw 입력을 보존하고 차단 |
| 출력 목록 + → 새 이름/타입 → 배치/값 → 저장 | +는 정의만 추가, 실제 위치 선택 전 node를 만들지 않음. 새 정의와 assignment/routes/value가 기존 rootParameters 한 계획으로 저장됨 | 다른 노드 편집·root-body 등 기존 혼합 저장 제한은 유지. 모든 특수 실행 출력/직접 검색 메뉴 조합을 추가하지 않음 |
| 취소·저장·재시작·명시적 Confirm | 잘못된 이름 raw draft의 Save 차단/cold 복원/Escape, 루트 계획 Save 및 실제 compiler Confirm 완료 | 실제 사용자 프로젝트/Windows 장치 결과로 확대하지 않음 |
| 기본 터치/보기/찾기 | 원본 pan/pinch/cancel helper, 전체 보기·미니맵·설명 및 기존 local placed finder, 선택한 실행선 메뉴 어댑터 | 영역 선택/다중 노드 선택은 비활성. 내부 흐름/async와 모든 특수 핀/ABI/복사 문맥의 원본 범위는 아직 미완료 |

## 연결 방식

`feature-authoring.js`의 기존 root output 이름 핸들러를 재사용하여 배치되지 않은 새 출력 정의도 이름/타입을 편집한다. 기존 타입 picker에 넘기는 unplaced pin은 현재 owned root output을 가리키는 presentation adapter이며 서버 영수증/프로젝트 권한/정의 조회 범위를 만들지 않는다.

새 정의의 위치 배치는 `outputCreates`, `outputEntry`, `outputRoutes`, `valueJson`을 기존 `changeRootContract` 계획에 넣는다. 서버 계약이나 mixed-save guard를 완화하지 않았다. 실제 확인한 신규 정의/값/경로 편집의 private author cell은 `root-parameters` 한 개다. backend의 기존 rootParameters 검증/acyclic/type/소유권/CAS와 별도 compiler Confirm을 사용한다.

Inspector에서 확정하지 못한 이름은 `contract-draft:export-name`으로 보관한다. 저장이 차단되어도 새 정의/값/경로를 버리지 않는다. Escape는 원본 overlay 닫힘과 해당 raw 이름 취소를 수행한다. 기존 출력 선택은 같은 typed binding/계약 편집 경로를 호출하며, 연결된 값과 호환되지 않는 타입 변경은 provider source 쓰기 전에 거부한다.

원본 `app.js`의 `bindTouchCanvas` pointer lifecycle을 `bindBlueprintTouch`로 재사용했다. camera/zoom만 변경하며 기존 범위를 유지한다. Ctrl/F 및 터치 메뉴 찾기는 새 검색 데이터/서버 요청을 만들지 않고 기존 `find.js`의 화면 내 검색에 modern author context를 연결한다. 현재 숨김/소유 프로젝트/세대가 달라진 문맥의 callback은 기존 검사로 거부된다. 영역 선택 메뉴는 연결하지 않은 상태를 명시한다.

## 실제 엔진 검사

- `mobile-output-definitions-engine-4.log`, `/tmp/confectory-mobile-output-definitions-b3qqn23v`: **3 PASS 후 fixture의 마지막 타입 선택에서 중단**. 새 정의만 생성/이름·long 타입/위치·7 값의 단일 root plan, 잘못된 이름 Save 거부와 cold raw 입력 복원/Escape 취소, 실제 rootParameters Save 및 별도 compiler Confirm을 완주했다. Confirm 전 원본 바이트 불변, 이후 Serial/SerialBlueprintBody 및 owned Blueprint만 변경했다. 마지막 실패는 재시작 전 `page`에서 만든 `picker` locator를 재사용한 `TargetClosedError`였으며 제품 실패로 단정하지 않았다.
- 같은 소비된 fixture를 reset 없이 이어 쓴 `mobile-output-select-type-1.log`: **집중2 PASS**. 기존 출력(return/reply) 선택/되돌림/checked Save, 연결된 long 값에 bool 타입을 적용하려는 시도 거부·값7/확정 source 보존. `select-type-evidence.json`이 최종 근거다. 앞 전체4개 검사를 모두 처음부터 통과한 것으로 합쳐 보고하지 않는다. 전체 test의 오래된 page locator도 현재 page에서 조회하도록 수정했다.
- `mobile-touch-engine-4.log`, `/tmp/confectory-mobile-touch-m819iymy/evidence.json`: **4 PASS**. 실제 owned graph의 원본 View 메뉴/fit/minimap/description, Chromium protocol touch pan+두 손가락 pinch, touchCancel의 camera/zoom 복원, 기존 local finder와 실제 배치 node focus. source 바이트/private author input은 불변이고 finder에서 Blueprint provider 호출이 없다. **브라우저 합성 입력 검사이며 실제 터치 하드웨어/Android/Windows QA가 아니다.**
- 기존 출력 배치의 변경 영향 회귀 `mobile-output-place-regression-2.log`, `/tmp/confectory-mobile-output-place-bpgjbsaa/evidence.json`: **실제4 PASS**. 원본 선택 취소·앞뒤 연결/값 저장·cold/컴파일 Confirm·삭제 splice/재확정을 새 inspector와 함께 확인했다.
- `mobile-outputs-desktop-regression.log`, `/tmp/confectory-feature-serial-renderer-o5zzrns4/evidence.json`: **통제 renderer15 PASS**. 실제 backend/계정 성공과 구분한다.

첫 출력 test의 Python syntax 오류는 엔진 실행 전이었다. 다음 실행의 예상 메시지(일반 raw-draft 오류)보다 우선한 실제 mixed-save guard 메시지는 그대로 유지하고, test에서 정확한 mixed-save 거부와 raw draft 보존을 함께 검사했다. 이어 Escape가 원본처럼 inspector도 닫는 상태를 무시한 locator 기대를 수정했다. 모든 실패 로그를 보존한다.

터치 첫 실행의 Playwright `arg` 호출 형식을 고친 뒤 pan/pinch/cancel3개가 통과했다. 다음 메뉴를 즉시 마우스 클릭하는 fixture는 원본의 400ms ghost-click 보호에 막혔다. 보호를 제거하거나 sleep을 넣지 않고 실제 후속 터치 탭으로 검사하여 최종4개가 통과했다.

## 화면·환경과 한계

`named-output-inspector.png`, `touch-graph-view.png`를 실제 열어 원본 `blueprint.js`의 export inspector, View menu, touch helper와 대조했다. 전체 화면/모든 객체 상태의 pixel-exact 수용은 아직 아니다. 원본 CSS는 변경하지 않았다.

환경 disconnect 중 exec-server가 명령 생성을 거부했고 뒤이어 실행 환경이 unavailable이었다. 같은 환경의 실제 `pwd` 응답 및 build4 로그를 확인한 뒤, 테스트 로그/파일이 없는 것을 확인해 미시작 명령만 재개했다. 다른 환경으로 옮기지 않았다. 마지막 Linux `mobile-outputs-build-4.log` compile exit0, resource62/canonical text53의 SHA·크기 및 JS/Python 구문·diff 검사를 확인했다. 실제 계정·OAuth·토큰·유료 추론·새 권한·main/Android/원본 ZIP/사용자 자료 변경은 없다. 새 Windows package/checkout/commit/push도 없다.

## 다음 고정 범위

모바일 완료로 묶지 않은 항목은 공유/고정 반환 이름과 잠정 빈 출력, 영역/다중 선택, 원본 내부 흐름/async, 특수 실행 핀과 나머지 ABI/ref/out·다중 구현/복사 문맥이다. backend에 없는 동작을 성공처럼 표시하지 않는다. 검사 조합을 무한 확대하지 않고 이 목록을 고정한다.

요소 Browser 다음 묶음은 v536 개념 직접 속성 열기, Unit→Monster→Slime 실데이터의 상속/자체 속성·기능·하위 Browser 구조와 동작, 문서/독립 View 소유권 및 저장/취소/Confirm 대조다. 이후 Helper 이미지/삭제, 전투로그/신문고/Yogi, 창별 Run, 전체 수용과 Windows 패키징/게시 순서는 그대로 유지한다. 앞서 남긴 모바일 미완료 항목을 전체 완료로 소급하지 않는다.
