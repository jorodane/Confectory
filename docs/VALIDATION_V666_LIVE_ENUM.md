# 실제 객체 enum 접근 검증

[지원 경계](V666_LIVE_ENUM.md)의 제품·검사를 `549eb40128ea003b3603531b69683bd72f1f58e1`에서 고정했다.
최종 **42단계(신규26·동등 재사용16)·실패0**을 통과했다. 후속 결과 문서 커밋은 제품·검사·
실행 코드를 바꾸지 않는다. 실제 Windows/모바일·전체 UI 완료로 합산하지 않는다.

게시본 `059111512c8c9444a98292072eb083f086b4ca0e`에서 enum C# 타입 자체는 생성되지만
실제 ObjectModel.Create/Access가 해당 필드를 거절함을 실제 CLR로 재현했다. primitive
객체 descriptor와 숫자 매핑 없는 enum 필드의 기존 descriptor를 golden 입력으로 보관하며,
수정 후 byte-for-byte 비교한다. golden 입력과 과거 실행 증거 재사용을 구별한다.

새 native 검사는 caller-owned 객체, 서로 독립인 상속 객체, 실제 Blueprint Read→Set→Read,
반복 호출과 이전 enum 출력 보존을 확인한다. raw ID/정수/다른 enum/정의 밖 값/null,
잘못된 배열·비vector 배열, source hash와 mutable enum ref 거절도 검사한다. 배열 참조와
이전 배열 출력, 호출자가 직접 잘못 바꾼 배열의 Read 거절·명시 복구를 확인한다. 멤버
이름·순서 변경은 숫자·필드 hash·contract 산출물을 유지하고, 실제 멤버 계약 변화는
pinned property node를 거절한다. 정확한 원문 복원이 원래 key와 실행을 회복한다.

UI는 기존 속성 editor·resource 검색·모바일 값 선택과 실제 engine/checkpoint/compiler를
사용한다. 새 읽기·receiver·소비 binding·실행 attachment를 한 후보로 Save하고 cold 복원한다.
저장 실패·enum source 충돌, 응답/receipt 유실의 중복 apply 없는 복구, 늦은 별도 입력,
기존 C# 본문의 취소·저장 실패·후속 Save, 반복 Review/명시 Confirm·최종 CAS를 확인한다.
기존 enum 지역값 초기화 문법은 확장하지 않고 fixture의 명시 C# 숫자 변환을 사용한다.

최종 검증은 독립 LF/CRLF·빈 engine cache·공개 SDK/기존 NuGet seed, 기존 primitive/ref
runtime·authoring·동기/async 속성 UI·module·정보 배열 회귀다. 새 Windows 교차패키지의
구조/무결성·패키지 engine 실행·전체 ZIP 복원과 실패 수명관리를 구별한다. 최종 SHA·
증거·보관·정리 결과는 아래와 같다.

| 최종 범위 | 신규 실행 | 동등 재사용 |
| --- | ---: | ---: |
| LF 독립 checkout·빌드·native/UI·primitive/ref/async/module 회귀 | 6 | 10 |
| CRLF 독립 checkout·빌드·native/UI·authoring/정보 배열 회귀 | 10 | 5 |
| 관리 IPC 수명 | 0 | 1 |
| 새 교차패키지·무결성·패키지 UI·전체 ZIP 복원·native/수명·실패 정리 | 10 | 0 |

`tools/verify_desktop.py --suite live-enum`을 공개 SDK
`/workspace/toolchains/dotnet-10.0.401`과 기존 NuGet seed로 실행했다. native probe의
6개 내부 확인과 각 UI의 내부 체크를 별도 단계로 부풀리지 않는다. 기존 검사를 새로
실행한 것과 보관된 실행 증거 재사용을 구분한다. 최초 최종 실행은14단계 통과 뒤
환경 재연결 때 출력 파이프가 끊겨 `Broken pipe`로 종료됐고 증거를 보관했다. 같은
제품·harness·SDK/NuGet·정규화 명령을 검증해 통과 증거를 연결했다.
두 번째 실행의 CRLF 늦은 입력 검사는 Save 발행 전 cold 화면의5초 준비 기대로 실패했다.
미지원 표시에서 실제 편집 작업 표시로 바뀌는 중이었고 checkpoint는335bytes로 미반영
상태였다. enum fixture의 준비 대기만60초로 고정했으며 활성 Save·pending 동일성 검사는
유지했다. 실패한 검사는 재사용하지 않았다. 새 고정본은 이2개 테스트 대기 외의 차이가
없음을 원문 비교로 확인했다. LF10·CRLF5·IPC1의16단계는 이전의 더 짧은 준비 조건으로
통과한 동등 증거이고, 필요한 LF/CRLF checkout·복원·빌드·엔진12단계 및 나머지 검사는
신규26단계다. 새 패키지·전체 복원도 새로 검사했다. 제어기 출력은 연결 수명과 무관한
파일로 보관했다.

개발 기록은 22회 실행 중 8회 실패를 보관했다. 새 함수 준비
입력의 잘못된 provide 절과 enum 지역값 초기화 fixture를 수정했고, 제품의 초기화 의미는
확장하지 않았다. 응답 유실 검사의30초 창은 후보 컴파일 완료 전에 끝나 enum fixture만
120초로 늘렸다. 원래 apply/receipt 성공 응답·cold 정산·중복 적용 없음은 관측됐다.
그 뒤 UI 재진입 실패는 저장 완료로 미저장 입력이 없는 상태에서 Save 버튼 활성화를
기대한 검사 준비 오류였다. 재진입은 실제 그래프 로딩을 기다리도록 고쳐 loss/late를
검증했고 제품의 저장·Review 조건은 약화하지 않았다. 늦은 입력의 첫 출력 클릭 정체는
Playwright의 viewport 밖 클릭 반복으로 확인했다. phase/stack/동작 로그를 보관했고
완료 요청 관측으로 바꾼 가설은 원인을 해결하지 않아 되돌렸다. 기존 전체 보기 UI로
카드를 맞춘 enum fixture를 검증했다. 타임아웃/정체 진단은 자식 회수 후 종료했고
실패나 진단 중단을 통과로 세지 않았다.
동일 환경의 연결 회복 후 이미 완료된 엔진 빌드/worker receipt와 미커밋 변경을 회수했고,
실패한 transport 명령의 미실행을 확인한 뒤 fixture만 수정했다. 연결 직후 실행 중인
검사나 완료된 엔진 빌드를 중복 시작하지 않았다. 정리된 검증 작업공간의 실행 산출물
재생성은 위 신규 단계에 포함했다. 개발 증거 보관 중 남은 Chromium IPC는 자식 종료
영수증과 커널 endpoint 부재·소유 메타데이터를 보관한 뒤 소유 임시 영역에서만 정리했고,
일반 관리 도구의 미인증 IPC 거절 조건은 변경하지 않았다.

- 개발 기록: `/workspace/artifacts/v536-verification-managed/runs/d52784149fc0490784e2ceeca96b8ac9.json`
- 개발 증거 ZIP SHA256: `b0d86df9254f1f67cc751b2ae1427fc370036defee32df63093462ef5012c183`
- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/d9175035a3e149e3b532796fb03d9e45.json`
- 최종 증거 ZIP SHA256: `2192f510f9a44b90e09b8d376eb7824f19ef5ee5a901ec383103e6974ccf0969`
- latest runtime: `549eb40128ea003b3603531b69683bd72f1f58e1`
- latest ZIP SHA256: `cf182d1884c030645338641054fc8dec027ec4e07df05cc79ba0c329522e440d` (53984799bytes)
- rollback runtime: `b775adde470c9ce2aac079362ab0a07d878264b2`
- rollback ZIP SHA256: `b194696b9663edb134e2d0fb97628d679bce4c6ca428f16a9d5058fd032339e8` (53981519bytes)

관리 store는 `/workspace/artifacts/v536-verification-managed/packages`다. 전체 압축 복원과
실행 후 latest/rollback을 승격하고 durable 증거 archive/무결성 확인 뒤 이 단위 소유
임시 workspace만 정리했다. 기존2세대 보관 및 정리 계약을 넓히지 않았다.
보관 직후 디스크 여유는 25496231936bytes (23.75GiB)다. 원래 checkout
`b5ea38c3d7eec3eb20f170e68f0f4215b86b2aee`와 main
`0d2459b463798d11031c20f46a6c8d1a4ecc35dd`를 보존한다.

Linux/.NET compiler·엔진·브라우저·패키지/전체 복원 자동화 결과다. 실제 Windows/모바일·
물리 화면/오디오·전체 UI와 모든 구 reader 실행은 미검증이다. 초기 빈 화면의 원인은
미확정이다. 살아 있는 참조의 나머지 bridge, compound/function 필드와 module async/공개
실행 결과의 완료로 합산하지 않으며 [정확한 지원 경계](V666_LIVE_ENUM.md)를 따른다.
