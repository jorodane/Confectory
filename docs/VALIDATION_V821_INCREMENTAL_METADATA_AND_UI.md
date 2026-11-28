# 저장 전후 정확한 메타데이터 재사용 및 Browser 표시 갱신

기준: `fc3ceb9df49fbfc804df8f70d086e27f98ffc9d5`. Linux 실제 EditorHome/Chromium/.NET SDK 10.0.401. Windows 실기 미검증.

## 구현 범위

- `MixedOwnerCopyEdits`의 일반 단일 루트 long/string/reference data 값 수정에 한해, 같은 요청의 변경 전 Registry가 실제로 관찰한 정확한 원문을 변경 후 Registry에서도 사용한다. 변경 후에 새로 필요한 경로는 직접 읽는다. manifest 및 다른 초안 overlay가 정확히 동일할 때만 공유한다. 양쪽에서 이전과 동일한 전체 graph/schema/object 검증 수행, 후보 Registry/draft/effective cache는 독립한다. 양 단계에서 원문 물리적 재확인은 이전과 동일하게 유지하고, 변경 후 관찰 원문의 링크도 다시 검사한다.
- `ExactDocumentReadMemo`는 같은 경로의 정확한 관찰 UTF-8 bytes에서 파싱한 선언만 최대 2048개/16MiB 보관한다. mutable collections/JSON data/함수 signature는 분리 복사한다. 다른 bytes는 새로 파싱한다. `Registry.Effective`의 opt-in 경로에서도 같은 안전한 구조 복사로 JSON serialize/deserialize roundtrip을 제거한다. 어떤 권한, 최신성, 검증 결과도 캐시하지 않으며 memo는 한 요청에서만 존재한다. 다음 스트림 요청은 다시 현재 물리 원문을 읽는다.
- opt-in Registry의 등록 경로는 같은 검증 pass의 공통 경로 요소만 공유한다. 실제 declaration `Get`의 기존 소유 경로 확인은 변경하지 않는다. 결과 반환 전에 별도의 새로운 pass에서 전체 보관된 locator의 실제 소유 경로를 다시 계산/비교한다. 상한 초과분은 기존 경로로 검증한다. 파일 lease, checkpoint, Review, 최종 CAS 동작에 변경 없음.
- UI: 권위 있는 relation map의 소유 ID→revision index 및 projection ID→row index로 반복 선형 검색을 제거한다. 표시되는 정체성/순서/종류/권한/아이콘/이름/확장 affordance가 동일한 Browser 카드는 revision 변경만으로 DOM을 교체하지 않는다. 실제 열기/드래그/삭제 등은 최신 owner/revision/hash를 이전과 같이 확인하며, 참조 tooltip은 현재 관계 투영을 읽는다. 동일 projection의 tree forest 및 정확한 breadcrumb는 재사용한다. Data 모드와 검색 gate는 기존 경로를 유지한다.
- Browser inventory/저장된 필터 대기는 100ms polling 대신 기존 `whenIdle`/`whenReady` 완료 신호를 사용한다. activation/generation, window, dirty와 실제 필요 여부를 다시 검사한 후 기존 read를 수행한다. 명령 활성화 gate, 외부 변경 재검증, 프로젝트 전환 보호를 생략하지 않는다.

정확히 변경된 5개 JS 리소스의 canonical size/SHA-256 pin을 갱신했다. 변경 전 bundle로 처음 실행 시 기존 pin이 새 리소스를 정상 거절했으며, 새 정확한 pin과 실제 EditorHome 재빌드 후 통과했다. 리소스 검증을 완화하지 않았다.

## 구조적 증거

실제 authoring tool의 40/400 합성 프로젝트(상속, 복합 datum, 참조 및 Unicode 포함). 기준 tool의 응답과 candidate의 전체 응답이 정확히 동일했고, 비최적화 경로와도 기존 결과가 동일했다.

| 객체 | 편집 | 이전 관찰 원문 | 변경 후 원문 재사용 호출 | 새 parse | 변경 후 parse 재사용 |
|---:|---|---:|---:|---:|---:|
| 40 | Count/Note/Target 각각 | 41 | 43 | 41 | 41 |
| 400 | Count/Note/Target 각각 | 401 | 403 | 401 | 401 |

참조/스키마 projection이 이미 관찰된 일부 원문을 다시 요청하므로 원문 호출 재사용 수는 unique declaration 수보다 많다. 원문 최종 물리 재확인은 별도로 수행한다. mtime을 그대로 두고 다른 소유 객체를 잘못된 type으로 바꾸는 경우, unreadable source, namespace 밖 symlink locator 모두 거절되었다. 같은 resident stream의 다음 fresh 요청에서 복원된 정확 원문은 정상 처리됐다(쓰기 없음). Core 회귀: mutable nested collection을 바꿔도 재사용 parse는 독립, bytes 변경은 새 parse, 소유 locator가 달라지면 마지막 검증에서 거절.

실제 400 객체 Browser의 catalogue에서 값 저장 전후 변경된 row 및 변경되지 않은 peer row의 동일 DOM node 유지 검증도 성공했다.

## 초기 실제 400개 주 창 진단

직전 기준 tool 및 구 UI와 동일 창 연속 다섯 번 저장 비교. 첫 memo 후보는 공통 경로 검증 최적화 및 UI 변경 전이다. 아래 결합 후보는 최종 lazy allocation 정리 전의 동일 의미 구현이다.

| 경로 | 파일 확인 | 새 성공 표시 | 명령 준비 | 준비 host consumer | mixedOwnerCopyEdits |
|---|---:|---:|---:|---:|---:|
| 기준 | 1070.2 | 1141.8 | 1610.0 | 347.2 | 124.3 |
| memo 후보 | 1081.6 | 1121.3 | 1417.8 | 329.6 | 109.4 |
| 결합 후보 | 953.2 | 997.3 | 1330.3 | 246.4 | 111.5 |

시간 ms; 실제 file completion 확인은 100ms 파일 polling 포함, 새 성공 표시/명령 준비는 브라우저 실제 click 이후의 새로운 status mutation과 enabled frame. CLI 빌드와 계측을 동시에 실행하지 않았다. 이하 최종 교차와 보호 경로 검증을 별도 기록한다.

## 최종 실제 Chromium 연속 저장 교차

동일 창의 다섯 번 warm 저장 중앙값(ms). `파일`은 원본 확인 polling 포함, 두 UI 값은 실제 browser click에서 측정. 마지막 열은 각 표본의 새 성공 표시 이후 명령 준비까지 차이의 중앙값이다. 정수와 참조도 별도로 실제 다섯 번 원본 값 변경을 했다. 기준 tool/기준 pinned UI와 후보 tool/새 pinned UI를 순차 교차 실행했다. 참조 profile은 strace 없이 비교했으며 별도 trace 검증은 아래 보호 경로에 기록한다.

| 객체 | 창 | 값 종류 | 원본 파일 확인 | 실제 성공 표시 | 실제 명령 준비 | 성공 이후 준비 |
|---:|---|---|---:|---:|---:|---:|
| 40 | 주 | string | 549.4 → 551.7 | 550.4 → 532.8 | 833.2 → 798.6 | 264.9 → 263.5 |
| 40 | 주 | integer | 551.6 → 535.0 | 474.2 → 470.8 | 731.8 → 731.4 | 261.2 → 260.7 |
| 40 | 주 | reference | 555.9 → 537.9 | 522.0 → 470.2 | 798.1 → 733.2 | 261.4 → 263.0 |
| 40 | 독립 | string | 654.5 → 573.1 | 612.4 → 562.9 | 797.3 → 719.4 | 208.9 → 219.9 |
| 40 | 독립 | integer | 641.9 → 559.7 | 570.3 → 503.4 | 784.2 → 712.7 | 213.9 → 129.6 |
| 40 | 독립 | reference | 944.9 → 1039.1 | 1018.1 → 1005.5 | 1241.5 → 1215.2 | 214.9 → 209.7 |
| 400 | 주 | string | 962.9 → 986.2 | 982.8 → 1044.1 | 1482.6 → 1423.8 | 327.2 → 422.5 |
| 400 | 주 | integer | 775.8 → 764.4 | 831.4 → 858.1 | 1152.0 → 1133.5 | 420.4 → 319.0 |
| 400 | 주 | reference | 957.1 → 950.8 | 958.6 → 900.6 | 1294.0 → 1243.2 | 323.1 → 323.3 |
| 400 | 독립 | string | 980.9 → 975.6 | 1069.6 → 1002.1 | 1326.9 → 1232.6 | 237.4 → 233.7 |
| 400 | 독립 | integer | 1063.3 → 1067.7 | 1082.5 → 1091.6 | 1334.2 → 1336.5 | 251.7 → 231.9 |
| 400 | 독립 | reference | 1470.9 → 1490.9 | 1532.9 → 1554.2 | 1781.3 → 1794.0 | 248.4 → 239.8 |

최종 400개 주 창 문자열 준비 consumer 325.5→264.5ms, mixedOwnerCopyEdits 141.1→102.9ms. 별도의 최신 tool + 구 UI만 실행한 분리 표본에서는 준비 201.7ms, mixedOwnerCopyEdits 103.6ms, 파일/성공/준비 866.6/861.4/1279.1ms였다. 최초 기준 표본(347.2/124.3ms)과 다른 UI의 결합 효과를 분리해야 하며 단일 표본을 보장된 개선율로 해석하지 않는다.

## 실제 40/400 × 0/1/8창 복원·검색

각 행 기준→후보 단일 교차 표본(ms), 0창은 편집 대상 없음. 모든 조합 실제 검색까지 통과. 단일 표본 전체 latency 개선으로 주장하지 않는다.

| 객체 | 창 | 경로 | 첫 편집 가능 | 마지막 편집 가능 | 일반 명령 | 실제 검색 |
|---:|---:|---|---:|---:|---:|---:|
| 40 | 0 | warm | — → — | — → — | 161 → 84 | 874 → 700 |
| 40 | 0 | cold | — → — | — → — | 396 → 401 | 1475 → 1498 |
| 40 | 1 | warm | 198 → 239 | 198 → 239 | 364 → 364 | 722 → 703 |
| 40 | 1 | cold | 653 → 683 | 653 → 683 | 653 → 683 | 1192 → 1409 |
| 40 | 8 | warm | 280 → 199 | 280 → 199 | 607 → 584 | 930 → 905 |
| 40 | 8 | cold | 558 → 636 | 771 → 846 | 1035 → 1081 | 1332 → 1412 |
| 400 | 0 | warm | — → — | — → — | 146 → 187 | 1758 → 1494 |
| 400 | 0 | cold | — → — | — → — | 406 → 398 | 2158 → 2082 |
| 400 | 1 | warm | 204 → 194 | 204 → 194 | 365 → 465 | 887 → 840 |
| 400 | 1 | cold | 789 → 800 | 789 → 800 | 788 → 800 | 2117 → 2127 |
| 400 | 8 | warm | 458 → 472 | 458 → 472 | 758 → 746 | 1494 → 1307 |
| 400 | 8 | cold | 646 → 665 | 1227 → 1123 | 1921 → 2186 | 2750 → 2815 |

## 보호 동작 및 구조 회귀

- 실제 40/400개 카드 유지(변경 owner 및 변경되지 않은 peer node identity), 문자열/정수 5회 연속 저장, 독립 미저장 입력 유지, 재시작 값 확인 통과.
- 실제 40/400개 string/integer 경로 `strace` 검증: compiler exec 0, project DLL open 0. 400개는 주 창 문자열/정수 및 독립 창 정수 반복까지 trace로 확인했다. 읽을 수 없는 다른 소유 source 및 외부 물리 owner 변경의 저장 거절과 입력 유지 통과.
- `metadata_read_reuse.py` 최신 tool의 exact baseline/비최적화 응답 동등성 및 물리 변경/권한/소유권 실패. Core의 parse memo 변경/독립성 및 마지막 locator 검증 두 테스트 통과. `reference_preparation_stream`, `authoring_read_stream`, 정확한 128-path optional proof 한계, connection settings transform, 257 frame 두 bounded rotation 및 비정상 worker 회수 테스트 통과. 기존 stream protocol 14/스코프/회수 한계는 그대로다.
- 실제 40/400 × 주/독립 창의 참조 5회 반복 저장은 네 경로 모두 trace에서 picker/저장 compiler/DLL 0/0. 새 참조값으로 명시적 Run exit 0, compiler 7/DLL 84.
- Worker Review 취소/다른 Worker 동시 준비/오래된 token 거절/정확한 새 검토 채택. 400 객체 역참조 거절 및 삭제 취소/확정, 재시작 복구, 동일 namespace 다른 프로젝트 불변, compiler/DLL 0/0.
- 40/400개 8창 외부 schema 갱신+작업 사본 필터, 미저장 입력 유지, map 직접 reload 및 정확한 public metadata token/scope guard. `primary-external-during`, `primary-close-persist`, `stale` 통과. label 검색 및 외부 이름 변경, 계층 focus/scroll, caret, 동일 namespace 서로 다른 프로젝트 격리 통과.
- 실제 400개·8창 trace warm/cold 복원 및 검색 compiler exec 0, 합성 프로젝트 DLL open 0.

분리 warm authoring tool의 실제 400개 exact request 9회 교차(두 process 각각의 첫 2회 제외, long/string/reference 순환, 동일 결과 응답): 기준 191.9/355.6/278.1/181.3/143.9/199.7/91.9/111.4/85.9ms, 후보 152.0/131.7/171.7/209.5/74.8/90.0/65.5/92.0/167.5ms, 중앙값 **181.3→131.7ms**. 브라우저/다른 build와 별도로 순차 실행했다. 준비 RPC에서 검증 결과가 아닌 정확한 원문/parse 재사용의 독립적 개선을 확인했다.

## 저장 이후 UI 구간 분리 및 추가 비교

실제 400개 주 창의 Browser trace를 새 성공 표시부터 처음 enabled frame 사이로 제한하여 추가 5회 warm 저장을 계측했다.

| 조합 | 새 성공 | 명령 준비 | 성공 이후 구간 | update 수 | render 수 | browserDrafts 수 | relationsMap 수 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 기준 tool + 기준 UI | 1018.0 | 1393.8 | 320.2 | 11 | 3 | 2 | 1 |
| 기준 tool + 새 UI | 1040.1 | 1449.0 | 421.5 | 12 | 3 | 2 | 1 |
| 새 tool + 새 UI | 907.6 | 1353.5 | 319.8 | 11 | 3 | 2 | 1 |

상세 trace의 기준/결합 후보 median duration 합계(update 174.9→160.6, render 24.3→22.1, browserDrafts 61.9→87.1, relationsMap 67.9→128.7ms). 겹치는 update/call 비용이므로 독립 구간 합계로 해석하지 않는다. 최초 400개 주 창의 성공 이후 중앙값은 414.9→319.6ms였으나 최종 교차에서는 327.2→422.5ms, 추가 분리에서는 위처럼 사실상 동일했다. **저장 성공 뒤 일반 명령 활성화 자체의 일관된 시간 개선은 확인하지 못했다.** 단, 400개 전체 저장 명령 준비는 반복 교차에서 대부분 개선됐고 UI 표시 구조 변경은 실제 노드 identity로 확인했다. 기존 두 카드 모두 교체(기준 `False False`) → 후보 두 카드 모두 동일 노드. 값 변경 후 유지된 400개 참조 카드의 실제 Hover는 새 관계도의 `Nonzero label`을 표시했고, 원래 reference label을 표시하지 않았다.

복원 느린 표본을 추가로 교차했다. 400개 8창 warm 명령 773→755ms, 검색 1440→1388ms; cold 명령 2150→2072ms, 검색 2870→2654ms. 처음 cold 명령 1921→2186ms의 차이는 재현되지 않았다. 40개 1창 warm 명령 365→347ms, 검색 616→635ms; cold 명령 692→798ms, 검색 1413→1430ms. 40개 1창 cold 명령 준비는 두 교차에서 각각 30/106ms 느렸으므로 이를 개선했다고 말할 수 없다. 전체 복원/검색의 일정한 성능 개선은 미검증이다. 기능 보호는 모두 통과했다.

다음 큰 병목: 실제 저장 성공 뒤 같은 Browser 상태 구간에서 2회의 `browserDrafts`와 1회의 `relationsMap`, 그 사이 약 11회 transport update가 남는다. 향후 같은 authoritative map/draft version에서 Browser status와 관계 변경분을 함께 반환하거나 중간 낡은 상태 조회를 완전한 새 관찰까지 지연하여 실제 요청을 줄이는 별도 구조 실험이 필요하다. 준비 단계도 한 요청 내 중복 read/parse는 제거했으나 다른 저장 요청의 physical freshness 확인은 여전히 전체 새 관찰이다. 정확한 source bytes 확인 후 request 간 declaration parsing만 증분 재사용하는 방식이 다음 후보이며 권한 및 최종 persistence를 재사용하면 안 된다. 일반 편집 수십 ms 목표는 아직 미완료다.

격리 브라우저 실행 59회, 58회 통과, 처음 baseline bundle의 새 리소스 pin 불일치 한 번 실패(정확한 pin 갱신/재빌드 후 모든 최종 실행 통과), 매 실행 소유 자손 잔류 0. 별도 400×8 복원 trace 17,839행 compiler/DLL 0/0. 실제 SDK 빌드 및 tool 회수 과정에서 PID 1 소속으로 이미 종료한 일부 Git/SDK 프로세스는 건드리지 않았다.
