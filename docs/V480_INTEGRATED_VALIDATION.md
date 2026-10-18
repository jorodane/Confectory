# v480 통합 검증: 같은 프로젝트와 최종 기준 소스

이 기록은 좁은 타입 확장 후의 통합 확인이다. [현재 지원 지도](EDITOR_V480_STATUS.md)와 [단일 우선순위 목록](V480_REMAINING_WORK.md)을 함께 읽는다. 전체 v480 완료나 모든 가능한 클릭/실패 조합의 통과를 주장하지 않는다. 과거 62/73 등의 단계별 검사 수를 이번 결과에 더하지 않는다.

## 연결한 사용자 흐름

`WebUITests.test_actual_editor_v480_integrated_home_data_graph_set_ref_run_workspace_and_restart`는 하나의 소유 프로젝트에서 아래를 연속 실행한다. 프로젝트 ID와 source bytes를 단계 사이에서 비교한다. 서로 다른 예제의 성공 로그를 이어 붙인 결과가 아니다.

1. 실제 Home에서 프로젝트를 검색/열고, 선언 metadata를 Apply한다. 같은 브라우저의 Data에서 객체·필드를 명시적으로 선택해 `amount=7`을 Apply한다. Confirm 전 원본이 그대로인지 확인하고 실제 compiler Review/Confirm 후 원본 값과 Home의 확정 편집 receipt를 확인한다.
2. 같은 함수 graph에서 field-ref의 명시적 profile 전환·제한된 catalog·명시 receiver·실제 ref 매개변수·위험한 remap 거부·cold 미적용 입력·그룹 Confirm을 실행한다. 기존 `v480_property_ref.verify_property_ref`를 그대로 재사용한다. 내부 helper의 PASS 출력은 추가 검사 건수가 아니다.
3. 같은 graph에 checked property Set을 넣어 `spawn → Set(31) → field ref → C#`로 연결한다. C#은 실제 ref에서 31을 확인하고 42로 바꿔 반환한다. compiler Confirm 전후에도 사용자 producer가 실행되지 않았음을 파일 counter로 검사한다.
4. Run UI에서 최종 compiler 산출물을 Linux 별도 프로세스로 실행한다. 실행 진입점은 빌드의 실제 `public-linkage.json`에서 확정 Data 7을 읽어 위 graph에 전달한다. producer는 정확히 한 번 입력 7을 받는다. 반환과 같은 인스턴스의 checked Read가 모두 42임을 실제 출력 `INTEGRATED_V480`로 검사한다. 실제 callback loop에서 Pause ack 1, Step ack 2와 정확히 한 frame 증가, 소유 Stop을 확인한다.
5. private Workspace 메모를 저장하고 원본 소스가 바뀌지 않았음을 확인한다. 호스트를 완전히 재시작해 같은 프로젝트·메모·source-ready graph·확정 Data/source bytes·Home receipt가 복원되고 실행 상태가 idle, 실행 handle이 없음도 확인한다. 기록으로 이전 실행 권한을 채택하지 않는다.

테스트는 일반 ButtonGame 프로젝트의 임시 소유 사본에 CELEM/schema/graph fixture를 만들고, 기존 FrameLoop의 실제 협력적 callback loop를 사용한다. FrameControl/RealTimeUpdate 호출 계약을 정확히 연결한 entry와 관측용 body는 테스트 fixture다. 테스트 전용 AppDomain 슬롯은 최종 인스턴스를 검증하기 위한 관측만 담당하며 graph의 receiver는 명시적 producer 결과 pin에서만 온다. 제품의 receiver 추론이나 새 전역 객체 서비스가 아니다. 준비 단계의 CLI build도 사용자 코드를 실행하지 않는다.

## 기준 소스와 결과를 읽는 방법

최종 결과는 [기계 판독 실행 기록](validation/v480-integrated-regression.json)에 실행 메서드·단계·원본 hash·log hash와 함께 기록한다. 구현 기준은 `62d90153b72e648c9639159b38676d2f72d76820`이며 2,751개 입력의 canonical manifest SHA-256은 `f083fb09013215d1b5378ebb4157529b17162c79b243e7a64918820bf9a2383d`다. 제품·테스트·설정의 tracked 파일 및 새 통합 테스트 파일을 모두 고정하며, 변경된 파일만 고정하지 않는다. 문서와 읽기 전용 레퍼런스 ZIP은 별도 보존 검사로 관리한다. 각 gate 전후에 같은 manifest를 다시 확인한다.

통합 시나리오는 하나의 C# test method다. 동일 field-ref helper를 별도로 감싼 `test_actual_editor_v480_field_ref_restricted_catalog_true_parameter_cold_and_confirm`는 이번 최종 선택에서 제외한다. 다른 메서드가 공통 기능을 검사하더라도 고유 메서드 이름은 한 번만 계산한다. 지도에서 같은 검사를 여러 행에 인용해도 추가 건수로 세지 않는다. 초기 실패/재실행은 최종 통과 수와 분리한다.

최종 gate는 graph/compiler/실제 CLR, 소유 모델/실행/편집/권한 fixture, web UI/transport, Linux X11 dummy native, Windows/Android 관리 프로필 compile-only, 구현 커밋의 일반 Git checkout/리소스 시작으로 구분한다. UI/transport 그룹에는 순수 invariant/전송 검사도 있으므로 그룹의 모든 메서드를 Chromium 사용자 시나리오 수로 표시하지 않는다. 체크아웃 gate는 별도 커밋 HEAD에서 일반 checkout을 만들며 LF/CRLF 정책·41개 pinned 리소스·실제 Home 시작과 변조/범위 거부를 검사한다. 리소스 41개와 시작 검사 하나를 별도 테스트 42건으로 세지 않는다.

## 최종 선택 결과

같은 구현 커밋과 2,751개 byte 기준의 최종 21개 gate는 **235 통과·0 실패·0 건너뜀**이다. 최초 동시 부하 시도의 230 통과·5 실패는 아래에 별도로 남긴다. 재검사한 메서드를 추가 건수로 합산하지 않는다.

| 검사 범위 | 고유 메서드 · 최종 통과 |
|---|---:|
| graph/compiler/실제 CLR | 117 |
| 검증된 캐시 동시 게시 | 1 |
| 소유 모델·실행·편집·권한 fixture | 36 |
| web UI/transport/invariant | 75 |
| Linux X11 dummy native | 4 |
| Windows/Android 관리 프로필 compile-only | 1 |
| 일반 Git checkout·리소스 실제 시작 | 1 |
| 합계 | **235** |

## 초기 시나리오 보정

초기 준비/시나리오 실행은 최종 회귀에 합산하지 않는다. semantic-only Review에는 추가 C# acknowledgement가 없으므로 존재하는 경우에만 체크하도록 고쳤다. fixture의 RealTimeUpdate.Advance는 실제 네 double 입력과 명시 provider를 사용하도록 바로잡고, UI 시작 전 실제 CLI build로 진단한다. Run 로그는 닫힌 details 안에 있어 `inner_text()`가 빈 값을 반환하므로 완성된 JSON marker의 `text_content()`를 읽는다. Home의 목록 카드 ID와 실제 열린 프로젝트의 identity가 서로 다른 계약이므로 재시작 비교는 선택된 실제 projectId를 기준으로 보정했다. compiler Confirm/CAS·권한 거부 경계를 느슨하게 바꾸지 않았다. 이후 재현된 추가 실패와 보정은 실행 기록에 남긴다.

## 통합 회귀에서 재현한 제품 수정

기존 `test_actual_editor_and_button_game_common_web_transport_chromium`이 별도 필드 창에서 7을 Apply한 뒤 0을 Apply하고 창을 해제하는 흐름에서 실패했다. 부하 없는 단독 실행에서도 38.644초에 재현됐다. 요청 추적에서 두 Apply가 모두 revision 2/이전 hash를 보냈고, 첫 적용 뒤 실제 초안은 revision 3이었다. CAS는 두 번째 오래된 요청을 올바르게 거부했다.

원인은 schema DOM의 중복 렌더 캐시였다. 첫 Apply의 응답을 기다리는 동안 새 schema를 표시하면서 이전 pending 입력의 revision/hash를 handler에 포획했고, 응답 뒤 pending 입력을 지워도 같은 schema JSON이라는 이유로 그 handler를 재사용했다. 성공한 설명·필드·필드 정의 적용 뒤 `schemaRendered`도 무효화해 다음 렌더가 새 기준의 handler를 만들도록 수정했다. 미적용 입력이나 외부 변경의 CAS 거부는 유지한다. 잠정 busy 버튼 가설은 같은 실패를 해결하지 못해 제거했으며 최종 변경에 포함하지 않는다.

같은 기존 UI 검사는 대기나 거부 조건을 바꾸지 않고 RED/GREEN으로 재실행한다. 진단용 요청/호스트 추적은 최종 소스에서 제거했다. pinned app.js의 canonical LF 길이/hash만 갱신하며 binary 리소스·CSP·Android 설정은 유지한다. 초기 중단 회귀의 부분 결과는 최종 합계에서 제외하고 수정 후 모든 최종 gate를 새 단일 manifest에서 다시 실행한다.

Home 전환 회귀에서는 별도 두 경계도 보정했다. sidebar를 다시 만든 Home 갱신 분기에서 공통 `controls()`를 다시 적용해 비동기 작업 중 새 Agent 버튼이 활성화된 상태로 노출되지 않게 했다. 기존 공통 UI fixture는 프로젝트 카드 바깥 article 대신 실제 `[data-enter]` 버튼을 클릭해 사용자와 같은 활성화 조건을 따르도록 바꿨다. Agent 준비 fixture의 실패 진단도 setup이 없을 때 원래 오류를 가리지 않도록 보정했다. 동작을 자동 재시도하거나 권한/CAS 조건을 바꾸지 않는다.

초기 UI 대조의 75개는 68개 통과·7개 실패·0개 건너뜀으로 끝났으며 나머지 159개를 실행하지 않았다. 이 결과는 최종 합계에서 제외한다. 산출물 동시성 회귀 1개를 추가해 최종 선택은 235개다. 보정 뒤 실패 경계 8개를 우선 같은 소스에서 검사하고, 통과하면 나머지 227개를 서로 겹치지 않는 묶음으로 실행한다. 단계가 나뉘어도 manifest와 실제 실행 메서드는 하나의 최종 결과로 확인한다.

후속 보정은 다음 경계를 지킨다.

- 빈 Home에서는 집계할 카드가 없으므로 불필요한 summary 작업을 시작하지 않는다. 비어 있는 목록의 Agent 진입을 배경 작업이 다시 막지 않게 하며 실제 카드 집계는 바꾸지 않는다.
- Helper 소유 범위 전환 후 view를 다시 읽을 때 일시적 `busy`만 제한적으로 기다린다. 재연결 중 버튼을 막고 입력을 보존하며, 명령·소스 CAS·기존 실행 권한은 재실행하거나 채택하지 않는다.
- 정기 Workspace 체크포인트는 한 snapshot만 저장한다. 기존 `flush()`는 저장 응답 중 생긴 카메라 변경까지 재귀 저장해 한 정기 tick에 두 번 쓸 수 있었다. 명시적 종료/flush는 계속 최신 변경까지 저장하고 정기 tick만 `persist(true)` 한 번으로 제한한다. 기존 inotify 검사의 실제 서로 다른 두 카메라 저장 기록이 RED 근거다.
- fixture는 새 동의 token이 도착한 뒤 체크박스를 조작하고, 잘못된 단독 Review 검사는 실행되지 않은 transport `stale_revision`에만 제한적으로 새 view를 읽는다. consumer/source CAS 실패는 재실행하지 않는다. 성공해야 하는 준비/시작 API의 실제 성공도 확인한다.
- v196 도구 모음의 기존 DOM 구조 비교에서는 v480의 명시적 선언 관계 다시 읽기 버튼 하나만 복제 DOM에서 제외하고, 실제 새 버튼의 표시를 별도로 확인한다. 전체 v196/v480 픽셀 일치를 주장하지 않는다. 현재 ButtonGame 팩 수 기대값은 실제 도달 집합의 FrameControl을 포함한 11개로 바로잡으며 제품 집계를 바꾸지 않는다. 첫 보정 후 하단의 예전 10 기대값 한 곳도 재검사에서 찾아 고쳤고, 해당 6통과/1실패 단계는 최종 합계에서 제외한다.

추가 Home 회귀는 실제 요약 요청을 보류해 진입 버튼을 잡은 뒤 응답을 풀었다. 기존 코드는 통계만 바뀌어도 카드 전체 DOM을 교체해 버튼이 떨어졌고 6.473초에 재현됐다. 통계 부분만 갱신해 버튼·handler를 유지하고, background metadata 읽기는 진입 버튼을 중간에 비활성화하지 않게 했다. 사용자가 시작한 명령은 해당 읽기를 기다린 뒤 새 revision에서 한 번 실행한다. 같은 검사에서 보류 중의 실제 진입 클릭과 이후 저장/Confirm/cold 복원까지 63.422초에 통과했다. 공통 fixture의 탐색 메뉴도 실제 열림/닫힘 상태를 확인해 다음 Review 클릭을 가리지 않게 보정했다. 이 원인 확인 단계도 최종 합계에 더하지 않는다.

app.js와 workspace-host.js 두 text 리소스의 canonical LF 길이/hash만 갱신했다. 나머지 39개 pinned 항목과 binary 원본은 바꾸지 않는다. 진단용 추적이나 실계정/설치는 최종 제품에 추가하지 않는다.

병렬 빌드의 실제 캐시 게시에서도 `Directory not empty`가 재현됐다. 기존 코드는 같은 키의 두 producer가 존재 확인/손상 삭제/rename 사이에서 충돌할 수 있었다. 컴파일 callback은 병렬로 두고 게시 시점의 검증·손상 복구·rename만 키별 FileShare.None lease로 묶었다. 완료 후 hash 검증된 결과만 재사용하며 잠금 파일은 동시 대기자의 inode를 바꾸지 않도록 유지한다. 생성 ABI는 바꾸지 않는다. 정상 최초 게시와 손상 엔트리 복구를 동시에 실행하는 새 회귀는 기존 코드에서 0.155초에 실패하고 수정 후 0.429초에 통과했다. 반복 round는 추가 검사 건수가 아니며 최종 선택에 이 메서드 하나만 추가한다. 이 RED/GREEN과 이전 6통과/1실패 단계는 최종 합계에 더하지 않는다.

원본 설명을 바꾼 뒤 Augment를 여는 흐름도 `stale_revision`으로 실패했다. 조회 요청에만 제한된 재시도를 넣은 단독 실행은 통과했지만 병렬 선행 묶음에서 다시 실패해 해결 근거로 채택하지 않았다. 해당 흐름은 조회 전 `savePresentation` private checkpoint도 실행한다. 이 저장 요청의 expectedRevision만 한 번 오래되게 만들어 실제 transport가 실행 없이 거부하도록 했을 때 같은 증상을 결정적으로 재현했다. 같은 snapshot과 프로젝트 소유 범위를 유지해 이 미실행 저장 거부만 제한적으로 갱신하며, consumer/source CAS 실패나 소스 편집·실행 명령은 재시도하지 않는다. 두 7통과/1실패 단계와 원인 확인 RED/GREEN은 최종 합계에서 제외한다.

추가 공통 fixture 실패는 description Save 뒤의 schema projection이 끝나기 전에 API snapshot을 읽은 경우였다. Save 버튼이 다시 활성화되는 완료 경계까지 기다린 뒤 기존 dirty/schema/CAS assertion을 그대로 실행한다. 진단용 endpoint 기록은 최종 소스에서 제거했으며, 체크포인트의 1회 미실행 거부 주입은 기존 Augment 회귀에 남겨 같은 경계를 검사한다.

## 같은 소스의 부하 시도와 순차 재검사

첫 235개 시도는 **230 통과·5 실패·0 건너뜀**이었다. 4 CPU에서 gate 최대 6개를 동시에 실행했다. graph 하위 dotnet 프로세스의 180/240초 timeout 두 건, native ButtonGame/Engine frame 대기 90초 두 건, Run 닫기 직후 전체 자식 프로세스 0 assertion 한 건을 [첫 부하 기록](validation/v480-integrated-loaded-attempt.log)에 보존한다. 마지막 assertion은 실제 실행 프로세스와 Home metadata 조회의 PID를 구분해 기록하지 않아 원인이 확정되지 않았다.

재검사는 `native`, `ui3`, `graph2`, `graph3`의 **완전한 네 묶음**을 한 번씩 순차 실행해 모두 통과했다. 제품·테스트 2,751개 파일, 구현 커밋과 timeout/assertion을 바꾸지 않았다. 최초 시도의 성공/실패와 재검사를 더하지 않고, 최종 고유 메서드 235개는 각 완성된 최종 gate에서 한 번만 계산한다. 최초 시도의 모든 method outcome과 gate hash도 기계 판독 기록에 별도로 남긴다. 낮은 부하의 성공만으로 최초 실패 원인이나 동시 부하 안정성을 확정하지 않으며 [ENV4](V480_REMAINING_WORK.md)에서 추적한다.

최종 성공 gate와 빌드의 원문은 [검사 로그](validation/v480-integrated-tests.log), 같은 프로젝트의 Run/cold 관측은 [journey JSON](validation/v480-integrated-journey.json)에 연결한다.

## 검증 한계와 현재 필요한 결정

실계정/provider/유료 호출·사용자 PC 설치·Android 실기기/서명 배포·Windows native/접근성은 검사하지 않는다. Linux X11 dummy의 실제 소유 Engine/Button 창과 callback 검사는 해당 장면의 native 근거이며 전체 desktop/device 검증이 아니다. managed profile compile은 장치 실행/설치와 다르다.

새 ABI·제약 field ref·overflow 정책·소스 삭제/참조 치환·영속 실행 권한·CSP 변경·실계정 설치는 추가하지 않았다. main·원본 ZIP·Android 설정을 보존한다. 남은 구현/설계/승인/환경 항목은 우선순위 문서에 분리했으며 **이번 통합 범위를 마치는 데 새 사용자 결정은 없다.**
