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
