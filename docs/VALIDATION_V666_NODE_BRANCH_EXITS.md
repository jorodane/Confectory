# M11 내부 흐름의 명시적 분기 반환

## 원본과 의미

기준은 저장소의 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`이다. 원본 `dist/blueprint.js`의 `branch-exit` 카드(1010행 부근)는 기존 분기 ID를 선택하며, 실행 계획은 `branchReturn: return-from-function`으로 해당 내부 함수에서 반환한다. 원본의 카드 추가·선택·실행선 연결·삭제 보호를 현재 직접 소유 내부 흐름에 연결한다. 공개 함수의 실행 계약 편집인 M12, 정보 종류 Enum/EnumValue의 데이터 표현과 구분한다.

기존 C#의 `Result`는 내부 실행 줄을 선택한다. 분기 반환 카드가 없는 기존 래핑은 계속 그 계산값 자체를 바깥으로 전달한다. 명시적 종료점을 편집한 경우에는 연결된 카드가 선택한 기존 ID의 수치를 반환한다. 따라서 같은 C#이 Alternate를 계산하더라도 그 경로 끝의 카드에서 Continue를 명시적으로 선택하면 바깥에는 Continue를 반환한다. C#을 파싱하거나 문자열로 고치지 않는다. 바깥 ID·enum primary/멤버/수치/순서·signature·arguments·branchOwner·실행선·계속 동작은 보존한다.

## 저장과 보호

종료점은 기존 `exit:` 경계와 `exits` 문서에 `{executionBranch: 기존ID}`로 보관한다. 명시적 종료 모드는 도달 가능한 모든 종료가 선택된 카드에 연결돼야 한다. 빈 선택·삭제되거나 모르는 ID·암시적 미연결 종료·고립된 반환 카드·명시 선언 분기(primary 제외)의 반환 누락·빈 계획은 전체 거절하며 기본 분기를 추정하지 않는다. 연결 중 카드 삭제는 실행선을 먼저 해제하도록 안내한다. C#이 쓰지 않은 out의 기존 진단과 할당 완료 정책을 분기 선택 정책과 섞지 않는다.

새 형식은 선택된 private graph에만 `schema: 2`와 `executionExitMode: true`를 사용한다. 물리 Root의 schema와 기존 profile은 바꾸지 않는다. 해당 private 형식은 관측된 switch 경계와 실행 계약이 있을 때만 허용한다. 이는 구형 실행 파일이 새 선택값을 무시하고 과거 계산값 전달로 실행하지 않도록 하는 버전 구분이다. 구형 롤백 UI에서 이 초안이나 소스를 확정하는 호환성을 주장하지 않는다.

기존 팝오버/카드 모양·자원 검색·실행선·Undo/Redo를 사용한다. 반환 카드에는 기존 이름만 표시하고 선택 ID를 저장한다. 첫 래핑 미리보기에서도 종료 계획과 선택적 본문/helpers 입력을 같은 `internalizeNode` 후보에 넣을 수 있다. 미리보기의 일반 계약·데이터 핀·다른 노드 생성 보호는 유지하고 종료 선택과 실행선만 추가로 허용한다. 미완성 계획 때문에 래핑만 중간 저장하지 않는다.

저장된 내부 graph의 계획은 기존 `authorBatch`의 격리 후보·완전한 원본 증거·checkpoint CAS로 저장한다. Root의 Save는 같은 구현에서 명시적으로 편집한 단일 내부 종료 계획을 확인해 해당 frame에서 저장하고 Root로 돌아온다. 다른 frame이나 구현의 입력을 추정해 결합하지 않는다. 실패한 요청의 수정은 원래 checkpoint와 전체 소스가 미적용 상태임이 증명될 때만 새 시도로 바꾼다. 응답 유실은 저장 receipt를 먼저 확인하고, 늦은 입력은 정확히 수락된 이전 증거와 일치하는 경우에만 새 basis로 이어간다.

미확정 래핑의 원래 C# 파일은 기존 `nodeFlowOrigin` 원자 그룹의 baseline으로 Save와 receipt 확인에서도 다시 검사한다. 아직 저장을 시도하지 않은 새 카드의 삭제가 원래 계획으로 돌아오면 해당 입력만 취소한다. 저장 중이거나 결과가 불확실한 시도에서는 원래 값으로 되돌린 입력도 보관한다.

Review→Confirm과 최종 파일 CAS, 원문 guard, 취소·Undo·재시작·프로젝트/표면 범위·부모/외부 원본 보호를 유지한다. 공개 override 계약을 바꾸거나 독립 계약 복제·새 공개 ID를 만들지 않는다. 로컬 반환 카드의 ID는 기존 공개 분기 ID와 다른 소유 문맥의 표시/종료점 식별자다.

## 검증과 남은 경계

새 API fixture는 Root와 중첩 frame, ref/out 동일·별도 저장소, 누락/삭제/미연결 종료의 native 진단, 원자 Save·cold·최종 CAS, 실제 분기·반환·out·반복 호출을 확인한다. C#을 그대로 둔 종료 선택 변경과 선택기를 거치지 않는 명시적 종료를 별도로 확인한다. 화면 fixture는 생성·선택 취소·연결·실제 핀 정렬·Undo/Redo·삭제 보호·첫 미리보기/저장된 흐름·Root Save·쓰기 실패·충돌·응답 유실·늦은 ref/out 입력·Review 취소/Confirm·재시작을 다룬다. 사용한 자료는 모두 생성한 fixture다.

초기 진단의 private 배치 허용 누락, 구조 재그리기로 건너뛰던 실행선 정렬은 수정 대상으로 구분한다. C# 버튼/가려진 캔버스 선택과 저장 receipt를 편집 입력으로 오인한 검사 실패는 검사 수정으로 구분하고 통과로 합산하지 않는다. 원본 레이아웃을 바꾸거나 기능 검사를 제거하지 않는다.

이번 단위는 직접 소유 내부 함수의 명시적 분기 반환이다. M11의 copy/상속/참조 전환과 private 미지원 기존 profile, M4/M12, B2 다른 사용자/그룹 권한 backend, 종류 C# 표현/사용 중 삭제 대응 및 3D·권한 별도 팩은 별도 고정 잔여다. 3D 이동은 표시이며 실행 선행 조건이 아니다. 실제 Windows apphost/WebView2·모바일 기기·전체 UI·Library/Space 전달은 교차 패키지와 구분한다. 이 종료 선택 작업으로 C# 임의 의미 변환이나 기존 profile 자동 승격을 구현하지 않는다.

## 최종 검증 결과

최종 패키지 source commit은 `dae566a1fecc0fcdb0fa80120603b13c3dfdf120`다. 제품 코드 `31a4ece93de279e526a4dcbd7c1e7e37f3b88ced`의 독립 LF **22단계**, CRLF **18단계**가 모두 통과했다. 이후 생성 패키지에서 검사 helper를 제품 `content/tests` 아래에서 찾는 경로 오류가 발견됐다. assertion·제품 코드를 바꾸지 않고 helper를 실행 검사 스크립트 옆에서 읽도록 두 줄만 수정했다. 정확한 Git diff와 전체 보관 증거를 확인하여 제품 코드 동등성이 입증된 checkout **40단계**를 재사용했다. 이 실패를 통과로 합산하지 않았다.

최종 source로 새 독립 LF checkout/복원/Release/MCP/엔진 **6개 준비 단계**를 수행하고, 새 교차 패키지·전체 압축 복원·실패 수명관리 **8단계**를 모두 통과했다. 따라서 수용 검증은 LF22·CRLF18·최종 패키지8의 **48단계**이며, 수정 뒤 추가 준비6과 최초 패키지 통과3/실패1은 따로 기록한다. 두 기존 checkout 각각 native switch/중첩/whole-body/ref-out **28개**와 소유 보호 **2개**가 실패/skip 없이 통과했다. 기존 일반 Root·void·공통 선언/헤더 이미지·원문 편집·계산 Result 전달 API를 이번 단위에서 실행했고, LF에서는 기존 늦은 ref/out 본문 입력 화면도 실행했다.

신규 API는 기본·중첩·ref/out 실제 호출, 정확한 거절 진단, 미확정 원문 guard 경합, 최종 CAS·cold·원문/바깥 연결 보존을 확인했다. 신규 화면은 첫 미리보기의 결합 Save, 저장된 흐름의 Root Save, 선택 취소·카드 삭제 취소·실행선 정렬·Undo/Redo·쓰기 실패·충돌·응답 유실·늦은 ref/out 입력·Review 취소/Confirm·재시작을 확인했다. 생성 패키지의 첫 미리보기와 전체 복원본의 ref/out 응답 유실 흐름도 Linux .NET 런타임에서 확인했다. 최종 패키지 8단계는 수정된 검사와 최종 source에서 새로 실행했다.

이번 변경과 독립적인 이전 57단계에서 확인한 프로젝트 왕복 화면·고정 call/After compiler·whole-body 문맥/저장소 API 결과는 재사용 근거로 구분한다. 구형 정상 패키지 `ce127d874a049cfb4460b5361086392ceffaa799`는 전체 SHA/CRC/모드 복원 후 새 private schema를 명시 거절하고 입력 소스 파일을 변경하지 않는 집중 검사를 통과했다. 이 호환성 집중 증거는 최종 코드 검증과 함께 보관하며, 구형 실행 파일로 새 형식을 실행했다는 뜻은 아니다.

- 최종 패키지 관리 record: `/workspace/artifacts/v536-verification-managed/runs/aabf40bae305496c9da92d154dab16d2.json` (14단계, cleaned).
- 재사용 checkout/경로 오류 record: `/workspace/artifacts/v536-verification-managed/runs/f78216c0877c4bc994ca4c777f8ff1b6.json` (43통과·1실패, cleaned), 증거 `/workspace/artifacts/v536-verification-managed/runs/f78216c0877c4bc994ca4c777f8ff1b6.zip`, SHA-256 `682a4f75c127f675fd38101d578c446b047a5d260e085da5521caa94544f0cb0`. 최종 증거의 `checkout-reuse.json`에 정확한 동등성 근거가 있다.
- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/aabf40bae305496c9da92d154dab16d2.zip`, SHA-256 `7e4b982535eb72929ad8413bae69e2ed1a7f7c594948f667f87439e697fcf10d`.
- 집중 증거: `/workspace/artifacts/v536-verification-managed/runs/4bd4332a4246498e9af3ab5dcafc8a25.zip`, SHA-256 `465962ee77318fcf421673c01c650481551bd26ba7daa26b87971236c6be66c9`.

| 보관본 | 실행 코드 commit | ZIP SHA-256 | bytes | manifest SHA-256 |
|---|---|---|---|---|
| 최신 | `dae566a1fecc0fcdb0fa80120603b13c3dfdf120` | `2c44b766588b73fc6fa2aff84e52e0cf8ea59e77d4be42656a5f2885bd8ea58a` | 51,261,730 | `2b3cd6aa50d404db196aa432ddccd5325ccc2faf2cf1ff9a2520273ce5cd72a9` |
| 정상 롤백 | `ce127d874a049cfb4460b5361086392ceffaa799` | `ef92b8bb8338f1fa1ec65e79e8bb921ea4309954aba43f46ca2f536ed84edd1e` | 51,251,080 | `8537cf2e79d74106e93865f7e143219e4d7fbed3874e7f14c76beaf897660bf0` |

보관 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신은 이번 코드로 새 생성·전체 파일 SHA/CRC/모드 복원과 복원본 실행을 검증했다. 롤백의 이전 정상 실행 증거를 재사용하고 ZIP SHA를 다시 확인했다. 최신 2510항목(2363파일/147디렉터리) / 롤백 2510항목(2363파일/147디렉터리). 새 schema의 프로젝트는 최신 실행 코드가 필요하며 롤백으로 묵시적으로 이전 의미를 적용하지 않는다.

최종 검증 두 시도의 디스크 여유는 2071.96 MiB → 정리 후 2064.67 MiB, 순증가 **7.29 MiB**였다. 단계 샘플 최소 여유 2066.89 MiB, cgroup 메모리 피크 4388.56 MiB였다. 기존 144 MiB 추가 디스크 예산(64 MiB 안전 여유 포함)과 RAM/메모리 예산을 유지했다. 집중/최초 실패/최종 소유 임시 root는 증거 보관 뒤 정리했다. 승인된 관리 저장소의 최신/롤백 회전과 해당 실행의 임시물 정리만 수행했고 과거 비관리 자료를 추가 삭제하지 않았다. 이번 순증가는 향후 보장값이 아니다.

결과 보고 HEAD와 패키지 코드 commit의 차이는 문서뿐임을 확인한다. 보관 패키지는 위 코드 commit에서 생성한 바이트이며 보고서 commit으로 다시 빌드했다는 뜻은 아니다. 해당 종료점 지원 단위와 M11 전체 완료를 구분한다. 실제 Windows apphost/WebView2·모바일·전체 UI·Library/Space 전달 및 위 별도 문맥은 미완료다.
