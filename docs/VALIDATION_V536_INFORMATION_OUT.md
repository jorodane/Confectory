# I5-6: 일반 out 이름 변경의 화면 수용

직접 소유 정보 함수의 일반 out 이름 `count → count2`를 기존 v536 상세창에서 바꾸고 callee 내보내기·실제 scoped caller의 출력 연결·공개 metadata를 함께 저장/확정하는 경로를 검증했다. 기존 `01ce248` 실행 코드가 이 동작을 이미 지원하므로 제품 코드·HTML/CSS·권한은 추가 변경하지 않았다. 이번 커밋은 격리 회귀와 지원 범위 문서를 고정한다. 전체 I5-6/v536 완료가 아니다.

## 원본 동작과 보존 계약

저장소 `196c605`의 v536 `openOwnFunctionPopover` / `renderFunctionSignatureEditor`가 기준이다. 기존 outputs 행의 같은 ID를 편집하며 새 팝업이나 제어를 만들지 않는다. 함수/내보내기/code 노드 ID, 기존 C#의 내부 `count` 매개변수와 본문은 유지한다. 공개 함수의 새 out 이름과 caller가 소비하는 출력 이름만 명시적으로 대응한다. 설명 및 일반 입력 이름을 함께 바꾸는 같은 함수 후보도 검증했다.

Fixture는 `(long amount, out long count) -> long`과 `count=amount+1;return amount+2;` 본문, 정보의 직접 provide, 해당 정보 scope에서 `count`를 실제 반환값으로 연결한 caller다. 저장 후 `export.output=count2`, 그 값의 내부 `body/count` 연결, caller의 `invoke/count2` 소비, 기존 C# source와 정확한 64비트 기본값을 확인한다. 공개 snapshot의 `fields`도 `count2`이며 기존 읽기 전용 SourceContext 의미를 유지한다. 프로젝트/외부 공유 권한이 아니다.

기존 C# After가 `context.count`를 읽는 경우에는 자동 문자열 치환하지 않고 전체 거절한다. 연결/구현이 남은 출력 타입 변경·삭제·반환 삭제·ref 역할 변경·잘못된 중복 대응도 원문과 입력을 유지한다. 이름은 현재 native 식별자 문법 범위다. 원본의 한글/공백 표시명을 native ID와 분리하는 어댑터까지 완료했다는 뜻은 아니다.

## 실제 검증

실제 사용자 프로젝트·계정·유료 AI·프로젝트 Run은 사용하지 않았다. 격리 fixture의 실제 엔진/Chromium/compiler Review/Confirm을 사용했다. 실행 결과 숫자나 Windows native 실행을 검증했다고 주장하지 않는다. 물리 source·graph 바인딩·공개 metadata/읽기 전용 계약과 compiler 결과를 확인했다.

| 검사 | 결과 |
|---|---|
| 실제 API normal | 2 PASS. out/공개 이름·callee/caller 전체 후보·cold·compiler Confirm·cold |
| API 쓰기 실패/재시도 | 3 PASS. checkpoint/live 미적용과 원문 보존, 명시 재시도 및 Confirm |
| API 입력/out/설명 혼합 | 2 PASS. 같은 함수의 양쪽 이름·설명만 원자 후보로 저장/확정 |
| API 타입/삭제/반환/ref/중복/식별자 거절 | 1 PASS. 모든 변경 미적용 및 원문/checkpoint 유지 |
| API C# After 보호 | 1 PASS. 기존 공개 이름을 읽는 C#를 추측하지 않고 전체 거절 |
| 실제 화면 | 기본 2, 독립 2, 입력/out 동시 2, 취소 2, 응답·조회 유실/cold 2, 타입 거절→Undo 재시도 3 PASS. 6회 실행, 총 13 check |
| 원본 외형 | style/consumer/runtime CSS 및 제품 코드가 01ce248과 동일. 기존 출력 상세 행 사용 |
| 깨끗한 checkout | 소스 커밋 후 별도 실제 API/화면 재현 기록을 마감 단계에서 갱신 |

API는 5회 실행 9 check다. check 수를 기능 개수나 통과/실패 비율로 해석하지 않는다. 처음 API fixture는 공개 응답의 실제 key인 `fields`를 `published`로 잘못 읽어 멈췄다. 지원 규격에 맞춘 field 이름 검증으로 고친 뒤 저장/확정까지 완주했다. assertion/보호를 제거하지 않았다. 원시 로그와 실패 근거는 `/workspace/scratch/v536-information-out`에 있다.

기본 [화면](evidence/v536-information-out/primary.png), 독립 [화면](evidence/v536-information-out/detached.png), 같은 후보의 양쪽 이름 [화면](evidence/v536-information-out/both.png)을 남겼다. 전체 화면 pixel/native 비교는 아니다.

## 패키지와 후속

앱 실행 코드가 같으므로 이전에 교차 빌드·검사한 Windows x64 PE 패키지를 재사용했다. `/workspace/artifacts/v536-information-out/Windows-x64`에 별도 복사하고 **2330파일 전체 SHA-256**, 현재 실행 source 9개와 Native DLL byte 일치를 확인했다. manifest SHA-256은 `76d88adfb9b228c3fcf4649ee3753cedf7273dc3051ee5231209ad05c1cf8a51`다. 이번 단위에서 재빌드/동일 패키지 기동 검사를 반복하지 않았으며 이전 runtime-only/no-SDK 웹 기동·74리소스·변조/누락 의존성 거절 근거는 `VALIDATION_V536_INFORMATION_FUNCTION_CONTRACTS.md`에 있다.

Windows에서는 `Confectory.exe`가 진입점이다. 실제 Windows apphost/WebView2·모바일 기기·Library 전달은 미검증이다. 로컬 경로를 전달 성공으로 간주하지 않는다. 생성 빌드·프로필·인증·로그는 Git에 넣지 않는다.

남은 출력 타입/추가삭제·반환 편집, C# 명시 source 결합, 복잡한 ref/out·중첩·등록/복사 문맥, 외부 타입/표시명, 여러 함수 동시 후보는 [고정 목록](V536_I5_6_REMAINING.md)에 유지한다. 다음은 입력 추가/삭제 시 각 caller의 명시 값/저장소 remap 결합이다. I6/B2 및 A4~A6/M4/M11/M12와 Helper 작업은 별도 후속이다.
