# v666 일반 C# 본문 저장 복구 검증

제품·검사·도구·delta의 최종 동결은 `b045f85a6b7b1a5a7333e98147944bdc9a13a73a`다. 이후 마감 commit은
검증 문서 두 개만 바꾼다. [원본 근거와 지원 경계](V2_SOURCE_RECOVERY.md),
[로직 및 안내 6개/기존 8곳의 정확한 delta](v666-source-recovery-delta.json)를 따른다.

## 실제 재현과 변경

기존 게시본 dfdf043의 생성 프로젝트에서 Main의 직접 소유 ordinary next code 본문을
명시적으로 바꾸고 checkpoint 쓰기를 실패시켰다. 기존 순서는 live source를 수정하고
개인 입력을 제거한 뒤 saveDraft를 시도했다. checkpoint와 물리 원본은 그대로였으나
cold에서 입력한 C#은 사라지고 이전 본문만 복원됐다. 수정 전 source·입력·traffic·
checkpoint·스크린샷·재현 결과를 개발 증거에 보존했다.

일반 code source를 기존 authorBatch 후보/checkpoint CAS/receipt 수명에 연결했다.
source/intent/인자만 포함한 직접 소유 root code 범위이며, 다른 owner/slot/frame·호출
참조·forward/native 문맥·root 계약·route/rename 혼합을 새로 허용하지 않는다.
그래프 text가 그대로인 source-only에서는 graph receipt가 checkpoint에서 빠지는
추가 결함도 고쳤다. 서버가 생성한 ownedSource receipt만 Export에 명시적으로 포함하여
C# 파일이 모두 clean인 반복 Save도 재시작 후 판정한다. 현재 C# 본문도 원래 요청의
텍스트와 대조한다. 보관을 위해 사용자 graph/C#을 가짜로 변경하지 않는다.
공유 Undo/Redo는 앞 단위의 같은 bounded 기록기를 후보에서 재사용한다. 기존 한도와
구조/소유권 경계를 유지하고 source/intent의 실패 후 새 텍스트는 확실히 미반영된 같은
checkpoint/proof/물리 원본에서만 명시 재시도한다. 응답 유실·늦은 입력은 정확한
receipt와 분리하여 오래된 C#을 다시 적용하지 않는다.

속성 노드 또는 propertyObservations가 있는 root는 기존 property source 검증에 남긴다.
관측 없는 최초 source 저장 거절과 원래 receiver/객체/스키마/등록 source guard를 일반
code 경로로 우회하지 않는다. 분류와 체크를 같은 live draft gate 안에서 수행한다.
일반 Save는 물리 파일을 쓰지 않고, 실제 C# 컴파일·원본 쓰기는 Review/Confirm과 최종
CAS를 따른다. 컴파일 오류를 자동 수정하거나 잘못된 본문을 정상 실행으로 바꾸지 않는다.

제품 변경은 feature-authoring.js·해당 JS canonical 크기/SHA·Blueprint.csbody의 명시
차이와 owned source receipt를 보존하는 Export.csbody뿐이다. 레이아웃/HTML/CSS와 공개 .celem 계약, 기존 source editor·핀/분기/호출·
원문/권한 규칙을 임의 변경하지 않았다. V2의 지정 안내 6개/8곳만 formal 문체로 맞췄고
이전 C# 14개/16곳·값/핀 15개와 설명 복구 단위의 나머지 로직을 보존했다.

## 최종 검증

독립 LF 17·CRLF 17·새 교차 패키지/전체 복원/실패 수명관리
8, **총 42단계** 통과. 신규 42·동등 재사용
0이다. 빌드/엔진 캐시·NuGet/home·Git 객체와 실제 checkout 줄바꿈을 분리했다.
개발의 통과 수나 이전 42단계는 이 최종 수에 합산하지 않는다.

- 정확한 source delta, canonical asset, JS syntax와 이전 안내를 대조했다. 공유 draft
  history의 inverse/CAS/restart/owner 경계 및 표시명/실제 의미 변경 native 보호를 확인했다.
- 실제 엔진 API에서 stale checkpoint·위조 closure·없는 노드·참조 call·잘못된 owner/
  slot/frame·혼합 route/매개변수 수정을 거절했다. 새 C# source 후보는 private 상태에서
  멱등·cold·공유 history를 유지하며, 이미 바뀐 물리 source를 Save가 덮어쓰지 않는다.
  물리 publication은 최종 Confirm의 CAS를 따른다. clean source의 no-op Save/cold도
  receipt를 유지하며 위조 hash를 거절한다. 이전 설명/값 API도 회귀 확인했다.
- Chromium에서 고정 선언 거절·source editor Undo/Redo/취소·정확한 multiline Unicode
  입력/cold, 쓰기 실패 후 새 C# 수정·명시 재시도와 peer checkpoint 충돌을 확인했다.
  응답 유실은 receipt만 회수하고, 늦은 새 본문은 cold 후 별도 Save로 보관한다.
  두 경우 모두 이전 source를 재전송하지 않으며 공유 Undo/Redo/cold가 유지된다.
- 실제 compiler Confirm의 `CS0103`/`UnknownV666SourceSymbol` 원문 진단과 미확정
  checkpoint·입력·원본을 보존했다. 사용자가 명시적으로 수정한 뒤에만 재확정했다.
- Review 취소·검토 뒤 After.node.json의 물리 원문 충돌 거절·새 Review/Confirm·실제
  .NET 실행/cold를 통과했다. 수정 body만 정확히 반영하고 Main의 ID/graph/profile/
  핀·호출/분기 연결과 Flow의 다른 C# 원문 bytes를 보존했다. 반환 10과 실행 출력
  `callee:1 → edited:10` 또는 늦은 입력의 `callee:1 → latest:10`을 확인했다.
- LF의 기존 async property 실제 UI/실행 회귀에서 관측 전 source-only 거절, 원래
  receiver·읽기/Set·원자 저장, 보관 관측을 유지한 후속 C# 쓰기 실패/cold/재시도와
  전체 Review/manifest 최종 CAS·반복 Confirm/Save를 검사했다. 실제 출력은
  `1020 → 2030`이다. CRLF에서는 별도의 property observation metadata/부분 Review/
  원본·경로 위조/expected-missing·readonly CAS 거절을 확인했다.
- 새 패키지의 구성/무결성·실제 packaged 엔진 웹 시작과 C# Save/UI/실행을 검사했다.
  압축의 CRC·전체 파일 SHA/모드를 검증해 완전히 복원하고, 복원 엔진에서 쓰기 실패
  뒤 새 C#과 늦은 입력·Review/Confirm·실행/cold를 새로 확인했다. 성공/실패/예외의
  임시 복사본 수명관리도 통과했다.

모든 개별 안내의 오류 조건을 UI에서 각각 새로 주입하거나 모든 문맥/프로젝트 왕복을
새로 검사한 것은 아니다. actual property 전체 UI 회귀는 LF에서, observation guards는
CRLF에서 실행했다. 위에 적은 범위 외 전체 UI 통과로 표현하지 않는다.

## 개발 검사와 증거

응답 유실/cold에서 graph text가 바뀌지 않으면 receipt가 Export되지 않는 실제 결함을
확인했다. C#은 저장됐고 입력도 유지됐지만 settled 판정이 불가능했다. checkpoint와
traffic·스크린샷을 보존하고 selective source receipt 보관을 수정했다. 위조 receipt
hash와 source가 모두 clean인 no-op Save/cold 판정도 검사했다. 이 제품 변경 이후에는
초기 통과를 재사용하지 않고 최종 영향을 새로 검사했다.

초기 동결 254ea89의 LF 17단계와 CRLF native/API/설명 회귀까지 통과했다. 다음
property observation guard 호출에서 engine report 인자가 빠져 fixture 초기화 전에
IndexError가 발생했다. 기존 호출 예와 동일하게 인자만 보완했다. 이 시점에는 제품과 검사 코드는
변경하지 않았다. 봉인 증거의 전체 manifest/SHA, Git diff, SDK/NuGet/configuration,
독립 LF/CRLF와 정확한 실행 명령을 대조하여 통과한 10개를 중간 실행에서 재사용했다. 뒤의 receipt 제품 수정 후 최종 수에는 재사용하지 않았다.

재사용은 LF history/runtime·source API·설명 API·property 전체 UI·source storage-new/
conflict/late와 CRLF history/runtime·source API·설명 API다. 실패한 property guard와
새 checkout/빌드·나머지 UI·패키지/전체 복원은 새로 실행했다.
[엄격한 재사용 검증기](../tools/verification_source_reuse.py)는 제품·검사 변경이나
명령 차이를 허용하지 않는다. 중간 실행의 source-reuse.json과 개별 reused 기록에만 출처를 보존한다. 최종 실행은
receipt 제품 수정의 영향 검증을 모두 새로 수행했다.

초기 독립 실행 record `/workspace/artifacts/v536-verification-managed/runs/19608322190d4ef4b644d5f274e2f762.json`, 증거 SHA `d169cc443a57b901af5ae19ce5eccf5921b23cd0c042310c61eba1a2632be079`.

receipt 결함을 발견한 두 번째 실행 record `/workspace/artifacts/v536-verification-managed/runs/9fff9f109a234d5fa1a7472aa38d7e8c.json`,
증거 SHA `9101233b8bdca34f794cea38095abb69f45654396b0fe8c3fa9c3db30869d017`. 위 두 실행은 최종 통과 수에 포함하지 않는다.

최초 probe는 multiline 본문을 JSON 직렬화 문자열에서 그대로 찾는 잘못된 fixture
가정을 사용했다. 실제 blueprint cell의 text를 비교하도록 고치고 제품 변경 전에 손실을
확인했다. 이를 제품 결함과 구분하며 실패/재현 자료를 삭제하지 않았다. 개발의
storage-new와 late 검사도 실제 엔진의 최종 확정/실행까지 통과했으며 최종 source의
독립 LF/CRLF 검증과 구분한다.

최초 재현·초기 UI 개발 record `/workspace/artifacts/v536-verification-managed/runs/7078e1eb6d0a4d4c82b1dd6e6bda0516.json`,
증거 SHA `0163a834ab967d37ccbe87cfd691d57214a647081b98e64b461bb28cacca3f3b`.

receipt 수정 개발 record `/workspace/artifacts/v536-verification-managed/runs/8a438c4894944168a3d153db792cbd0a.json`

개발 증거 SHA `9a5a33cac2cd464a2de84e96e9291767a5ff5ef106f9634d7075029a2cd9842f`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/135194b7f95046539e3b5791aa9321ab.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/135194b7f95046539e3b5791aa9321ab.zip`

SHA256 `f53985ccc0011a659537313f98383ed3a1fa3d04cc3d31ff931c57759a53e04b` (2.55MiB).

## 보관과 공간

보관 index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `b045f85a6b7b1a5a7333e98147944bdc9a13a73a`, `4d65204674f377bef362bcae791f8b6d247b75434d38aa07fb5eb095cb35ce00.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `73a459d0c2675b3975a8ef47b776a49952d9d86d1f362747c2955c8c1fc53658`.

- rollback: 출처 `db0a781b6e657c59d71d0b8e3230e8bfd1610542`, `99865f87d8093532aefb154b57d6a14a1721cf117899a6cd12d9611c91654652.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `530626dd159966e54b302a28228ecd589593c765568f63aaa4072544dec046e5`.

최신 패키지는 위 최종 동결 코드와 일치한다. 정상 롤백·증거와 기존 원본을 보존하고,
자식 종료와 archive 검증 후 이 실행이 만든 임시물만 승인 수명대로 정리했다.
다른 과거 자료를 추가 삭제하지 않았다.

단계 표본 최소 여유 1637.80MiB, 최대 cgroup 메모리 4656.35MiB.
최종 실행 순증가 3.59MiB, 개발 시작부터 보관 확인까지 측정
순증가 8.11MiB, 문서 마감 전 여유 1634.26MiB.
이를 이후 실행의 고정 증가량 보장으로 사용하지 않는다.

## 유한한 잔여와 한계

다른 일반 rename/route/root 핀/export·혼합 함수 signature/description 등은 아직
읽기 점검 후보이며 이 source body 단위의 입력 손실 수정 완료와 구분한다. 원래
없는 조합·legacy 자동 migration·비소유 편집을 새 필수 요구로 늘리지 않는다.
V2의 나머지 계약·일반 검토·탐색/시스템 안내와 V3–V9·기존 별도 팩/backend·종류
호환성 결정, 실제 Windows/모바일·전체 UI·Space 전달은 남는다.

컨테이너 Chromium·실제 .NET 컴파일/실행·Windows 교차 패키지 검사다. 실제 Windows
apphost/WebView2·모바일 기기·DPI/IME·전체 독립 창/프로젝트 왕복·전체 UI·Space 전달은
미검증이다. live AI/계정·자격증명·유료 호출·새 외부 권한은 사용하지 않았다.
