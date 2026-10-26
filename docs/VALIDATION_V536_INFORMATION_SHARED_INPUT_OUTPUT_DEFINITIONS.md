# 고정 8행: 입력 정의와 출력 정의·void 반환 결합

기준은 `e83b827c90b57cbdf5379bc756614c04bbe62dd7`의 기존 v536 상세창과
단일 함수의 명시 입력/출력 계획이다. 이번 단위는 scalar 값 입력 추가·사용 중
삭제/새 입력 대응과 out 추가·전체 writer 삭제·양방향 void 반환 전환을 함수 간/
같은 함수 안에서 한 후보/CAS로 결합한다. 남은 핀 식별자·순서·역할과 사용자
본문을 보존하며 새 UI·레이아웃·계약 ID·권한이나 C# 자동 재작성을 만들지 않는다.

## 고정 수용 조작

- normal: A의 count 출력 전체 writer 삭제/fresh 추가와 B의 extra 입력 추가.
  B의 원래 amount가 읽는 A.count는 명시한 A.fresh로 연결한다. 입력 정의만
  바뀐 B에는 출력 재선택 계획을 주지 않는다.
- joint: A의 extra 추가+출력 삭제/추가·유지 writer/반환 타입 변경과 B의
  사용 중 amount 삭제/incoming 추가+출력 계획을 결합한다. callee 사용은
  incoming, caller는 원래 amount 바인딩의 명시 재사용을 선택한다.
- void: A의 extra 추가+출력 계획/비void→void, B의 amount 삭제+유지 출력/
  반환 타입 변경. 실제 callee 사용처는 명시 리터럴, caller 바인딩은 명시 해제한다.
- fromvoid: A의 extra 추가+출력 삭제/추가와 void→string, B의 amount 삭제/
  incoming 추가+유지 출력/void→string. 새 반환의 한글·이모지와 caller 바인딩을
  보존한다. 새 출력/반환을 자동 공개하지 않는다.

각 count의 실제 writer 두 개를 모두 선택해야 하며, 원래 exit·삽입 위치와
호환 소비 대응이 빠지면 모두 거절한다. 입력 `9223372036854775806`, 삭제 대체값
`9223372036854775800`, 새 출력 23/정확한 64비트 값, 기존 C# 매개변수·본문·
공개 출력 목록/순서와 실행 경로를 보존한다. 편집 역순도 같은 후보 및 원래
source hash를 만들어야 한다. 원래 out 이름을 새 입력으로 재사용하는 역할
변경은 이 단위에 포함하지 않는다.

## 변경 경계

`InformationFunctionBatch.Begin`에서 입력 정의 변경을 출력 그래프 변경과
구별해 분류한다. 삭제된 입력은 남은 핀 집합에서 제외하고, 유지 입력의 명시
ID/순서/타입과 새 scalar 입력·입출력 역할을 검사한다. caller 입력 수는 다음
계약을 기준으로 검사하되 실제 old use·새 값·재사용/해제·writer·그래프 경로·
소비자는 원래 단일 closure에서 먼저 검증한다. 실제 출력 변경 행만 투영하며
입력 전용 행의 출력 재선택이나 출력 전용 행의 입력 재선택을 허용하지 않는다.

`MappingFor`·`ProjectOutputs`·`Merge` 및 원래 hash/CAS 처리 본문은 불변이다.
원본 요청 전체 검증 후 내부 overlay만 합성하고 한 번에 저장한다. 원본·부모·
외부 파일과 권한을 보존한다. 오버라이드는 원래 매개변수·출력 계약을 유지하며
독립 계약 복제/새 ID는 필수 범위에서 제외한다.

## 검증 기록

수정 전 joint/void/fromvoid 3흐름·6확인에서 단일 후보 유효/그룹만 거절됨을
재현했다. Native Release 경고·오류 0이다. 집중 18흐름·50확인과 영향
7흐름·23확인이 통과했다. 원래 hash/역순·누락/잘못된 사용처·값·해제·writer·
경로·소비 대응·역할 및 실제 source 충돌의 전체 거절, 네 형태의 API/컴파일·
기본/독립 460px UI 편집·취소·Undo/Redo·미저장/저장 cold·Review 취소/Confirm을 확인했다.
checkpoint 실패/재시도, 저장/조회 응답 유실 후 receipt 확인과 중복 방지,
peer 입력/프로젝트 전환·오래된 창 제출 차단, 마지막 미완성 매핑 거절 후
Undo·명시적 재시도도 통과했다.

초기 normal API는 추가 전용 마지막 행에도 implementations가 있다고 가정한
테스트 KeyError로 applySlots 요청 전에 종료됐다. 실제 명시 새 입력 값을
잘못된 타입으로 바꾸어 마지막 계약 오류/전체 미적용 검사를 보존했다.
제품 검증은 완화하지 않았고 실패 로그/ZIP을 보존했다. 수정한 실제 API는
저장·cold·Review/Confirm까지 통과했으며 이전 API 경로도 추가 회귀했다.
미해결 실패는 없다.

입력 정의/기존 out·반환 타입, 입력 타입/출력 정의, 입력 이름/출력 정의,
입력 정의/타입 혼합, 오버라이드 보호와 이전 출력 없는 경로도 통과했다.
원본 UI 74리소스+WebBundle(75파일)은 82e2676와 바이트가 같고 실제 원본
기본/독립 창 렌더와 핀을 확인했다. 새 증거 ZIP 29개 전체 목록·권한·바이트·
SHA-256을 재검증했으며 기존 자료 삭제는 없다.
[집중·영향 근거](evidence/v536-information-shared-input-output-definitions/focused-verification.json)에 실패/수정/통과를 구분한다.
독립 checkout·새 교차 패키지는 이후 별도 기록한다.

## 정확한 잔여

이번 단위는 8행 전체 완료가 아니다. 위 단위 밖의 입력/out/반환/정의 동시 편집,
ref·출력 역할·매개변수 순서, 수동 C#/혼합 native·중첩/private/whole/postCall,
같은 원래 ABI copy/상속/등록/소유 정보 속성의 여러 closure 결합 및 scalar 밖
함수 타입은 별도 잔여다. 완료한 입력 정의+출력 정의/양방향 void 결합을 다시
미완료로 분류하지 않는다.

9행 정보/참조/외부 함수 타입·표시명/native 식별자 분리 및 I6 아이콘/B2 실제
배지·A4~A6/M4/M11/M12는 후속이다. Helper 실제 에디터 도구는 UI 이후 별도
단계며 새 이미지/협의/렌더 backend는 이번 범위 밖이다. 전체 v536 UI·실제
Windows apphost/WebView2·모바일 기기 실행·Library 전달 완료를 의미하지 않는다.
기존 원본·보관 빌드·캐시·로그·스크린샷·fixture·profile·사용자 자료는 보존한다.

## 독립 checkout·새 교차 패키지 완료

실행 소스는 `28bf7386d3fa3ded72ffdd637a7f1dcebdf54301`다. 기존 독립 checkout을 정상 fast-forward하고
9개 Git blob·기존 LF/CRLF 설정·clean 상태를 확인했다. Native Release 경고/
오류 0, 후보·API·독립 UI·기존 경로·오버라이드 보호 5흐름·13확인이 통과했다.
root solution 및 별도 MCP Release도 경고·오류 0이다.

새 Windows x64 교차 패키지의 manifest 2,343항목/marker 포함
2,344파일, 132,770,169바이트의 집합·전체 해시 및
현재 제품 소스·Native DLL과 7개 Core DLL 일치를 확인했다. manifest SHA-256은
`d7783ea5fcf1340f1f7db51317a50f83a87be939104b498ae184aa82521300a3`, Native DLL SHA-256은
`23c0ea5ab398e1e199c41d9a5ae4b06a872dad1541fac519f01765ccd9f9f62d`이다.

SDK 없는 새 소유 runtime에서 무관한 cwd의 Linux managed 엔진 웹 기동,
74리소스·synthetic profile/명시 override 보존·변조/DLL 누락 거절과 패키지
backend 후보 4확인이 통과했다. 검사 6단계를 순차 수행했으며 OOM/oom_kill은 0이다.
실제 Windows apphost/WebView2·모바일 기기 실행 및 Library 전달과 구별한다.

새 증거 ZIP 36개의 파일 집합·권한·전체 바이트·해시를 재검증하고 전체 manifest와
fixture 증거를 보존한 뒤 이번 소유 임시 RAM 패키지만 종료 cleanup했다.
기존 자료 삭제·압축 변환이나 새 영구 배포 파일 보관·전달은 하지 않았다.
패키지 단계 최저 디스크 여유는 1,982,799,872바이트다. 후속 결과 문서 커밋은
실행 소스를 바꾸지 않는다.
[checkout·패키지 근거](evidence/v536-information-shared-input-output-definitions/package-clean-verification.json)에 단계·소스·해시·검증 한계를 기록했다.

API/UI 재현은 `CONFECTORY_SHARED_INPUT_OUTPUT_DEFINITIONS=1` fixture를 선택한다.
이전 API 영향 검사는 이 변수를 해제하고 `CONFECTORY_SHARED_INPUT_OUTPUT_DEFINITION_MIX=1`을 선택했다.
