# V6 프로젝트 자료 사본 보관 최종 검증

[지원 범위](V6_RESOURCE_IMPORT.md) · [팩 계약](../packs/project-resources/README.md) ·
[닫힌 제품 delta](v666-resource-import-delta.json).
제품·검사·도구 동결 `69b27171e12c26014a2c647a85ab9357ce7b0481` 이후 저장소 변경은 문서뿐이다.
**총 44단계: 신규 26·동등 근거 재사용 18**. LF 19·CRLF 17·
새 패키지/전체 복원/수명관리 8로 구분한다. 개발 실패/중단은 통과 수에 넣지 않는다.

## 실제 구현과 확인

- 검증된 저장소 v666 ZIP의 `app.js::resourceDatabase`, `importResourceFiles`,
  `resourceItems`, `renderResourceItems`, `renderResourceBrowser`가 근거다.
  ZIP SHA `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`.
  원본 Browser shell·검색/밀도·파일명 확장자 표시를 재사용했다. CSS 원래 prefix와
  원본 파일명 보조 함수의 바이트를 검증했다. 원본에 없는 새 편집기/디자인을 추가하지 않았다.
- 별도 ProjectResources 팩의 실제 독립 DSL 소비자에서 34개 검사를 통과했다.
  빈 목록 읽기는 저장소를 만들지 않으며 명시 선택한 사본의 ID·Unicode/CRLF·원래 bytes와
  metadata를 보존한다. canonical padded base64url·전체 SHA·형식/크기/개수 예산을 검증한다.
  손상된 저장소를 빈 목록으로 덮지 않고 원본 경로·추가 필드·다른 project/알 수 없는 ID·
  잘못된 hash·link·읽기/쓰기 실패를 거부한다. 파일1MiB·총4MiB·64개/한 번1개가 현재 지원 한계다.
- 실제 관리형 엔진 UI에서 생성한 검사용 File만 사용했다. 사용자 개인 파일/외부 자료는
  읽거나 업로드하지 않았다. 실제 File 선택은 활성 ProjectContext에서만 사본을 보관하며
  파일명/MIME은 metadata일 뿐 경로·코드 실행 힌트로 사용하지 않는다. C#/HTML을 실행하지 않았다.
  실제 최대1MiB File을 invoke→저장→read로 왕복하여 모든 bytes를 비교했다.
  드롭은 같은 선택 handler를 공유하지만 별도의 OS drag/drop 조작은 이번 검사에서 실행하지 않았다.
- 실제 새 읽기 전용 ProjectManager ReadIdentity를 통해 기존 ID를 관측한다.
  누락/namespace 변경 fixture에서 읽기를 거부하고 identity와 자료를 새로 만들거나 복구하지 않음을
  확인했다. 기존 Identity의 명시 프로젝트 열기 생성 의미·경로/namespace 규칙은 바꾸지 않았다.
- 원자 CommitPlan은 자료 저장소 한 파일만 쓰고 같은 lease 안에서 정확한 자료 revision·
  source manifest·기존 identity를 최종 확인한다. 실제 production Request/CommitPlan/
  BoundedSnapshot/WriteAtomic/LeasePath 몸체를 추출한 통제 harness에서 정상·manifest 경합·
  identity 경합·자료 경합·쓰기 실패 5개를 확인했다. 이 검사는 pre-CommitPlan 의존성의 통제 주입이며
  실제 DSL wiring/Windows 기기 검증으로 주장하지 않는다. 별도 독립 팩/엔진 검사가 실제 연결을 검증한다.
- 실제 성공 응답만 보류한 뒤 클라이언트 응답 유실을 주입했다. 동일 명령 재시도는 뒤에 다른
  append가 있어도 사본을 중복 생성하지 않는다. 실제 readonly 목적지 실패·stale store CAS에서도
  기존 저장본/선택 File/새 검색어를 보존한다. 새 revision으로 묵시 재시도하지 않으며 사용자가
  명시 취소·재선택해야 새 의도가 된다. 입력 취소는 이미 저장한 사본 삭제가 아니다.
- 실제 File 읽기 지연 중 Home/동일 프로젝트 왕복, 폐기한 탭·밀도·목록 callback과 필터 변경을
  확인했다. 이전 수명의 읽기/응답은 현재 창을 바꾸거나 자동 보관하지 않는다.
  실제 cold engine에서 확정된 ID/bytes·개인 검색/선택을 복원하고 같은 namespace/source ID인
  다른 실제 프로젝트와 A→B→A 왕복을 격리했다. 미보관 File/command를 presentation에 넣거나
  재시작 뒤 자동 재전송하지 않는다. 원본 C#·핀/계약·권한·Review/Confirm·기존 Undo를 보존했다.
- 기존 office Worker/찾기·패널 찾기·정확한 C# target 열기/입력 보호·개인 배치와
  source Review/Confirm/최종 CAS·Undo/Redo·실패/프로젝트 격리를 회귀 검사했다.
  자료 metadata 보관은 C# 확정으로 위장하지 않으며 원본 소스에 새 권한을 부여하지 않는다.
- 독립 Git 객체·NuGet/home·빈 엔진 cache/출력의 LF/CRLF를 빌드했다.
  새 Windows 교차 패키지의 관리형 엔진에서 정상 UI, 전체 압축 복원본에서 수명/재시작 및
  기존 본문 찾기 회귀를 검사했다. ZIP 전체 SHA/CRC·파일/디렉터리 mode manifest·복원 구조,
  실패/예외 증거 보존·소유 자식 종료/임시물 정리를 확인했다. 실제 Windows apphost/WebView2,
  모바일 기기·전체 UI·모든 crash 시점/물리 전원 장애 검증은 아니다.

## 실패·중단과 재사용

개발 첫 독립 소비자는 필요한 FileStream provider 바인딩이 fixture에서 빠져 실패했다
(`b374b98f1e5f4accad56df56b64d6b63`, 증거 SHA
`15a20bee777134c1f887c33342de6295ea2140eb3df4658cf6c7e07ba7e25c89`).
두 번째는 DSL C#에서 LINQ 확장 메서드를 암묵 import한다고 가정해 컴파일 실패했다
(`1d8ea1a760b14f4183f05df068b70cea`, 증거 SHA
`bb1ef1c28d2fe4d9ba54a58c7da44a6954e05f7fd580c3c62ad6701a17771faa`).
fixture 바인딩과 명시 호출을 고친 뒤 예비31개/정상·수명 UI를 통과했지만 최종 근거로 재사용하지 않았다.

첫 최종 실행 `9d8958991fcc45b1b6187f726f19fbd6`은 30단계 통과 뒤 ID의 지연 생성 API가
읽기 검증에 사용되는 점을 발견해 보존 중단했다. 증거 SHA
`7aeb74ddfb633a454b21414ac376334bccd180845ad85064b7fc52abd582256e`.
읽기 전용 계약/바인딩으로 좁힌 뒤 영향받은 자료 경계/native/CAS/UI를 수정된 제품 코드에서 다시 확인했다.
이후 변경은 수명 fixture의 전환 조작뿐이다. 최종 신규/재사용 집계는 위44단계와 아래 세 시도별 근거를 따른다.
LF office 찾기·패널 찾기·본문 찾기·source 복구·source 충돌 **5개만** 재사용했다.
해당 검사/UI/비자료 실행 소스가 동일하고 변경 바인딩이 자료 경로에만 연결됨을 비교했다.
각 완료 traffic에 projectResources 호출이 없고, SDK/NuGet/config/RID와 정규화 명령도 같다.
원래 archive 전체 무결성을 확인했으며 각 `.reused.json`에 이전 기록·변경 목록·traffic SHA를 보존했다.
전체 제품이 이전과 동일하다고 주장하지 않고 중단 중인 CRLF UI를 통과 근거로 사용하지 않았다.

두 번째 실행 `c2607b7ca7b640cfa51528577a6089d5`는 최종 코드의 LF 자료 UI까지 통과한 뒤
재사용 driver가 동일 Python 실행 파일의 python/python3 symlink 이름을 다르게 비교해 멈췄다.
제품·검사·도구 소스는 변경하지 않고 실행 파일의 실제 경로와 나머지 정규화 인자를 확인했다.
증거 SHA `7d3ecb0840a392c3cd66419ae135c858ffc7f4a3879a5b73cd3f5864e51e98d6`.
동일 동결 source·전체 입력과 명령이 같은 소유 IPC 수명관리·LF 정적2·자료 boundary/native/CAS/UI의
완료7개를 추가 재사용했다. 소유 작업공간은 실패 수명 절차로 이미 정리돼 빌드/checkout은 새로
생성했다. 이 시점의 재사용12개는 driver와 증거에 따로 표시했다.

세 번째 실행 `9e271b693a0946cb9f64fecf6c5a3f9a`의 CRLF 수명 fixture는 raw helper가
Home 이동으로 만료된 이전 scope에서 results만 기다려60초 대기를 실패했다. transport는
기존 `scope_changed`를 반환했고 helper가 이를 무시한 것으로 확인했다. 제품은 바꾸지 않고
해당 두 raw 호출만 원래 ‘프로젝트 나가기 → Home 카드 열기’ UI 조작으로 바꿨다.
실패 JSON·마지막 확인 화면/입력 증거 SHA
`27571274e15a44a8ae14d205e9b6c0e2a65582857574ec27278e6fc0c6af4bd4`를 보존했다.
이미 통과한 LF 배치와 CRLF 정적2·자료 boundary/native/CAS 6개를 추가 재사용했다.
변경은 수명 모드 한 줄뿐이며 정상 모드 본문·제품·해당 검사/SDK/명령의 동일성을 검증했다.
최종 재사용은18개다. 실패한 수명 검사는 재사용하지 않았으며 LF의 실제 UI 수명 보강1개와
CRLF·전체 복원 수명 검사를 새로 실행했다. 빌드 산출물은 이전 실행 수명 종료 시 정리돼
필요한 독립 checkout/빌드는 새로 생성했다.

## 보존·공간과 한계

- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/f6a20129c6e541bdab98af80db1efe70.json`
- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/f6a20129c6e541bdab98af80db1efe70.zip` · 4,855,851 bytes
- 증거 SHA: `d343829f183851d58319923ba1a79f31656396b51a19593c552ce52aa2b18108`
- 최신 source: `69b27171e12c26014a2c647a85ab9357ce7b0481`
- 최신 ZIP: `7ff3ed2f310f13327ee7554c1654f61798d06a1850407cc591b60b42786f2bde.zip` · 51,890,551 bytes · 파일2490 / 디렉터리153
- 최신 전체 manifest SHA: `884a49c33cdd026be01ed5d396b315607ae269ef494a8e372b2c2729926cfcd4`
- 정상 롤백 source: `2d4c202207bb3d00542e6003d577d34dc25bb56a`
- 롤백 ZIP: `896f4fb01d9870385542a14248f2a69c36f9f6ac5d3a4181a50c567f3397db7b.zip`
- 롤백 전체 manifest SHA: `2150b7332fd55afbf4ab278693cb82a6a2a4b6ebdcd1ac546990e72f1da04109`

패키지는 `/workspace/artifacts/v536-verification-managed/packages/`의 기존 index를 따른다.
두 보관본과 모든 재사용/실패/예비 증거의 전체 SHA/CRC/manifest 무결성을 확인했다.
검증 완료 뒤 기존 승인된 두 세대의 원자 승격만 사용했으며 다른 과거 자료는 삭제하지 않았다.
모든 이번 실행의 소유 RAM root는 종료/증거 보존 뒤 정리됐고 지속 증거는 남겼다.

최종 실행 디스크 순증가 5.65MiB, 개발/실패·중단 증거와 검토 화면을
포함한 이번 측정 구간 순증가 16.46MiB다.
측정 시 여유 1238.35MiB, 단계 표본 최소 여유 1243.95MiB,
peak memory 4895.06MiB다. 최초/최종 사전 검사에서 지속 공간144MiB
(안전64MiB 포함), RAM3GiB+512MiB와 추가 메모리7GiB+1GiB를 확인하고 순차 실행했다.
이 증가량을 다음 단위의 보장값으로 사용하지 않는다.


이번에는 실제 사본 보관/목록/검색/표시 크기/선택·성공 복원 기반을 마감한다.
원본의 폴더·이름 변경/이동·삭제/복구·다중/큰 파일·배치와 V7 내용 미리보기/편집은 남는다.
자료 파일은 영속 프로젝트 데이터이며 cache/outputs가 아니다. 프로젝트 전체 이동/내보내기에
자료를 동반하는 흐름을 완료했다고 표시하지 않는다. V4/V5는 실제 신원/권한 backend가 선행한다.
V2의 다른 원본 안내·종류 C# 호환성 결정·Run 고해상도/GPU/native·물리 오디오는 기존 고정 잔여다.
초기화 간헐 빈 화면은 원인 미확정이다. M11/M12/M4를 다시 열거나 임의 조합을 새 필수 행으로 늘리지 않는다.
main은 사용자 검토/merge를 위해 보존했다. 실제 Windows/모바일·전체 UI·Library/Space 전달은 미완료다.
