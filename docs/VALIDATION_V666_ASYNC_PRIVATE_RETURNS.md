# v666 M4 내부 완료선의 일반 결과 복귀 · 최종 검증

제품 동결 `7358ed1ef57ee43f4abcfaac67464c34360fb29e`를 `tools/verify_desktop.py --suite async-private-returns`로 검증했다.
원본 v666 `dist/blueprint.js:blueprintSetAsync`의 완료 포트 보존 동기 복귀를 연결한다.
공개 IO·원래 Result/source ID·C# 원문/helper·literal 연결과 기존 소유/권한을 유지한다.
[지원과 호환 경계](M4_ASYNC_PRIVATE.md)를 따른다. 첫 생성 Save 전 입력 결합은 별도 M4 잔여다.

## 최종 검사

신규 **57단계 모두 통과**, 재사용 0. 독립 LF 25, CRLF 23,
새 교차 패키지·전체 압축 복원·실패 수명관리 9다.
Core/runtime은 각 18 passed/0 failed/0 skipped, 기존 private 실제 실행 probe는
LF/CRLF 각각 11/11개 확인을 포함한다. 개발 검사를 최종 수에 합산하지 않는다.

- 연결된 private Task의 동기 복귀가 같은 완료 marker ID/이름/값과 실행선을 유지한다.
  native 반환/out은 지역 실행 선택과 분리하고 C#·공개 헤더·호출자 원문을 보존한다.
  기존 Result forwarding은 원래 source ID와 enum을 같은 후보에서 일치시킨다.
- 기존 종료점은 None이며 완료를 자동 선택하지 않는다. 반환 카드에서 일반 완료를
  명시 선택한 경우에만 같은 실행선이 같은 native/out 값을 한 번 전달한다.
  선택된 완료 반환을 둔 재활성화는 거절하고 명시 None 선택 뒤 같은 Task ID로 재전환한다.
- native 데이터 binding 교체·없는 분기·부분 Review·Review 뒤 원문 충돌을 거절하고
  전체 입력/checkpoint를 보존한다. 기존 비소유/참조/copy/ref/source hash 보호를 유지한다.
- 실제 기본 창의 Undo/Redo·반복 Save·cold·저장 권한 실패·원문 충돌·응답 유실·늦은 입력,
  이전 receipt 재조회와 별도 Save, Review 취소/Confirm·실행·확정 cold를 검사했다.
- 기존 private Task/성공·실패 실행 순서·정보 함수 생성·M11 중첩/API·최종 read-CAS와
  전역 생성/템플릿·완료 어댑터/receipt를 변경 영향 회귀로 신규 확인했다.

새 패키지와 전체 복원본에서 같은 UI/실제 실행·늦은 입력·저장 실패를 확인했다.
전체 파일 SHA/CRC·파일/디렉터리 mode manifest와 assembly 동일성 검사를 통과했다.
Linux 관리 코드 실행과 Windows 교차 패키지 검사이며 실제 Windows apphost/WebView2·
모바일·독립 정보 창/모든 프로젝트 왕복·전체 UI·Space 전달 완료를 뜻하지 않는다.

## 수정과 개발 증거

원래 차단된 private 완료 결과의 데이터/실행 캡처를 연결하고, private 전환의 source enum과
명시 종료점을 원자 후보에 보존했다. 실제 UI 조회가 executionSource만 인정해 새 소유
결과 반환 카드를 숨기던 누락도 검증된 동일 소유 경계로 좁게 연결했다. 소유/완전 연결/
원문/계약/Review·최종 CAS 검사는 낮추지 않았다.

초기 생성 fixture의 이미 구현된 선언 재사용, Confirm 후 빈 묶음 Review 선택,
반환 카드 locator와 forwarded fixture의 전환 전 완료선은 검사 준비를 수정했다.
실패·입력·overlay·이미지·로그는 개발 record `124e0282b4b24ff68834251d00cacbac`, 증거 SHA256
`5248daa2f93bb1c9c9ac41b5c45ac7cdf94dccd5559c8f2acdc9cf01f4bbc522`에 보존했다.
최종 검사는 수정된 최종 코드에서 모두 신규 실행했다.

## 보관과 공간

- record `/workspace/artifacts/v536-verification-managed/runs/78120aaa3fa34d799e484ba452c40a6c.json`
- 전체 증거 `/workspace/artifacts/v536-verification-managed/runs/78120aaa3fa34d799e484ba452c40a6c.zip` · SHA256 `650e6e1f701099419c5015d907f1816c895d62e9f4e9be161e5687e24c91361f` · 4,893,668 bytes
- 최신 source `7358ed1ef57ee43f4abcfaac67464c34360fb29e` · ZIP `a0c81c5e81e2eea24745671340ad7048e937e088088e50d7f326bc4c6fe149f6` · 51,503,092 bytes
- manifest `f366501e68a586ef6dcd60c9a31272f71b678f434cedc7744c1967486acc74db` · 파일 2,381/디렉터리 147
- rollback `83187d5320523076d923169a2620517964e82b11` · ZIP `2d4e23a713ee5330a43d4ca49beda065b95ec3053a525e8fb182c3c726863bde` · manifest `ec71f1c87e74b16c9d31c3ce3bab6007833411fccc8c9b7d81d55c1b0ed33733`

완전 복원 확인 후 승인된 최신/롤백 원자 승격과 해당 실행 소유 임시물 정리만 수행했다.
기존 자료 추가 삭제는 없다. 개발 시작 여유 1,801,277,440 bytes, 최종 검사 전
1,798,295,552, 검사/보관 뒤 1,792,208,896; 전체 단위 순증가 9,068,544 bytes다.
검사 중 최소 디스크 1,798,209,536 bytes, stage 최대 cgroup 메모리 4,971,216,896 bytes.
RAM 실행 root는 제거됐고 증거/두 패키지는 지속 보관한다. 새 private 결과/receipt는 과거
parser가 거절할 수 있으며 코드 롤백으로 새 초안이 자동 이행되는 것은 아니다.
