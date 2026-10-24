# v536 고정 잔여와 완료 조건

넓은 혼합 Save의 current-widget 범위와 이후 잔여를 구별한다. 원본 `196c605` v536 레이아웃·좌→우 자연어 Blueprint·기존 명시적 Review/Confirm/CAS·소유권을 유지한다. 아래 미완료는 완료로 세지 않으며 새로운 시각적 분기/반복 모델을 발명하지 않는다.

| 고정 작업 단위 | 현재 기반 / 실제 부족 | 다음 완료 조건 |
| --- | --- | --- |
| 일반 ABI의 이름·순서·타입/out/반환 변경 | 기존 지원 문맥의 명시 mapping을 연결·검증했다(`VALIDATION_V536_GENERAL_ABI.md`). 기존 binding/새 primitive 값·출력 대응만 사용하고 전체 typed graph를 checkpoint 전에 검사한다. | 아래 미지원 교차 문맥은 별도 source closure가 필요하다. bound input/consumed output 제거·임의 cast는 자동 승인하지 않는다. 일반화된 전 문맥 완료로 세지 않는다. |
| 복사/상속/opaque C#·whole-body context·같은 호출 복수 사용·등록 callable의 여러 target | seed/ownership·직접 등록 receipt 및 ordinary2target 그룹 backend가 각각 존재. 전체 문맥을 결합한 계약과 어댑터는 미완료 | 선택 대상의 모든 영향 target/source closure/import/record와 원래 snapshot을 하나의 후보/CAS·검토 그룹에 결부한다. opaque 본문은 자동 재작성하지 않는다. 마지막 target 실패 시 전체 미적용, donor/상속/등록 원본 불변, 취소/cold/명시 Confirm을 확인한다. 단일 문맥 통과로 일반화하지 않는다. |
| 다른 편집과 결합 Save | 현재 owner widget+1~8 new private copy 및 primary 요소의 원자 Save/직접 소유 primitive schema 타입 첫 단위는 연결(`VALIDATION_V536_SCHEMA_SAVE.md`). 직접 소유 root schema 표시 이름/삭제는 후속 단위(`VALIDATION_V536_SCHEMA_MUTATIONS.md`), 복합/중첩 정의·독립 View/raw source 결합, saved-copy ABI+owner, multi-target ABI+copy/owner, Set/property+다른 계획, 다른 provider/raw source 결합은 미지원 | 원본에서 실제 허용한 각 조합의 source closure·공통 baseline·필수 Review 그룹을 먼저 고정한다. 현재 여러 endpoint를 순서 호출하지 않고 한 검증 후보/CAS로 전체 성공/미적용, 실패/응답 유실/충돌/취소/cold 및 입력 보존을 수용한 뒤 차단을 제거한다. |
| 공유/고정 반환 이름·잠정 빈 출력 | 기본 출력 정의/이름 대응 backend는 존재. 해당 모든 UI 문맥은 미수용 | 표시 별칭과 native ABI를 구별하고 원본의 고정 이름 제한을 그대로 적용한다. 원래 연결/정확한 출력 타입을 유지하며 desktop/mobile 같은 초안의 편집/취소/Save/cold/Confirm을 확인한다. 원본에서 잠정 UI만인 항목은 compiler 지원으로 주장하지 않는다. |
| 영역/다중 선택·특수/readonly 핀 | 일부 selection/핀 backend와 enum/Set/property의 한정 연결은 존재. 카드/선택 문맥의 전수 대응은 미수용 | 원본에 실제 있는 선택·이동·연결/삭제 동작을 유한 목록으로 대조한다. readonly/다른 owner는 계속 차단하고 관계없는 노드/입력/실행 경로를 보존한다. 가능한 browser pointer/keyboard 회귀와 실제 기기 미검증을 분리한다. |
| 내부 흐름/async 특수 문맥 | 기존 데이터/실행 계약 일부가 있으나 모든 원본 문맥을 결합하지 않았다 | 원본 소스·변경 설명과 현재 backend가 같은 의미인 경로만 연결한다. 불명확/없는 runtime은 backend 미지원으로 남긴다. 새 시각적 분기/루프 또는 가짜 성공은 추가하지 않는다. |
| 최종 조작·화면 수용 | 각 묶음의 선택/삭제/검색/줌/IME/폭 전환 검사는 부분 완료 | 남은 연결 문맥의 줌/검색/키보드·노드/핀 선택·삭제·밀집 rail·한글 IME·desktop/mobile 폭 전환·창/프로젝트 전환을 원본과 대조한다. 미저장 입력/소스/소유권을 유지하고 취소/Save/cold/Confirm 영향 경로를 검사한다. 전체 pixel equality나 native 기기 검증으로 확대 주장하지 않는다. |

이번 넓은 혼합 Save는 CSS/HTML/크기/컨트롤 배치를 바꾸지 않는다. 실제 fixture는 두 copy(Blueprint+wrapper와 C# 본문)를 사용했고 8copy/모든 타입·모바일 터치 전수 검증은 아니다. 임시 Save는 전체 draft를 보관하며 C# 검증은 명시적 Confirm에서 수행한다.

이미지 제공자/자산·이력, 협의·승자·공유 Confirm, 실행창 내장 렌더/FPS backend는 이 UI 복원 묶음에서 구현하지 않는다. Browser의 모든 source 범용 이동·외부 runtime Data·작업자 배지와 플랫폼 native 수용도 현황표의 제한을 유지한다. 실제 Windows/Android/터치·DPI는 미수용이다. UI 완료 후 Helper 에디터 도구 누락 감사는 별도 후속이며 기존 계정/동의가 Confirm·프로젝트 실행·다른 프로젝트 접근 권한으로 확대되지 않는다.

후속 독립 properties View의 설명/기존 값/owner 후보는 `VALIDATION_V536_VIEW_SAVE.md`의 창별 한 후보/CAS·receipt/취소·프로젝트 전환 경계로 연결했다. 앞 표의 독립 View 미완료 중 해당 범위만 해제하며, 복합/중첩 **정의**와 raw source/다른 계획 결합은 남아 있다. 원본의 재사용 정보 정의·기본값과 기존 inline compound를 구별해야 하므로 임의 새 타입/버튼을 추가하지 않는다.
