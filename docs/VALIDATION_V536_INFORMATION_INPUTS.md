# v536 I5-6: 정보 함수 입력 추가·삭제의 명시적 호출 대응

직접 소유한 정보 함수 하나의 일반 Blueprint 입력을 추가할 때, 각 호출에 전달할 값을 사용자가 선택한 뒤 함수·구현·호출자·typed import·graph/record를 기존 단일 후보와 checkpoint CAS에 넣는다. 새 값은 추정하지 않는다. 삭제는 callee graph에서 사용하지 않는 입력에 한해 기존 caller 연결을 명시적으로 해제한다. C# 본문이나 복잡한 ref/out을 자동 재작성하지 않는다. I5-6 전체 완료 문서가 아니다.

## 기존 UI와 저장 경계

원본 정보 상세창의 입력 추가/삭제와 기존 `호출 계약 갱신` 선택창을 연결했다. 기존 값/저장소 대응 또는 직접 값을 선택하며, 직접 값은 `valueJson` 문자열로 보관해 64비트 숫자 원문을 유지한다. 각 호출에서 기존 바인딩 하나를 새 입력 하나로 옮길 수 있고, 같은 바인딩을 조용히 복제하지 않는다. 삭제할 입력의 기존 연결은 별도 선택으로 확인한다. 구현 본문에서 그 입력을 여전히 사용하면 전체 저장을 거절한다. 화면 배치·CSS·계정/Agent/실행/Confirm 권한은 변경하지 않았다.

`readOwnerEdits.includeFunctionInputs`는 현재 정보의 직접 소유 함수인지 서버에서 확인하고, 읽기 전용 호출/target 목록과 원래 graph 해시를 반환한다. 클라이언트가 임의 units나 프로젝트 권한을 지정하는 API는 추가하지 않았다. 저장할 때 서버가 원래 함수의 `before/args`와 선택한 호출의 graph/node/hash, 정확한 입력/해제 대응을 모두 검사한다. 빠진 호출, 오래된 graph, 잘못된 타입/모드, 사용 중인 callee 입력, 알 수 없는 호출/해제, 남은 연결은 전체 미적용이다. 원본 파일/전체 closure 검증과 저장 직전 CAS, 응답 receipt 확인, 기존 Review/Confirm은 유지한다.

원래 입력의 해제 증거는 JSON 문자열로 보관하고 서버의 원래 바인딩과 대조한다. 숫자를 JavaScript Number로 되읽어 반올림한 뒤 저장하지 않는다. raw C#/wrapper, 중첩, 전체 본문/forwarded storage는 기존 명시적 편집 경계 없이 허용하지 않는다.

## 발견 및 수정

재사용한 선택창에서 출력 연결을 `없음`으로 바꿔도 새 입력 어댑터가 그 선택을 무시하던 화면 결함을 집중 fixture로 재현했다. 입력 대응 단위에서 유지해야 하는 원래 출력 대응과 모순되는 선택을 거절하도록 고쳤다. 출력 이름 대응은 상세창의 원래 핀 ID 대응에서 가져오며, 모호한 출력 변환을 추정하지 않는다.

초기 검사는 리소스 identity 갱신 전 strict canonical size 검사에서 중단됐다. 변경된 두 JS의 실제 canonical size/hash를 갱신했으며 검사를 완화하지 않았다. 삭제 fixture는 새 root 계약 해시의 조회 출처/검증 순서를 잘못 사용해 두 번 준비에 실패했다. 올바른 root 해시를 구성한 뒤 기존 code 노드 정의를 조회하도록 fixture만 수정했고, 이후 실제 삭제 저장/컴파일 경로를 완주했다. 최초 loss UI의 검증은 통과했으나 fixture 종료 때 Playwright pending 경고가 남아 종료 정리를 보완했다.

## 현재 검증 기록

실제 격리 엔진/API/Chromium/compiler를 사용한다. 사용자 프로젝트, 실제 로그인·유료 추론·프로젝트 Run은 사용하지 않는다. 상세 실행 근거는 `/workspace/scratch/v536-information-inputs`에 보존한다. 아래 숫자는 각 시나리오의 check 수다. 아래는 원래 작업 트리에서 확인한 결과다. checkout/패키지 결과는 별도로 구분한다.

- Native SDK 컴파일: 경고/오류 0. 최종 Linux engine-5: stderr 0.
- API: 새 명시 값 3, 미사용 입력 삭제/연결 해제 3, 두 호출 동시 후보 3, 실제 동시 초안 충돌 2, 기존 caller 저장소 재대응 3 PASS. 미선택/잘못된 값/원본 해시/사용 중인 callee 입력 삭제 거절과 물리 원문·기존 초안 보존 포함.
- 실제 UI: 기본 창 입력 추가 2, 독립 창 입력 삭제 2, 독립 창 저장 실패/재시도 3, 저장·조회 응답 유실/cold receipt 복구 2, 독립 창 기존 저장소 대응 2 PASS. Undo/Redo, 선택 취소, 미저장/저장/cold, Review 취소·명시적 compiler Confirm 포함.
- 최종 출력 선택 수정 후 기본 창 실제 UI 3 PASS(모순된 출력 선택 거절·Undo/저장/cold·compiler Confirm). 같은 namespace/ID의 다른 프로젝트 전환·오래된 form 제출은 추가 UI 2 PASS. 원래 작업 트리 UI 합계 16 check.
- 기존 회귀: Native 계약 7, 일반 ABI 순수 어댑터 3, 실제 out 이름 변경 API/컴파일 2 PASS.

[기본 창](evidence/v536-information-inputs/primary.png)과 [독립 창 삭제](evidence/v536-information-inputs/detached-delete.png), [640×500 기존 선택창 스크롤](evidence/v536-information-inputs/picker-small.png)을 확인했다. CSS의 baseline byte 일치는 `layout-evidence.json`에 기록했다. 전체 화면 pixel 일치나 native 기기 검증이라는 뜻은 아니다.

## checkout·패키지

소스 커밋 `df9b3d2f1723cbfdc0eceaa152aa1083536b4844`의 깨끗한 checkout에서 Native SDK 컴파일과 Linux 엔진 재생성은 경고/오류/stderr 0으로 통과했다. 새 API의 두 호출 동시 후보·거절 보호·cold·compiler Confirm 3 check도 통과했다. 같은 checkout의 독립 창에서 명시 값 선택·Undo/Redo·cold 입력 복원과 저장/조회 응답 유실 뒤 receipt 확인 2 check도 통과했다. 중복 apply 없이 보관 후보를 복원했고 stderr는 비어 있다. 전체 solution/full suite를 반복했다는 뜻은 아니다.

기존 등록 callable 일반 ABI의 실제 선택창·명시 대응·취소·raw 입력/cold·저장·Review/Confirm 4 check를 추가 확인했다. 실제 Git CRLF pull/fresh LF 74개 리소스와 내용/인코딩/BOM/binary/budget 거절도 통과했다.

최종 Windows x64 교차 패키지는 `/workspace/artifacts/v536-information-inputs/Windows-x64`의 2,330개 파일이며 진입점은 `Confectory.exe`다. manifest SHA-256은 `e44803e0ea202d27f4913cd05b2f445be098c83ef5b7a78466b5eb61c54b630a`다. 바뀐 실행 source 6개와 Native DLL의 byte 일치를 대조했다. SDK 없는 별도 런타임, 다른 cwd에서 실제 패키지 웹 엔진 기동·74개 리소스·최소 연결창 렌더·변조/누락 의존성 거절·격리된 기존 profile 재사용을 확인했다. 테스트/프로필/로그는 패키지 manifest에 없다. 생성 패키지·프로필·로그·인증 자료는 Git에 포함하지 않는다. 실제 Windows apphost/WebView2 실행이나 Library 첨부 전달을 뜻하지 않는다.

## 지원과 잔여

검증된 범위는 일반 `long` 새 입력의 명시 값/기존 바인딩 선택과 구현이 사용하지 않는 `long` 입력의 명시적 caller 연결 해제다. UI의 기본형 직접 값은 기존 typed JSON/서버 타입 검사를 재사용한다. 여러 직접 호출을 모두 선택하며 하나라도 부적합하면 모두 거절한다. 새 입력을 기존 코드에서 사용하도록 본문을 자동 변경하지 않는다.

입력 삭제와 새 입력 생성을 동시에 하면서 삭제된 핀의 바인딩을 새 핀으로 옮기는 일부 혼합 선택은 현재 UI가 해제 선택을 요구해 안전하게 거절한다. 일반적인 별도 추가/삭제 완료와 구별해 미지원으로 남긴다. 임의 기본값이나 자동 연결 제거로 우회하지 않는다. 새로운 저장소를 임의로 만들어 연결하는 조작도 추가하지 않는다.

C# 본문 재작성·복잡한 ref/out·중첩 호출, 출력 타입/추가삭제/반환 전체 편집, 등록/복사 출처, 여러 함수 동시 후보 등은 [고정 잔여](V536_I5_6_REMAINING.md)다. 이번 일반 입력 지원과 I5-6 전체를 구별한다. 실제 Windows apphost/WebView2·모바일 기기·Library 전달은 이 Linux 검증으로 확인되지 않는다.
