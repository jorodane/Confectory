# V666 void root 입력 이름 저장 복구 검증

제품·검사·도구·delta 동결은 `0bf4c635dcbe510e288776901dc45063d54a8f10`이다. 이후 마감 commit은 문서만 바꾼다.
[닫힌 경계](V2_ROOT_VOID_NAME_RECOVERY.md)와 [정확한 delta](v666-root-void-name-recovery-delta.json)를 따른다.

## 실제 결함과 수정

게시본 `da5e0eee3260f268f28df628d35b2e666872ca1a`의 원래 입력 이름 UI에서 직접 소유
동기 void 함수의 값 입력 하나를 바꾸었다. 쓰기 실패 뒤 개인 계획 하나가 사라지고
live만 바뀌었으며 cold에서는 원래 이름이 복원됐다. checkpoint·반환 void·출력 없음·
원래 C#/caller와 물리 원본은 같았다. baseline JSON SHA는
`b60329f03a5849f891db103e1aec6c5a98bd997caf260ba8c82a4cfbee13f372`다.

기존 1–64개 값 입력 중 하나의 이름/같은 이름 Save를 원래 반환·출력 형태를 보존한
void root에도 기존 원자 후보·checkpoint CAS·ownedRootInputName receipt·함수/구현/
graph 묶음과 공유 이력으로 연결했다. void의 outputOrder는 빈 배열이며 nonvoid는
기존 return 핀 하나를 유지한다. 반환 타입·출력/인자 생성·삭제·타입/mode/순서·두 이름
동시 변경·다른 private 입력과의 혼합은 허용하지 않는다. 기존 nonvoid 지원, private/
copy/slot·부모/외부/참조·공유 함수·async·공개 분기·native 문맥의 보호를 유지한다.
공개 override 입출력 계약·원래 C#·위치 기반 IInvoke 계약·caller·ID·핀·값·실행선·
profile은 그대로다. 명시한 식별자와 root 참조만 기존 metadata로 갱신한다.
writer·receipt 형식·그룹/이력 planner·권한·원본 레이아웃·Review→Confirm·최종 CAS는
바꾸지 않는다. 자동 C# 변환·새 외부 접근이나 소스 편집 권한은 없다.

## 최종 검증

독립 LF 17·CRLF 17·새 교차 패키지/전체 복원/실패 수명관리
8, **총 42단계(신규 42·재사용 0)** 통과했다.
개발 검사는 이 수에 합산하지 않는다. Git 객체·실제 EOL·NuGet/home·엔진 캐시를 분리했다.

- 정확한 세 runtime 경로와 canonical 자산 SHA/크기, 실제 void/nonvoid 이름 guard와
  늦은 이름의 같은 위치 대응, 기존 표시명/반환 위치/값 입력 이름/텍스트 proof·공유 이력/
  컴파일 probe를 검사했다. 첫/중간/마지막 중 하나와 no-op 이름의 기존 1·2·3·64개 값
  입력은 실제 guard로 검사했다. 실제 native API/UI fixture는 두 값 입력의 동기 void 함수다.
- API에서 stale checkpoint·변조 전체 closure·잘못된 origin·미관측 owner/private·새 public
  출력/본문/mode·인자 추가삭제·타입/순서/ref/out·반환/출력 변화·누락/추가/잘못된 remap·
  두 이름 동시 변경·충돌/공백/비문자/길이 초과 이름·다른 source/계약 혼합을 거절했다.
  쓰기 실패 시 live/checkpoint/원본을 보존하고 정확한 미적용 checkpoint·전체 closure·
  물리 원본에서만 재시도했다. 정상 적용·멱등성·전체 세 멤버 root 묶음·cold receipt와
  변조 receipt 거절을 확인했다.
- 원래 root 입력 이름 UI의 local Undo/Redo와 private 계획 cold 복원, 실패 뒤 Undo 취소/
  빈 Save/Redo/수정 이름/cold 재시도를 확인했다. 실패 뒤 무관한 표시명이 더해지면
  두 입력과 원래 시도를 유지하고 legacy live 변경으로 우회하지 않았다. 동료 root
  checkpoint의 충돌은 cold/재시도 후에도 덮어쓰지 않았다.
- 응답 유실은 확정 receipt만 회수하고 중복 authorBatch를 만들지 않았다. 보류 중 새로
  입력한 이름은 같은 위치의 명시 remap으로 cold 뒤 별도 저장했다. 다른 작성자의 이름에
  remap을 합성하거나 다른 원본/누락 origin을 cold revision 차이로 허용하지 않았다.
- 공유 Undo/Redo/cold는 함수·구현·graph를 함께 보관했다. Review 취소·Review 후 물리
  graph 변경의 최종 CAS 거절·새 Review→Confirm·실제 Linux .NET 실행·최종 cold를
  확인했다. 기존 `body`, `10`, `done` 출력과 exit 0을 유지했다. 명시한 root 이름/참조
  외 물리 C#/caller bytes·ID·타입·반환 void·출력 없음·값·실행선·profile은 동일했다.
  반복 no-op 이름 Save와 뒤이은 unchanged C# Save도 zero-dirty 전체 root 묶음과
  receipt를 cold 복원했다.
- 기존 nonvoid 값 입력 이름 API와 반환 위치 API, 기존 nonvoid 이름/후속 본문의 늦은
  입력 UI를 현재 엔진에서 새로 회귀했다. 다른 완료 기능 기록은 기존 증거에 남기며
  신규 단계에 재합산하지 않는다.
- 새 Windows 교차 패키지 구조/무결성과 패키지 엔진의 정상/응답 유실을 검사했다.
  전체 SHA·압축 CRC·권한 모드로 모두 복원한 엔진에서 실패 복구와 늦은 이름의
  Confirm/실행/cold를 확인했다. 성공/반복/실패/예외 수명관리·증거 보존·자식 종료·
  해당 실행 소유 임시물 정리를 통과했다. 실제 Windows apphost/WebView2·모바일은 아니다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/cd81dd726b7e445188a7a28be2affbaf.json`

개발 증거 SHA `b04d29de0233e45118830d61907b3e7093fa59578ed5c20380b0843c8e0bfffd`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/4fca5b8db6704033aab3236140d51282.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/4fca5b8db6704033aab3236140d51282.zip`

SHA `5eb3a500f4a65c5980db5131668e56bdec02b23ce8cc8520d7254ac787505095` (2.66MiB).

## 보관·공간·잔여

보관 index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `0bf4c635dcbe510e288776901dc45063d54a8f10`, `4f87ec458487e4dbf76dda4bf3dbb083f00618954a304e1cd2959fe9c16b910e.zip`, 49.14MiB, 파일 2381·디렉터리 147, manifest `f6e0685de639342e842b620acfbcac7031b98d47c8dad8f638da026f623278a2`.
- rollback: 출처 `a310634d9a91af0ffa2f094845214163a24cbc01`, `6a6c1e94f3d386e06ff21ac52c828c9d1b7bfb9276c9398668fda1e30a604319.zip`, 49.14MiB, 파일 2381·디렉터리 147, manifest `b31120451e88d902b862f443858c139e6992a2f7c9d0641e59d5a65700057453`.

최신은 동결 코드와 같고 이전 정상 최신본을 rollback으로 보관했다. 전체 SHA/manifest와
복원 가능성을 확인한 뒤 이번 실행 소유 임시물만 승인 수명대로 정리했다. 다른 과거
자료·원본·로그·프로필·SDK·캐시 삭제나 보관 정책 변경은 없다.

최종 단계 표본 최소 디스크 여유 1531.34MiB, 최대 cgroup 메모리
4768.38MiB. 최종 실행 순증가 3.72MiB, 개발 시작부터
보관 확인까지 5.38MiB, 문서 마감 전 여유 1527.68MiB다.
다음 단위의 고정 증가량을 보장하지 않는다.

다른 root·혼합 저장·직접 배치는 재현 기반 점검 후보이며 반환/인자 조합마다 새 필수
항목을 늘리지 않는다. 완료 M11/M12/M4를 다시 열지 않는다. 고정 V2 후속·V3–V9·팩/
backend·종류 호환성 결정과 실제 Windows/WebView2·모바일·DPI/IME·전체 독립 창/프로젝트
왕복·전체 UI·Space 전달은 별도 잔여다. 3D/권한 별도 팩·이동 연출/실행 분리·동기
caller의 명시 async 전환 원칙을 유지했다. live AI·계정/키·유료 호출·새 외부 접근은 없다.
main은 사용자 검토/병합용으로 보존한다.
