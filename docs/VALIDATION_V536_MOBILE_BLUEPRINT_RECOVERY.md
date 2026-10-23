# v536 모바일 Blueprint 복원·수명·핀/출력 배치 검증

2026-10-23, `work/current`의 미게시 구현. 저장소 원본 v536(196c605, ZIP SHA256 `b53156e73fdbbe1f6b8b36a0829cdbfdaec002352304da0060fa53026314bd22`)과 기존 원본 CSS/배치를 유지한다. 이 기록은 앞 묶음의 두 미해결 결함과 그 뒤 고정된 모바일 경계 검사 결과다. 전체 UI 수용·Windows 실행·게시 완료 기록이 아니다.

## 재현과 수정

1. **검토창 뒤 cold 복원**: 원본 profile의 Blueprint 문서 레코드에는 정확한 기능/graph가 있었지만, `feature-editor.restoreAuthor`가 숨긴 탭을 무효화해 읽기를 취소했다. 임시 숨김과 프로젝트/창/세대 변경을 구분한다. 소유 문맥이 유효한 백그라운드 탭은 읽기·입력 복구를 수행하되, `authorPassiveRestore` 동안 기존 전경 화면을 활성화하거나 새 모바일 탭으로 옮기지 않는다. 기존 source proof/슬롯 소유권 검사는 그대로다.
2. **복원 중 무시된 탭 클릭**: 실제 프로젝트 바인딩 복원 중 `windowDocuments.activate`는 동작하지 않는데 탭은 클릭 가능했다. 복원 중에만 기존 문서 탭을 비활성화하고 완료 시 기존 controls 경로에서 해제한다. 임의 sleep으로 테스트를 통과시키지 않았다. 첫 수정만 적용한 contract-confirm run4는 여전히 실패했고, 실제 resource instrumentation으로 숨긴 탭의 source 읽기는 완료되었지만 초기 클릭이 무시된 것을 구분했다.
3. **성공한 생성 뒤 대상 변경 알림**: 원본 검색 메뉴의 늦은 `callables` 읽기가 메뉴를 닫고 새 private 노드를 만든 뒤 도착하면 transport의 정상 owner 검사에 거부되었다. 이미 폐기된 읽기 전용 catalog의 결과/오류만 버린다. 현재 열려 있는 메뉴의 실패와 source 쓰기/CAS 오류는 숨기지 않는다. 테스트 전용 지연 provider에서 수정 전 동작의 오류를 실제 renderer로 재현하고 수정 후/활성 오류를 각각 검증했다.
4. **프로젝트 B→A→B 재진입**: 첫 실제 통합 run에서 A/B private 입력은 보존됐지만 B의 정리된 author DOM을 그대로 다시 사용해 카드가 없었다. `workspace-host.restore`는 현대 author 문서에 대해서만 기존 retained 창을 현재 owned source와 private 입력으로 재바인딩한다. 다른 창의 DOM 보존 경로는 유지한다. 같은 namespace/id/파일명인 서로 다른 실제 프로젝트에서 재검증했다.

모든 조사는 격리 `/tmp` fixture와 계정 없는 생성 Linux 엔진에서 수행했다. 기존 실패 profile을 reset하거나 사용자 파일을 대신 만들지 않았다. 첫 계약 fixture는 최종 Confirm 전까지 원본 바이트를 보존했으며, Confirm 뒤에는 소비된 baseline으로 취급한다.

## 원본 동작 연결

- 원본 `bindBlueprintOrder`의 `bp-touch-actions`, 위/아래 버튼, aria label과 CSS를 사용한다. 루트 입력은 기존 `moveRoot`, 루트 출력은 기존 `moveOutput`, 소유 노드 입력/`out` 인수는 기존 `guardContract`에 연결한다. 현재 노드 반환값의 임의 위치 변경은 backend 계약이 없어 비활성 상태로 유지한다. 새 변환·조용한 연결 추정은 없다.
- 사용 중인 루트 입력/노드 출력과 값이 연결된 입력의 삭제 보호를 기존 계약에 위임한다. 새 미사용 입력의 추가/삭제와 원본 출력 삭제 취소를 실제 화면으로 검증했다.
- 출력 탭의 눈 버튼은 원래의 **호출 뒤 SourceContext 조회** 공개 상태를 바꾼다. 프로젝트 접근이나 외부 공유 권한을 추가하지 않는다.
- 기존 출력 정의의 `내보내기 배치` → 원본 위치 선택/취소 배너 → ＋ 위치 선택 → 값 편집을 연결했다. 새 nonterminal export와 앞뒤 실행 연결은 기존 checked `outputNodes` 저장으로 함께 전달한다. 배치 선택 자체는 source/private node를 만들지 않는다. 삭제는 기존 splice 계약을 사용하며 명시적 Confirm을 생략하지 않는다.
- 새 출력 정의와 미저장 루트 계약을 혼합한 배치, 특수 C# 실행 출력의 배치, 검색 메뉴의 모든 출력 경로까지 완료했다고 하지 않는다. 지원하지 않는 경로는 입력을 보존하며 기존 안전한 차단을 유지한다.

## 실제 엔진 결과

| 검사 | 결과 | 근거 |
| --- | --- | --- |
| 보존한 계약 fixture cold/Review 취소/탭 재진입/컴파일 Confirm | 3 PASS | `mobile-contract-confirm-5.log`, `/tmp/confectory-mobile-contracts-kxapswpu/cold-confirm-evidence.json` |
| 같은 이름의 A/B 프로젝트 live/cold 전환·각 입력 분리·retired rename/add/Save 거부 | 4 PASS | `mobile-projects-engine-2.log`, `/tmp/confectory-mobile-projects-goo68_vq/evidence.json` |
| 루트 핀 사용 보호·추가/삭제/터치 순서·공개 눈·출력 삭제 취소·노드 입력 순서·cold/명시 Confirm | 5 PASS | `mobile-pin-order-engine-1.log`, `/tmp/confectory-mobile-pin-order-cqrw0wq3/evidence.json` |
| 출력 선택 취소·위치/값 저장·successor 보존·cold/명시 Confirm·배치 노드 삭제/재확정 | 4 PASS | `mobile-output-place-engine-1.log`, `/tmp/confectory-mobile-output-place-y8_fz1x5/evidence.json` |
| 숨긴 문서의 source 복원과 전경 보존·Workspace/탭 재진입 | 2 PASS | `mobile-restore-visibility-1.log`, 계약 fixture `visibility-evidence.json` |
| 정상 검색 생성·Save/cold/Confirm 및 false target-change toast 없음 재검증 | 4 PASS | `mobile-search-engine-4.log`, `/tmp/confectory-mobile-search-d50jvu0w/evidence.json` |

앞 다섯 묶음의 18개 검사와 마지막 검색 회귀 4개를 구분한다. 모두 touch-emulated Chromium390×844이며 실제 터치 기기/Android/Windows 검증이 아니다. 원본 파일은 각 명시 Confirm 전까지 byte-identical이다. 프로젝트 경계 테스트는 최종 파일을 바꾸지 않았다. 핀 순서의 Confirm은 Serial/SerialBlueprintBody 선언 및 owned graph에만 적용되었고 다른 프로젝트·객체는 그대로다. source/CAS/승낙/실제 모델 호출은 우회하지 않았다.

추가 통제 renderer: catalog 수명3개(`mobile-catalogue-lifetime-1.log`, 수정 전 재현 포함), 문서 탭8개(`mobile-recovery-documents-regression.log`), 기존 desktop serial canvas15개(`mobile-recovery-desktop-regression.log`)가 통과했다. 총26개의 통제 검사는 실제 backend 결과와 구분한다.

첫 project run의 실패와 contract run4/기존 실패 로그를 보존했다. source 읽기 전 사용자 클릭을 임의 지연하는 fixture로 대체하지 않았다. 임시 resource instrumentation은 scratch probe의 브라우저 응답에만 적용했고 배포 소스/권한 API에 diagnostic 우회를 추가하지 않았다.

## 화면·빌드와 남은 범위

실제 PNG `ordered-mobile-inputs.png`, `choose-output-position.png`를 열어 원본의 터치 순서 행/위치 선택 구조와 기존 CSS를 확인했다. 기존 원본 `blueprint.js`의 `bindBlueprintOrder`, `queuePlacement`/`renderFlow`와 대조했다. 데이터 수가 다른 원본/fixture 화면의 전체 픽셀 일치 또는 모든 모바일 조합 완료를 주장하지 않는다.

최종 Linux `mobile-recovery-build-4.log` compile exit0. 리소스62/정규 텍스트53의 SHA/크기, 수정 JS6개·모바일 Python12개 구문·diff 검사가 통과했다. v536 원본 ZIP SHA는 위 기준과 동일하다. 네이티브 Windows/Android·가상 IME/실제 터치 장치·실제 계정/추론은 미검증이다. 새 Windows 패키지·checkout·commit/push는 없다.

모바일 잔여: 출력 정의/노드 이름·기존 출력 선택과 새 정의/미저장 계약 혼합 배치, 모든 검색 종류와 특수 실행 출력/일반 핀 ABI/ref/복사/readonly 문맥, 원본 그래프 터치 선택·보기/내부 흐름·async 및 정밀 화면/키보드 전체 수용. 기존 제한을 새 시각적 분기/반복 언어로 대체하지 않는다.

고정 후속: 요소 정의/하위 Browser, Helper 이미지·변경 이력/폼 삭제, 전투로그·신문고/Yogi의 실제 계약, 창별 Run, 기존 ABI/복사/혼합 저장/독립 View 제한 및 전체 UI 수용, Windows 교차 패키지·checkout·승인된 work/current 정상 게시. Helper 에디터 기능 확장은 그 뒤다. main/Android/원본 ZIP/실제 사용자 데이터는 보존한다.
