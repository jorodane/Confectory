# v666 M4 직접 소유 private Task · 최종 검증

제품 동결 `83187d5320523076d923169a2620517964e82b11`를 `tools/verify_desktop.py --suite async-private`로 검증했다.
[지원 경계](M4_ASYNC_PRIVATE.md)는 기존 직접 소유 기능의 private Task·leaf 명시 전환과
원자 Save/Review→Confirm이다. **M4 전체 완료가 아니다.** 연결된 private 완료 실행선의
일반 결과 보존 동기 복귀와 첫 생성 Save 전 입력 결합은 원래 유한한 잔여다.

## 최종 실행

신규 55단계 모두 통과, 재사용 0. 독립 LF 24, CRLF
22, 새 교차 패키지·전체 복원·실패 수명관리 9다.
Core/runtime은 각 18 passed/0 failed/0 skipped이며 private 실제 실행
probe는 LF 11/CRLF 11개 확인을 포함한다.
개발 검사를 최종 수에 더하거나 과거 통과를 신규로 세지 않는다.

- 내부 Task의 입력/정수 반환/out 공개 → 완료 → 정확한 기존 성공·실패 분기 → 다음
  동작을 실제 컴파일·실행했다. 실패 분기는 성공 경로로 흐르지 않는다. 반복/Task 예외/
  중단 후 재시도와 미전환 동기 호출자 오류를 확인했고 원문 CRLF·helpers·ID를 보존했다.
- 순수 후보/receipt 검사는 기존 nested profile의 첫 전환과 명시 sync 복귀를 포함한다.
  잘못된 owner/경로·누락 record·위조 source hash·부모/copy를 거절하고 공개 IO와
  source를 보존한다. 연결된 완료 실행선의 sync 복귀는 현재 거절하며 완료로 세지 않는다.
- 실제 API에서 내부 전환·반복 영수증 조회·cold·부분 Review 거절·Review 뒤 C# 충돌·
  전체 Confirm·실제 실행·확정 cold를 확인했다. 공개 실행 방식이 같으면 헤더 원문도 같다.
- 실제 기본 창 UI에서 부모 Task/내부 leaf 메뉴, Undo/Redo·취소·반복 Save·Task 코드
  편집 취소·cold·저장 권한 실패·충돌·응답 유실·늦은 입력을 검사했다. 이전 결과 조회가
  중복 저장하지 않고 늦은 입력은 별도 Save로 보존된다. Review 취소/Confirm·실행도 통과했다.
- 정보 소유·전역 생성·강제 포함 값/out/object 템플릿·완료 어댑터/receipt와 기존 정보
  자체 함수 API/M11 중첩 API·최종 read-CAS를 영향 회귀로 신규 확인했다.

새 패키지와 전체 압축 복원본에서도 private UI/Task와 실패 입력 보존을 실행했다.
전체 파일 SHA/CRC·mode·디렉터리 manifest와 assembly 동일성을 확인했다. Linux 관리
코드 실행 및 Windows 교차 패키지 검사이며 실제 Windows apphost/WebView2나 모바일
실행은 아니다. 새 private 경로의 독립 정보 창·프로젝트 왕복 등 전체 UI 검증은 고정
V1 잔여와 구분하며 이번 기본 창 검사로 완료라 하지 않는다.

## 발견 사항과 개발 증거

실제 누락은 private async 배치 진입 검사, 노드만 바꿀 때의 공개 헤더 재포맷, 기존
nested profile에서 완료 어댑터를 포함한 sync 복귀의 profile 충돌이었다. 명시 async
배치만 연결하고 실행 방식 변경 때만 헤더를 쓰며 필요한 switch profile만 보완했다.
소유권/원문/최종 CAS와 실행선 검사는 약화하지 않았다.

초기 fixture의 소유 경로 누락·Review 이전 비교 기준·불완전 종료점/분기 coverage는
검사 준비만 고쳤다. 제품의 정상 거절을 실패 원인에 맞춰 완화하지 않았다. 개발 record
`eda452c1892345c89879914ea1d776c5`, 증거 SHA256
`57bc3d40cf08493a672e052543650e8ef8c9ca6d3c5d3f092ebf579f1f438a77`에 실패와 수정,
당시 overlay·입력·로그·이미지·실행 결과를 보존했다. 최종 검사는 모두 신규다.

## 지속 보관과 공간

- 최종 record `/workspace/artifacts/v536-verification-managed/runs/6ebf6f04039a471d9dc81778a93ef824.json`
- 전체 증거 `/workspace/artifacts/v536-verification-managed/runs/6ebf6f04039a471d9dc81778a93ef824.zip` · SHA256 `ad64e3e168563dbe6658a4abdf1e19f11f61c88202e6001ad59653c301ce76b1` · 4,159,061 bytes
- 최신 source `83187d5320523076d923169a2620517964e82b11` · ZIP `2d4e23a713ee5330a43d4ca49beda065b95ec3053a525e8fb182c3c726863bde` · 51,496,163 bytes
- manifest `ec71f1c87e74b16c9d31c3ce3bab6007833411fccc8c9b7d81d55c1b0ed33733` · 파일 2,380/디렉터리 147
- rollback `4b18f79236e6380669821ec30663d7448f50eb54` · ZIP `4ce1a0bf8ef2b4ea14df85015ad7ac1f899ae44e60290da6c97e82bcd8a8daba` · manifest `778ed53a5fa5cae6e1966f60d89b4667336b0d63d23cbe8dd227340bdf64cdab`
- 최종 실행 전 1723.0 MiB, 종료 1717.9 MiB, stage 중 최소 1722.9 MiB.
  전체 작업 순증가 9.6 MiB; 이후 단위당 고정 증가량 보장은 아니다.

보관·복원 검증과 증거 보존 후 이번 실행이 직접 만든 임시 root만 정리했다.
임시 root 제거 `True`. 기존 승인된 최신/rollback 두 세대 교체 외
과거 자료 추가 정리는 하지 않았고 64 MiB 안전 여유를 유지했다. 동결 뒤 후속 문서는
제품과 구분하며 다른 HEAD를 패키지 source로 표시하지 않는다. 이전 rollback이 새
private Task 데이터/receipt를 읽지 못할 수 있고 자동 migration을 추가하지 않았다.

다음은 같은 M4의 연결된 내부 완료 분기 보존 동기 복귀와 첫 생성 Save 전 입력 결합이다.
M11/M12는 구체적 회귀 없이 다시 열지 않는다. 고정 V1 검증/V2–V9·기존 ABI/고급 타입/
표시명·팩/backend·종류 호환성 및 실제 기기/전체 UI/Space 전달은 별도 잔여다.
