# 공통 함수 상세창 IME Escape 보호 검증

동결 `ecb47f0acd220c617281374d6db42594e5e74d33`의 신규29단계·재사용0을 통과했다. 분포 `{"signature": 1, "lf": 11, "crlf": 11, "windows": 2, "packaged": 1, "restored": 2, "package": 1}`.
[원본 근거·지원/호환 경계](V2_SIGNATURE_IME.md)를 따른다.

| 범위 | 확인 결과 |
|---|---|
| 기준·변경 | 고정 v666 ZIP SHA와 게시 833617c7를 대조했다. 공통 함수 상세/타입 검색의 Escape listener 두 곳과 bundle 크기·해시만 제품 변경이다. native backend·공개 ABI·원본 C#·권한·CSS/HTML·레이아웃·저장 문법은 동일하다 |
| 재현 | 게시본의 실제 상세창과 타입 검색창에 isComposing 또는 legacy keyCode229 Escape를 각각 전달하면 미저장 입력이 사라지는 네 경우를 개발에서 재현했다. 원본/체크포인트는 변경되지 않았다 |
| 입력 보호 | 실제 Chromium DOM에서 설명·미확정 핀 이름·타입 검색어를 보존한다. 일반 Escape는 검색창을 먼저 닫고 다음 Escape는 상세창을 취소한다. 반복 취소·명시 닫기·cold 재진입은 미확정 팝오버 복사본만 버린다 |
| 명시 저장·실행 | 계약을 바꾸지 않는 설명 Save·기존 feature Save·cold·Review 취소·새 Review/Confirm을 실행했다. Pair.celem 설명 외 원본 바이트와 C#·호출자/핀 정체성을 보존하며 실제 C# 실행 결과10, stdout body→10을 확인했다 |
| 독립·패키지 | LF/CRLF 각각 no-hardlinks checkout·독립 HOME/NuGet·Release/MCP·빈 Linux engine cache와 공통 boundary/normal/cancel UI를 새로 실행했다. Windows 교차패키지 생성/구조·SHA, 포함 Linux engine 정상 UI, 전체 ZIP CRC/SHA/파일·디렉터리 mode 복원 뒤 cancel/cold 및 실패 수명 관리를 확인했다 |

개발의 완료10단계는 모두 통과했으며 최종29단계에 재사용하거나 합산하지 않았다.
실제 UI fixture는 직접 소유 Owned.Elements::Pair다. 공통 helper의 다른 진입점을 모두 개별
실행한 것은 아니며 기존 call site/수명 처리 불변은 정확한 소스 대조로 확인했다.
native 저장/Review/최종 CAS 구현을 바꾸지 않은 작은 키 라우팅 수정이다. 기존 충돌·응답 유실·
권한 거절 전체 행렬을 이번에 새로 실행했다고 주장하지 않는다. 명시 Save·Review 취소/Confirm·
cold와 입력 취소 경계는 동결 코드에서 신규 검사했다.

브라우저 CompositionEvent/KeyboardEvent는 생성한 이벤트이며 OS IME 드라이버 실험이 아니다.
일반 Escape는 브라우저 키보드 입력으로 검사했다. 실제 Windows/WebView2·모바일/터치·
물리 키보드/IME·GPU/오디오·전체 UI·Space/Library 전달은 미검증/미완료다.
초기 빈 화면 및 과거 Agent 준비 지연 원인은 미확정이며 이 재현을 그 원인으로 간주하지 않는다.

저장 형식·계약·마이그레이션을 추가하지 않았다. 이전 runtime도 같은 데이터를 읽지만 이번
IME 키 라우팅 수정은 없다. 핀 표시명과 native 식별자 분리·고급 ABI·나머지 고정 혼합 계약·
실제 신원/그룹 권한 backend·정보 종류 C# 표현과 사용중 항목 삭제 정책은 별도 잔여다.
M11/M12/M4를 재개하거나 가능한 조합을 새 필수 범위로 늘리지 않는다.

## 증거와 보관

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | ecb47f0acd220c617281374d6db42594e5e74d33 | 39a59e2b7698dd18c35870db6f279391a7542d396c2c55593e6b7c4b08e06a4b | 53,856,143 |
| rollback | 047a71fab211d0ebf08925e395890d1a7771d1c2 | 662f770cd7509775c9ef93099e8b14563bf4acd4be5089627c3056b342b700d9 | 53,856,158 |

record `/workspace/artifacts/v536-verification-managed/runs/79839c44a0074947ade988a874be5a6d.json`, evidence SHA `b848ce80c2290bf6fb0b9d60e3051f5423dc77afe0f911ac8d80fcbc952ce674` (1,820,112B).
개발 evidence SHA `56e032ddae33a6260653844094f1420ee8b4fda1df7745989c0de4b9b33c9a43` (811,900B).
두 보관본의 전체 manifest와 실제 SHA를 대조했고 완료된 owned RAM root만 정리했다.
기존 승인 두 세대 정책의 관리 rollback3897515c만 교체했고 다른 과거 자료/증거는 보존했다.
시작 index는 최종 봉인 archive에 포함하며 SHA `911331f196b576a672dddfe76890dcbd71a61243cb7737a99eb4fff67ad29251`,
closing index SHA `69f1df4a5644b81bdfef11edd7303cf94b817052b9f153de881e4d5018bdca9b`다.

증거 수집 중 개발 preflight.json을 최종 preflight.json 경로로 복사한 실수가 있었다.
최종 시작 당시 memoryCurrent/ramAvailable 두 표본은 회수하지 못해 null과 한계로 명시했다.
개발 원본은 unit-development-preflight.json, 오류 경위는 preflight-collection-note.json에
보존한다. 시작 df는 run.json/최종 summary와 일치한다. 동결 harness는 실제 최종 preflight를
통과한 뒤 실행했고 해당 파일을 재독하지 않으므로 제품/검사 입력·실행 결과는 변하지 않았다.
고정 예산은 봉인된 harness에서 확인하며 모든 단계의 memory/disk 관측은 남아 있다.
누락된 표본을 개발 수치나 사후 수치로 대신했다고 주장하지 않는다.

단위 첫 df 25,891,418,112B, 마감 25,884,721,152B (24.1070GiB),
순증가 6,696,960B (6.3867MiB).
개발/최종 표본 cgroup peak 9,157,664,768B는 limit 17,179,869,184B에서
안전 1,073,741,824B를 남긴 범위다. 추가9GiB·RAM4GiB·안전1GiB·최종 증거512MiB
예산을 유지했다. 같은 작업의 직전 완료 latest ZIP에만 적용한 read-only FD/FADV_DONTNEED의
SHA·inode/크기/mode/mtime 불변 증거를 보존한다. 전역 cache/allocator/cgroup 변경은 없다.
이번 생성 bytecode만 마감 뒤 제거하며 게시 후 원격SHA/clean·main/원본 보존·df는 scratch
publication.json에 기록한다.
