# I5-6 3행: 출력 정의 추가·삭제와 void 반환 전환

기준은 저장소 `196c605`의 v536이다. 기존 정보 함수 상세창의 출력 추가/삭제와 기존 계약 대응창을 사용한다. CSS·창 배치·권한·C# 원문은 변경하지 않는다. 새 출력의 값/실행 위치와 출력 삭제의 전체 배치 확인을 같은 대응창의 기존 field/select 형식에 연결했다.

## 지원 경계

직접 소유한 함수 하나와 직접 소유한 직렬 Blueprint target들의 출력 정의를 편집한다. 기존 입력 이름·타입·순서·역할과 유지하는 출력 이름·타입·상대 순서는 그대로다. 출력 추가·삭제를 함께 편집할 수 있으며 하나의 후보와 CAS로 함수·구현·import·graph·code definition hash·공개 출력 계약을 검증한다. 모든 target과 호출자가 맞아야 저장한다. 명시적 Review/Confirm 전에는 source를 최종 반영하지 않는다.

- 새 출력마다 값과 삽입 위치를 직접 선택한다. 정확히 같은 타입의 현재 루트 입력 또는 직접 입력한 scalar 값을 사용한다. 임의 기본값/형변환은 만들지 않는다. 숫자 원문은 typed JSON으로 보존한다. 삽입은 기존 실행 시작 위치, 유지한 노드 다음, 앞서 생성한 출력 다음이다. 원래 직렬 실행 순서를 보존하며 도달 불가능한 위치·바뀐 후속 경로·중복 삽입 위치는 거절한다.
- 삭제는 원래 graph hash, 해당 정의의 **모든** 내보내기 노드 ID, 원래 exit 바인딩을 확인한다. 같은 출력이 여러 번 배치돼 있으면 전체를 하나의 삭제로 처리한다. 소유한 graph의 내보내기와 해당 root 계약만 바꾸며, 그 값을 계산하던 기존 code 노드의 out/return 계약과 C# 계산을 삭제/재작성하지 않는다.
- 호출자는 기존 출력에서 어떤 현재 출력을 받을지 명시한다. 소비 중인 출력의 대응이 없거나 타입이 다르면 선택창에서 알리고 Save 요청 전에 차단한다. 서버도 전체 사용처와 타입을 다시 검증한다. 연결을 조용히 지우거나 다른 핀으로 추측하지 않는다.
- 값 반환→void는 원래 반환 내보내기/exit와 소비 대응을 함께 처리한다. void→값 반환은 원래 legacy `return: null` 키와 새 반환 정의를 구분하고 명시 값/실행 위치를 요구한다. 공개 출력은 삭제한 정의만 제거하고 새 출력을 자동 공개하지 않는다. 의미는 기존 호출 후 SourceContext 읽기이며 프로젝트 접근/외부 공유 권한이 아니다.

이번 실통합 fixture는 일반 long 출력의 정확한 64비트 값 추가, 두 배치가 있는 out 전체 삭제, long 반환→void, void→문자열 반환, 기존 out 삭제+새 문자열 출력의 같은 후보, long/bool 두 출력 생성의 직렬 연결을 대상으로 한다. 모든 타입·그래프 조합을 전수 검사했다는 뜻은 아니다.

## 검증 기록

격리 fixture와 실제 엔진/Chromium/컴파일러만 사용한다. 사용자 자료·계정·유료 추론·사용자 프로젝트 실행은 사용하지 않는다. 원시 로그와 실패/진행 기록은 `/workspace/scratch/v536-information-output-definitions`에 보관한다. 체크 수는 기능 개수나 통과율이 아니다.

| 검사 | 실제 결과 |
|---|---|
| 순수 후보 | 추가·복수 writer 삭제·양방향 void·삭제/추가 혼합·두 출력 추가 6개 후보 성공. source write 없음 |
| 실제 API | 혼합·복수 writer 삭제·void·fromvoid·두 출력 추가, 각 3 check로 총 15 통과. 마지막 새 출력의 source가 부적합한 경우에도 앞선 출력이나 선언을 부분 적용하지 않음 |
| 실제 화면 | 독립 추가/쓰기 실패 3, 기본 복수 writer 삭제 2, 독립 void 저장·조회 응답 유실 3, 기본 fromvoid 2, 혼합 취소 2, 실제 peer 충돌 2: 총 14 check 통과. Undo/Redo·미저장 cold·명시 선택 누락 표시·Save·저장 cold·Review 취소/Confirm·확정 cold 포함 |
| 영향 회귀 | 기존 숫자 반환 타입 API 3, Native 함수 계약 7 check 통과 |
| Native/Linux | 최종 0 warning/0 error, 실제 Linux 엔진 빌드 성공·stderr 0 |
| clean checkout | 소스 `233ce265ca22ae73a67ca9ed753b747a63d90485`에서 Native/Linux 새 빌드, 실제 혼합 API 3 + 독립 창 두 출력 연속 생성 UI 2 check 통과. 마지막 경로 최소 변경 보완을 포함해 cold·Review/Confirm까지 재현 |
| 리소스 | 보존 CRLF checkout의 실제 fast-forward와 fresh LF checkout, 74 canonical/exact snapshot·변조/인코딩/BOM/binary/budget 거절 통과 |
| Windows 교차 패키지 | win-x64 2,333파일 생성. 소스/Native DLL 9개 byte 일치, test fixture/인증파일/프로필/로그/Git 미포함. SDK 없는 runtime-only 복사와 별도 cwd에서 실제 패키지 웹 엔진 기동/74리소스, 변조·의존성 누락 거절, fixture 기존 프로필 보존/최초 로그인 화면 검사 통과. Windows apphost/WebView2 실행은 아님 |

기존에 유지되는 실행 edge는 다시 생성하지 않고 삽입으로 달라지는 edge만 기존 root 계획에 제출한다. 원래 노드와 C#는 보존한다. 새 출력 위치와 값 선택, 전체 writer 삭제 확인은 source/hash와 함께 서버에서 다시 검증한다.

초기 Native 빌드의 지역 변수 중복을 수정한 뒤 0 warning/0 error로 빌드했다. 초기 편집 스크립트가 문자열 일치 검사에서 중단된 상태도 확인해 나머지 연결을 완료했다. 보호 조건을 제거하거나 실패한 검사를 성공으로 처리하지 않았다.

## 남은 3행과 고정 목록

이번 단위가 3행 전체 또는 I5-6 전체 완료는 아니다. 기존 숫자 타입 변경은 단일 writer와 정확히 같은 타입의 현재 root 입력 source 범위다. 여러 writer의 **타입 변경**, 여러 출력 동시 타입 변경, 비숫자 기존 출력의 타입 변경과 다른 값/source 선택, 입력 계약 변경과 출력 정의 변경을 동시에 묶는 경로는 지원하지 않는다. 여러 writer의 전체 정의 삭제와 타입 변경은 구별한다. 새 scalar 출력 생성에서 string/bool을 쓰는 것은 기존 비숫자 출력 타입 변경까지 구현했다는 뜻이 아니다.

비직렬/중첩 graph, C# After/enum 후처리의 formal 계약 변경, raw C#/전체 본문/복사·등록 출처/여러 함수 동시 closure는 기존 차단을 유지한다. 사용자가 편집한 C# 원문을 명시적으로 결합하는 것은 고정 9행의 4~9행에 남기며 새 시각적 분기·반복이나 자동 소스 치환을 도입하지 않는다. 고급 핀 타입/표시명 및 I6/B2, A4~A6/M4/M11/M12와 Helper 작업 도구도 기존 후속이다.

실제 Windows apphost/WebView2·모바일 기기·Library 전달은 미검증이다. 교차 빌드 및 Linux에서 패키지 웹 엔진 기동을 그 검증과 혼동하지 않는다.


## 화면·빌드 근거

기존 수용 레이아웃 `d4e3793`의 style/consumer/runtime CSS는 byte 동일하다. 실제 clean 엔진의 독립 정보 창에서 [상세 편집](evidence/v536-information-output-definitions/output-definition-popover.png)과 [값/삽입 위치 선택](evidence/v536-information-output-definitions/output-definition-mapping.png)을 열어 확인했다. 원본 상세창/계약 대응창에 필요한 field/select를 연결했으며 새 상시 패널이나 CSS를 만들지 않았다. 전체 화면 pixel/native 일치 검사는 아니다.

로컬 패키지는 `/workspace/artifacts/v536-information-output-definitions/Windows-x64` 폴더 전체이고 Windows 진입점은 `Confectory.exe`다. source 커밋은 `233ce265ca22ae73a67ca9ed753b747a63d90485`, manifest SHA-256은 `754683e7c2ea371e6a3c9a2d2b93a89da3c113b9bbe864c9a29da7d1e9282833`이다. .NET Desktop Runtime 10 x64와 WebView2 Runtime 전제는 유지한다. 생성물은 Git에 넣지 않으며 Library로 전달하지 않았다.
