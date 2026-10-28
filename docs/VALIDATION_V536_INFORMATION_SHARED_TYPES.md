# v536 공유 호출자의 값 입력 타입 결합

이 문서는 f4b9780의 입력 타입 단위 기록이다. 후속 일반 out 이름 결합은 [별도 검증](VALIDATION_V536_INFORMATION_SHARED_OUTPUT_NAMES.md)과 고정 범위 문서를 따른다.

고정 8행의 후속 단위다. 같은 정보가 직접 소유한 일반 Blueprint 함수 2~8개의 같은 위치·이름·수를 가진 값 입력의 scalar 타입 변경을 함께 저장한다. callee는 import 없는 code/export leaf이며, 공유 caller는 선택한 함수들의 call/export만 사용하고 반환 계약은 바꾸지 않는다. 현재 scalar는 bool/int/long/float/double/string이다. 새 메뉴·화면·ID·권한은 추가하지 않았다. 7행 독립 복제 정책은 여전히 답변 대기이며 이 구현과 무관하다.

각 함수의 기존 검증기를 원래 스냅샷에서 먼저 실행하여 caller·callee 매핑, 해제 동의, 원문과 hash를 확인한다. 내부 후보 결합 시 선택한 호출 자체는 원래와 같아야 한다. 다른 선택된 호출의 서명·인자만 앞선 검증 결과로 바뀔 수 있고, 그래프의 연결·실행 경로·기타 필드는 동일해야 한다. 그 경우에만 복제한 내부 매핑의 graph hash를 내부 후보에 맞춘다. 사용자 요청은 변경하지 않으며, 최종 업데이트는 원래 hash 한 개씩과 기존 후보/CAS·receipt·Review/Confirm을 사용한다. 실패한 선택을 최신 소스로 무조건 재시도하지 않는다.

## 검증 상태

격리된 두 leaf와 한 공유 caller를 사용한다. 두 번째 호출은 원래 첫 호출의 long 반환을 사용한다. 각 amount 입력을 string으로 바꾸면서 기존 code의 long amount 사용은 count로, caller 입력은 명시한 한글 문자열로 교체하고 원래 연결 해제를 확인한다. C# 매개변수·본문, 반환 연결과 exact64 기본값은 보존한다.

구현 커밋은 `820c1bdf7d9421ee1a66a054e14ff6d6ba77d4ab`이다. [집중/checkout 근거](evidence/v536-information-shared-types/focused-verification.json)에 명령·종료 코드·로그 해시를 남겼다.

| 검사 | 통과 결과 |
|---|---|
| 순수 후보 4 check | 사용자 요청 불변, 한 소스당 원래 hash 한 개, 역순 동일 결과, 명시 bool/double 값, 마지막 선택의 원문/hash/누락/타입/연결·실행 경로/역할/반환 오류 전체 거절 |
| 실제 API 3회 / 7 check | 정상 저장·재시작·compiler Confirm, 두 번째 함수 오류, 물리 caller 파일 경합, 다른 편집자의 live 변경 보존 |
| 실제 화면 6회 / 13 check | 기본/독립 창, 상세창 취소, 두 단계 Undo/Redo, 미저장 cold, 저장 실패·재시도, 저장/조회 응답 유실 뒤 receipt 조회만 수행, 전체 변경 취소, 프로젝트 전환·오래된 submit 차단, Review 취소·명시 Confirm |
| 영향 회귀 7 check | 기존 공유 caller 이름 변경/설명 편집 4, 기존 상속·외부 원본 보호 3 |
| clean checkout 9 check | 기존 깨끗한 checkout을 로컬 구현 커밋으로 ff, Native Release, 순수 후보 4·실제 API 3·독립 화면 2 재현 |

집중 합계는 24 check 문구다. 반복 준비 단계가 포함되어 고유 기능 수가 아니며 영향 회귀·checkout 재현·패키지 4 check와 합쳐 새 기능 수로 세지 않는다. 초기에 fixture는 합법적인 CallerBody import 타입 갱신을 누락한 기대와 타입 편집+매핑 승낙을 한 번의 Undo로 간주한 기대 때문에 실패했다. import 두 개와 호출자 ABI 불변을 정확히 확인하고 실제 두 사용자 동작을 Undo/Redo하도록 수정했다. 보호 조건이나 레이아웃을 약화하지 않았다. 최신 기본/clean 독립 화면은 Confirm+cold 뒤 두 amount 핀이 실제로 글자로 표시됨도 기다려 검사했다.

460px 원본 정보 카드와 exact64 입력을 검사하고 [기본](evidence/v536-information-shared-types/primary.png)·[독립](evidence/v536-information-shared-types/detached.png) 화면을 열어 살폈다. 전체 UI 소스와 WebBundle은 e827a52에서 바이트 변경이 없다. 원본 레이아웃 재설계나 전체 v536 화면의 새 픽셀 비교를 했다는 주장은 하지 않는다.

Release solution, 별도 MCP Release 및 Linux build `tool.ok=true`를 확인했다. Windows 교차 패키지는 아래 RAM 경계에서 생성·검증했다. [패키지 근거](evidence/v536-information-shared-types/package-verification.json)에 전체 manifest 검증, 제품 소스·Native DLL·Core 7개 사본의 일치 및 명령/로그 해시를 남겼다. 파일 집합은 manifest 2,343개+marker 총 2,344개, 132,727,682 bytes이며 symlink가 없다. manifest SHA-256은 `a55dbf35e836ee9f868003246b98d77795afdbd9b6e4e495fca2815abf8f530b`이다. 패키지에 포함된 Native로 후보 4 check도 통과했다.

SDK 없는 기존 fixture 런타임을 전체 파일·해시 대조 후 읽기 전용으로 재사용했다. 새 legacy profile tree는 같은 RAM 패키지의 읽기 전용 hard link이며 변조 검사가 끝난 뒤 만든다. 다른 cwd에서 packaged managed 엔진 기동, 74리소스·최소 로그인 화면, 변조/누락 DLL 거절, 기본 프로필·명시 경로 override를 모두 통과했다. 로그인·유료 추론·사용자 프로젝트 실행은 하지 않았다. 이는 Linux/Chromium 및 교차 빌드이며 실제 Windows apphost/WebView2·모바일 기기 실행이나 Library 전달은 아니다.

패키지의 실행 코드 기준은 구현 커밋 820c1bd다. 이후에는 검증 문서·evidence만 변경하며 제품 소스는 동일하다. 커밋 전 e827 버전 DLL을 섞지 않도록 커밋 후 solution/MCP를 다시 빌드했고 모든 Core 사본이 현재 Release와 같음을 확인했다.

## 지원하지 않는 결합

입력 추가/삭제·순서·ref/out, 출력/반환 변경, 수동 C# 본문·중첩/private/whole/postCall, copy/상속/등록 문맥, 다른 속성 변경의 여러 함수 결합은 미완료다. 같은 위치의 scalar 변경이라도 callee 간 호출 의존이나 caller의 code/locals가 섞이면 보수적으로 입력을 유지하며 거절한다. 단일 함수의 기존 지원이나 첫 이름 변경 단위를 제거하지 않는다. 이 제한은 기존 명세의 미구현이며 새로운 설계 결정을 요구한다는 뜻이 아니다. 9행 named 타입/표시명, I6/B2 및 A4~A6/M4/M11/M12는 별도 후속이다.

## 공간과 실행 한계

작업 볼륨 약72MiB, /tmp 약101MiB에서 새 보관 패키지 약133MB는 만들 수 없다. 기존 파일을 삭제하지 않고 같은 환경의 전용 RAM 임시 경로에서 fixture와 교차 패키지 검증을 진행한다. 로그·선택한 화면·해시를 작업 볼륨에 보존하며 새 임시 fixture만 종료 후 정리한다. RAM 패키지는 영구 보관 파일이나 사용자 전달 성공으로 표시하지 않는다. 기존 보관 패키지는 이전 e827a52 실행 코드 기준으로 그대로 남긴다.
