# v536 Browser 단일 부모 이동 — 부분 복원

원본 `app.js`의 browserDropDestination/canMoveBrowserObject/moveBrowserObject/setupBrowserObjectDrop를 대조했다. 개념 위 드롭은 상속 부모를 바꾸며, 카테고리 폴더 배치와는 의미가 다르다. 원본 레이아웃/CSS의 browser-move-target을 재사용한다. 프로토타입의 객체 배열 직접 수정이나 자손 자동 이동을 실제 소스 저장으로 복제하지 않는다.

## 구현 범위

- 현재는 같은 프로젝트의 소유 `object` **하나**를 다른 소유 개념으로 드롭하는 embedded Browser 경로다. 드래그 시작의 project/id/revision/hash를 바인딩한다. 다른 프로젝트, 다중 개념, Category/Root 폴더 드롭은 이 묶음에서 지원하지 않는다.
- 기존 `editObjectStructure`의 source CAS, 전체 소유 그래프 타입/상속/순환 검증으로 작업 사본에 적용한다. 소스 파일 확정은 기존 명시적 Review/Confirm만 수행한다.
- 다른 대상의 private 입력은 보존한다. 이동 대상의 미적용 필드/독립 View/소스/충돌 입력은 기존 `blueprintPending` 범위 검사로 차단한다. 변경된 드래그 원본을 새로운 버전으로 자동 재바인딩하지 않는다.
- 드롭 뒤 기존 private 선택/schema를 복원하고 실제 relations map을 읽는다. source 적용 후 목록 갱신만 실패하면 적용 사실을 구분해 안내하며 같은 쓰기를 자동 반복하지 않는다.
- source 변경 자체의 transport admission `stale_revision` 재시도만 허용하고 원래 source CAS proof는 유지한다. 최종 Confirm의 자동 재시도는 추가하지 않았다.

## 실제 확인 결과

`elements-browser-parent-move-1.log`: 처음2건은 통과했다. fixture가 browserDrafts의 status 성공을 discard 완료로 잘못 기다려 취소 결과 assertion이 너무 먼저 실행됐다. 실제 action의 후속 schema 응답까지 기다리도록 수정했으며 보호나 기대 상태를 삭제하지 않았다.

**`elements-browser-parent-move-2.log`: exit0, 실제 엔진+Chromium 5 PASS**, 격리 case `/tmp/confectory-element-mutation-z32uzmg7`.

1. Monster→Other 드롭은 실제 source 작업 사본의 부모만 바꾸고 final 파일/Unit private111/Slime 소스를 보존.
2. Other→자손 Monster 드롭은 source mutation 전에 거절.
3. 명시적 source 취소는 원래 부모 Unit으로 복원하며 final bytes와 다른 입력 보존.
4. Save 뒤 실제 프로세스를 재시작하면 부모 Other 작업 사본과 Unit private111 복원. 자동 Confirm 없음.
5. Review 취소 뒤 새 Review/명시적 compiler Confirm으로 Monster 부모만 최종 반영. Slime 참조, Other/Unit 및 나머지 source 바이트 유지.

브라우저 DataTransfer 합성 입력으로 실제 렌더러→엔진을 검사했다. 실제 OS 마우스 드래그/Windows/모바일 기기 테스트는 아니다. JS 오류/외부 네트워크 요청 없음. 캡처 `parent-explicitly-confirmed.png` 보존.

`elements-browser-parent-boundaries-1.log` exit0, 실제 엔진 경계 **2 PASS**, case `/tmp/confectory-element-mutation-i8b5t8p6`: (a) 이동 대상 독립 View의 private Speed3이 있으면 mutation 전 차단, Unit111과 Speed3 보존, (b) 드래그 후 다른 실제 API 편집에서 source 설명을 바꾸면 오래된 drop proof로 이를 덮어쓰거나 parent를 바꾸지 못함. final 바이트/기존 parent 보존. 여러 동시 편집의 모든 조합을 검증한 것은 아니다.

실패 표시를 새 시도 시작 때 비우고, backend 거절은 원본/상속 조건 확인 안내로 표시하도록 마지막 소폭 보완했다. **최종 `elements-browser-parent-build-3.log` compile exit0 후 `elements-browser-parent-boundaries-2.log` 실제2건 재검증 exit0**. case `/tmp/confectory-element-mutation-y2yhi8of`. 새 실패 표시가 이전 오류를 그대로 사용하는 것이 아니라 새 드롭의 결과를 기다리도록 확인했다. 런타임/검사 프로세스 종료. 이 문서의5건을 전체 Browser·삭제·UI복원·Windows패키지·게시 완료로 해석하지 않는다.

## 잔여

다중 부모 이동의 원자적 처리, Category containment, Root/폴더 경로, standalone Project Browser 내부 이동은 미연결이다. 삭제/복구는 Changes/Export/Restore/Confirm/Commit의 write-only 계약에 실제 제거/등록/복구를 표현해야 하는 별도 미구현 항목이며 File.Delete·빈 소스·sentinel로 우회하지 않았다. 다른 고정 v536 목록은 V536_UI_RESTORATION_SCOPE.md를 유지한다.
