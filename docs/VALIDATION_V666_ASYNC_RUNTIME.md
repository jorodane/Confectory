# v666 M4 명시적 async 런타임 검증

제품 코드는 `671d477f104aea37522f21d21f53a3dce46fc189`로 동결했다. M12는 기존 [유한한 마감표](M12_CLOSURE.md)에서 닫혀 있다. 이번 단위는 [M4 지원 경계](M4_ASYNC.md)의 실제 Task/await 계약·ordinary 동작/직접 호출자 실행과 metadata scaffold다. 화면의 async 전환/초안·원자 저장 UI 전체 완료를 뜻하지 않는다.

## 신규 검증과 범위

최종 독립 실행 **50단계: LF 22·CRLF 20·새 패키지/전체 복원/실패 수명관리 8, 신규 50·재사용 0**가 모두 통과했다. 단계 수이며 개별 assertion 수와 구별한다. 최종 코드를 수정한 뒤 영향 검사 결과를 이전 코드에서 재사용하지 않았다.

- LF/CRLF 각각 async·switch Core 18개(새 async 11개·기존 switch 7개), M12 runtime 17개, 소유 경계 2개가 통과했다. 기존 계약·ID/숫자값·반환/out, 원문, ref/부모 계약 거절과 완료 ID/출력 이름 충돌을 포함한다.
- 새 async graph와 실제 CLI 실행에서 await 뒤 native/out 값 게시 → 완료 → 결과 분기 → 다음 동작을 확인했다. 빈 완료 영역, None, 기본 반환, 원래 Task 오류와 동기 Graph/C# caller 거절을 포함한다. 동기 import는 IInvoke만 노출하며 InvokeAsync에 바로 접근할 수도 없다. 자동 blocking/호출자 전환을 추가하지 않았다.
- checkout LF/CRLF·새 패키지·전체 압축 복원본의 실제 Core/CLI/metadata/컴파일러 각각에서 `async_runtime.py`의 5개 검사가 통과했다. 반복, 원문 불변, Task 오류, 자체 child 중단·새 재시도, 동기 caller 오류를 포함한다. 생성한 테스트 자산/프로젝트만 사용했다.
- 기존 M12 UI의 정상·취소·저장 권한 실패·cold·Undo/Redo·응답 유실·늦은 입력·외부 충돌, copy/자식·wrapper·비void·등록 부모와 최종 read guard를 새로 실행했다. Review 뒤 외부 함수/scope/manifest 또는 caller 변경은 전체 CAS 미반영하며 입력을 유지했다. 이것을 새 async 전환 UI 검사로 계산하지 않는다.
- 새 패키지 구조/SDK-less runtime/엔진·UI와 전체 파일 복원을 확인했다. 복원본에서도 async 실행 및 늦은 입력 저장/복구를 검사했다. 성공/실패/예외·재시작 증거 보존과 FIFO 등 수명관리 검사도 통과했다. 기존 LF 최종 화면 증거 한 개를 시각적으로 확인했으며 UI/CSS를 변경하지 않았다.

최종 기록: `/workspace/artifacts/v536-verification-managed/runs/fa4cfd0fe2904197b1a7b9fa27a6ec44.json`

전체 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/fa4cfd0fe2904197b1a7b9fa27a6ec44.zip`

증거 SHA256: `9c99a1224f82bc8e7c9dd913d89413099c34e832e56a08f2a9564b514dc945de`

별도 보조 검사는 소유 구현의 명시 async 참조 scaffold 두 양성과 동기 caller 거절, 3개다. `/workspace/scratch/v666-async/reference-probe.json` (SHA256 `eb95194944449ab22130d95dd7cfb522d696a56665b2826a773d6640eb14f290`)에 소스 commit/실제 LF metadata assembly SHA와 결과를 보존했다. 처음에는 새 일반 함수 scaffold operation을 잘못 사용한 fixture 요청을 바로잡았으며 제품 변경은 없었다. 이 3개는 위 50단계에 포함하지 않는다. 활성 workspace의 재채택은 원래 owner guard가 거절하여 실행하지 않았고 우회하지 않았다. 보조 JSON은 별도 지속 공간에 보존하며 최종 ZIP에 포함됐다고 주장하지 않는다.

## 최종 코드 전 진단 보존

개발 기록 `20530c11757c42fe99fdd0a1b1f4cfd0`은 새 테스트 미등록(0개 실행), fixture provider/JsonObject 경로 오류, 실제 생성 라벨 범위 오류와 수정/재검사를 구분해 보존했다. 최종 코드의 합격 근거와 혼합하지 않는다. `1110800` 기준 첫 최종 시도 `fcaa80fbc5144e16813de89b47031566`는 동기 C# import의 async 노출 문제를 고치기 위해 5단계 뒤 명시적으로 중단·보존·정리했다. 수정된 `671d477`로 전부 새로 검사했고 중단한 결과를 재사용하지 않았다.

## 지속 패키지와 공간

| 보관 | 제품 source | ZIP SHA256 | 전체 파일 manifest SHA256 |
|---|---|---|---|
| 최신 | `671d477f104aea37522f21d21f53a3dce46fc189` | `df85fbb43ac67533e63198c9484b6dba651d9422912ddcd80bd0128f7390d808` | `c87e42db954064a3734a382f2ef254d824f29b5aae4008a52847e209bdd639ed` |
| 롤백 | `a6dd2876100f08197f9d34feb304a7e2ac1e6528` | `f4b8ec56e3b19d643e4202083ea47894d75c02a085442da5939acd25ad0e97c7` | `916463f323425ca44a255846ab21c7a4361d4ca67e1585bb73a257dad3f22a3c` |

보관 index: `/workspace/artifacts/v536-verification-managed/packages/index.json`. 최신 ZIP은 51,411,968 bytes다. 승인된 2세대 승격/실패 복구 절차를 사용했고 기존 M12 최신본은 롤백으로 유지했다. 그 정책에서 이전 managed rollback만 교체했으며 과거 자료 전체 정리나 별도 삭제를 하지 않았다. 새 async 자료의 구버전 실행 제한은 [호환성 경계](M4_ASYNC.md)를 따른다.

최종 검증 시작 여유 1,916,321,792 B → 증거/패키지 지속 보관·임시물 정리 후 1,911,697,408 B, 이 실행의 순증가 **4.41MiB**. 개발 진단·중단 기록과 코드 commit을 포함한 이번 작업 전체는 1,917,444,096 B → 1,911,697,408 B, **5.48MiB** 순증가다(이 문서/게시 기록 추가 전 측정). 샘플링한 메모리 peak는 **4162.23MiB**. 기존 디스크 144MiB(안전 64MiB 포함), RAM 작업공간 3GiB 및 추가 메모리 7GiB+안전 1GiB 예산을 낮추지 않았다.

원래 workspace·사용자 데이터·SDK·과거 출력/로그/스크린샷은 보존했다. 이번 실행이 직접 생성한 RAM checkout·독립 cache·빌드·패키징 임시물만 원래 owner의 자식 종료/증거 검증 뒤 정리했으며 최종 RAM root는 존재하지 않는다.

## 남은 범위

원본의 명시 async 메뉴/완료 포트와 기존 초안·저장·Review/Confirm 연결, 실제 기존 C#·내부/소유 본문 전환 경계가 M4의 두 실제 잔여 흐름이다. 정상 비소유/override 계약 보호나 타입/문맥 조합을 새 필수 항목으로 늘리지 않는다. V2–V9, 종류 C# 표현/사용 중 삭제 대응 및 별도 기존 UI/팩/backend는 고정 수용 목록의 잔여다.

실제 Windows apphost/WebView2·모바일 기기/DPI/IME·전체 UI·Space/Library 전달은 실행하지 않았다. 교차 패키지와 Linux에서의 실제 Task/엔진 검사를 이들 완료로 표현하지 않는다. main은 사용자 검토/merge 대상으로 유지한다.
