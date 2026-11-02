# 등록 외부 함수의 저장 copy 반환 검증

## 지원 범위와 원본 근거

원본 v666의 readonly 공개 분기 반환 배치(`dist/blueprint.js:969–976`)와 원계약 우선 구현(`dist/app.js:2469–2476`)을 저장된 등록 외부 함수 copy에 연결했다. 정보(schema)의 단독 명시 배정, 동기 void·값 입력·선택적 정수 out 하나, switch-profile Root의 기존 분기 ID/None 반환을 다룬다. 외부 계약/권한과 donor를 바꾸지 않고 로컬 copy의 entry/edges/exits만 원자 저장한다. C#·핀·ID·provenance·caller 연결과 원본 UI/CSS/HTML은 보존한다.

기존 copy ABI/소유 증명과 등록 함수의 readonly 헤더 receipt를 재사용한다. 화면 첫 dependency hash를 원래 저장된 copy 선언·author receipt와 결합하여 Save/복원/반복/Review 및 최종 source lease의 typed reads까지 확인한다. 직접 등록된 프로젝트/구현을 먼저 확인하며 snapshot 경로를 임의 파일 읽기로 사용하지 않는다. 외부 함수는 writable group에 포함하지 않는다. 기존 C# 카드 표시만 backend의 검증된 반환 가능 신호에 연결하고 C# 계약 편집 권한은 확장하지 않는다.

## 동결 소스·신규 검사와 재사용

동결 source commit은 `8a208174064c56b63e6bfec6caa03e66c97acd1d`이며 이후 결과 문서·수용 표만 갱신한다. 새 독립 **LF 17·CRLF 14·새 교차 패키지/전체 복원/실패 수명 관리 6, 총 37단계**가 통과했다. 최종 실행의 실패·생략은 없다. 독립 checkout은 no-hardlinks Git, 별도 home/NuGet·빈 엔진 캐시로 준비했다.

- 신규 양쪽 API는 외부 함수 source를 writable 그룹에 넣지 않고 copy 반환·out 발행·호출 다음 줄 실행, 부분 Review·계약/연결/proof/owner 거절, receipt 누락/변조·경로 위조·raw 변경, Save/Review 뒤 외부 함수 변경, cold·반복·확정 후 재진입을 확인했다. LF는 out 없는 함수와 기존 ordinary 등록 provider·소유 함수 saved-copy 회귀도 새로 실행했다.
- 신규 독립 화면 검사는 LF normal/project, CRLF loss 및 독립 정보 창 late를 포함한다. 새 패키지 normal과 전체 복원본의 독립 정보 창 late도 새로 확인했다.
- 집중 정상/취소/저장 실패/경합/응답 유실/늦은 입력/프로젝트 왕복은 최종 제품 파일 SHA를 동결 Git blob과 대조해 증거를 재사용한다. 기본/독립 창, Undo/Redo·선택 취소, Review 취소/Confirm, cold·명시 재저장·실제 호출을 포함한다. 집중 14단계, 진단 실패 0개를 보존하며 최종 통과 수와 섞지 않는다. 보조 스크립트의 중복 경로 오류는 clone/빌드/검사 전에 발생했고 같은 소유 공간을 재개했으므로 검사 실패나 중복 실행으로 세지 않는다.
- production Review/Confirm/CommitPlan의 local/external 최종 경합 4개와 기존 copy 읽기 CAS 4개는 양쪽에서 새로 실행했다. 의미·등록/권한 receipt는 별도 실제 엔진 API로 확인한다.
- Core/test 파일 일치만으로는 native 재사용 동등성이 충분하지 않았다. `BlueprintConversionTests`·`ExternalRefTests`가 변경된 authoring/workspace를 간접 호출하므로 이전 80개를 이번 완료 근거로 재사용하지 않았다. 패키지 검증이 끝나고 동일 동결 source에서 별도 no-hardlinks LF/CRLF checkout·home/NuGet/cache를 준비해 **native 38개+소유 경계 2개씩, 총80개를 새로 실행**했다. 추가 16개 준비/실행 단계가 모두 통과했다. 증거 `/workspace/artifacts/v536-verification-managed/runs/20c6be407a284adca3543bca71032d9b.zip`(SHA256 `133ff144d5f8065a6ce6e7f332ec0f3e29a3aa99dcda3640564b7ad0434048d1`)를 지속 보관했다. 제품 수정이나 패키지 재생성은 없으며 M11을 새 기능으로 다시 열지 않았다.
- 새 패키지 probe·hosted UI, 전체 파일 SHA/CRC·파일/디렉터리 모드 복원, 복원본 probe·hosted UI 및 실패 수명 관리를 새로 통과했다. 실제 Windows apphost/WebView2 실행을 뜻하지 않는다.

## 보관·수명 관리와 측정

| 구분 | source commit | archive SHA256 | 전체 manifest SHA256 | bytes / 파일 / 디렉터리 |
|---|---|---|---|---|
| 최신 | `8a208174064c56b63e6bfec6caa03e66c97acd1d` | `6a7e165835443b07201954ac62d270cf624651405699dfab28646ee463305360` | `33f4e87b84e50c95014800f700dc75d7003b4e494c62dec11185f0b18964f14f` | 51332130 / 2369 / 147 |
| 정상 롤백 | `c8c9cfd7f94bc9b9c536f2903dfa6c08c30aa3e0` | `a98e2b0435289f6c92c53831ea40cfe7f05246a1852fc9c7cf2dd474200052a2` | `8ceee2814a7ebe239ba0ddd488b7eeb71bc6b83792951d80923d9dfddbb941e5` | 51330275 / 2369 / 147 |

index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신은 전체 복원/복원본 실행을 새 검증했다. 롤백 실행은 이전 정상 근거를 재사용하고 압축 SHA를 다시 확인했다. 이전 엔진은 새 외부 함수 copy 반환 draft receipt를 지원하지 않으므로 최신 초안의 이전 엔진 복원을 보장하지 않는다. source 문법·원본 C# migration은 없다.

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/ba4ebdc7f1264fecbe30c6010807bad8.zip`(SHA256 `a226cc54c59fdbc6d181957a73db9e8486a02ffa094035ea08adfcd8ad506250`), 집중 증거 `/workspace/artifacts/v536-verification-managed/runs/34a58a79f60f4e6aa7a6582db01d1250.zip`(SHA256 `c7b6d7552d69eda81ab38cb62ab21368f9ae3db0fef1458eea7b616f4765446e`)를 지속 보존했다. child 종료와 보관 무결성 확인 후 집중·패키지 검증이 소유한 두 RAM 작업공간만 정리했으며 현재 존재하지 않는다. 기존 승인된 최신/롤백 승격과 관리 보관본 세대 교체 외에 과거 산출물·캐시·로그·프로필·원본·SDK의 추가 삭제는 없다.

집중 디스크 1933.05→1929.89MiB(순증가 3.17MiB), 최종 1929.55→1926.33MiB(순증가 3.22MiB), 수집 시 여유 1926.14MiB다. stage 표본 최소 여유 1926.30MiB, cgroup memory 관측 peak 4153.88MiB다. 기존 추가 persistent 예산 144MiB(안전 64MiB 포함), RAM 3GiB+512MiB 및 memory 7GiB+1GiB 기준을 낮추지 않았다. 추가 native 실행 디스크는 1926.32→1926.14MiB(순증가 0.18MiB)이며 증거 보관 뒤 해당 소유 RAM 공간도 정리했다. 이 순증가를 후속 실행의 보장값으로 쓰지 않는다.

## 유한한 잔여와 한계

등록 외부 함수의 새 copy 미리보기/첫 Save는 아직 연결하지 않았다. 직접 소유 계약의 새 copy 완료와 중복하지 않는 생성 수명 경계다. 다른 데이터 출력 ABI·복합 호출 closure 및 M4는 [유한한 M12 대조표](BLUEPRINT_ROOT_EXECUTION.md)에 분리한다. 부모/참조 원본 쓰기·공개 override 계약 변경은 정상 거절이고, 독립 새 계약 복제·자동 legacy 승격은 요구하지 않는다. 새 권한/자격증명/유료 호출은 없다. M11은 완료 상태를 유지한다.

교차 패키지와 Linux hosted UI 검사는 실제 Windows/WebView2·모바일 실행, 전체 UI나 Space/Library 전달 완료를 뜻하지 않는다. 이전 엔진의 새 draft receipt 복원 호환성을 보장하지 않으며 원본과 이전 보관본은 유지한다.
