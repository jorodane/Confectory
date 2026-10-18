# ENV4: 제한된 부하 재현과 수명 측정

최초 다섯 실패 중 **graph timeout 두 건, native Engine ACK 대기, Home 닫기 자식 수 assertion**을 제한된 묶음에서 재현했다. Engine과 자식 수 검사는 기존 계약과 맞지 않는 검사 순서/관측 범위를 보정했다. graph 두 건은 진행 중 전체 wall-time 예산이 끝났으며, 같은 소스·같은 제한에서 gate 수를 6→2로 줄인 대조에서 통과했다. **native ButtonGame의 최초 90초 실패는 재현하지 못했다.** 모든 실패를 환경 원인이라고 결론내리지 않는다.

기준은 게시된 `8ea1471`이다. 계측 전용 코드는 `e73350e`, 검사 보정은 `fd8fabc`에 있다. runtime pack·Core·새 ABI·권한·lease/timeout 정책은 바꾸지 않았다. 수정한 예제는 [두 runtime 검증 client](../examples/project-execution/frame-verify.csbody)이며 제품 서버의 2초 lease는 그대로다. main·원본 ZIP·Android 설정을 유지한다.

## 범위와 조건

- Linux cgroup `cpu.max=400000 100000`(4 CPU), `memory.max=17179869184`(16 GiB / 약 17.18 GB), .NET SDK 10.0.401, Chromium, 소유 Xorg `:97` dummy/TCP 비활성. 기존 표기의 “17 GiB”는 정확히 16 GiB로 바로잡는다.
- 처음 9개, 이후 관련 UI를 이어 붙인 11개 고유 메서드만 사용했다. 235개 전체를 다시 실행하지 않았다. 각 묶음에는 원래의 두 graph, native 4개, Run UI와 property Set/ref 관련 검사가 들어 있다.
- 원래 graph driver 180/240초, native predicate 90초, UI condition/전체 timeout, ACK/frame/CAS assertion을 유지했다. 실패한 gate를 자동 재시도하거나 통과 수에 재실행 건수를 더하지 않는다.
- `/proc`의 PID와 출생 tick, PPID, 실행 파일/assembly 역할, 상태, CPU/RSS/thread를 수집했다. argv 전체·환경·frame pipe secret·웹 session URL은 기록하지 않았다. 프로세스는 0.2초 또는 0.5초, 자원은 1초 간격으로 관측했다. 짧은 프로세스는 놓칠 수 있다.
- 교차 프로세스의 “종료 전 5초” 도구 수는 managed UTC와 Python UTC/monotonic 대응 및 샘플 간격에 따른 근사다. 각 driver의 180/240초와 native predicate 대기는 해당 프로세스의 Stopwatch로 별도 측정했다.
- 관측기 비용은 Python runner 전체 CPU(샘플링·gzip·hash·orchestration 포함)다. cgroup CPU에는 공유 서비스와 이 비용도 포함된다. cgroup task 수에는 thread와 zombie도 포함되며, RSS 합계를 실제 메모리 사용량으로 간주하지 않는다.

[기계 판독 근거](validation/v480-env4-diagnosis.json), [각 시도 원문 로그](validation/v480-env4-attempts.log), [원자료·계측 source·분석기 압축 파일](validation/v480-env4-measurements.tar.gz)을 함께 읽는다. 원래 235개 결과는 [이전 통합 기록](V480_INTEGRATED_VALIDATION.md)의 해당 커밋 증거이며 이번 검사와 합산하지 않는다.

## 재현별 결론

| 최초 실패 | 이번 관측 | 처리·남은 한계 |
|---|---|---|
| graph 생성/제거 driver 180초 | 6-gate 재현에서 180.345초에 timeout. 88개 계측 RPC 완료, 끝의 query는 11.156초 진행 중. 종료 전 5초에도 자식 도구 3개 생성/3개 종료 | 같은 소스 2-gate 대조 103.440초에 전체 검사 통과. 이번 경로는 작업 진행 중 누적 wall-time 예산 소진과 일치. 모든 잠재 race를 배제하는 증거는 아님 |
| graph 함수 참조 driver 240초 | 6-gate 재현에서 240.231초에 timeout. RPC 157개 완료, 끝의 query는 4.202초 진행 중. 마지막 5초에 RPC 3개 완료, 자식 도구 3개 생성/5개 종료 | 같은 소스 2-gate 대조 156.120초에 전체 검사 통과. timeout 증가 없이 동시 gate 2개를 이 환경의 해당 묶음 실행 지침으로 사용 |
| native Engine 90초 | 첫 runtime 준비 뒤 두 번째 준비에 2.317초가 걸림. 이후 첫 owner를 재관측하지 않고 Pause. 대기는 `running process / paused / ACK 0 / not-accepted`로 90초 유지됨 | 2초 lease가 끝난 owner에 명령을 보낸 검사 순서 오류. 같은 owner를 `observe`한 뒤 명시적 Pause를 보내도록 수정. ACK 1, 실제 frame·Step·외부 owner 거부 조건 유지. 보정 후 같은 6-gate native 4개 통과 |
| Home 닫기 전체 자식 0 | 닫기 전 editor 1210366 → Run worker 1215043 → runtime 1215376. 실패 순간 직접 자식은 1215662 `Confectory.ElementAuthoring.dll`; 직전 `homeSummaries` 요청. worker 종료, runtime은 PID 1의 `Z`로 관측 | 전체 host 자식 수를 실행 소유권으로 사용한 관측 오류. 실제 Run PID 출생 식별자를 기억하고 재부모된 활성 Run까지 직접 검사. 새 Run descendant도 금지. 살아 있는 paused Run을 거부하는 음성 대조 추가. metadata 조회는 실행 프로세스가 아님 |
| native ButtonGame 90초 | 세 6-gate 묶음에서 재현하지 못함. 대기의 phase·process state·frame/ACK는 새 계측에 남김 | 최초 기록에는 어느 predicate가 90초를 기다렸는지 없어서 Engine과 같은 원인이라고 단정할 수 없음. cache/실행 순서/스케줄 이력의 영향을 포함한 잔여 불확실성 |

## 자원과 검사 스케줄

동일한 2,754개 source 파일 hash를 가진 6-gate 재현과 2-gate 대조를 비교했다. gate 수 외에 assertion·timeout·대상 11개 메서드는 그대로다. 두 시도는 순차 수행했으므로 cache·공유 compiler·프로세스 시작 순서까지 통제한 실험은 아니다.

| 관측 | 6-gate 재현 | 2-gate 대조 |
|---|---:|---:|
| cgroup 평균 CPU core | 3.788 | 2.170 |
| 제한된 CPU period / 전체 | 2366 / 2849 | 63 / 4600 |
| `throttled_usec` 차이(초) | 156.219 | 1.408 |
| 샘플된 `memory.current` 최고 | 7.632 GB | 5.374 GB |
| OOM kill 차이 | 0 | 0 |
| gate 하위 활성 프로세스 최고(주기 샘플) | 56 | 21 |
| gate 하위 zombie 최고(주기 샘플) | 12 | 12 |
| runner/관측기 평균 core | 0.107 | 0.105 |

`throttled_usec`는 cgroup 누적 카운터 차이다. 이를 한 검사에서 잃은 wall-time으로 환산하거나 과거 다섯 실패의 단일 원인으로 쓰지 않는다. 이 제한된 묶음의 권장 실행은 `--workers 2`이며, `--workers 6`은 실패를 보존하는 재현 조건이다. 기존 일반 테스트 harness는 순차 실행이며 제품 실행 정책은 바꾸지 않았다.

실행 예시는 [bounded runner](../tests/diagnostics/env4_load.py)를 사용한다. 압축 원자료의 `context/xorg.conf`를 풀어 `--xorg-config`에 전달하고, `CONFECTORY_DOTNET`과 `DOTNET_CLI_HOME`을 해당 SDK/쓰기 가능한 임시 위치로 설정한다.

```sh
python3 tests/diagnostics/env4_load.py /tmp/env4-repro --workers 6 --extended-load --xorg-config /tmp/env4-data/context/xorg.conf
python3 tests/diagnostics/env4_load.py /tmp/env4-control --workers 2 --extended-load --xorg-config /tmp/env4-data/context/xorg.conf
```

## 보정 후의 제한된 검사 결과

- 동일 source의 2-gate 대조: 11개 통과·0 실패·0 건너뜀.
- 3초 lease 지연 회귀: native Engine의 ACK 1, 세 번의 정확한 Step, lease/reconnect/소유 Stop 조건 모두 통과.
- 계측 비활성 관련 회귀: 6개 통과·0 실패·0 건너뜀. 실제 native ButtonGame/Engine·협력적 FrameLoop, Run UI, published-revision admission, 캐시 동시 게시를 포함한다.
- 위 검증의 고유 메서드 이름은 **14개**다. 재실행과 3초 시나리오를 더하지 않는다. 이 수는 6-gate에서 graph 두 건까지 모두 통과했다는 뜻이 아니다. 해당 timeout 두 건은 원문과 원자료에 남아 있다.

계측된 native ButtonGame의 최초 ready/pause/Step 대기 최대는 각각 아래와 같다. 원래 실패의 predicate를 알 수 없으므로 성공한 숫자를 과거 90초 실패의 원인 설명으로 쓰지 않는다.

| 묶음 | ready ms | Pause ms | Step ms |
|---|---:|---:|---:|
| parallel-6 | 33879 | 39 | 3 |
| parallel-6-sustained | 2715 | 26 | 52 |
| final-parallel-6 | 32468 | 35 | 16 |
| control-2 | 1478 | 18 | 19 |

## 수명 판정과 잔여 불확실성

활성 실행 종료와 PID 소멸을 구분한다. `Z`는 사용자 코드를 실행하지 않지만 PID slot이 남아 있다. 이번 container에서 worker를 tree-kill한 뒤 runtime zombie가 PID 1 아래 남는 현상을 관측했다. PID 1의 reaping이나 다른 권한을 변경하지 않았으며, 이 자원 잔류를 최초 timeout의 원인으로 확정하지 않는다.

첫 9개 진단에서는 기존 닫기 실패보다 앞에서 Pause ACK가 0인 추가 실패가 한 번 있었다. 당시 요청 결과 코드 계측이 없어 원인을 확정하지 못했고, 이후 결과 코드 계측 시도에서는 같은 실패가 재현되지 않았다. 이 추가 실패를 원래 다섯 실패의 재현 수에 넣거나 삭제하지 않았다.

native ButtonGame의 최초 wait phase, 원래 235개에서의 정확한 cache/프로세스 시작 이력, 모든 부하에서의 race 부재는 미확정이다. Windows native·실기기·실계정 검증으로 확대하지 않는다. 후속 미확정 범위는 [ENV4](V480_REMAINING_WORK.md) 한 항목으로 관리한다. 새 사용자 결정은 필요하지 않다.
