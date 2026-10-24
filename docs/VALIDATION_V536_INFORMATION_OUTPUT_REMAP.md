# I5-6 3행: 다중 writer·비숫자 출력 타입의 명시 대응

기준은 저장소 `196c605`의 v536 화면과 기존 Blueprint 계약이다. 기존 정보 함수 상세창/계약 대응창을 사용하고 CSS·레이아웃·권한·C# 원문은 변경하지 않는다. 이번 단위는 직접 소유한 함수 하나의 일반 Blueprint 출력 편집이며 I5-6 전체 완료가 아니다.

## 연결 범위

- 같은 출력의 모든 내보내기 배치와 실제 exit 값에 각각 원래 graph hash·노드 식별자·바인딩과 새 타입/값을 제출한다. 여러 출력의 타입을 함께 바꾸거나 출력 이름 변경·추가/삭제와 결합할 수 있다. writer가 둘 이상이라고 첫 배치만 갱신하지 않는다. 단일 배치의 기존 선택 기록 키는 호환 유지한다.
- 사용자는 정확히 같은 타입의 루트 입력·기존 노드 결과·지역값/별칭 또는 명시한 기본형/배열 값을 선택한다. 자동 수치 변환이나 기본값 추정은 하지 않는다. 지역값의 타입/별칭 원본, 배열 구성과 정확한 숫자를 기존 컴파일러 규칙으로 재검사한다. 객체의 직접 값은 명시적 null만 가능하고 다른 객체는 기존 typed 연결을 선택해야 한다. 정보/참조/외부 핀 선택기는 고정 9행의 9행에 남는다.
- 호출마다 원래 출력의 소비를 어떤 현재 출력으로 받을지 명시한다. 소비 중인 출력의 무대응·타입 불일치는 화면과 서버 모두 거절한다. 정의·모든 생산자/소비자 본문·import·공개 계약은 한 후보와 CAS로 처리한다. 누락·오래된 기준·마지막 부적합 source가 있어도 일부 배치/선언을 먼저 저장하지 않는다. 기존 source 조회는 읽기 전용이며 getter/provider/AI를 실행하지 않는다.
- 실제 구현과 소비자가 전혀 없는 소유 함수는 없는 writer를 가정해 만들지 않는다. 전체 manifest/실제 소스 관측 후 해당 선언만 바꾼다. 기존 구현/소스를 요청에서 누락해 선언 전용으로 위장하면 거절한다.
- 공개는 호출 후 SourceContext 읽기의 기존 의미이며 프로젝트 접근/외부 공유 권한이 아니다. 함수 식별자·기존 code 노드 서명·C# 본문·다른 객체/함수/부모·다른 target은 보존한다.

## 검증 기록

격리 fixture와 실제 엔진/Chromium/컴파일러를 사용한다. 사용자 자료·로그인·유료 AI 호출·사용자 프로젝트 실행은 없다. 원시 기록은 `/workspace/scratch/v536-information-output-remap`에 남긴다. 아래 체크 수는 기능 개수나 통과율이 아니다.

| 검사 | 실제 결과 |
|---|---|
| 실제 API | 다중 writer 숫자 변경·배열 변경·이름/여러 타입/새 출력 혼합·기존 배열→문자열, 각 3 check로 총 12 통과. writer/exit 누락·오래된 hash/before·마지막 부적합 값·무대응 소비자·외부 node·초과 선택·알 수 없는 수식 연산과 0 나눗셈은 전체 거절 |
| 실제 화면 | 독립 문자열 쓰기 실패 3, 기본 배열 저장/조회 응답 유실 3, 독립 이름+두 출력 타입+새 출력 혼합 2, 독립 전체 취소 2, 실제 peer 충돌 2, 기존 배열→문자열 2 check: 총 14 통과. Undo/Redo·미저장 cold·정확한 선택 복원·Save·Review 취소/실제 compiler Confirm·확정 cold 포함 |
| 추가 순수 후보 | 선언 전용 출력 변경과 실제 C# 구현/누락 소스 보호 2 check 통과 |
| 영향 회귀 | 기존 출력 추가/삭제 혼합 API 3, 기존 숫자 반환 타입 API 3, Native 함수 계약 7 check 통과 |
| Native/Linux | root/clean Native 0 warning/0 error, root/clean 실제 Linux 엔진 빌드 성공·stderr 0 |
| 리소스 | 보존 CRLF checkout의 실제 fast-forward 및 fresh LF, canonical/exact 74 리소스·내용/인코딩/BOM/binary/budget 변조 거절 통과 |
| Windows 교차 패키지 | manifest 2,334항목 생성. source/Native DLL·Core DLL 9개 byte 일치. test fixture·인증파일·프로필·로그·Git 미포함. SDK 없는 runtime-only 및 별도 cwd에서 실제 패키지 웹 엔진·74리소스, 변조/의존성 누락 거절, fixture 프로필 보존/최초 로그인 화면 검사 통과. 실제 Windows apphost/WebView2 실행은 아님 |
| clean checkout 실제 경로 | 소스 `531a1f279fc4487304bd01c00ebbbe469ae11ba2`에서 Native/Linux 새 빌드 후 이름·두 타입·새 출력 혼합 API 3 + 기존 배열→문자열 독립 정보 창 UI 2 check 통과. Save·미저장/저장 cold·Review 취소/실제 compiler Confirm·확정 cold까지 재현 |

실제 [상세창](evidence/v536-information-output-remap/typed-output-popover.png)과 [각 writer/exit의 명시 대응](evidence/v536-information-output-remap/typed-output-mapping.png)을 열어 확인했다. 이전 수용 기준 `5735516`의 CSS 3개는 byte 동일하다([근거](evidence/v536-information-output-remap/layout-evidence.json)). 새 레이아웃/상시 패널을 만들지 않았다. 전체 화면 pixel 일치/실제 Windows 비교를 수행했다는 뜻은 아니다.

초기 화면 검사에서 출력 이름과 타입을 함께 바꾸면 요청에서 새 타입이 빠지는 결함을 재현했다. 기존 원래 이름으로 새 타입을 조회하던 부분을 명시 이름 대응을 사용하도록 수정했다. 불완전한 요청은 서버가 거절해 원문/입력을 보존했다. 후보 음성 검사의 fixture가 공유 caller-map dict를 변경해 다음 정상 요청까지 오염하던 오류는 독립 복사로 수정했다. 리소스 해시 갱신에서 canonical/raw 필드를 섞은 기동 실패도 기록하고 올바른 canonical 형식으로 수정했다. 실패를 통과로 계산하거나 보호를 완화하지 않는다.

## 고정 잔여와 다음 경계

이번 단위에서 일반 출력만 편집하는 다중 writer/비숫자/동시 타입 변경을 연결한다. **입력 계약 변경과 출력 정의/타입 변경을 같은 편집에 섞는 경로는 아직 차단 중**이다. 입력 사용처의 기존 before 증거와 출력 writer의 before 증거를 같은 원래 graph에서 검증하고, 명시 출력 대체 슬롯에 입력 대체를 이중 적용하지 않는 결합이 필요하다. 따라서 3행 전체 종료로 표시하지 않는다. 이 제한을 무관한 새 조합 목록으로 넓히지 않는다.

고정 4~9행은 별도 잔여다. 다음 구체적 4행 단위는 사용자가 실제 편집한 C# 본문/원래 함수·구현 기준을 함께 제출하여 직접 소유 target 하나의 계약/본문을 검증하는 것이다. 자동 문자열 치환·암묵적인 C# 식별자 재결합은 하지 않는다. 중첩(5), 전체 본문/ref·out 저장소 역할(6), 등록/복사 출처(7), 여러 함수 closure(8), 고급 핀 타입/표시명(9)은 기존 명세의 미구현으로 유지한다. I6/B2와 A4~A6/M4/M11/M12 및 Helper 실제 작업은 기존 후속이다.

실제 Windows apphost/WebView2·모바일 기기·Library 전달은 미검증이다. Linux에서 패키지 웹 엔진을 기동하는 검사를 실제 Windows 실행으로 표시하지 않는다.


## 로컬 재현 패키지

source 커밋은 `531a1f279fc4487304bd01c00ebbbe469ae11ba2`다. `/workspace/artifacts/v536-information-output-remap/Windows-x64` 폴더 전체이며 Windows 진입점은 `Confectory.exe`다. manifest SHA-256은 `a8a9991cca73a85540569c2f59fdf616d797394a06b2b6ad79784be2a3cb0adc`다. manifest 2,334항목과 manifest 파일 자체를 포함한 실제 2,335파일을 구분한다. 기존 .NET Desktop Runtime 10 x64·WebView2 Runtime 전제를 유지한다. 생성물은 Git에 넣지 않았으며 Library로 전달하지 않았다.
