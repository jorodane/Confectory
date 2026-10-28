# I5-6 4행: 혼합 Blueprint/C# target의 명시적 계약·본문

원본 v536의 정보 함수 상세창·핀 대응창·구현 선택창·Script 편집기를 유지한다. 같은 직접 소유 구현의 각 Blueprint/C# target을 원래 source 종류대로 검증하고, 공통 선언·모든 영향 본문·typed import·호출자를 한 후보와 기존 CAS로 저장한다. C# 원문을 자동으로 재작성하지 않는다.

## 결합 경계

먼저 원래 구현 선언과 source 증거를 고정한다. C# target은 원래 경로/해시/native 서명·현재 public 계약·직접 편집한 본문을 모두 요구한다. Blueprint target은 기존 graph/record·입력/출력 writer/소비자의 명시 대응을 검증한다. 각 target을 준비한 뒤 공유 native 선언과 import를 한 번만 구성한다. 다른 target이나 마지막 호출자의 오류·누락·오래된 기준이 있으면 후보 전체를 거절하며 checkpoint/물리 원본/입력을 보존한다.

혼합 그래프는 실제 기존 assembler로도 준비하여 정상 entry의 인자 이름과 native 선언이 일치하는지 확인한다. 명시 entry는 기존 생성기의 entry 서명을 유지한다. 맞지 않는 C# 이름을 문자열 치환하지 않는다. SourceContext 공개 출력은 기존 호출 후 읽기 의미를 유지하며 외부 공유/프로젝트 접근 권한이 아니다.

처음 out 출력을 추가한 호출자의 원래 기본 그래프가 out을 표현하지 못하는 결함도 수정했다. 사용자가 선택한 새 계약에 따라 기존 `Profile/ImplicitProfile`만 기존 `MultiOutputProfile`로 올린다. 상위 프로필·원래 핀/바인딩·C# 본문을 조용히 바꾸지 않는다. void 전환에서도 원래 반환 writer와 소비자마다 명시 대응이 있어야 한다.

선택창은 혼합 구현의 C# target과 Blueprint target을 모두 제공한다. Blueprint 선택은 기존 소유 검사와 임시 저장을 거쳐 정확한 graph를 연다. 불완전한 코드/핀 입력이 남으면 원자 저장을 거절하고 입력을 유지한다. 코드 미저장 입력·취소·Undo/Redo·cold·유실 후 settlement 조회와 별도 Review/Confirm은 기존 경로를 사용한다. 새 패널·메뉴·권한·C# 실행 의미는 없다.

## 실제 검증

격리 fixture만 사용한다. 사용자 자료·실제 계정·유료 AI·프로젝트 Run은 사용하지 않는다. 확인한 check 수는 기능 수/통과율이 아니다. 로그와 최초 실패는 `/workspace/scratch/v536-information-mixed-targets`에 보존한다.

| 검사 | 결과 |
|---|---|
| 순수 후보 | 혼합 callee/caller의 명시 입력 대응·마지막 오류 거절 2, 첫 out 추가·void 전환의 원래 writer/소비 대응 및 잘못된 C# out 할당 거절 2: 총 4 check 통과 |
| 실제 엔진 API | 입력 타입 변경 및 명시 C#·BP 대응 3, out/void 계약·본문·소비자 결합 3: 총 6 check 통과. Save/cold/실제 compiler Review·Confirm/cold, 누락·구문·타입·외부 source·graph 오류 시 전체 미적용 포함 |
| 실제 화면 | 독립 창 정상 2, 기본 저장 실패/재시도 3, 독립 저장/조회 응답 유실 3, 전체 취소 2, 동시 편집 충돌 2, 동일 namespace 프로젝트 전환/늦은 코드 저장 차단 2: 총 14 check 통과. C# 두 본문 선택·코드 취소·private cold·Undo/Redo·명시 저장·Blueprint common 열기·Review 취소/Confirm·cold 포함 |
| 영향 회귀 | 기존 Native 계약 7, C# 여러 target·직접 호출자/서명 보호 4, 기존 입력·출력 결합 API 3: 총 14 check 통과 |
| 실제 target 컴파일 | 확정 fixture의 별도 사본에서 Main이 실제 정보 scope의 Caller를 호출하도록 하고 portable(common Blueprint)와 windows(C#)를 각각 컴파일했다. 2 target 모두 경고 없이 통과. 컴파일 receipt에서 common의 두 graphMap과 windows의 두 실제 C# body 읽기를 각각 확인했다([근거](evidence/v536-information-mixed-targets/target-selection.json)). 결과 프로그램은 실행하지 않고 원래 fixture도 변경하지 않았다 |

[검사 기록](evidence/v536-information-mixed-targets/acceptance.json), [C# 편집창](evidence/v536-information-mixed-targets/manual-body-code.png), [Blueprint target](evidence/v536-information-mixed-targets/mixed-target-blueprint.png)을 보관한다. CSS 3개는 `ed63fc1`과 byte 동일하다([근거](evidence/v536-information-mixed-targets/layout.json)). 전체 screenshot pixel 일치 주장은 아니다.

화면 fixture의 최초 두 실패는 실제 창 이름 `입력 연결 갱신`과 선택 값 `pin:count`를 기존 C# 전용 테스트가 다르게 예상한 것이었다. 원본 조작에 맞춰 테스트를 수정했으며 기능/CAS 검사를 완화하지 않았다. target 컴파일 fixture도 없는 `DotNet::Windows` 대신 제품과 같은 `windows` 키의 `DotNet::Portable` 선언으로 바로잡았다. 이미 저장한 fixture는 별도 컴파일 사본에서만 선언을 수정하고 원본 해시 보존을 확인했다.

환경 연결이 한 번 끊겼으나 같은 환경의 실제 명령/변경 파일/로그를 확인하여 복구했다. 이전 unified 세션은 재개되지 않았으므로 완료된 로그와 live process 상태로 결과를 회수했다. 완료 검사를 중복 시작하거나 환경을 교체하지 않았다.

## 4행 종료와 고정 후속

앞선 native C# 단위와 이번 혼합 단위를 합쳐 **직접 소유 정보 함수 하나·현재 기본형/배열 계약·native C# 본문·직접 C#/일반 Blueprint 호출자**라는 고정 4행 지원 경계를 마감한다. 코드 원문 자동 재작성은 지원 기능으로 주장하지 않는다. 더 넓은 실행/타입 문맥을 이 완료 판단에 추가하지 않는다.

5행 중첩/private graph 호출, 6행 whole-body/forwardCallerStorage의 ref/out 저장소 역할, 7행 등록 callable receipt·상속/copy 출처, 8행 여러 함수의 공유 caller 후보, 9행 고급 핀 타입/표시명은 미완료다. 기존 우선순위대로 다음은 6행의 명시 whole-body 본문/저장소 계약, 이어 5·7·8행의 소유·참조 문맥과 9행의 catalogue/표시명 경계다. 이번 직접 native out/void 검사를 6행 전체 문맥 완료로 표시하지 않는다.

I5-6 전체/v536 전체 UI·I6/B2·A4~A6/M4/M11/M12·Helper 실제 편집 작업은 완료가 아니다. 실제 Windows apphost/WebView2·모바일 기기·Library 전달도 별도 미검증이며 교차 빌드/브라우저 폭 검사와 구분한다. main·Android·원본 ZIP·사용자 자료는 보존한다.

## checkout·교차 패키지

소스는 `af6b26b685b39122e94e08bec0887462597097b0`다. root/clean Native 빌드는 0 warning/0 error, Linux 엔진 빌드 stderr는 0이다. 실제 Git fast-forward의 보존 CRLF/fresh LF에서 74개 canonical/exact 리소스와 내용·인코딩·BOM·binary·budget 변조 거절을 통과했다.

로컬 패키지 폴더는 `/workspace/artifacts/v536-information-mixed-targets/Windows-x64`, 진입점은 `Confectory.exe`다. manifest 2,335항목, manifest 자체 포함 2,336파일, manifest SHA-256 `02f061a4713fd4a0cde1c4245de25d61cfe3031e86f9ec780f56e5e2286c9ea7`다. 변경 실행 source 6개와 Native/Core DLL 2개를 패키지와 byte 비교했다([근거](evidence/v536-information-mixed-targets/package-identity.json)). 기존 Microsoft .NET Desktop Runtime 10 x64·WebView2 Runtime 전제를 유지한다.

별도 cwd·SDK 없는 runtime-only에서 실제 패키지 managed 웹 엔진·74리소스·최소 로그인 화면을 기동했다. 변조/의존성 누락 거절 및 격리 기존 프로필·명시 override 보존도 통과했다([결과](evidence/v536-information-mixed-targets/package-probe.json)). Windows apphost/WebView2를 실행하거나 실제 로그인/추론·프로젝트 Run·Library 전달을 한 결과는 아니다. 생성물/fixture/인증정보는 Git에 넣지 않는다.

깨끗한 checkout에서 혼합 out/void API 3 check와 독립 창 정상 UI 2 check도 통과했다([재현](evidence/v536-information-mixed-targets/clean-checkout.json)). 미저장 cold·CodeSave·Undo/Redo·Save/cold·Blueprint 선택/열기·Review 취소·실제 compiler Confirm·cold까지 확인했다. source 이후 최종 기록 커밋은 문서/근거만 변경하며 위 `af6b26b` 패키지와 실행 입력이 같다. 별도 재빌드의 바이너리 전체 bit-for-bit 동등성 주장은 아니다.
