# V666 기존 일반 동작 표시명 묶음 저장 복구 검증

제품·검사·도구·delta 동결은 `a310634d9a91af0ffa2f094845214163a24cbc01`이다. 이후 마감 commit은 문서만 바꾼다.
[닫힌 경계](V2_NODE_NAMES_RECOVERY.md)와 [정확한 delta](v666-node-names-recovery-delta.json)를 따른다.

## 실제 결함과 수정

게시본 `1055fd0a0c083a00a52cabc71a9df145081d49f7`의 원래 title inspector에서 같은
직접 소유 root의 기존 일반 동작 두 개의 이름을 바꾸었다. 쓰기 실패 뒤 개인 입력
두 개가 모두 사라지고 live만 바뀌었다. cold에서는 이전 두 이름으로 돌아왔다.
checkpoint·signature·C#/caller와 모든 물리 원본은 같았다. baseline JSON SHA는
`c29138d431b0daf75c18396b1f89c223717a88afdc9ec70d091d7611b655682b`다.

기존 2–64개 batch 예산 내 서로 다른 기존 code/next 노드의 **표시명만** 같은 원자
후보·checkpoint CAS·ownedRename receipt·공유 이력으로 저장한다. 단독 이름과 같은
노드의 2–3개 텍스트 저장은 유지한다. 다른 노드의 설명/본문·인자·실행선·핀·계약·
생성/삭제를 표시명 묶음에 섞거나 private/copy/slot·부모/외부/참조·native 문맥의
기존 경계를 넓히지 않는다. 소스 편집 권한이나 새 타입/마이그레이션 정책은 없다.
writer·receipt 형식·공유 이력 planner·소유/권한·레이아웃·Review→Confirm·최종 CAS는
바꾸지 않았다. C# bytes·ID·공개/override 계약·값·연결·profile·설명은 그대로다.

## 최종 검증

독립 LF 17·CRLF 17·새 교차 패키지/전체 복원/실패 수명관리
8, **총 42단계(신규 42·재사용 0)** 통과했다.
개발 검사는 이 수에 합산하지 않는다. Git 객체·실제 EOL·NuGet/home·엔진 캐시를 분리했다.

- 정확한 세 runtime 경로와 canonical 자산 SHA/크기, 실제 JS guard·원본 origin proof,
  기존 반환 위치/값 입력 이름/같은 노드 텍스트 복구와 공유 이력/컴파일 probe를 검사했다.
  서로 다른 2·3·64개 기존 일반 노드의 이름, 65개 예산 초과·중복 ID·다른 종류·문맥은
  실제 guard로 검사했다. 실제 native API/UI fixture는 기존 노드 두 개다.
- API에서 stale checkpoint·변조 전체 closure·누락/중복 node·미관측 owner/private·다른
  노드의 source/intent·인자/실행선/계약 혼합·공백/제어문자/예산초과/비문자 이름을 거절했다.
  쓰기 실패 시 모든 live 이름/checkpoint/원본을 보존하고 정확한 미적용 checkpoint·전체
  closure·물리 원본에서만 재시도했다. 정상 원자 적용·멱등성·cold와 변조 receipt 거절,
  전체 이름의 공유 Undo/Redo/cold를 확인했다. 기존 ownedRename receipt를 사용하며
  ownedSource 표시는 추가하지 않았다. 표시 metadata가 소스 편집 권한을 부여하지 않는다.
- 원래 title inspector의 native Undo/Redo, 두 private 이름의 cold 복원, 쓰기 실패 뒤
  두 이름 수정/명시 재시도, 동료 저장 충돌/cold 재시도 거절을 확인했다. 실패 뒤 다른
  root 값이 더해지면 세 입력과 실패한 시도를 보존하고 legacy live 저장으로 우회하지 않았다.
- 응답 유실은 확정 receipt만 회수하고 중복 authorBatch를 만들지 않았다. 응답 보류 중
  입력한 두 새 이름은 자신의 key/node/type/origin과 같은 전체 소스 ID/해시를 대조한 뒤
  cold에서도 별도 저장했다. 다른 원본/누락 origin을 cold revision 차이로 허용하지 않았다.
- 공유 Undo/Redo/cold는 선택 이름을 함께 움직였다. Review 취소·Review 후 물리 graph
  변경의 최종 CAS 거절·새 Review→Confirm·실제 Linux .NET 실행·최종 cold를 확인했다.
  기존 `body`, `after`, `10` 출력과 exit 10을 유지했고 물리 변경은 graph의 두 표시명뿐이다.
  반복 no-op 이름 Save도 zero-dirty ownedRename receipt와 원본을 cold 복원했다.
- 기존 반환 핀 API·같은 동작 세 텍스트 API, 단독 이름/같은 동작 텍스트의 늦은 입력 UI를
  현재 엔진에서 새로 회귀했다. 다른 완료 기능의 기록은 기존 증거에 남기며 신규 수에
  재합산하지 않는다.
- 새 Windows 교차 패키지 구조/무결성과 패키지 엔진의 정상/응답 유실을 검사했다.
  전체 SHA·압축 CRC·권한 모드로 모두 복원한 엔진에서 실패 복구와 늦은 이름의
  Confirm/실행/cold를 확인했다. 성공/반복/실패/예외 수명관리·증거 보존·자식 종료·
  해당 실행 소유 임시물 정리를 통과했다. 실제 Windows apphost/WebView2나 모바일은 아니다.

## 개발 검사 경계와 증거

초기 개발 드라이버의 stage 이름은 새 이름 검사를 표시했지만 실제 명령은 기존 반환 핀
API를 가리켰다. 이 통과는 기존 기능 회귀 증거로만 보존했다. 실제 명령/로그를 확인하고
새 fixture와 최종 suite의 API/UI 파일 경로를 바로잡은 뒤 새 API/UI와 최종 전 단계를
검사했다. 제품 변경 없이 검사 대상만 수정했으며 최종 수에 중복 합산하지 않았다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/da54debf376b4f778a380f362ebe1cd5.json`

개발 증거 SHA `af145cd2d0c1ccf7249d910510ef73473a35fa76629d87a23a8a056ae974049e`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/f8dce05203da41bbb860644812e6bc31.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/f8dce05203da41bbb860644812e6bc31.zip`

SHA `2ef1015a036516f9e56b68c85d01f7e7bbc4de12beb5a3bb755860d6bd948b20` (2.64MiB).

## 보관·공간·잔여

보관 index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `a310634d9a91af0ffa2f094845214163a24cbc01`, `6a6c1e94f3d386e06ff21ac52c828c9d1b7bfb9276c9398668fda1e30a604319.zip`, 49.14MiB, 파일 2381·디렉터리 147, manifest `b31120451e88d902b862f443858c139e6992a2f7c9d0641e59d5a65700057453`.
- rollback: 출처 `e4c39322b2730ef37528838aba905a68b2d8932e`, `fe70b41845932113a00dbb88ab47fc4a5bd46f10cbbb6455842b68a4b2d2fb68.zip`, 49.14MiB, 파일 2381·디렉터리 147, manifest `63b9830db2f34ee0e9e550ac9d759ca789f8e6e4bc5bf8168d6ed6015268f061`.

최신은 동결 코드와 같고 이전 정상 최신본을 rollback으로 보관했다. 전체 SHA/manifest와
복원 가능성을 확인한 뒤 이번 실행 소유 임시물만 승인 수명대로 정리했다. 다른 과거
자료·원본·로그·프로필·SDK·캐시 삭제나 보관 정책 변경은 없다.

최종 단계 표본 최소 디스크 여유 1536.82MiB, 최대 cgroup 메모리
4781.10MiB. 최종 실행 순증가 3.71MiB, 개발 시작부터
보관 확인까지 5.36MiB, 문서 마감 전 여유 1533.17MiB다.
다음 단위의 고정 증가량을 보장하지 않는다.

다른 root·혼합 저장·직접 배치는 재현 기반 점검 후보이며 조합별 새 필수 항목을
늘리지 않는다. 완료 M11/M12/M4를 다시 열지 않는다. 고정 V2 후속·V3–V9·팩/backend·
종류 호환성 결정과 실제 Windows/WebView2·모바일·DPI/IME·전체 독립 창/프로젝트 왕복·
전체 UI·Space 전달은 별도 잔여다. 3D/권한 별도 팩·이동 연출/실행 분리·동기 caller의
명시 async 전환 원칙을 유지했다. live AI·실제 계정/키·유료 호출·새 외부 접근은 없다.
main은 사용자 검토/병합용으로 보존한다.
