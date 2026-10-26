# 고정 8행: 입력 정의와 출력·비void 반환 타입 결합

기준은 `d93b9d90a11cdca633c2bb23084b0763b9411327`의 기존 v536 화면과
단일 함수의 명시 입력/출력 계약이다. 이번 단위는 입력 추가·사용 중 입력 삭제/
삭제 후 새 입력 대응과 **기존 scalar out·비void 반환 타입** 편집을 함수 간/
같은 함수 안에서 한 후보와 CAS에 결합한다. 새 레이아웃·메뉴·계약 ID·권한을
만들거나 C# 본문을 자동 재작성하지 않는다.

## 고정 수용 조작

- normal: A에 long extra 입력을 추가하고 B의 기존 count/반환 타입을 double로 바꾼다.
  A의 원래 반환을 읽는 B.amount와 caller 반환 소비는 명시한 호환 출력으로 유지한다.
- joint: A의 extra 추가+count/반환 변경, B의 사용 중 amount 삭제/fresh 추가+
  count/반환 변경을 결합한다. B.fresh는 원래 amount 바인딩을 명시 재사용하며
  A의 변경된 반환 대신 stable을 선택한다. callee의 기존 amount 사용은 fresh를 선택한다.
- delete: A의 extra 추가+반환 변경과 B의 amount 삭제+count 타입 변경을 결합한다.
  B의 실제 사용처는 명시 long 리터럴로 바꾸며 원래 caller 바인딩은 명시 해제한다.

각 count에는 실제 writer 두 개가 있다. 모든 원래 writer를 선택해야 하며 출력
consumer 대응 누락은 전체 거절한다. extra `9223372036854775806`, 삭제 대체값
`9223372036854775800`, 기존 값·핀 식별자·C# 매개변수와 원문·노드/실행 경로·
출력 공개 목록/순서를 보존한다. 편집 역순도 같은 최종 후보와 원래 source hash를
만들어야 한다. 임의 기본값이나 자동 연결 삭제는 허용하지 않는다.

## 변경 경계

`InformationFunctionBatch.Begin`의 입력 정의 분류에 scalar 출력/비void 반환
변경을 구별해 기록한다. 입력 순서/역할 및 남은 출력 ID/순서를 유지하고 각
원래 단일 closure에서 실제 입력 사용처·새 값·해제·writer·호환 consumer를
검증한다. 출력이 바뀐 행만 원래 producer 선택을 투영한다. 출력 전용 행에는
입력 재선택을, 입력 정의 전용 행에는 출력 재선택을 허용하지 않는다.

`MappingFor`·`ProjectOutputs`·`Merge` 및 원래 hash/CAS 처리 본문은 변경하지
않았다. 원본 요청의 모든 단일 후보를 먼저 검증하고 내부 overlay만 합성하며,
외부 소스·checkpoint 경합에서 전체 미적용을 유지한다. 오버라이드는 원래
매개변수·출력 계약을 유지하며 독립 계약 복제는 필수 범위에서 제외한다.

## 검증 기록

수정 전 joint/delete의 원래 단일 후보는 유효하지만 그룹만 거절됨을 2흐름·
4확인으로 재현했다. Native Release 경고·오류 0이다. 집중 15흐름·41확인과 영향 6흐름·20확인이 모두 통과했다.

집중 검사는 순수 후보/역순·원래 hash와 실제 소스 충돌, 세 형태 API의 마지막
계약 오류 전체 미적용·단일 저장·cold·Review/Confirm, 기본/독립 460px UI의
취소·명시 대응·Undo/Redo·미저장/저장 cold·검토 취소/Confirm을 포함한다.
저장 장치 오류/재시도, 저장 및 조회 응답 유실 후 receipt 조회·중복 방지,
실제 peer/source 경합과 입력 보존, 프로젝트 전환/오래된 창 제출 차단,
불완전한 마지막 매핑 거절 후 Undo·명시적 재시도도 통과했다. 미해결 실패는 없다.

기존 입력 타입/출력 정의·void 전환, 입력 타입/out/반환, 입력 정의·입력 정의/
타입 혼합, 오버라이드 계약 유지와 출력 없는 이전 경로를 영향 회귀로 검증했다.
UI 74리소스와 WebBundle(75파일)은 `82e2676`와 바이트가 같고 실제 원본
선택창/직접 값·기본/독립 창 렌더를 확인했다. 새 증거 ZIP 23개의 파일 집합·
권한·전체 내용·SHA-256을 재검증했으며 기존 자료는 삭제하지 않았다.
[집중·영향 근거](evidence/v536-information-shared-input-definition-return-mix/focused-verification.json)에 기록했다.
clean checkout·새 Windows 교차 패키지는 이후 별도 기록한다.

## 정확한 잔여

이번 단위는 8행 전체 완료가 아니다. 입력 정의 추가·삭제와 **출력 정의 추가/
삭제·void 전환**의 결합, ref·출력 역할·매개변수 순서, 수동 C#/혼합 native·
중첩/private/whole/postCall, 같은 원래 계약 copy/상속/등록/소유 정보 속성의
여러 closure 결합 및 scalar 밖 함수 타입은 별도 잔여다. 이미 완료한 값 입력
타입/이름과 출력 정의·반환 타입 결합을 다시 잔여로 분류하지 않는다.

9행 정보/참조/외부 함수 타입·표시명/native 식별자 분리 및 I6/B2·A4~A6·
M4/M11/M12는 후속이다. Helper 실제 에디터 작업은 UI 이후 별도 단계이며
새 이미지/협의/렌더 backend는 이번 UI 복원 범위 밖이다. 실제 Windows
apphost/WebView2·모바일 기기 실행·Library 전달과 브라우저/managed 검증은 구별한다.
원본/부모/외부·main·사용자 자료와 기존 보관 빌드/로그/스크린샷/fixture는 보존한다.
