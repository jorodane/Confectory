# V666 여러 값 입력 중 하나의 이름 저장 복구 검증

제품·검사·도구·delta 동결은 `93512e020fb4e43f9a84112f951c27945d003a68`이며 이후 마감 commit은 문서만 바꾼다.
[지원 경계](V2_ROOT_VALUE_RENAME_RECOVERY.md)와 [정확한 delta](v666-root-value-rename-recovery-delta.json)를 따른다.

## 재현과 수정

게시본 `8649dbdb9216d14bdf03a37b5b5e53099eaef92d`에서 원래 root 입력 이름 UI로
두 int 값 입력 `amount`, `scale` 중 두 번째를 `multiplier`로 바꿨다. checkpoint 쓰기 실패
뒤 개인 계획 1개가 사라지고 live에만 새 이름이 남았다. checkpoint와 원본·C# 본문/호출자
bytes는 같았으며 cold에서는 `scale`만 복원됐다. baseline JSON SHA는
`f4bf27f895b894b9f3e2757e27c6e683d56a418c92e9d9547057f7ad54f76bc8`이다.

이전 원자 저장 진입은 입력이 정확히 하나일 때만 허용했다. 이를 기존 1–64개 값 입력 중
하나의 이름만 바꾸는 완전한 명시 remap으로 연결했다. 다른 입력은 identity remap이며
입력 수·위치·타입·mode·반환/출력 계약을 유지한다. 같은 이름의 no-op도 기존 의미대로
허용한다. UI와 native 양쪽에서 두 이름 변경·중복 이름·불완전 대응·추가 편집을 거절한다.
기존 원자 후보·권한/소유 검증·checkpoint CAS·receipt·세 멤버 그룹·공유 이력·최종 CAS를
재사용하며 writer·receipt 형식·권한 정책·원본 레이아웃을 바꾸지 않는다.

확정 요청의 전체 remap을 역대조해 원래 입력 위치를 확인하고, 현재 모든 이름/타입이 그
확정 요청과 같을 때만 늦은 입력의 remap을 새 기준에 잇는다. 예를 들어 응답 대기 중 입력한
`factor`는 `multiplier → factor`, 첫 입력은 `amount → amount`로 남는다. peer 변경이나
미확인 origin을 허용 근거로 사용하지 않는다. 원래 C# `amount+scale`과 caller
`Pair.Invoke(7,3)` bytes를 그대로 유지하며 root 그래프 참조만 기존 계약에 따라 바꾼다.

## 최종 검증

독립 LF 17·CRLF 17·새 교차 패키지/전체 복원/실패 수명관리
8, **총 42단계(신규 42·재사용 0)**를
통과했다. 개발 결과는 이 수에 합산하지 않는다. Git 객체·checkout의 실제 EOL·NuGet/home·
엔진 캐시를 분리해 최종 코드를 검증했다.

- 정확한 runtime delta 세 경로와 canonical bundle 크기/SHA를 확인했다. 실제 JS guard의
  첫/비첫 위치·1/2/3/64개·no-op·0/65 거절, 실제 늦은 remap 코드, 기존 paired-source
  proof와 공유 이력/컴파일 probe 회귀를 확인했다.
- API의 stale checkpoint·변조 전체 closure·owner/private 권한 추정·추가 출력/본문/
  입력/mode/타입/반환·잘못된 이름·동시 두 이름/중복/순서 변경·identity remap 누락을
  거절했다. 실패 시 live/checkpoint/원본을 보존하며 baselineUnchanged는 원래 checkpoint와
  전체 closure·물리 원본이 일치할 때만 인정했다. 정상 원자 적용·동일 요청 멱등성·공유 이력·
  세 멤버 그룹·cold receipt·변조 receipt 거절도 확인했다.
- 원래 inline 이름 입력·개인 Undo/Redo·cold 복원을 확인했다. 저장 쓰기 실패 뒤 Undo로
  취소한 계획은 Save가 재생하지 않았고 Redo·새 이름 수정·cold 재시도가 입력을 보존했다.
  무관한 노드 표시명이 섞이면 두 입력을 cold 뒤에도 보존하고 legacy live 편집으로
  우회하지 않았다. 동료 root-group checkpoint 충돌을 재시작/재시도 뒤에도 거절했다.
- 응답 유실은 확정 receipt만 회수하며 같은 이름 저장을 재실행하지 않았다. 늦은 이름은
  원래 저장과 분리해 새 대응으로 저장했다. 공유 Undo/Redo·cold와 Review 취소·Review 후
  물리 그래프 변경의 최종 CAS 거절·새 Review→Confirm·실제 .NET 실행을 확인했다.
  결과는 `body`와 10을 출력하고 10을 반환하며, 본문/호출자 bytes·위치 ABI·ID·값·연결·
  profile은 유지했다.
- 같은 이름 no-op 뒤 zero-dirty 함수·구현·그래프 묶음과 receipt를 보존했다. 이후 별도
  동일 C# 본문 Save가 receipt를 바꿔도 전체 묶음이 cold에서 유지됐다. 기존 단일 입력
  이름 API/늦은 입력 UI·반환 핀 위치 API·paired 표시명/본문 늦은 입력 UI도 회귀했다.
- 새 Windows 교차 패키지 구조/무결성·패키지 엔진의 정상/유실 UI를 확인했다. 전체 파일
  SHA·압축 CRC·권한 모드로 전부 복원한 엔진에서 쓰기 실패 복구와 늦은 이름의
  Confirm/실행/cold를 확인했다. 실패/예외·반복 수명관리, 증거 보존·자식 종료·소유 임시물
  정리도 통과했다. 실제 Windows apphost/WebView2·모바일 검증은 아니다.

## 개발 실패와 증거

첫 개발 late UI는 검사 코드의 보류 상태 변수 초기화 누락으로 `NameError`가 발생했다.
원래 입력·개인 Undo/Redo·cold 단계까지만 통과했으며 제품의 늦은 입력 판정 전이었다.
변수 초기화만 고친 뒤 같은 제품 코드의 late 검사와 정상/후속 본문 복원을 통과했다.
제품 정책을 바꾸거나 실패를 통과로 합산하지 않았다. 최종 검사는 모두 최종 동결 코드에서
새로 실행했으며 실패 검사나 개발 결과를 재사용하지 않았다.

LF 회귀 중 환경이 잠시 starting으로 표시됐다. 같은 환경 복구 후 원래 driver와 자식
프로세스·checkout·결과가 유지됨을 확인해 재시작하지 않았다. 실행 세션 핸들만 사라졌으며
지속 로그와 같은 record를 관측했다. 해당 관측은 최종 증거의 environment-reconnection.json에 남겼다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/c2c8e660ba3a447d82688f5a94ad4e07.json`

개발 증거 SHA `49c15d9e17ccca5595887d31b0fd49949ea3b48e44b051403c1657765ba15c53`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/a480c19c0ccf417685dfc0ff542f8468.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/a480c19c0ccf417685dfc0ff542f8468.zip`

SHA `e40243509240839195dc0733d6d1374058eb602b301b6f419b0be7fb516bbffe` (2.66MiB).

## 보관·공간·한계

보관 index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `93512e020fb4e43f9a84112f951c27945d003a68`, `af82b94505ededa7e968d22344e662597ba3b1f465b3416a7835bb45dc138dfe.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `f61a5693f88c5e8ed3a34ac5252a11eae660d63058aa10fdb2433de25efe7c2c`.

- rollback: 출처 `302d8ae2c833a569d5ba6b0ce3e9a63005adf06d`, `dee03d74bc5eb80817ef66dcb0d2f711c3554a7c8818e9b3bbd99e037a2a8989.zip`, 49.14MiB, 파일 2381·디렉터리 147, 전체 manifest `91b191ea36d3cf0fcbdcaf431c164669aabb23d4704aee3408e694788ff3d52f`.

최신은 동결 코드와 같고 이전 정상 최신본을 rollback으로 보관한다. 전체 SHA/manifest와
복원 가능성을 확인한 뒤 이번 실행 소유 임시물만 승인 수명대로 정리했다. 다른 과거 자료·
원본·로그·프로필·SDK·캐시의 삭제나 보관 정책 변경은 없다.

최종 단계 표본 최소 디스크 여유 1553.36MiB, 최대 cgroup 메모리
4730.14MiB. 최종 실행 순증가 3.76MiB, 개발 시작부터 보관
확인까지 5.24MiB, 문서 마감 전 여유 1549.68MiB다.
다음 단위의 고정 증가량을 보장하지 않는다.

이번에는 값 입력 중 하나의 이름 편집 흐름만 마감했다. 다른 root 정의·혼합 계약·직접 배치
형태는 실제 재현을 확인할 점검 후보이며 개수·타입·문맥 조합마다 필수 범위를 늘리지
않는다. 완료 M11/M12/M4를 다시 열지 않는다. 고정 V2 후속·V3–V9·팩/backend·종류
호환성 결정, 실제 Windows/WebView2·모바일·DPI/IME·전체 독립 창/프로젝트 왕복·전체 UI·
Space 전달의 한계는 별도로 남는다. 실제 AI 계정/키·live AI·유료 호출·새 외부 접근/
권한은 사용하지 않았다. main은 사용자 검토/병합용으로 보존한다.
