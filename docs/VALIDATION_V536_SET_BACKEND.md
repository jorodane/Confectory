# v536 Set backend 계약 첫 묶음

이 단계는 **backend/컴파일·저장 계약**이다. 원본 Set 카드·저장 대상 선택·값/타입 입력·모바일 편집은 아직 연결하지 않았다. 기존 UI 레이아웃/CSS는 변경하지 않는다. 따라서 Set UI 전체, 취소 버튼, 사용자 입력 복원 완료로 보고하지 않는다.

## 변경

- 기존 Set의 `local`, `(value) -> void` 계약은 그대로다. 선택적 `outputLocal`을 가진 Set만 `stored` 출력이 생긴다. 출력은 같은 graph의 같은 타입인 plain local이어야 하며 alias를 출력 저장소로 삼거나 다른 종류의 노드에 이 필드를 넣거나 두 Set이 같은 출력 local을 소유하면 거절한다.
- 값을 한 번 평가한 뒤 대상 local과 출력 local에 대입한다. 대상에 후속 Set을 해도 별도 출력 local의 값은 바뀌지 않는다. 배열/객체는 기존 CLR 참조 identity를 유지하며 임의 deep-copy나 대상 필드의 live getter로 바꾸지 않는다. 출력 local 자체를 이후 쓰기 대상으로 명시적으로 선택하는 것은 별개의 저장소 변경이다.
- `stored`는 타입 있는 노드 출력이며 기존 dominance/availability를 확인한다. 아직 실행하지 않은 Set의 출력을 소비하면 거절한다. 기존 노드 출력 alias·속성 입력 검증에도 같은 출력 계약을 사용한다.
- 같은 소유 root의 `setPlan`은 새 local 선언·Set 대상/출력·값 binding·entry/route·exit·명시적 Set 제거만 한 authorBatch 후보에서 처리한다. 기존 저장소의 타입/초기값과 기존 Set의 출력 식별성/branch region은 바꾸지 않는다. 새로운 target/output은 쓰기 가능한 plain local의 같은 타입이어야 한다.
- 계획의 종류·키·개수/크기를 제한한다. 외부 직접 호출, slot/private path/copy provenance, readonly alias target과 잘못된 타입을 거절한다. 최종 후보의 값/경로 검증이 invalid이면 전체를 폐기한다. 기존 source proof/checkpoint CAS·WriteChecked·receipt 복구를 재사용하며 중간 변경을 live 상태나 원본 파일에 반영하지 않는다. Review/Confirm은 별도다.

## 검증

`dotnet build Confectory.sln -c Release --no-restore`: 성공, 경고/오류0. 최종 생성 엔진 build3도 성공했다. 초기 generated C#의 Count 확장/변수명 충돌은 수정 후 재검증했다.

`LocalBlueprintTests` **7건 통과**(`core2.log`). 기존4건과 새3건을 포함한다. 격리 fixture의 실제 생성 CLR에서 첫 Set 출력과 뒤의 현재 대상 값이 서로 다름, 호출별 새 값, 실행 전 출력 소비 거절, legacy Set이 출력을 자동 취득하지 않음, missing/wrong type/alias/non-Set/중복 출력 소유 계약 거절, 배열 참조 보존을 확인했다. 기존 지역변수/배열/ref 경계도 유지한다. Core 검사는 안전한 fixture CLR을 실행하며 사용자 프로젝트/엔진 Run은 실행하지 않는다.

`tests/web/v536_set_plan.py`: 실제 엔진 API, **렌더러 없음**.

- `backend4.log` exit0 **9건**, `/tmp/confectory-set-plan-gzygjst7/evidence.json`: 직접 호출 차단; 두 Set/저장소/연결/출력 binding의 한 checkpoint 저장; 결과를 사용하지 않은 뒤 receipt 조회/멱등 재시도/프로세스 재시작 복구; 두 번째 Set 실패 시 앞선 이름/값 변경도 미적용; 값 타입 오류; readonly alias target 위조 거절; peer source/checkpoint 변경 차단; 명시적으로 다시 읽은 후 peer 설명 보존 재시도; 실제 compiler Review와 명시적 Confirm에서 graph만 반영.
- `copy-boundary.log` exit0 **2건**, `/tmp/confectory-set-plan-_oio2l_j`: 직접 호출과 graph copySource를 가진 owner 생략 우회를 차단했다. 복사본 편집 성공 검사가 아니다.
- 서버 검사의 입력 계획은 원래 JSON과 동일한지 확인한다. 실제 사용자 UI 입력/취소는 아직 검증하지 않았다. 응답 미사용/receipt 재조회는 실제 네트워크 단절·저장 도중 프로세스 강제 종료 검사가 아니다. 새 저장 내구성 범위로 확대하지 않는다.

중간 fixture는 이미 provide가 있는 함수로 새 기능 준비 API를 호출해 거절됐다. 제공 없는 동일 서명으로 canonical hash만 조회하도록 고쳤다. 제품의 준비/권한 조건을 완화하지 않았다.

## 남은 순서

1. 원본260px Set 카드와 모바일 저장 대상·출력 필드·값 편집을 backend에 연결한다. private 계획과 실제 적용을 구별하고 기존 local/출력 식별성을 보존한다. 새 local+Set+연결을 한 setPlan에 묶고 다른 source/copy 입력과 섞지 않는다. 실제 화면 취소·cold·오류/재시도·늦은 입력·Review/Confirm·충돌 보존을 검증한다.
2. 사용자 답변대로 속성 읽기 작업의 실행 시점 현재 값, 재실행 시 재읽기, 이미 생성된 출력 보존을 연결한다. 기능 전체 최초값 캐시나 live getter/ref로 치환하지 않는다. 읽기→쓰기→다시 읽기 회귀를 별도로 수행한다.
3. `V536_PIN_AND_ATOMIC_NEXT.md`의 정확한 복사본 ABI → 공유 import의 모든 target/body → 동일 owner 선언+copy 원자 Save를 구현한다. 이 계약들은 아직 구현하지 않았으며 이번 Set 계획을 혼합 Save 완료로 부르지 않는다.

원본 ZIP/main/Android 설정·사용자 데이터와 계정은 보존한다. 실제 계정 로그인·토큰·OAuth·유료 호출을 사용하지 않았다. Windows 교차 패키지와 clean checkout 결과는 후속 최종 검증 기록에 구분한다. 실제 Windows exe/WebView2 또는 모바일 기기 통과로 표현하지 않는다.

## 최종 구성 검사

최종 `compile2.log`: solution Release 성공, 경고/오류0. `core2.log`7건과 `build3.json` 생성 엔진에 대한 `backend4.log`9건을 확인했다. Windows 교차 package-final 및 desktop_package probe-final 성공: 선언2305파일/66 UI 리소스, 누락/변조 거절, 다른 cwd, SDK 없는 packaged managed 엔진 웹 기동, 프로필 재사용/override 및 최소 로그인 렌더를 확인했다. 로컬 실행 파일은 `/workspace/artifacts/Confectory-v536-set-backend/Windows-x64/Confectory.exe`다. .NET Desktop Runtime10.0 x64와 Edge WebView2 Runtime이 필요하며 자동 설치하지 않는다.

Core가 변경됐으므로 커밋 후 clean checkout에서는 solution을 다시 컴파일한 다음 생성 엔진·CRLF 일반 pull/fresh LF·66 리소스를 검사한다. 결과는 `/workspace/scratch/v536-set/CHECKPOINT.txt`/`RESULT.json`에 보존한다. 실제 Windows exe/WebView2·모바일 실행 및 Set 카드 조작은 미검증이다.
