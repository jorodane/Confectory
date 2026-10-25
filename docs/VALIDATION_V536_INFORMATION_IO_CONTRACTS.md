# I5-6 3행: 입력·출력 계약의 결합 저장

저장소 v536 `196c605`의 기존 정보 함수 상세창과 명시적 계약 대응창을 사용한다. 화면/CSS·권한·C# 원문은 유지한다. source 커밋은 `3003328dae8705b4a1ce9efadd1ac500dd468fe4`다.

## 이번에 닫은 경계

원래 그래프에서 출력 계획의 모든 hash·writer/exit·before 증거를 먼저 검증한다. 그 슬롯을 입력 계획이 또 덮어쓰거나 복구하지 않는다. 중복된 두 선택을 받으면 전체 거절한다. 실제 삭제한 출력의 원래 writer/exit도 같은 경계를 사용한다. 나머지 code 인자·별칭 저장소·변경하지 않은 반환/출력 exit는 기존 입력 계획에서 명시적으로 대체하고, 출력 이름이 바뀌면 그 현재 exit에 복구한다.

기존 바인딩의 입력 이름은 원래→현재 대응으로 바꾼다. 명시 출력 대체와 새 출력 값은 이미 현재 서명을 사용하므로 다시 대응하지 않는다. 입력 이름 둘을 맞바꾸는 경우도 현재 값을 다른 핀으로 조용히 바꾸지 않는다. 출력 값의 지역 별칭은 정확한 타입/식별성을 유지하고, 원래 입력을 복구한 **최종** 그래프에서 별칭 source·가용성·모든 code 원문/정의·호출자/import를 검증한다. 별칭을 값 스냅샷으로 치환하거나 기존 입력을 추정하지 않는다.

함수 하나의 선언·각 소유 target 그래프·노드 record·직접 호출자의 서명/인자/소비 출력/import·공개 출력 계약은 같은 후보와 CAS로 저장한다. 마지막 부적합 source·실제 동시 수정·디스크 오류가 있으면 중간 후보를 저장하지 않고 기존 checkpoint와 입력을 유지한다. 공개 의미는 기존 SourceContext 읽기이며 외부 공유/프로젝트 접근 권한이 아니다. 저장과 명시적 Review/Confirm은 별개다.

## 실제 검증

격리 fixture와 실제 엔진/Chromium/컴파일러만 사용한다. 사용자 자료/계정·유료 추론·사용자 프로젝트 실행은 없다. 로그와 초기 실패는 `/workspace/scratch/v536-information-io-contract`에 남긴다. 체크 수는 기능 수나 통과율이 아니다.

| 검사 | 결과 |
|---|---|
| 실제 API | 입력 타입 변경+새 입력+출력 이름/타입+새 출력, 입력 타입+같은 타입 출력 이름 변경, 입력/출력 삭제+새 핀, 입력 이름+출력 변경, 두 입력 이름 교환+출력 변경: 각 3 check로 15 통과. 원래 입력을 읽는 두 writer·exit·별칭과 호출자 값/정확한 수치를 함께 확인 |
| 실제 화면 | 독립 혼합 정상 2, 기본 창 저장 실패/재시도 3, 기본 이름 변경 저장/조회 응답 유실 3, 독립 삭제/추가 전체 취소 2, 입력 이름 교환 실제 peer 충돌 2: 총 12 통과. Undo/Redo·미저장 cold·입력/원문 보존·저장·Review 취소/실제 compiler Confirm·확정 cold 포함 |
| 영향 회귀 | 기존 수식/별칭/exit 입력 대체 API 3, 다중 writer·출력 이름/타입/추가 혼합 API 3, Native 함수 계약 7: 총 13 check 통과 |
| Native/Linux·clean checkout | 소스 `3003328`의 root/clean Native 0 warning/0 error·Linux 빌드 stderr 0. clean 실제 혼합 API 3 + 같은 타입 출력 이름/입력 타입 변경의 독립 창 UI 2 통과. 미저장/저장 cold·Undo/Redo·Save·Review 취소/실제 compiler Confirm·확정 cold까지 재현 |
| 리소스·Windows 교차 패키지 | 보존 CRLF fast-forward/fresh LF의 canonical/exact 74 리소스와 내용/인코딩/BOM/binary/budget 변조 거절 통과. win-x64 manifest 2,334항목, source/Native DLL·Core DLL 10개 byte 일치. SDK 없는 runtime-only·별도 cwd에서 실제 패키지 웹 엔진/리소스·변조/의존성 누락 거절·fixture 기존 프로필 보존/최초 로그인 화면 검사 통과 |

화면 검사의 첫 fixture는 새 입력을 기존 출력 앞으로 이동한다고 잘못 예상했다. 원본 폼은 기존 pin ID 순서를 유지하고 새 입력을 append하므로 그 기대만 수정하고 재검증했다. 제품의 순서·타입 검사나 CAS를 완화하지 않았다. production Native 빌드는 0 warning/0 error다.

기존 [상세창](evidence/v536-information-io-contract/typed-output-popover.png)과 [명시 대응창](evidence/v536-information-io-contract/typed-output-mapping.png)을 실제로 열었다. 이전 수용 기준 `01f570b`의 CSS 3개는 byte 동일하다([근거](evidence/v536-information-io-contract/layout-evidence.json)). 전체 화면 pixel 일치나 실제 Windows 검사를 주장하지 않는다.

## 3행 종료와 4~9행

고정 9행 표의 **직접 소유 함수 하나·일반 Blueprint·현재 기본형/배열 선택기에서 제공하는 출력 편집** 수용 범위는 입력 계약 동시 편집까지 연결했다. 3행의 이 지원 경로를 마감한다. 새로운 callable/타입/실행 의미를 이 완료 조건에 추가하지 않는다. 기존 C# formal/본문 결합(4), 중첩(5), 전체 본문/ref·out 저장소 역할(6), 등록/복사 출처(7), 여러 함수의 공유 caller closure(8), 고급 핀 타입/표시명(9)은 여전히 미구현이며 안전한 거절을 그 기능의 완료로 표시하지 않는다.

다음 4행의 첫 단위는 사용자가 편집한 직접 소유 C# target 하나의 본문·원래 함수/구현 기준·명시 매개변수 대응을 같은 후보에서 검증하는 것이다. 기존 `rootBody`/source 기록 계약을 사용하고 원문 문자열 치환이나 컴파일만 성공하는 암묵 식별자 재결합을 하지 않는다. 4행은 이번 커밋에서 구현하지 않았다. I5-6 전체와 전체 v536 UI 완료도 아니다. I6/B2 및 A4~A6/M4/M11/M12·Helper 실제 작업은 기존 후속이다.

## 이전 패키지의 source 표기

이전 Windows 패키지는 구현/테스트 커밋 `531a1f2`를 빌드했다. 뒤의 게시 `01f570b`는 검증 문서와 스크린샷 7파일만 바꾸고 실행 코드/리소스를 바꾸지 않았다. Git diff와 패키지 source 7개를 게시된 blob에 byte 비교해 동일함을 확인했다([기록](evidence/v536-information-io-contract/prior-package-equivalence.json)). 따라서 **그 두 커밋의 실행 입력은 동등**하다. 두 번째 빌드를 따로 수행하여 모든 실행 파일이 bit-for-bit 같다고 주장한 것은 아니다. 이번 결합 코드는 그 이전 패키지에 없으므로 새 source `3003328` 기준으로 별도 패키징한다.

실제 Windows apphost/WebView2·모바일 기기 실행과 Library 전달은 미검증이다. 교차 패키지와 Linux에서 패키지 웹 엔진을 기동한 결과와 구분한다. 패키지 생성물/fixture/프로필/인증정보는 Git에 넣지 않는다.

새 로컬 패키지는 `/workspace/artifacts/v536-information-io-contract/Windows-x64` 폴더 전체이며 `Confectory.exe`가 진입점이다. source `3003328dae8705b4a1ce9efadd1ac500dd468fe4`, manifest SHA-256 `30be032c573b1f5600b4d7167b04137900431925ddc43dd59d8d56706a750270`다. manifest 2,334항목과 manifest 자체를 포함한 실제 2,335파일을 구분한다. 기존 .NET Desktop Runtime 10 x64·WebView2 Runtime 전제를 유지하며 Library로 전달하지 않았다.
