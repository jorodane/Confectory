# v666 값·연산/핀 안내와 실패 입력 보존 검증

제품·검사·도구와 문구/코드 허용 목록의 최종 동결은 `b7ec64b193dbc3b15b6179551629e34428d54401`다.
이후 마감 commit은 검증 문서 두 개만 바꾼다. [원본 근거와 지원 범위](V2_VALUE_GUIDANCE.md),
[문구 15개와 UI/native 코드 차이의 허용 목록](v666-value-guidance-copy.json)을 따른다.

## 실제 변경

값의 크기·배열·숫자 범위·연산 깊이/피연산자/0 나눗셈·동명이름·ref 저장소와 핀 이음의
지정 안내 15개를 v666의 “주십시오/습니다” 문체로 적용했다. 원본의 값을 선택하는 안내,
0 나눗셈 거절, 값/실행 연결 구분과 상수·연산식의 자료형 확인에 대응한다. native에만
존재하는 제한을 원본과 똑같은 문장이라고 주장하지 않고 문체 적용으로 표시한다.

개발의 실제 쓰기 실패 주입에서 레거시 일반 값 Save가 `blueprint argument`로 메모리
초안을 바꾸고 화면 입력을 지운 후 `saveDraft`를 시도함을 확인했다. 마지막 체크포인트
쓰기가 실패하면 기존 체크포인트는 그대로지만 재시작할 개인 값이 사라졌다.
이를 검사 기대 완화로 처리하지 않고 기존 `authorBatch`의 candidate·checkpoint CAS·receipt
수명에 연결했다. native가 값 전용 묶음을 받는 경계도 보완했다.

이 경로는 직접 소유한 root code의 선언된 인자 편집만 받는다. 다른 owner/slot·private
frame·copy·참조 문맥이나 source/route/계약을 섞은 편집을 새로 허용하지 않는다. 기존
원본 closure·checkpoint·권한 검사와 out 입력 금지·최종 Confirm CAS를 유지한다.
원래 C# byte, 핀 ID·타입·분기/외부 연결과 실행 의미는 바꾸지 않는다.

전체 JS를 LF로 정규화한 뒤 정확한 15개 문자열·명시한 원자 저장 진입 조건을 적용한
결과와 실제 source를 대조했다. native도 줄바꿈을 정규화한 뒤 지정한 3개 차이 이외의
변경을 허용하지 않았다.
제품 경로는 `feature-authoring.js`, 해당 자산 canonical 크기/SHA의 `WebBundle.csbody`,
`packs/pack-workspace/Blueprint.csbody`뿐이다. HTML/선택자/CSS·다른 backend 진단은
변경하지 않았다. 이전 C# 안내 14개/16개 표시 지점도 유지함을 확인했다.

## 최종 신규 검사

독립 LF 13·CRLF 13·새 패키지/전체 복원/실패 수명관리
7, **총 33단계** 통과. 신규 33·재사용 0이다.
Git 객체·빌드/엔진 캐시·NuGet/home을 분리하고 checkout의 실제 줄바꿈도 확인했다.

- 실제 엔진 API에서 stale checkpoint·위조 source proof·없는 노드·export 노드·out 입력·
  owner/slot·private frame·값/route 혼합을 거절하고 기존 체크포인트/원본을 보존했다.
  명시한 값 candidate는 한 번만 보관하며 동일 요청과 cold 뒤에도 멱등이다.
- 실제 Chromium UI에서 long 범위 오류와 정확한 입력의 취소/cold·명시 수정,
  ref 상수 거절, 미완성 연산과 0 나눗셈 거절·구조 Undo/Redo를 확인했다.
- readonly checkpoint 쓰기 실패 뒤 개인 입력과 이전 체크포인트를 보존하고, cold 뒤
  명시적 재시도로 저장했다. 저장 응답 유실은 이전 receipt를 조회해 중복하지 않았다.
  응답 대기 중 새 값은 cold 뒤 이전 저장과 분리하여 별도 Save로 보관했다.
- 반복 Save·Review 취소·최종 원문 충돌 거절·새 Review/Confirm·확정 cold를 통과했다.
  기존 C#과 다른 파일은 그대로이고, 수정한 Flow graph도 기존 profile/분기 연결을 유지했다.
  실제 .NET 실행은 일반 out 경로 20과 ref/out 경로 43, 각각
  `callee:2 → after:20`, `callee:2 → after:430:value:43:43`을 확인했다.
- 새 교차 패키지와 전체 추출본에서 값 UI/실행을 검사했다. 전체 복원본에서는 이전
  C# 안내의 고정 영역/enum 거절·Undo/Redo·compiler Confirm의 `CS0103` 원문 응답과
  입력/원본 보존·정상 수정/실행/재시작도 새로 검사했다.

이전 C# 안내 31단계나 M4 47단계/별도 Core suite를 이번 통과 수에 합산하지 않았다.
크기·배열·깊이·동명이름 및 모든 개별 핀 연결 거절을 각각 실제 UI로 새로 주입한 것은
아니다. 이 조건들의 무변경은 허용 목록/전체 source 대조로 확인하며, 실제 UI/실행
범위는 위와 같다. 값/연산식은 기존 배율 메뉴의 50%에서 조작했다.

## 개발 실패와 검사 수정

실제 결함은 `value-storage-1`의 입력 손실이다. 수정 전의 문구만 바꾼 JS가 최초
개발 overlay SHA와 일치함을 확인해 `regression-baseline`과 재현 설명을 보관했다.
UI만 원자 저장에 연결한 중간 상태에서는 native가 인자 전용 묶음을 받지 않아 재시도가
거절됐다. 위의 제한된 native 경계를 연결한 뒤 쓰기 실패/재시도/실행을 통과했다.

별도의 fixture 실패도 숨기지 않았다. 좁은 창의 125% 배율에서 식의 버튼이 viewport
왼쪽 밖에 있어 뒤의 정의 창에 가려졌다. 포커스/헤더 이동만으로 해소되지 않았으며
실제 스크린샷·hit 좌표를 보존하고 기존 50% 메뉴로 식을 보이게 했다. 제품 레이아웃은
고치지 않았다. UI 실행 전에 발견된 진단 코드의 괄호 오타도 실패 로그와 함께 보존하고 수정했다.

초기 API fixture는 물리 원본이 바뀌면 개인 초안 Save도 거절해야 한다고 기대했다.
기존 동작은 개인 candidate를 보관하되 물리 원본을 덮어쓰지 않고 최종 Confirm에서
CAS를 적용한다. 이 의미를 바꾸지 않고 Save 중 원본 변화 보존과 실제 Confirm 충돌을
각 경계에서 검사했다. 이 fixture 수정과 실제 입력 손실 수정을 구분한다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/1ab595d013cf4e989b38f3d9dfdec6ca.json`

개발 증거 SHA256 `186a3870cc633cf50699b6f5ca6c24117d60c0d0a8ee98bcb690684fefaee5f9`.

## 보관과 공간

최종 record `/workspace/artifacts/v536-verification-managed/runs/1fdabcb76e5a4d4e9fdf29e821a7516d.json`

증거 ZIP `/workspace/artifacts/v536-verification-managed/runs/1fdabcb76e5a4d4e9fdf29e821a7516d.zip`

SHA256 `b56631c24b1830cc24a0718d5baeef770205b5a0500c8a2737c4b9404f9312ba` (2.07MiB).

최신/롤백 index: `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `b7ec64b193dbc3b15b6179551629e34428d54401`, `f24fdade6b3132924b62e2db3a033828240cfceef83c47ab27db2db5f52bc27a.zip`, 49.13MiB; 파일 2381·디렉터리 147, 전체 manifest `bf4bca7c4ae21cfeb435ed793b6ea7dcfb9983fcbcfc1493e106e68b39038bff`.

- rollback: 출처 `7855881f17207f711673811dd9a29961c3fe3a76`, `f043e336b76651545c212db3fa339f3f15910fe8014b454dbce49dcc4713049b.zip`, 49.13MiB; 파일 2381·디렉터리 147, 전체 manifest `c42c17958c74dd5a2bbf0d7f96b0e66b20b4af19003ae6a812f8a2c4e4819a76`.

ZIP CRC·전체 파일 SHA·모드와 신규 패키지의 전체 추출 후 엔진/UI·실행을 검증했다.
자식 종료와 보관 증거 검증 뒤 이 실행이 직접 만든 임시물만 정리하고, 승인된
latest/rollback 승격 수명을 유지했다. 다른 기존 자료를 추가 삭제하지 않았다.

단계 표본 최소 여유 1653.46MiB, 최대 cgroup 메모리 4789.04MiB.
최종 실행 순증가 2.98MiB, 개발 검증 시작부터 최종 보관 확인까지
측정 순증가 5.48MiB, 문서 마감 전 여유 1650.54MiB.
이를 이후 실행마다의 고정 순증가 보장으로 사용하지 않는다.

## 유한한 잔여와 한계

V2의 계약 편집·일반 저장/검토·탐색/시스템 안내와 V3–V9의 팩/backend·종류 관련
미정 결정은 남는다. 다른 일반 편집의 레거시 Save 루프는 이번 값 전용 수정/쓰기 실패
주입 범위가 아니므로 다음 일반 저장 검증에서 입력 보존을 확인해야 한다. 선택적
타입/문맥 조합이나 호환성 보호를 새 필수 작업으로 늘리지 않는다.
M11/M12/M4의 완료 범위와 3D/권한 팩 분리·이동/실행 분리 합의는 유지한다.

검사는 컨테이너 Chromium과 실제 .NET 컴파일/실행·Windows 교차 패키지다.
실제 Windows apphost/WebView2·모바일·DPI/IME·전체 독립 창/프로젝트 왕복·전체 UI·
Space 전달은 미검증이다. live AI/계정/자격증명·유료 호출·새 외부 접근 권한은 사용하지 않았다.
