# v536 프로젝트 전용 Helper 삭제·복구와 실행/경합 경계

`VALIDATION_V536_HELPER_RETIREMENT.md`의 첫 묶음 다음 단계다. 당시 비활성이었던 project membership Helper 삭제·UI 복구를 이번에 연결했다. HEAD는 `cf2fcaef2788eab256e65f171b42e0579d7b1fbd`, work/current 미게시 작업이며 전체 UI 완료/Windows 게시 결과가 아니다.

## 실제 연결

- 원래의 Helper 설정창 삭제 버튼/중첩 확인창을 재사용한다. global membership Helper의 보관 삭제를 유지하면서 project membership은 **현재 열린 자기 프로젝트에서만** 삭제할 수 있다. 데이터 영구 삭제가 아니다.
- 삭제 계획과 보관 영수증에 projectId와 선택 manifest를 묶고 적용 시 다시 확인한다. 같은 표시 이름 또는 같은 projectId만으로 다른 manifest의 삭제 계획/복구를 재사용하지 못한다. 기존 소유권/프로젝트 문맥·확정 경계는 유지한다.
- Home에는 전역 보관 Helper만 보인다. 프로젝트 전용 보관 Helper는 자기 프로젝트의 기존 ‘도우미 배치’ 후보 타일로 표시한다. 기존 후보 영역을 사용하며 새 상시 패널이나 계약서 화면을 추가하지 않았다.
- 후보 클릭은 정확한 보관 영수증의 Agent 식별자를 읽고 기존 v536 생성/설정 공용 폼을 복구 모드로 연다. 보관 당시 Agent가 등록되어 있으면 먼저 표시하고, 없으면 다른 Agent를 조용히 선택하지 않고 원래 Agent 선택 제어에서 직접 선택해야 한다. 실제 계정/인증을 바꾸거나 자격증명을 복사하지 않는다.
- 복구 모드의 텍스트는 저장된 프로필을 읽기 전용으로 표시하고 ‘복구’에서 현재 선택한 등록 Agent로 명시적 가져오기만 한다. 원본 성격·기억·저장 프로필을 덮어쓰지 않는다. 복구한 Helper는 배치창의 미적용 선택으로 돌아오며 **별도의 배치 적용 전에는 프로젝트 배치/도구권한이 복구되지 않는다.** 취소해도 이미 명시적으로 복구한 Agent assignment는 보존되지만 프로젝트 권한은 생기지 않는다.
- 재배치는 기존 server plan/apply와 프로젝트 사용 범위 검사를 통한다. 새 계정 권한, 다른 프로젝트, 최종 Confirm/프로젝트 실행 권한을 추가하지 않는다. 기존 사용자를 자동 동의로 전환하지 않는다.
- 전용 Helper가 보관되기 전의 manifest 증거가 없는 과거 불완전 project 자료는 자동으로 믿지 않는다. 이 import 경로는 실제 보관 영수증의 helper/project/manifest 일치를 요구하며 불일치·누락은 오류로 남긴다.

## 재현하고 고친 결함

삭제 마지막 정리가 `helperContext`, `aiPreview`, 모든 준비된 전역 preview를 조건 없이 지웠다. 다른 Helper의 입력이 준비된 상태에서 해당하지 않는 Helper를 삭제하는 shipped HelperAgents 본문 검사로 재현했다. `/workspace/scratch/v536-reference/helper-retirement-guards-red.log`, 자료 `/tmp/confectory-helper-guards-rtkk8rtt`에서 실제 assertion 실패(exit134)를 남겼다.

이제 삭제 대상 Helper의 문맥/해당 preview/배치 계획만 정리한다. 다른 Helper의 대기 입력·prepared turn과 preview는 보존한다. 모든 grant를 유지하게 바꾸거나 running/queued 차단을 낮춘 수정이 아니다. 대화/worker는 계획과 적용 양쪽에서 재검사하고, 실제 파일 반영 전 해당 owner 정리와 scoped revoke를 유지한다.

## 실제 엔진·렌더러 결과

`tests/web/v536_project_helper_retirement.py`:

- 최초 `helper-project-ui-1.log`, 세션4018 exit0, `/tmp/confectory-node-contract-engine-l9zkxq5_` 7건.
- **최종** `helper-project-ui-2.log`, 세션17997 exit0, `/tmp/confectory-node-contract-engine-lvc44lf1` **7건 통과**, 마지막 Agent 복구 진입/다른 Helper 문맥 보존 수정 포함.

검증한 실제 경로:

1. 전용 Helper 삭제 취소와 실제 registry 파일 동시 수정의 CAS 실패. 화면 입력·외부 바이트·전체 roster를 보존하고 복구 영수증/부분 삭제를 만들지 않는다.
2. 외부 수정은 덮어써 되돌리지 않고 실제 프로세스를 종료·재시작해 새 저장본을 읽은 뒤 새 명시적 검토/삭제로 성공한다. 같은 삭제 토큰 상태조회/중복 요청은 동일 영수증 확인으로 끝나며 파일을 다시 변경하지 않는다.
3. 기존 프로젝트 후보→원본 공용 설정창의 Agent 표시→복구 취소/복구. 복구만으로 서버 roster/프로젝트 권한을 적용하지 않는다.
4. 별도 배치 적용 후에만 참여하며 모집 템플릿·프로젝트 기억·프로필·다른 Helper/Agent를 보존한다.
5. 프로젝트 밖에서는 전용 보관 Helper를 전역 후보에 노출하지 않고 복구/삭제 요청도 거부한다.
6. 같은 표시 이름의 다른 실제 프로젝트로 cold 시작해도 다른 프로젝트 Helper를 가져오지 못한다.
7. 원래 프로젝트 cold 복원과 600 너비 복구창 취소·inert 정리. 삭제 후에도 선택된 다른 Helper의 실제 공개 profile 문맥을 보존하는 assertion을 포함한다.

전용 모집·기억 및 프로필은 파일 바이트 동일을 검사했다. 실제 프로젝트 원본 전체도 base fixture와 바이트 동일이다. 모든 생성/변경/삭제 주입은 `/tmp/confectory-node-contract-engine-*`의 새 profile/복사 프로젝트에서만 했다. 실제 사용자 Helper/프로젝트를 삭제하지 않았다.

기존 전역 삭제도 `tests/web/v536_helper_retirement.py`, `/workspace/scratch/v536-reference/helper-global-regression-1.log`, 세션5985 exit0, `/tmp/confectory-node-contract-engine-c4fos8vn`에서 **7건 통과**했다. 전역 대화·기억 보존/기존 가져오기 복구/토큰 차단/600 너비 동작을 유지한다. 앞 묶음의 생성·설정6건은 관련 프로필 저장 동작을 변경하지 않아 결과를 보존했다.

두 실제 테스트의 JS 오류/외부 요청은 각각0. Responses 등록은 격리된 빈 credentialReference, loopback 미실행 endpoint이며 모델 시작을 하지 않았다. 실제 사용자 로그인/유료 추론/Codex 공통 grant 생성 테스트가 아니다.

## 실행/대기/경합: 격리 서버 본문 검사

`tests/probes/helper_retirement_guards.py`는 배포 파일 **HelperAgents.csbody 전체를 그대로** C# harness에 넣어 fixture owner/state와 파일, 호출 경계 stub으로 실행한다. 배포 엔진에 테스트 상태 주입 endpoint/우회 권한을 추가하지 않는다. 이 검사는 실제 Windows worker/provider 실행을 재현한 것이 아니다.

최종 `/workspace/scratch/v536-reference/helper-retirement-guards-3.log`, 세션78882 exit0, `/tmp/confectory-helper-guards-xzbrg_qc`, **11건 통과**:

- 실행 중 global owner, project owner, 대기 중 owned worker가 각각 삭제 계획을 차단한다.
- 계획 후 새 작업이 시작되면 적용 직전 다시 거부하며 registry/배치/입력을 보존한다.
- revoke 뒤 filesystem CAS 충돌은 외부 저장본/모든 배치/메모리 assignment를 보존한다. 해당 Helper의 scoped revoke는 실패를 허용으로 바꾸지 않으며 Agent 공통 grant 호출은 없다.
- owner 잠금 도중 대기한 binding은 삭제 적용 뒤 제거된 assignment를 얻지 못한다. 오래된 preview의 후속 start도 거부한다.
- 같은 projectId의 다른 manifest가 삭제 토큰/복구를 재사용하지 못한다.
- 다른 Helper의 context·미저장 preview·prepared turn을 보존한다.
- provider/account/credential/실제 grant 호출0.

실제 UI 파일 CAS 시험은 배포 FileStream 다중 파일 저장 경로다. harness의 CAS/계정 함수는 경계 stub이므로 이 11건을 하드웨어 내구성이나 실제 계정 성공의 증거로 사용하지 않는다. 기존 ChatUse의 selective revoke/tool guard를 우회하지 않았고, 이 작업에서 새로운 내구성 요구를 추가하지 않았다.

## 빌드·원본 화면·남은 범위

최종 생성 Linux 엔진 `helper-project-build-4.log`, 세션91762 exit0. 중간 build3의 nullable CS8602는 보관 Agent metadata의 누락/지원 ID 검증을 명시하여 해결했고 오류 로그를 지우지 않았다. 리소스62/canonical text53의 해시·크기 및 JS/Python 구문·diff check 통과.

최종 실제 `project-helper-delete.png`, `project-helper-restore-600.png`를 열어 원본 공용 폼 배치를 확인했다. 원본 캡처는 `helper-reference/original-settings.png`, `original-delete.png`. 복구/보관 의미의 문구와 자료 유무가 달라 전체 pixel 일치를 주장하지 않는다.

이미지에 관해 추가 확인한 기존 로컬 기능은 Helper 프로필 텍스트/채팅 초안/기억/모집 저장뿐이다. **현재 Helper 이미지 asset·선택·이력 저장 계약이 없어 이를 바로 연결할 기존 로컬 이미지 기능은 확인되지 않았다.** Yogi의 캡처 보관은 다른 자료/동의 범위이며 Helper 이미지로 바꾸지 않았다. 원본 샘플 회전/랜덤 생성을 실제 provider로 꾸미거나 이미지 제공자·유료 호출·계정 권한을 추가하지 않는다. 이미지 생성·선택/이력/재시작의 실제 연결은 고정 미구현으로 남긴다.

현재 Helper 삭제·복구 범위는 위의 global/current-project 보관 및 정상/충돌/실행 차단 묶음으로 닫는다. 모든 종류의 provider 스케줄러·OS 장애 조합을 보장하지 않는다. 다음은 고정 순서대로 전투 로그·신문고/Yogi 실제 계약 감사/연결 → 창별 실행창이다. Browser 일부 Data/참조/정밀 대조, 모바일 Blueprint 특수 계약·나머지 ABI/mixed Save 제한도 전체 수용 목록에 유지한다. 전체 회귀/Windows 교차 패키지/checkout/커밋·push는 아직 미완료다. 실제 Windows/WebView2/네이티브 터치/계정 성공도 미검증이다.
