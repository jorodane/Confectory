# v508 참조 수신과 Blueprint overview

`work/current@be37cf7` 이후의 첫 v508 구현 단위다. 원본 v480은 기존 기준으로 보존하고, 새 참조는 `reference/site-ui/Confectory-Editor-Prototype-v508.zip`으로 별도 보관한다. 이번 구현은 기존 graph를 탐색하는 전체 지도이며 async·wrapper·공개 출력 실행 계약을 추가하지 않는다.

## 참조 원본과 정적 확인

사용자가 main에 게시한 `71b7ea6613fd90a4db29492eb2dc416b9a533e8b` (`Add 508`)의 원본 ZIP이다. Git blob은 `0619403dd8673acc03a5c006d9bbf557861d77cc`, 크기는 16,433,599 bytes, SHA-256은 `b306ce4deff9616c4107ae224443d864f8fce0f52cf3c3e158de8745c17c659f`다. 내부 manifest는 `site_version:508`, prototype source `0c2f828fec72923e628c6006d73e8823712e9d98`을 기록한다. 26개 항목, 해제 크기 19,049,148 bytes이며 절대·상위·Windows 경로, 중복·대소문자 충돌, symlink/device, 암호화, 크기·압축비 및 CRC를 검사했다. manifest의 25개 파일 해시가 일치한다. README·launcher·호스팅 설정은 자료로 읽었으며 실행하지 않았다.

[수신 영수증](validation/v508-reference-receipt.json)에 확인한 원본·버전·해시와 초기 작업 브랜치를 기록한다. v480 대비 주요 변화는 분기 계약과 `branch-exit`, 공개 출력·wrapper, overview, 입력/출력/분기 정렬, 명시적 Rename, 비동기 UI·C# 계약 생성이다. C# enum/parameters/body/helpers 보호 편집 자체는 v480에도 있었다. 이미지 자산은 v480과 byte 단위로 같으며 prototype UI를 실행해 픽셀 일치를 검증한 결과는 아니다.

v508의 정적 실행 계획은 동기 version 4, 비동기 version 5이며 `sequential-header-rail`, `return-to-sequence`, `dispatch-result-then-continue`, `return-from-function`, `always-after-branch`를 기록한다. 비동기 계획의 순서는 await→출력 게시→완료 분기→결과 분기→메인 계속이다. 비동기 전환·시계·첫 ‘완료 시’ UI 방향은 사용자 승인 맥락을 따른다. 이 자료만으로 Task 결과 ABI, snapshot/복사·별칭, 취소·예외·재진입·동시성 정책을 새 엔진 실행 의미로 채택하지 않는다. 현재 switch continuation, node-time property와 legacy 명시 전환은 그대로다.

## 실제 연결 범위

overview는 현재 mount된 graph의 안정 node ID, 실제 DOM 크기와 기존 private 위치·카메라·zoom을 사용한다. 실행선과 현재 엔진의 branch-return 진단을 그리며, 기능·노드·인수·출력·분기 배열을 정렬하거나 쓰지 않는다. v508과 같이 가로·세로를 각각 내용 범위에 정규화하므로 작은 창에서도 지도 전체 폭을 사용한다. 지도 클릭/왼쪽 드래그는 선택 지점을 현재 viewport 중심으로 옮긴다. 방향키는 화면 크기의 10%, Shift와 함께는 50%, PageUp/PageDown은 세로 90%를 이동한다. Home/End는 현재 내용 범위의 시작/끝 중심으로 이동한다. overview 이동은 선택된 inspector를 바꾸지 않는다.

기존 bar header는 label을 통해 계속 이동하며 입력·버튼과 실행 핀의 동작을 보존한다. 노드 이동은 private 위치만 갱신하고 지도에 반영한다. v508의 명시적 Rename과 핀 정렬 UI는 이번 단위에 포함하지 않는다.

Escape·pointercancel·lostpointercapture·창 blur 및 graph/프로젝트 전환·뷰 종료는 진행 중 이동을 취소한다. 완료한 이동만 기존 private 카메라 상태로 저장한다. 이전 controller의 늦은 입력은 현재 scope를 바꾸지 못한다. 지도는 새 source basis를 만들지 않는다. source/property/노드 본문/설명/정확한 JSON 입력과 원래 CAS를 유지하며 cold 입력의 명시적 재검토·Apply 및 compiler Review/Confirm 경계를 보존한다.

## 범위와 수치

지도는 실제로 존재하는 노드를 반복 조회하고 렌더링한다. 제거된 저장 위치 ID와 없는 DOM은 표시 노드를 만들지 않는다. 잘못된 좌표는 기존 유한 기본값으로 되돌리며 prototype 키도 소유 key로 처리한다. 노드 위치는 기존 1e7 좌표 한도, zoom은 기존 3.125–300%다. 300%에서 끝 위치를 표현할 수 있도록 private 화면 카메라만 ±4e7 범위로 읽는다. 이 값은 엔진 정수 overflow 정책과 무관하다. 빈 지도는 탐색을 비활성화한다. source/model budget이나 언어 ABI는 확장하지 않는다.

256-node stress fixture는 실제 Chromium에 제품 viewport module을 mount하여 한 DOM 누락, 오래된 저장 ID, 잘못된 좌표, `__proto__` ID, 없는 실행 포트·대상, 매우 먼 위치, 지도 취소·모든 DOM 제거·retired controller를 검사한다. 이 검사는 독립 component 검사이며 일반 EditorHome 검사와 구분한다. 일반 EditorHome에서는 소유 프로젝트 두 개와 같은 node ID의 graph 두 개, bar 이동, 미제출 source/property/설명/JSON/C# 본문, graph 중간 전환과 cold 복원을 검사한다.

## 검증: 11 passed, 0 failed, 0 skipped

최종 source·fixture·정확한 메서드와 실행 로그는 [검증 기록](validation/v508-blueprint-overview.json)에 기록한다. 실제 Chromium의 일반 Home 실행, 소유 .NET 실행, Windows managed composition, Android export/metadata 검증을 구분한다. 실제 Windows OS·Android 기기·browser WASM target의 새 overview는 미검증이다. main·원본 ZIP·Android 설정·CSP·외부 AI·설치·지속 권한·미결 overflow는 변경하지 않는다.

이 단위 뒤에는 추가 UI/계약 연결과 async/wrapper/공개 출력의 실행 계약이 남는다. prototype의 stamp/계획 생성을 실제 compiler 실행 성공으로 표시하지 않는다.

최종 source/fixture는 `b40bd3a49e5068c8412fabc112538a5a9c11499f`다. 최대 두 gate에서 서로 다른 11개 메서드를 실행했다. UI·component 5개와 Core/checkout/managed 6개만 최종 합계에 넣는다. 큰 좌표 component는 256개 descriptor 중 현재 DOM 255개를 표시했고, `x=10,000,000`과 300% zoom에서 카메라 `x=-30,000,646`을 관측했다. 일반 Home은 graph 2개·프로젝트 2개와 137.125% zoom, 정확한 int64 입력·미제출 source/property/노드 본문·원래 CAS를 검사했다. cold 뒤 Apply는 명시적 기준 재검토를 요구하며 원본 58개 파일은 그대로였다. [실제 화면](validation/v508-blueprint-overview.png)을 보관한다.

초기 창 겹침·작은 viewport·비기록 DOM 스크롤과 표시 정규화 보정 전 실행은 로그와 원본 해시를 별도로 남기고 합산하지 않는다. 표시 조정 중 이전 host의 canonical resource 크기가 달라 거부된 재시작도 비최종 검사다. 최종 두 묶음은 동일한 고정 소스와 리소스 pin으로 통과했다. 원본 scratch 로그는 유지하며 Git 사본의 후행 공백만 정규화한다.
