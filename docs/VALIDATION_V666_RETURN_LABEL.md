# 정보 함수 반환 표시명 검증

최종 runtime `dcf4cf7b82a3d6f84515a4b921dfb17dcce62c94`의 **신규36단계·재사용0**을 통과했다. 분포 `{"crlf": 15, "lf": 13, "windows": 2, "restored": 3, "packaged": 1, "return": 1, "package": 1}`.
[원래 수용 근거·지원·호환 경계](V666_RETURN_LABEL.md)를 따른다.

| 범위 | 실제 결과 |
|---|---|
| 게시본 재현 | 원래 native 프로그램46 실행. v666 원본의 출력 이름 입력과 달리 게시본 상세창의 고정 반환 이름은 readonly이고 표시명 native 후보만 거절 |
| 후보/거절 | 두 반환 표시명의 순서를 바꿔도 같은 metadata 후보. 빈 값·과대·내부 control2종·숫자/null6개, stale hash·비소유 함수·추가 pin ID 전체 거절. 기본 `결과`는 선택 키 제거 |
| 호환 | optional 키 없는 후속 구 요청은 저장된 표시명 보존. 새 소유 함수 첫 생성 후보도 metadata만 추가. 기존 parser/value 문법, 공개/native signature와 C# 생성은 유지 |
| 실제 UI | 원래460px 기본/독립 창에서 한글·공백·emoji·HTML 기호를 표시 텍스트로 저장. 빈 값 오류/취소·Undo/Redo·미저장/저장 cold·Review 취소/새 Confirm·실제 실행46 확인. 정확64 기본값·입력 이름·원래 C#/ID/graph 연결 유지 |
| 실패/격리 | checkpoint 쓰기 실패 뒤 두 입력/원본 보존과 명시 재시도, 응답/결과 조회 유실 뒤 cold receipt 확인·중복 저장 없음. owner peer 충돌·같은 namespace 프로젝트 왕복·독립 창 취소 확인 |
| 늦은 입력 | queued Save 접수와 전달 사이 실제 상세창에서 새 반환 표시명 입력. 캡처한 두 이름만 저장하고 새 이름은 cold 뒤 보존. 두 번째 명시 Save/새 Review/Confirm으로 늦은 표시명 저장 후 실행46 |
| 회귀 | 공통 standalone 기능 상세창의 기존 IME Escape/저장 흐름과 기존 계약 그대로 native 본문 편집을 새로 검사. native caller의 Save 전 및 Review 후 변경 거절·cold 재시도·최종 실행20과 물리 원문/inode/mode/mtime 유지 확인 |
| 최종 패키지 | LF/CRLF no-hardlinks·독립 HOME/NuGet·Release/MCP·빈 cache 엔진에서 새 검사. 새 Windows 교차 패키지 구조/무결성, 포함 Linux 엔진 UI, 전체 ZIP CRC/SHA/파일·디렉터리 mode 복원과 늦은 입력/응답 유실, 패키지 실패 수명관리 통과 |

제품 변경6파일이다. 기존 UI 이름칸의 정보 전용 opt-in, 선택적 표시 metadata와
후속 입력 receipt 비교, 변경한 두 JS의 원래 canonical size/hash를 연결한다.
HTML/CSS·C# 원문·code generation·실행 계약·override·권한·최종 CAS는 바꾸지 않는다.
같은 원래 `return` 슬롯을 표시할 뿐 새로운 출력이나 원본 편집 권한을 만들지 않는다.
일반 인자/out 이름의 기존 계약 의미도 유지한다.

개발17단계 중16통과·1실패를 보존했다. 처음 변경한 JS와 번들 resource 크기/해시를
아직 맞추지 않아 host가 시작을 거부했다. 해당 두 descriptor만 갱신한 뒤 실제 UI를
통과했다. 개발 통과 결과는 최종 검사 수에 재사용하지 않았다. 제품 입력 유실이나
기존 간헐 초기 빈 화면 원인이 이 실패로 밝혀졌다고 간주하지 않는다.

초기 메모리 사전검사1회 차단을 별도 보존했다. 보관 ZIP/이전 owned evidence의
정확 해시·크기·inode/mode/mtime을 확인한 read-only FD에서 파일별 cache 조언만
사용했다. 전체 cache/예산을 바꾸거나 중복 빌드하지 않았다. 최종 preflight는 원본
그대로 보존하고 개발 계획·실패 기록은 별도 이름으로 수집했다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | dcf4cf7b82a3d6f84515a4b921dfb17dcce62c94 | dac9103fb29d20cc42cafa105204f95662a636253c53c0bdb8b249dce45ac82b | 53,865,648 |
| rollback | 464cb0c2c07b5b5cffeabe25d2112cc8451779b2 | 4782033421f891e9f62e7d868e418896aa9e873bcd733c2ac052b9e26b3fb452 | 53,863,807 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/531001f848a340eda705e9f524abbd32.json`, evidence `3c81435ff279fc0890c69cdb88ec387c9954d8bf5d12430636d1bd8c7b2a955f` (5,125,547B).
개발 evidence `55ee0dbfbd898f18c8cc7813dc40468b6fd506e46cd7ca333de0ecf304a3e435` (1,708,159B).
양쪽 evidence manifest와 보관 ZIP2개를 재검증했다. 시작 index `0faf5d85d555017712d28f6de1dfd61fd364529929e6af8eaf80c4a29fcc9ebf`,
종료 sidecar `c41ac48d31e2a4c49516fe98a1b9439be6674b184c009f6ef26de7e813eddac7`. latest/rollback 두 관리 ZIP만 기존 승인 절차로 교대해
이전 rollback `6a9b48d2af44eb4fa0227d80b164c24f17bcd164`의 관리 ZIP만 교체했다. 과거 evidence와
사용자 원본·기존 checkout은 보존했다. 새 개발/최종 RAM 작업공간은 evidence 봉인과
소유 identity 확인 뒤 정리했다. 재생성 build 출력은 SHA 목록을 남기고, 원문·checkpoint·
실패 로그/화면은 archive에 보존했다. 이 단위의 새 owned bytecode만 별도 해시 증거로 정리했다.

시작 여유 25,808,588,800B, 마감 25,799,032,832B(24.0272GiB), 순증가
9,555,968B(9.1133MiB). 최대 관측 cgroup memory 9,268,051,968B,
최종 stage 최소 디스크 25,804,259,328B. 추가9GiB+safety1GiB·RAM4GiB+
reserve512MiB·최종 evidence512MiB의 기존 예산을 유지했다.

고정9행의 일반 입력/out 표시명 분리와 정보·참조·외부 타입 실행 연결, 7/8행의
다른 실제 closure는 기존 잔여다. 고급 핀의 공통 값/참조 표현과 schema별 생성 C# 타입
선택은 사용자 응답 대기 중이며, 구현된 것으로 보지 않는다. 신원/그룹 backend·종류
CLR/사용 중 항목 삭제 정책도 임의 확정하지 않는다. M11/M12/M4를 새 조합으로 다시
열지 않는다. 초기 빈 화면 원인과 과거 Save 클릭 요청 미발행의 간헐 원인은 미확정이다.

검증은 Linux native 엔진·Chromium·생성한 격리 fixture다. Windows 교차 패키지는 실제
Windows/WebView2 실행이 아니다. 실제 모바일·물리 IME/GPU/audio·사용자 프로젝트·
전체 UI·Space/Library 전달과 모든 구 reader/checkpoint 교환은 미검증이다.
