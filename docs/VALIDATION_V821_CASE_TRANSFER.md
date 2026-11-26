# v821 같은 switch의 case 사이 동작 이동

기준은 `2d8b0c6273ea92373e9a8dcfaef800daa65d854b`이며 제품 소스는 `f092fec4fcc6bb23370751a6945bdc376cb085e5`이다. 제품 파일이 동일한 `87572a9d6c710bb82d7fb3f14c1a6e484f03cd59`에서 수정된 테스트와 패키지를 검증했다.

논리 코드 보기에서 일반 동작 셀의 손잡이를 같은 switch의 상대 case 탭에 놓으면 그 case의 끝으로 이동한다. 탭 아래에 놓을 위치가 표시되며 Escape로 취소할 수 있다. 같은 case 안의 드래그와 기존 순서 버튼·키보드가 유지된다. 대상은 직접 소유한 기존 root 그래프의 서로 독립적인 명시적 case 두 개다. 값 입력·출력·바인딩이 없는 일반 void 동작만 옮길 수 있으며, 대상 case가 기존 종료점에 바로 연결된 형태도 지원한다.

엔진은 원본에서 각 case에 속한 전체 사슬과 종료점을 다시 읽고 두 사슬을 하나의 후보로 검증한다. 옮긴 동작과 나머지 셀의 ID·원문·바인딩, 두 case의 종료점, switch의 원래 계속점을 보존한다. 편집기는 개인 Undo 한 건과 기존 공유 checkpoint·Review/Confirm 경로를 사용한다. 소스 관측과 CAS는 작성 후보의 checkpoint에서 최종 원본 반영까지 적용된다. 값 연결, 공유 진입, 로컬 저장소, 다른 소유자·frame, 암시적 case, 읽기 전용 원본은 이 경로의 대상에서 제외한다. 기존 저장 형식과 실행 규칙을 사용한다.

## 고정 소스 검증

독립 LF checkout의 제품 검증 19개를 충족했다. 첫 실행에서 통과한 UI 6개의 제품과 해당 단언·헬퍼·의존성이 동일함을 확인해 결과를 재사용했다. 나머지 13개는 테스트 수정 커밋에서 새로 실행했다. 첫 실행에서 실패한 검사는 재사용하지 않았다.

| 단계 | 실제 검증 |
| --- | --- |
| 1–6 | 독립 checkout, 의존성 복원, Release·MCP·Linux 앱 빌드 |
| 7–11 | 첫 실행에서 통과한 일반 및 빈 대상 case 이동과 값 연결·공유 진입·읽기 전용 거절 |
| 12–13 | 기존 일반 셀 드래그와 저장·실행은 첫 실행 결과. 같은 case 드래그는 값 연결 fixture를 고쳐 다시 실행 |
| 14–16 | Windows x64 교차 패키지 생성·구성 검사, 패키지 앱에서 Linux 정상 사례 실행 |
| 17–19 | 패키지 전체 복원, 복원본의 읽기 전용·네이티브 편집 회귀, 패키지 실패 시 기존 세대 보존 |

고정 실행 증거는 `/workspace/artifacts/v536-verification-managed/runs/85dc1e1f7cb64cdaa990e6114914d2e2.zip`에 보관했다. SHA-256은 `4a71a8dd80cfbe8c48cbe18cb1f52d6c6da55cb42b66c11fd8369ccf9f80c215`이다.

첫 실행 증거는 `/workspace/artifacts/v536-verification-managed/runs/7bdd69a576234b6b87416546be8cc912.zip`에 보관했다. SHA-256은 `02483bffb55eba938fc8f0134ceee4c86d3498531733a2444b4fb467b669885a`이다.

- 새 패키지 `87572a9d6c710bb82d7fb3f14c1a6e484f03cd59`, 54,282,337바이트, SHA-256 `3daff93d64e01c3cc282ada4bb12633a735bb13e7806e58b6aa21243ebd5d093`
- 복구용 이전 패키지 `d7f1abbff5d0a92da4498f9775190a0b42e1b4cb`, 54,264,465바이트, SHA-256 `4a485cb7cd0f232039cefeb2ae83a3c30926b792563a57c2de47fd7929fe6ff5`

전체 복원에서 파일 2,761개와 디렉터리 158개를 대조했다.

실제 Linux Chromium의 마우스로 탭 양방향 이동, 배치 표시와 Escape를 확인했다. 빈 case로의 이동, 저장 전 재진입, 개인·공유 Undo/Redo, 체크포인트 쓰기 거절 및 재시도, Review 취소, Confirm 시 관측 중인 C# 원문 수정의 거절과 재검토 후 적용을 격리 프로젝트에서 검사했다.

이동 전후에 실제 코드를 컴파일하고 동일한 두 입력을 실행했다. 양수 7의 반환값은 10, 음수 -2의 반환값은 41, 전체 종료값은 51이었다. 옮긴 동작의 로그만 양수 경로에서 음수 경로로 바뀌었다. 최종 graph에서 바뀐 것은 두 case의 실행 연결뿐이며, 나머지 graph 데이터와 모든 C# 원본·다른 파일의 바이트와 모드가 유지됐다.

개발 중 Chromium의 드래그 테스트 입력과 Review의 원본 관측 범위를 수정했다. 개발 기록은 `/workspace/artifacts/v536-verification-managed/runs/bb28b49de629465493165875566207ed.zip`에 보관했다. SHA-256은 `1faee9159e2e66c128c991560fe5da701371623b5c5bbc37aa284a160914d45e`이다.

실제 Windows/WebView2, 모바일, 물리 기기, 전체 UI, 신규 CRLF checkout과 v821 원본 목업의 직접 시각 대조는 미검증이다. Windows x64 패키지에 들어 있는 앱은 Linux에서 실행했다. 과거 초기화 빈 화면의 원인은 미확정이다.

## 직접 소유한 복합 내부 case 사이 이동

`d18b860` 이후의 기존 내부 case 순서 편집 경로를 확장한다. 같은 직접 소유 switch frame의 명시적 case 사이에서 값 의존성이 없는 일반 void 동작 한 개를 상대 case 탭 끝으로 옮긴다. 마지막 동작을 이동해 원래 case가 명시적 빈 case가 되는 형태도 기존 실행 의미로 처리한다. frame 경계를 넘는 이동, 값 연결이 있는 셀 및 임의 위치 교차 삽입은 별개 기능이다. 원본 연결 및 정확한 root/frame/source 관측을 기존 authorBatch, history 및 Review/Confirm에서 요구한다.

경량 Linux 에디터 빌드의 실행 경로를 포함한 report JSON과 동일 checkout을 사용한다. 기존 element-authoring 및 project-execution-host Release 빌드 경로를 각 환경 변수에 지정한 뒤 실행한다.

```sh
python tests/web/v821_child_case_transfer_ui.py "$REPO" "$REPORT" normal
python tests/web/v821_child_case_transfer_ui.py "$REPO" "$REPORT" single
```

`baseline`은 이동 지원이 없던 이전 빌드 전용 재현 모드다. 새 빌드에서 성공을 기대하는 검사는 아니다.

실제 Chromium에서 이전 빌드의 `baseline`, 확장 빌드 `normal` 및 `single` 모두 종료 코드 0을 확인했다. 값 의존 동작의 이동 거절, Escape, 개인/공유 Undo/Redo, 재시작, 동일 로컬 ID를 가진 별개 frame/프로젝트 격리, Save/Confirm 시 sibling 원본 변경 거절, Review 취소 및 재검토 뒤 실제 실행을 검사했다. 확정된 graph는 두 case 연결만 변경하고 다른 원본 파일을 바이트 단위로 보존했다. Linux 빌드 검증이며 Windows 실기 검증은 아니다.

## 프로젝트별 Blueprint 읽기 프로세스 재사용

`8a60ed03ee220d644a4715adaec1c0b5f270f478` 대비 같은 합성 `after` fixture를 실제 Linux Chromium과 동일 경량 빌드 구성에서 비교했다. 프로젝트에 묶인 기존 SchemaEditing 스트림의 프로토콜 4가 Blueprint 조회 및 값 기반 구조 검사, 원본 검증, Review 요약을 받아들인다. 프레이밍용 프로젝트 식별자는 실제 workspace에서 가져와 도메인 검사 전에 제거한다. 결과나 프로젝트 원본을 캐시하지 않는다. 기존 원본·초안·권한·충돌 검사와 컴파일을 유지하고 다른 프로젝트는 기존 스트림을 재사용하지 않는다. 이전 프로토콜과 명시적 취소 scope는 정상 one-shot 요청을 유지한다.

| 실제 UI fixture 계측 (ms) | 기준 | 후보 |
| --- | ---: | ---: |
| 첫 호스트 문서 조회 | 2207 | 413 |
| 전체 동일 조회 9건 중앙값 | 1830 | 82 |
| 셀 추가 클릭 → 새 셀 표시 | 151 | 196 |
| 셀 추가 클릭 → idle | 239 | 227 |
| 코드 창 클릭 → 입력 가능 | 76 | 85 |
| 실제 키보드 입력 | 6 | 10 |
| 외부 변경으로 저장 거절 → idle | 4627 | 1003 |
| 성공 Save의 authorBatch submit → 결과 | 17285 | 3382 |
| 성공 Save 클릭 → 후속 상태 확인 및 idle | 27200 | 5508 |
| 첫 Review 요청 → 결과 | 2316 | 1014 |
| 최종 Confirm 요청 → 결과 | 9002 | 8696 |

같은 실제 화면의 단일 저장 비교로, 새 셀/코드 입력 반응은 두 조건에서 비슷했다. 조회 9건은 각 시나리오 안의 반복이며 독립 프로필 9회 실행은 아니다. 성공 Save 전후의 `settledAuthorBatch` 확인까지 포함하여 화면의 처리 완료와 실제 Save 요청을 구분했다. 최종 Confirm의 8583ms 호스트 처리 중 기존 `validate` 컴파일 검증이 6745ms였다. 이를 생략하지 않았다.

실제 Chromium에서 기존 비어 있지 않은 case 삽입, 로컬 Undo/Redo, 재시작 미저장 입력, 외부 변경으로 Save/Confirm 거절, 정상 Confirm·실제 실행 및 재열기를 통과했다. 별도 case 이동 UI에서 동일 ID 다른 프로젝트 거절, 원본 보존, 공유 Undo/Redo, 실행을 검사했고 직접 속성 저장 UI의 별도 창 입력·IME·외부 충돌 및 기존 초안 Review 경계를 통과했다. `authoring_read_stream.py`는 프로토콜, 외부 변경, 스코프 격리 및 허용 operation을 검사한다. Windows 실기와 모바일/WASM 내보내기는 검증하지 않았다.

```sh
python tests/web/authoring_read_stream.py
CONFECTORY_UI_TRACE=1 python tests/web/v821_child_case_insert_ui.py "$REPO" "$REPORT" after
python tests/web/v821_child_case_transfer_ui.py "$REPO" "$REPORT" normal
python tests/web/v821_direct_property_save_ui.py "$REPO" "$REPORT"
```

실제 브라우저를 실행할 수 없는 환경에서는 별도 호스트 전용 확인을 사용할 수 있다. 이 결과는 포인터·렌더링·입력 반응을 검증하지 않는다.

```sh
python tests/web/v821_child_case_insert_host_perf.py "$REPO" "$REPORT" after
python tests/web/v821_child_case_transfer_host.py "$REPO" "$REPORT" normal
```

## 저장 확인/Confirm 관측 검사 후속 개선

기준 `73962cf5bbdb5166e32ae4084a175a3f28994db3`, 동일한 실제 Chromium `after` fixture 비교. 격리된 `author-batch`의 기존 선언 검사에 프로젝트 범위를 전달해 원래 판정과 CAS를 유지한다. 직접 소유한 frame의 성공 저장 확인은 선택적으로 검증한 projection을 반환한다. 원본 읽기·저장 receipt·정확한 프로젝트/그래프/체크포인트를 대조하고 projection 뒤 물리 원본과 체크포인트를 다시 검사한다. 이전 클라이언트, slot/copy 등 그 외 경로는 기존 재조회와 정착 검사 동작을 유지한다. 프로토콜 5는 기존 정보 body/property/type **검사**만 프로젝트에 묶인 authoring subprocess에서 실행한다. 준비/변경 작업과 컴파일은 이 스트림에 포함하지 않는다.

| 같은 UI 흐름 (ms) | 기준 | 후속 후보 |
| --- | ---: | ---: |
| 셀 추가 → 표시 | 186 | 185 |
| 코드 창 → 입력 가능 | 64 | 76 |
| 실제 키보드 입력 | 7 | 5 |
| 성공 authorBatch 요청 → 결과 | 2469 | 1087 |
| 성공 Save 클릭 → idle | 4326 | 2880 |
| 첫 Review 요청 → 결과 | 851 | 245 |
| 최종 Confirm 요청 → 결과 | 8254 | 6650 |
| 최종 Confirm의 컴파일 검증 호출 | 6426 | 6123 |

이는 독립 실제 UI 실행의 단일 전후 비교이며 Windows 시간이나 반복 실행의 통계적 추정이 아니다. 같은 Save 요청의 선언 검사 17건은 총 1506→206ms, 최종 Confirm의 body/property/type guard 13건은 총 1404→147ms였다. 모든 검사 호출을 유지했다. Confirm은 구조 확인, 소유 구현 전체 컴파일 및 실제 소비자 링크를 여전히 실행한다.

임시 타깃 세부 계측의 기준은 Builder 초기화 457ms, 구조 확인 39ms, 소유 구현 확인 2632ms, 소비자 링크 3198ms였다. 별도 SDK shared compiler 시험은 시간 초과했고 채택하지 않았다. 검증 한 건의 타깃 프로세스를 재사용하는 후보는 정상 아티팩트 동등성, 잘못된 코드 거절, 변경된 도구 설정의 거절을 확인했지만 정확한 파일 증명이 들어간 최종 실행의 컴파일 검증 6272ms/Confirm 8051ms로 이점이 작아 제품 변경에는 포함하지 않았다. 따라서 남은 약 6초 CPU/컴파일 처리 개선은 별개다.

추가 호스트 회귀: `v821_child_case_transfer_host.py`는 정착 projection과 일반 최신 조회 일치 및 저장 이후 외부 원본 변경 거절을 검사한다. `v821_child_case_insert_host_perf.py`의 `after invalid`는 실제 compiler의 CS0103 오류와 원본·체크포인트 보존을 검증한다.

```sh
CONFECTORY_UI_TRACE=1 python tests/web/v821_child_case_insert_ui.py "$REPO" "$REPORT" after
python tests/web/v821_child_case_transfer_host.py "$REPO" "$REPORT" normal
python tests/web/v821_child_case_insert_host_perf.py "$REPO" "$REPORT" after invalid
python tests/web/authoring_read_stream.py
```
