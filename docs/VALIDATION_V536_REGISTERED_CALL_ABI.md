# v536 직접 등록 callable ABI

선행 소유 슬롯(`50f5058`)·모바일 whole-body 수용(`bd0cd5f`) 이후의 별도 구현이다. 고정 잔여 분류는 `V536_REMAINING_BACKEND_MAP.md`를 따른다. 이번에는 기존 backend의 직접 등록 함수 receipt를 ABI 갱신에 연결했다. 전체 v536/모든 ABI 문맥의 완료가 아니다.

## 연결 및 보호

- `BlueprintCallableContracts.Query`의 직접 의존성 함수 선언/manifest receipt를 사용한다. 준비 단계는 provider 본문을 선택하거나 복사하지 않는다. 기존 참조 생성 경로와 같은 읽기 범위이며 새 registry/권한을 만들지 않는다. compiler Confirm의 통상적인 의존성 읽기와는 구별한다.
- 기존 계약 갱신 버튼이 호출 signature·source hash·정확한 등록 receipt를 보관한다. 서버는 owned caller 전체 source proof, checkpoint, 함수/등록 receipt를 적용 전과 checkpoint 결과 확인에서 다시 검사한다. 등록 소스는 쓰기/Review 대상으로 넣지 않는다.
- 단일 소유 root/본문/동일 callee 호출의 값↔ref만 허용한다. 이름·타입·순서·out·반환과 기존 명시적 storage binding을 보존하고 typed import 및 graph를 기존 원자적 단위로 갱신한다. callee 원본을 자동 고치거나 첫 provider를 선택하지 않는다. UI/CSS/레이아웃과 명시 Review/Confirm은 그대로다.
- 실패한 등록 재연결을 새 증거로 재확인하는 경우, 서버가 **원래 checkpoint와 해당 호출의 전체 소유 source closure가 그대로**임을 확인해야 이전 시도를 대체할 수 있다. UI도 같은 callee/owner manifest/서명·본문/helpers/enum/반환 매핑을 보존하는 단일 wrapper 재확인만 허용한다. 다른 source/checkpoint·불확실한 적용 결과·새 코드 입력에는 이 경로를 사용하지 않는다.

## 확인한 결함

등록 변경 때문에 Save가 거절된 뒤 새 계약을 명시적으로 선택해도 이전 author-attempt가 모든 재시도를 막았다. 현재 상태가 원래 기준과 동일하다는 서버 증거 없이 기록을 지우지 않도록 제한된 재확인 경로를 연결했다. 두 번째로 local preview를 다시 열면 `refreshFrom`이 원래 계약이 아닌 미저장 갱신안의 hash로 바뀌었다. 보관 중인 원래 기준을 유지하며, 진짜 원본 변경은 계속 거절한다. 격리 fixture의 실제 원본 hash와 실패 요청을 대조해 재현했다.

## 실행 결과

- `tests/web/v536_registered_call_abi.py`, 최종 `actual5.log` exit0: 실제 엔진/Chromium6건. 근거 `/tmp/confectory-registered-call-abi-fwdqlsro/evidence.json` 및 `registered-abi-confirmed.png`.
- 직접 등록 함수/manifest 확인과 기존 슬롯 진입; 누락/위조 receipt 차단; 같은 함수여도 manifest 변경 시 실제 UI Save 차단·입력 보관; 원래 checkpoint/전체 owned closure 검증과 잘못된 hash/checkpoint 거절; cold 후 새 계약 명시 확인/원래 refreshFrom 유지/원자 Save; Review 취소와 새 compiler Confirm에서 owned Caller 선언·graph만 변경하고 외부 팩/provider·다른 소스를 보존했다. 적용 후의 이전 기준은 재시도 기록 해제 증거로 사용할 수 없음을 확인했다.
- 변경된 batch/settled의 기존 소유 슬롯 회귀8건도 exit0(`/tmp/confectory-slot-call-abi-wnu9vs_m`, build3). 최종 한 줄의 refreshFrom 유지 수정은 위 build4 등록 통합에서 확인했다. 이전 모바일6건을 새 구현 검사로 세지 않는다.
- Linux 생성 build4 exit0, JS/Python 구문 및 diff 검사 통과. 중간 build2의 Count 확장 메서드 이름 오류는 정식 `System.Linq.Enumerable.Count`로 수정했다. 이전 실패/기대 오류 기록을 삭제하지 않았다.
- Windows x64 교차 패키지: `/workspace/artifacts/Confectory-v536-registered-call-abi/Windows-x64/Confectory.exe`, 선언2305파일/66 UI 리소스. `desktop_package.py` exit0(`/tmp/confectory-desktop-package-eau7ohva`): 구성·누락/변조 거절·SDK 없는 패키지 웹 기동·다른 cwd·프로필 재사용/명시 override·최소 로그인 화면을 확인했다. 깨끗한 checkout 결과는 게시 시 별도로 기록한다. .NET Desktop Runtime10.0 x64와 Edge WebView2 Runtime이 필요하며 자동 설치하지 않는다.

## 남은 범위

실제 검사 target은 common, long 값/ref 계약이다. 이미 적용된 결과가 등록 변경 때문에 더 이상 일치하지 않거나 다른 source/checkpoint가 바뀌면 자동 재기준화하지 않는다. 복사본 ABI/import/provenance 결합, 다중 target의 공유 import/모든 body 그룹, 일반 이름/타입/out/반환 재매핑과 특수 핀 전체는 미완료다. 혼합 Save는 속성/스키마+복사 intent의 원자 계약이 먼저 필요하며 차단을 유지한다. 기존 지원 문맥의 선택/삭제/검색/키보드 등 조작 검증은 별도 유한 목록으로 진행할 수 있다.

사용자 프로젝트·계정·자격 증명·유료 추론·프로젝트 Run은 사용하지 않았다. 실제 Windows apphost/WebView2/모바일 기기는 미검증이다. Library discovery의 기존 네트워크 실패에 새 복구 근거가 없어 재시도하지 않았으며 로컬 산출물을 전달 완료로 표현하지 않는다.
