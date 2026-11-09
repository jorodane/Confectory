# 값 이름과 본문의 결합 저장 검증

동결 `3897515cd1027f460dbabe33bd606631d1410b58`의 신규39단계·재사용0을 통과했다. 분포 `{"alias": 1, "lf": 15, "crlf": 15, "windows": 2, "packaged": 2, "restored": 3, "package": 1}`.
[원본 근거와 유한한 지원](V536_ALIAS_SOURCE_SAVE.md)을 따른다. 개발 단계는 최종으로 다시 세지 않는다.

| 검사 | 실제 확인 |
|---|---|
| source | LF/CRLF no-hardlinks 독립 checkout·HOME/NuGet·빈 engine cache·Release/MCP/Linux engine. 고정 v666 ZIP/SHA, 정확3개 제품 파일. CSS/원본 배치·고정 C# 편집기/본문 선언·Core/targets/계약·기존 alias helper·권한 원문 불변 |
| 정상 | 기존 code next 출력의 한글/공백/Unicode 별칭과 명시 C# 본문, 반환 consumer를 한 checkpoint에 저장. 기존 switch profile·함수/노드/핀·별칭 ID/저장소/type과 원문 CRLF/C# 바이트를 보존. 값 이름 자체는 코드 식별자가 아님 |
| atomic/history | source → aliasPlan의 임시 후보 전체 검증 후 checkpoint CAS. 잘못된 순서·복수 source·다른 owner/frame/node·stale proof·잘못된 이름/type/source는 전체 거절. 공유 Undo/Redo/cold로 본문·별칭/소비자를 함께 복원. 기존 별칭 단독 Save 유지 |
| 실패/복구 | 실제 checkpoint readonly 거절·원래 요청/입력 유지·동일 저장소의 이름/C# 텍스트 수정 후 명시 retry/cold. 초기 Save는 물리 원본을 덮지 않는 초안이고, 수정 retry의 baseline은 물리 원본까지 일치해야 함. 실제 동료 checkpoint 충돌과 cold retry는 전체 거절 |
| 유실/늦은 입력 | 적용/확인 응답을 실제 route에서 유실·보류. full source/checkpoint receipt가 적용분과 새 이름/본문을 구별하고 cold에서 수신 전 텍스트를 재생하지 않음. 새 입력은 같은 owner/source/저장소 증거 안에서만 재검증 |
| Review/실행 | Review 취소·실제 CS0103 compiler 진단·수정 보존, Review 뒤 물리 graph 변경을 최종 CAS로 거절. 새 명시 Confirm에서 graph/코드만 반영하고 기존 caller의 명시 본문 실제 실행 결과11을 확인 |
| 영향 회귀 | 기존 표시명+본문의 LF native API/history와 CRLF lost-response UI 경로를 확인. M11/M12/M4 전체 재검사는 미실행이며 해당 기본 경로의 새로운 필수 조합을 만들지 않음 |
| package | 새 Windows 교차 생성/구조·의존성·SHA. 포함 Linux engine과 전체 ZIP CRC/SHA/파일·디렉터리 mode 복원본의 실제 UI/원자성/late/conflict. 실패 증거 보존과 owned 임시 수명관리 |

LF native API는 전체 거절/실패/receipt 경계를, CRLF와 패키지 native API는 대표 순서/저장소
거절·정상/idempotent 저장을 실행했다. 신규 UI는 LF normal/storage/compiler, CRLF loss/late/conflict,
패키지의 집중 정상 실행과 전체 복원 late/conflict로 나누어 실행했다. 동일 사실을 전수 재실행으로 표현하지 않는다.

개발16개 기록 중14개는 exit0, 두 실패는 검사 기대값을 바로잡은 기록이다. 첫 UI fixture가
원래 switch profile을 alias 전용 profile로 바뀐다고 잘못 기대했다. 실제 제품은 원래 profile을
유지했다. 두 번째 native fixture는 초기 초안 Save와 수정 retry의 물리 CAS 경계를 혼동했다.
기존 source recovery API는 초기 draft Save의 외부 물리 변경 보존을 명시하며, text-pair recovery
API는 수정 baseline의 물리 변경 거절을 명시한다. 이 기존 계약을 바꾸지 않고 fixture를 고쳤다.
최종 제품의 build/unit/API/normal/storage/late 여섯 개발 단계를 통과했고 실패 자료·수정 전
스크립트·원인·프로필/로그/스크린샷·입력을 보존했다. 개발에서는 저장 실패/late 후속 본문 결과12의 실제 실행도 별도로 확인했다. 개발 실행에 사용한 전체 수명 검사 파일은
executed-inputs/manifest로 별도 보존하고, 최종은 중복 컴파일/Confirm을 줄인 집중 변형을 실행했다. 최종39단계는 전부 신규다.

개발 검토에서 속성 관측/Set/전달 문맥의 별도 source 보호를 확인하고 새 결합 admission에서
제외했다. 기존 단독 source·alias·공개/override 계약이나 권한 의미는 바꾸지 않았다. 새 receipt
형식/profile/고정 pin ID·C# 자동 변환은 없다. 이전판은 확정 source/기존 alias graph를 읽지만
새 결합 author-attempt의 미확정 복구를 지원하지 않는다. 자동 분해/순차 적용/입력 폐기는 없다.

같은 작업에서 이미 생성·검증한 직전 최신 package의 SHA와 metadata를 확인한 뒤 read-only FD의
POSIX_FADV_DONTNEED로 사용이 끝난 해당 파일 읽기 캐시만 반납했다. read-cache.json에 기록했다.
원본 파일 삭제·보관 정책/전역 cache·allocator/cgroup/추가9GiB·안전1GiB 예산 변경은 없다.
검증기는 소유 scratch에 precompile한 동일 Python 모듈로 실행하며 생성 bytecode는 Git에 넣지 않는다.

검사 중 exec-server 연결이 끊겨 기존 출력 세션 재연결은 실패했다. 새 읽기 전용 명령이
응답한 뒤 원래 검증기와 worker의 PID·시작 시각, root inode, 동결 HEAD/clean과 로그를
대조했다. 같은 프로세스가 복원 late/conflict와 실패 수명 검사까지 계속 진행했고 최종
39단계·보관·정리를 정상 종료했다. 빌드/검사/수정 명령을 재실행하거나 환경을 재생성하지
않았다. 해당 관측은 같은 run의 `.environment-recovery.json` sidecar에 보존한다.

다른 고정 혼합 저장/고급 함수 ABI·실제 신원/그룹 권한 backend·정보 종류 C# 표현/사용중 삭제
정책은 기존 잔여다. 실제 Windows/WebView2·모바일/기기 IME·GPU/물리 오디오·전체 UI·Space/
Library 전달은 미실행/미완료다. 초기 빈 화면과 과거 Agent 준비 일시 지연의 근본 원인은 미확정이다.

## 보관과 공간

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 3897515cd1027f460dbabe33bd606631d1410b58 | 752f087a97a9be604258a29af21e6589cb06ea95665d7466314ee3d0505ba84c | 53,856,992 |
| rollback | 11b38f1a76ef421cb06fc1db89f47aa1a743dcf3 | a36bf0f461ec6d222e5feb40a43b6c6af8a6309e7cadc250c758b2bbb78f35ab | 53,854,590 |

record `/workspace/artifacts/v536-verification-managed/runs/90da18416a5b4efe9612b77e5eae9719.json`, evidence SHA `b6135c4a901e3e0ee7ca040e72eeba1bfb3bcf06b978d93458c5f28f0c7d20ad` (2,871,222B).
개발 evidence SHA `a4bf547bacaf3b7eda7d1338a6a55d09e742509f4d43d0244b072bd996f8cd5a` (1,448,190B).
두 archive/전체 manifest를 대조했고 owned RAM root는 제거됐다. 직전 관리 rollback만 승인된
두 세대 정책으로 교체했고 다른 과거 자료·증거는 삭제하지 않았다. closing index `/workspace/artifacts/v536-verification-managed/runs/90da18416a5b4efe9612b77e5eae9719.closing-index.json`,
SHA `56c5be45d6ce9729829f896d1510893f9e573222278595f94fb063c9e3633215`.

단위 최초 읽기 전용 확인 df 25,910,644,736B, 종료 25,901,662,208B (24.1228GiB), 순증가
8,982,528B (8.5664MiB). 표본 cgroup peak 9,144,274,944B는 limit
17,179,869,184B와 안전 1,073,741,824B 안이다. 추가9GiB·RAM4GiB 예산을
유지했다. 게시/후속 문서와 원격/clean/main/원본 확인은 scratch publication.json에 남긴다.
