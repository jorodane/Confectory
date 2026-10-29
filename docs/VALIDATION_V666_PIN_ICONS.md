# v666 모듈 인터페이스·Set 출력 아이콘

기준은 저장소 `Confectory-Editor-Prototype-v666.zip`(SHA-256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)이다. `blueprint.js`의 모듈 인터페이스 `renderFunctionSignatureEditor(...propertyStyle:true...)`와 Set 출력의 `fixed:true, readonly:!!node.targetVariableId`, `app.js`의 field 아이콘 핸들러를 대조했다. 이 핸들러는 field의 표시 아이콘만 바꾸며 실행 계약을 다시 만들지 않는다. 숨긴 루트/모바일 핀이나 propertyStyle이 없는 함수 상세 핀은 추가하지 않는다.

## 이번 연결

- 현재 프로젝트가 직접 소유한 모듈의 직접 `require` 입력·out·반환 슬롯에 기존 공통 팝오버의 기호/이모지·로컬 이미지·아이콘 해제를 연결했다. 기존 모듈 계약 흐름 안의 표시 제어를 사용하며 CSS·함수 계약 편집기를 바꾸지 않는다. 포함/상속 요구는 읽기 전용이다. 원본 함수와 기본 구현·외부 팩을 변경하지 않는다.
- 모듈의 기존 primitive `value` metadata에 qualified 함수 ID·현재 위치·전체 타입/모드/반환 서명·아이콘을 기록한다. 위치는 기존 native 모듈의 순서 기반 계약이다. metadata 이름의 ID 인코딩은 저장 키이며 새 실행 핀 ID가 아니다. 요청·원본 hash/리비전·직접 요구·현재 전체 서명을 확인하고 주석/CRLF/정확한 수치·다른 구문을 보존해 같은 owner 후보/CAS로 저장한다. `icon`/설명 거래와 같은 receipt를 사용하며 모듈은 최대 64개의 서로 다른 표시 변경을 받는다. 비모듈 헤더의 기존 2개 제한은 유지한다. 결과 UTF-8 소스는 기존 1MiB 읽기 예산을 넘기지 않는다.
- Set은 기존 Set 편집이 지원하는 직접 소유 일반 root 그래프에서 자체 출력(`local == outputLocal`)만 편집한다. 다른 저장소를 대상으로 한 Set과 출력이 없는 legacy Set은 잠금을 유지한다. copy 초안·slot 문맥·private copy/path·private conversion·결합 copy가 필요한 문맥과 implementationContext/forwardCallerStorage가 있는 그래프의 기존 Set UI 경계는 유지한다. 해당 문맥은 현재 미지원으로 남기며 원본의 정상 금지로 확정하지 않는다.
- Set 출력 표시는 기존 graph `node.icon`을 사용한다. Set에는 별도 동작 카드 헤더 아이콘을 만들지 않는다. 기존 Core의 semantic graph/stamp 계산은 이 표시값을 제외한다. 새 Set 계획과 아이콘은 하나의 `setPlan` 표시 목록으로 처리하며 기존 단일 계획 제한·전체 후보·최종 CAS를 유지한다. 실제 저장소 ID·타입·순서·값·실행/데이터 연결을 아이콘 때문에 바꾸지 않는다. 기존 Set 계획 재편집도 저장된 표시값을 보존한다.
- 기존 5MB 입력·128×128 WebP 정규화·native bounded container 검증·CSP·private 입력/Undo/Redo·cold·Review→명시 compiler Confirm을 사용한다. 개인 파일명·경로·원본을 저장하거나 외부에 업로드하지 않는다. 테스트 이미지는 생성 자산이다. 일반 정보/객체/기능 헤더와 속성/정보 함수/graph 동작 카드 이미지를 다시 구현하지 않는다.

## 발견·검증 경계

집중 기록은 `/workspace/artifacts/v536-verification-managed/runs/83b7bbc3d6d3406684028263c744c572`이다. base `8ec4f24`, 각 엔진 overlay와 검사 입력을 기록하며 초기 실패를 통과에 합치지 않는다.

Set에서 아이콘 기록 때 전체 카드를 다시 그리던 새 연결은 저장 중 원래 문맥을 잃어 cold 뒤 다음 Save를 막았다. 기존 동작 카드의 아이콘 전용 기록 경로를 재사용해 새 입력만 기록하고 문맥을 유지하도록 수정했으며 늦은 입력·아이콘 해제 중 새 입력을 재검증했다. 새 Set+아이콘을 두 작업으로 보내던 후보는 기존 단일 Set 계획 검사에서 거절됐다. 이 검사는 유지하고 표시 목록을 해당 계획 안에 넣어 전체 검증한다. 기존 계획이 node를 재구성할 때도 표시값을 보존한다.

모듈 행에 잘못 적용한 서명 grid 클래스는 타입 표기를 세로로 줄바꿈했다. 기존 흐름의 일반 행 제어로 수정하고 화면 치수·실제 픽셀을 확인했다. CSS를 바꾸지 않는다. 실패 입력 비교에서 기존 임시 엔진 토큰과 보존되는 author-attempt 기록을 사용자 내용과 혼동한 가정도 수정했다. 생성·실행 연결·아이콘의 모든 내용과 실패 기록의 원래 요청을 정확히 비교하고 공유 출력 변조를 전체 거절한 뒤 정상 재시도·cold·Confirm을 확인한다. JavaScript metadata 키도 native와 같은 UTF-8으로 인코딩하고 동일성을 검사한다. 검사 변수의 `icon` 이름이 화면 조회 함수를 가린 실패와, 숨긴 모바일 제어/비활성 문서의 완료 버튼을 누르려던 검사 가정은 제품 결함과 구별한다. 해당 검사는 실제 노출된 데스크톱 제어·기존 문서 탭 선택을 사용하며 강제 클릭이나 약한 Confirm 조건으로 바꾸지 않았다. C# 빌드 오류와 source-merge/byte 예산 진단도 보존한다.

모듈 native는 입력/out/반환의 문자·생성 이미지·해제, 부모/외부/원문/등록·계약 유지와 잘못된 위치·서명·glyph/URI·중복의 전체 거절을 확인한다. receipt 검사는 qualified 함수·위치·서명이 다른 입력을 재기준하지 않는다. native가 두 번 확인한 settled 후보와 같은 source hash에 대해서만 늦은 아이콘을 보존한다. 실제 UI는 기본/독립 창·동시 핀·Undo/Redo·cold·취소/취소 중 입력·checkpoint 실패·peer CAS·응답 유실·프로젝트 왕복을 확인한다. Set의 정상·해제·늦은 입력·오류·공유 저장소 보호와 새 계획 결합은 별도 기록한다.

## 최종 마감

최종 검증 소스는 `2e4b8e444a63c4a6d77a8f292df7de15c4d98af1`이다. `tools/verify_desktop.py --suite pin-icons`로 **LF 30·CRLF 26·패키지/복원/실패 수명관리 14, 합계 70단계 모두 새로 실행해 통과**했다. 기존 57단계의 조건을 유지하고 이번 13단계를 추가했다. native 모듈 표시·receipt·다중 핀, Set 계획 표시 보존·새 Set/아이콘·cold/Confirm, 패키지/복원본의 모듈 다중/반환 늦은 입력과 Set 늦은 입력을 포함한다. 기존 copy/직접 private 동작 카드·실제 프로젝트 왕복·소유 복합 전환·배율·속성 이미지도 이번 실행에서 회귀했다.

첫 `bc637c5` 실행은 24단계 통과 후 out 핀을 다시 선택하고 3개를 기대한 검사 오류로 중단됐다. 기록 `a9ce788ca7924463abcc8caa37487fd9`를 보존하고, 시작 핀의 이미지를 유지하며 서로 다른 입력/out/반환 슬롯과 저장값을 정확히 비교하도록 검사만 수정했다. 제품 코드는 바꾸지 않았다. 해당 실행은 증거 보관 후 임시공간이 정리되어, 새 독립 checkout에서 수정 검사부터 먼저 확인하고 전체 70단계를 마감했다. 집중 실행의 통과 44단계와 진단 실패 11단계도 별도 보존하며, 실패를 최종 통과 개수에 합치지 않는다.

최종 기록은 `/workspace/artifacts/v536-verification-managed/runs/df593d756baf499c9be9bd2f4325d531.json`, 지속 증거 ZIP은 같은 이름 `.zip`이다. 증거 SHA-256은 `b2a867ae8e096c08cea3d5e2c2b39b75972338635c6a99815ddae31392c7cb96`, 크기 8,387,345 bytes이다. 재연결 때 도구 세션 번호는 소실됐지만 실제 검증 PID·같은 RAM root·로그를 회수해 중복 실행 없이 완료했다. 마지막 로그의 `status: passed`, 70개 종료 코드 0, 보관 index, `status: cleaned`와 root 부재를 확인했다.

최신 패키지는 source `2e4b8e4`, `/workspace/artifacts/v536-verification-managed/packages/6d47e892b9bda5d4546c055181a4b971e10ecc4f3d4ed728c11f481a8412fb74.zip`이다. ZIP_LZMA 51,206,752 bytes, 전체 2,505항목(파일 2,358·디렉터리 147), ZIP SHA-256은 파일명과 같고 내부 package manifest SHA-256은 `b7fa23e4446be537188e24bba0f52df4c6dfec9c070fc45018025cf0b9a8cd8d`이다. 전체 파일 SHA/CRC/권한 복원, 복원본 기동·UI, 패키지 DLL과 독립 빌드 DLL의 동일성을 확인했다. 게시 마감은 문서만 바꾸며 이 소스와 모든 비문서 파일의 동일성을 확인한다. 패키지 출처 commit을 게시 문서 commit으로 바꾸어 표시하지 않는다.

정상 롤백본은 `b4a83596710015a524d2fd14079b2123408fc489`, ZIP SHA-256 `293dea989c27da167db833fe88b0aca00d9ef585bf1972e4901d86ea049a2aec`, 51,202,397 bytes이다. 이전 검증 증거와 manifest를 재사용하고 지속 보관 SHA를 다시 확인했다. 승인된 관리 store의 두 세대 승격으로 이전 rollback `450ce762`만 해당 store에서 퇴역했다. 별도 과거 보관 패키지·원본·캐시·로그·프로필·fixture는 추가 정리하지 않았다. 공용 SDK 10.0.401과 NuGet seed 바이트는 해시를 확인해 재사용했고 Git checkout·엔진 캐시·출력은 각각 독립했다.

공간 사전 예산은 새 지속 공간 144MiB(안전 64MiB 포함), RAM 파일시스템 3GiB, 추가 메모리 7GiB와 메모리 안전 1GiB이다. 최종 실행의 df 여유는 2,304,233,472→2,293,141,504 bytes, 관측 순증가 **10.58MiB**이며 증거와 manifest/index를 포함한다. worker 관측 최저 여유 2,303,041,536 bytes, cgroup 관측 최대 메모리 4,513,153,024 bytes이다. 원래 RAM root `/tmp/cv-8u15espm`은 자식 프로세스 종료·증거 보관·패키지 승격 뒤 제거됐다. 증가량은 이번 실행의 측정치이며 고정 3–6MiB 보장이 아니다. 패키지 실패/예외 수명관리 회귀도 통과했다.

종류 항목은 별도 정의 기반의 고정 후속이다. ABI closure·고급 타입/핀 표시명·B2/M4/M11/M12·V2–V9는 별도다. 기존 Set 지원 문맥 밖의 실제 미구현과 정상 읽기 전용을 같은 완료/금지로 묶지 않는다. 공개 override 원계약 유지·독립 계약 복제 제외·3D/권한 별도 팩·이동 연출과 작업 실행 분리 합의를 유지한다. 배율 일시 실패 원인은 여전히 미확정이며 새 재현 근거 없이 해결로 표시하지 않는다. 실제 Windows/WebView2·물리 모바일/DPI/IME·전체 UI·Space/Library 전달은 미검증이다.
