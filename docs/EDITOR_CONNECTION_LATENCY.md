# Agent 연결 클릭 오류와 지연 검증

기준 소스는 `f3f282dc4904b3c3a5922996f55bc051b7f0fd49`이다. 사용자가 보고한 Windows 시간은 Agent 추가 약 1초, 모달 이후 provider 활성화 약 1초, Codex 오류 약 2초, 닫기 약 0.3초다. 아래 수치는 Linux/.NET 10/Chromium에서 별도로 측정했다. Windows 실기 성능 측정값으로 해석하지 않는다.

기존 Codex 기본 진입은 `connectionSetup`을 호출해 로컬 provider 설정 파일과 스키마를 먼저 읽었다. 부분적으로 남은 `Settings.celem`과 없는 `project.cpack`으로 같은 공통 소스 오류를 재현했다. 해당 예외는 WebInvoke에서 `consumer_error`로 바뀌고 WebState에서 `source_operation_failed`로 표시되었다. 사용자의 실제 Windows 설정 파일은 확보하지 않았으므로 그 컴퓨터의 구체적인 파일 오류까지 확정하지 않았다.

기존 첫 Agent 열기는 `connectionCatalog` 프로세스 1개를 시작했고, 첫 Codex 선택은 catalog/settings/describe/inspect/effective 프로세스 5개를 시작했다. 반복 선택도 3개를 시작했다. catalog는 등록 팩과 객체 선언을 조회하고, effective는 새 Registry로 스키마를 계산했다. 스냅샷 생성은 계측된 Home 경로에서 중앙값 1ms 미만이었다. 클릭 구간의 컴파일 프로세스는 0개였다.

수정한 기본 진입은 설치된 앱의 public linkage에서 읽은 표시용 연결 카드와 기존 MCP 엔진 패널을 사용한다. 카드 표시는 실행·인증·프로젝트 권한의 근거로 사용하지 않는다. 명시적인 목록 새로 읽기와 모든 provider 작업은 현재 선언을 다시 검증한다. 로컬 provider 화면을 선택할 때 설정과 스키마를 연다. 엔진 표시 화면을 열고 닫는 작업에는 backend invoke나 authoring 프로세스가 없다.

공통 WebView는 같은 세대의 동시 update를 합친다. invoke acknowledgement 후 결과 조회를 깨워 이미 완료된 작업이 다음 정기 poll까지 기다리는 시간을 줄인다. 작업의 중복 사전 갱신과 연결 표시 작업의 중복 workspace 렌더를 제거했다. expectedRevision, 서버 실행 전·후 scope 검사, CAS와 입력 flush 순서는 유지하며 mutation을 자동 재실행하지 않는다. 퇴역한 세대의 응답은 새 화면에 적용하지 않는다.

연결 메타데이터와 effective 조회는 요청마다 새 Registry와 제한된 파일 reader를 사용한다. stamp 기반 문서 캐시를 이 조회의 근거로 사용하지 않으며 프로젝트·권한·조회 결과를 전역 캐시하지 않는다. 파일당 1MiB, 조회당 16MiB/2048 파일 제한을 적용한다.

provider 설정 창은 소유한 동의·작업을 취소한 뒤 닫힌다. 닫힌 창의 이전 설치·로그인·확인 토큰을 다시 사용할 수 없다는 기존 계약을 유지한다. 이 취소 확인이 필요한 창의 지연은 기본 엔진 표시 화면의 닫기 시간과 구분한다. 연결 진단은 `operationError`로 분리하고 `sourceError`는 비운다. 실패한 설정 읽기는 원본과 미적용 입력을 유지하며 단계와 고정 원인 코드, 복구 후 재시도를 제공한다. 예외의 원문·경로·자격 내용은 public state나 진단 로그에 내보내지 않는다.

Linux 실제 클릭 3회의 DOM 완료 중앙값이다. 실제 화면 합성·Windows 입력 지연은 이 수치에 포함하지 않는다. 첫 실행 샘플과 전체 요청 수는 JSON에 별도로 남긴다. 클릭 중 컴파일 프로세스는 전후 모두 0개다.

| 동작 | 기존 | 수정 | authoring 프로세스 |
|---|---:|---:|---:|
| Agent 열기·provider 활성화 | 1069.7ms | 1.4ms | 1 → 0 |
| Codex 기본 화면 | 3032.6ms | 1.1ms | 첫 5 / 반복 3 → 0 |
| 기본 화면 닫기 | 186.9ms | 0.8ms | 0 → 0 |

측정의 각 샘플과 요청/프로세스 수, 구간별 시간 및 최종 회귀 결과는 [connection-ui-latency.json](validation/connection-ui-latency.json)에 기록한다. 측정은 `strace -f -ttt -e trace=execve`와 브라우저의 실제 click/DOM/fetch 시간을 사용한다. strace와 테스트 실행 부하가 포함되므로 제품의 절대 성능 보장값이 아니다. 정기 update 요청은 클릭이 만든 invoke와 구분해서 센다. 입력값이나 전체 스냅샷을 계측하지 않는다.

재현 명령은 준비된 .NET 10 SDK, Chromium, Playwright, strace를 사용한다. 설치나 계정 설정을 수행하지 않는다.

```sh
dotnet src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack linux > /tmp/editor-home-report.json
python3 tests/probes/connection_ui_latency.py "$PWD" /tmp/editor-home-report.json /tmp/owned-connection-timing
dotnet tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll test_actual_agent_connection_presentation test_web_ui_client_coalescing test_connection_metadata_reads_current_bytes
```

`CONFECTORY_UI_TRACE=1`은 호스트 stderr에 consumer/snapshot/authoring 시간과 예외 타입만 기록한다. 브라우저에서 앱을 읽기 전에 `globalThis.confectoryWebUITrace=[]`를 설정하면 최대 512개 update/call/render 시간 기록을 얻는다. 기본값은 비활성화다. 실제 사용자의 Windows 실행, 계정·설치·마켓플레이스 등록, 실제 ChatGPT 앱 연결은 이 검증에 포함하지 않는다.

이전 단계별 검증에서는 고유 검사 11개가 통과했다. 전체 회귀의 구현은 `0c2b47c`, 독립 history 검사 보완은 `3b35e79`, 연결 진단의 source 분류 분리는 `4207822`다. 마지막 분류 변경 후 실제 클릭·실패·재시도 검사를 다시 통과했다. 각 검사별 실행 커밋과 개발 중 제외한 실패의 해결 근거는 JSON, 통과 목록은 [검증 로그](validation/connection-ui-latency-tests.log)에 있다.

## 동일한 최종 소스의 전체 재검증

HEAD `3d81e54a1ec3e6755a70e76c0cd3ccbb4798451c`를 고정해 위의 11개 검사를 모두 다시 실행했다. 연결 4개와 범위·CAS·체크아웃 7개가 **11 passed, 0 failed, 0 skipped**로 통과했다. 두 그룹의 시작·종료 HEAD와 깨끗한 작업 트리를 확인했다. docs를 제외한 제품·검사 파일은 `42078226bfbcbe8f3984638cf33ff122b6e1aacd`와 동일하다. 제품 변경은 하지 않았다.

이 작업에서는 성능 probe를 재실행하지 않았다. 기존 before/after/instrumentedBaseline 데이터의 SHA-256을 비교해 동일함을 확인했다. 이전 소스 단계별 결과는 JSON의 `stagedValidation`, 이번 동일 HEAD 결과는 `validation`에 분리했다. [전체 재검증 로그](validation/connection-ui-final-head-tests.log)와 JSON에 검사별 HEAD, 시간, 종료 코드 및 보호 파일 확인 결과를 남겼다. 실제 사용자 앱 설치·계정 연결과 Windows 실기 실행은 포함하지 않았다.
