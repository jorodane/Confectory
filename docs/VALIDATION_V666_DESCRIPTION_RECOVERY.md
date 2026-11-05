# v666 일반 설명 저장 복구 검증

제품·검사·도구·정확한 delta의 최종 동결은 `db0a781b6e657c59d71d0b8e3230e8bfd1610542`다. 이후 마감 commit은
검증 문서 두 개만 바꾼다. [원본 근거·지원/미지원](V2_DESCRIPTION_RECOVERY.md)와
[11개 문구/기존 13곳·로직 허용 목록](v666-description-recovery-delta.json)을 따른다.

## 재현과 실제 수정

기존 d63e8f7에서 생성한 소유 프로젝트로 root code intent와 함수 description-only의
checkpoint 쓰기 실패 입력 손실, 함수의 기존 Blueprint 직접 편집 진입 시 미보관 설명
손실을 재현했다. 개인 입력을 먼저 제거하는 기존 순서를 기존 원자 후보/checkpoint CAS/
receipt 수명으로 연결했다. 재현 자료와 이전 소스는 개발 증거에 보존한다.

함수 설명은 원래 revision/hash를 그대로 이관한다. 혼합 signature 입력·다른 owner·
private/copy/참조/부모/외부 문맥을 자동 승인하지 않는다. root intent의 실패 후 새 입력은
이전 시도가 확실히 미반영이고 checkpoint·전체 proof·물리 원본이 그대로인 경우에만
명시 재시도한다. 일반 Save는 물리 파일을 쓰지 않으며 최종 Confirm CAS를 유지한다.

기존 일반 저장은 공유 Undo/Redo를 지원했다. 초기 원자 저장 제안이 이 기능을 잃는
회귀를 개발 검사에서 발견하여, 같은 제한의 기존 기록기를 후보 snapshot에서 재사용했다.
unit ID/kind/path가 그대로인 두 bounded 경로에만 적용한다. 구조·소유권 boundary와
기존 history 용량 제한은 그대로이며 공개 API/권한 계약을 추가하지 않았다.

intent는 semantic 입력이다. 변경 후 원래 C#은 계속 `needs-implementation`이며,
사용자가 원문을 명시적으로 확인·적용한 뒤에만 완성할 수 있다. C#을 자동 재작성하거나
준비 상태를 자동 갱신하지 않는다. 함수의 표시 설명은 실행 계약을 바꾸지 않는다.

## 최종 검사와 동등 증거

독립 LF 17·CRLF 17·새 패키지/전체 복원/실패 수명관리
8, **총 42단계** 통과. 신규 30·재사용 12이다.
별도 Git 객체·NuGet/home·엔진/빌드 캐시와 실제 checkout 줄바꿈을 확인했다.

- 정확한 delta와 두 JS 자산 canonical 크기/SHA를 검사했다. 이전 C# 14개/16곳 및
  값·핀 15개 안내도 보존했다. HTML/CSS/레이아웃·다른 source/계약은 허용하지 않았다.
- 실제 native API에서 stale checkpoint·위조 proof·없는 노드·export·잘못된 owner/
  frame·혼합 route/parameters를 거절하고 checkpoint/원본을 보존했다. intent+인자
  한 후보의 멱등·cold·공유 history·C# 재검토 필요 상태를 확인했다.
- 기존 값 전용 API의 out 입력 금지·소유 경계·physical source 변화 보존·최종 CAS
  경계를 회귀 검사했다. 공유 초안 history 원자 inverse/CAS/restart/owner 경계와
  표시명 변경의 의미 보존·실제 intent 변경의 stale 보호 native 검사도 실행했다.
- 실제 Chromium에서 설명 textbox Undo/Redo·정확한 Unicode 입력·cold, 쓰기 실패 뒤
  새 설명·명시 재시도, 함수 직접 편집 진입의 durable Save, peer checkpoint 충돌을
  확인했다. 응답 유실은 receipt만 회수하며 이전 편집을 재전송하지 않는다. 늦은 설명은
  이전 저장과 분리해 cold 후 새 Save로 보관하고 각각 공유 Undo/Redo를 유지했다.
- Review 취소·검토 후 물리 원본 변경의 최종 CAS 거절·새 Review/Confirm·확정 cold를
  확인했다. 원래 C# bytes·핀·기존 분기 연결/profile은 그대로다. 실제 .NET 실행은
  반환 10, 출력 순서 `callee:1 → after:10`을 확인했다.
- 새 Windows 교차 패키지의 구조/무결성 및 packaged 엔진의 저장·거절을 검사했다.
  전체 파일 SHA/CRC/모드를 검증해 완전히 복원하고, 복원 엔진에서 응답 유실·늦은
  입력·Review/Confirm·실행/cold를 다시 확인했다. 실패/예외 수명관리도 통과했다.

이전 단위의 통과 수는 이번 수에 합산하지 않았다. 개발 중 통과는 최종 수에 합산하지 않는다. 최종 재사용은 아래 동일성 증거를 갖춘 LF/CRLF 12단계뿐이며 나머지는 위 final source에서 새로 실행했다. 모든 문구의 개별 화면이나 모든 기존
타입/문맥/프로젝트 왕복을 새로 주입한 것은 아니다. 실제 검사 범위는 위에 한정한다.

## 개발 실패와 fixture 보완

실제 결함은 앞의 세 입력 손실과 중간 원자 제안의 공유 Undo 회귀다. Ctrl+Y textbox
redo 가정은 Linux Chromium의 Ctrl+Shift+Z로 바로잡았다. 함수 Review는 원래 존재하는
관련 변경 검토 모달을 먼저 통과하도록 고쳤다. late Save의 Undo는 먼저 확정된 A로
돌아가야 하므로 원래 초깃값으로 돌아간다는 잘못된 fixture 가정도 보완했다.

초기 동결 2a358c7에서 함수 선언의 Unicode가 escape로 저장되는 증거를 확인하여
raw 문자열 포함 검사를 native 파서의 description 값 비교로 고쳤다. native 표시명
검사의 선택 이름도 실제 메서드 이름으로 고쳤다. 제품 byte는 그대로다. 초기 실행은
13개 통과 단계와 중단 사유/증거를 보존해 종료했다. 최종 수는 위
보완을 포함한 최종 실행과 명시한 동등 증거만 센다.

다음 독립 실행에서는 설명 단독 Review에 additionalChanges가 없어 추가 확인 checkbox가
렌더되지 않는 것을 화면과 renderer에서 확인했다. 항상 checkbox가 있다고 가정한
fixture를 실제 렌더 조건에 맞췄다. 제품은 변경하지 않았다. 이 실행의 통과 LF 4개
(history/runtime·설명 API·기존 값 API·node storage-new)는 seal·전체 manifest/SHA·
제품 및 다른 검사 파일 Git 동일성·SDK/NuGet/configuration·동일한 실행 명령과 LF
독립 checkout을 검증한 뒤 재사용했다. node는 이전 실행에서 해당 checkbox를 실제
확인하고 통과하여 새 존재 조건이 그 통과 경로를 바꾸지 않는다. 실패한 함수 검사는
재사용하지 않았으며 새 checkout/빌드·다른 UI·패키지/전체 복원은 새로 실행했다.
[재사용 검증기](../tools/verification_description_reuse.py)는 명시한 fixture 세 차이
외에 제품/검사 변경이 있으면 거절한다. 최종 archive의 description-reuse-*.json에
각 출처와 invocation을 보존한다.

다음 late fixture에서는 응답을 의도적으로 멈춘 상태에서 busy 해제를 기다리는
flush를 호출해 스스로 기다린 원인을 확인했다. 입력만 바꾼 뒤 응답을 해제하고
flush/보존/cold를 확인하도록 수정했다. 이 실행에서 통과한 함수 entry는 response
pause를 쓰지 않으므로 같은 엄격한 동일성 검사로 추가 재사용했다. 실패/중단한 late
검사는 새로 실행하며 제품 byte는 그대로다. 해당 시점의 재사용 출처는 두 개·5단계였다. 이후 LF/CRLF 34단계와 새 패키지 구조
검사가 통과했지만 package content에는 검사 helper가 없어 packaged UI 시작 전에
fixture 경로 오류가 발생했다. helper를 검사 스크립트의 __file__ 기준으로 읽도록
고쳤다. checkout 검사에서는 두 경로가 같고 제품·패키징 byte는 그대로다. 검증기는
이 한 경로 차이까지 정확히 대조하고, 통과했던 나머지 LF late와 CRLF 6단계를 추가
재사용한다. 최종 재사용은 세 출처·총 12단계이며 실패한 package 검사는
재사용하지 않는다. 새 package/전체 복원·수명관리는 모두 새로 실행했다.

네 번째 독립 실행 record `/workspace/artifacts/v536-verification-managed/runs/f9bf5e21b77b40638ba771a3c0664232.json`, 증거 SHA `e4440c3c578c5ca8c22f0ea3fe7f5ad68cec90a8495a5d5bbae10766fc5fce39`.

세 번째 독립 실행 record `/workspace/artifacts/v536-verification-managed/runs/116ca5bf7296417db6d7676d722fd1f0.json`, 증거 SHA `c4523e98722238723c6c62c2f02d1921d122c38ee0a339339f8500b991622be5`.

두 번째 독립 실행 record `/workspace/artifacts/v536-verification-managed/runs/99fa5344ec0b45bd940d098d48d01744.json`, 증거 SHA `f986df1e24085b8200d4c663a74ea500d0761779f6c20e369c8e990acb954f4a`.

초기 invocation의 잘못된 CLI 옵션은
작업공간 생성 전 argparse에서 거절됐으며, 해당 로그도 별도 보존한다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/b78d3213745c40b89848593f5335e6f2.json`

개발 증거 SHA `ec3d5e2c44cb646fb8ba818921c1f65dd6bca8f7fc6e2689e9721ee287f9de96`.

초기 독립 실행 record `/workspace/artifacts/v536-verification-managed/runs/62f6f4a2bc0a4c8097dd63c33cdba128.json`, 증거 SHA `f7654e3799edd5f6b2e40bc0408e008eaaf9a49d49cc1aef90ac8ebad70ece40`.

## 보관과 공간

최종 record `/workspace/artifacts/v536-verification-managed/runs/de74d3091927479bbaea640b762115fe.json`

증거 `/workspace/artifacts/v536-verification-managed/runs/de74d3091927479bbaea640b762115fe.zip`, SHA256 `b4635661941bb4573ab04c8b7b0e55c6d152448bf8ef703233c7de17c5f46238` (1.32MiB).

보관 index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `db0a781b6e657c59d71d0b8e3230e8bfd1610542`, `99865f87d8093532aefb154b57d6a14a1721cf117899a6cd12d9611c91654652.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `530626dd159966e54b302a28228ecd589593c765568f63aaa4072544dec046e5`.

- rollback: 출처 `b7ec64b193dbc3b15b6179551629e34428d54401`, `f24fdade6b3132924b62e2db3a033828240cfceef83c47ab27db2db5f52bc27a.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `bf4bca7c4ae21cfeb435ed793b6ea7dcfb9983fcbcfc1493e106e68b39038bff`.

최신은 최종 동결 코드이며 롤백은 기존 정상본이다. 자식 종료와 증거/보관본 검증 후
이 실행이 직접 생성한 임시물만 정리했다. 다른 과거 자료를 추가 삭제하지 않았다.
단계 표본 최소 여유 1644.52MiB, 최대 cgroup 메모리 4730.87MiB.
최종 실행 순증가 2.12MiB, 개발 시작부터 마감 확인까지 측정
순증가 8.00MiB, 문서 마감 전 여유 1642.45MiB.
다음 단위의 고정 증가량 보장으로 사용하지 않는다.

## 유한한 잔여와 한계

다른 legacy source/rename/route/root 핀/export·함수 signature+description 혼합은
읽기 점검 후보이며 이번 쓰기 실패 수정 완료에 포함하지 않는다. 원시 소유/독립 창의
기존 snapshot/receipt 경로도 읽기 점검만 했으며 이번 전체 UI 통과를 의미하지 않는다.
V2의 나머지 계약·일반 검토·탐색/시스템 안내, V3–V9와 기존 별도 팩/backend·종류
호환성 결정을 구분한다. M11/M12/M4의 완료 경계를 선택 조합으로 다시 늘리지 않는다.

컨테이너 Chromium·실제 .NET 컴파일/실행·Windows 교차 패키지 검사다. 실제 Windows
apphost/WebView2·모바일·DPI/IME·전체 독립 창/프로젝트 왕복·전체 UI·Space 전달은
미검증이다. live AI/계정·자격증명·유료 호출·새 외부 접근 권한은 사용하지 않았다.
