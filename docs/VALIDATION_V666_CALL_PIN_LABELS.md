# Blueprint 호출 핀 표시명 검증

제품 동결 `5b45f3bec2e265da5f221be9251d2e0f3ecea91a`의 [한정 지원](V666_CALL_PIN_LABELS.md)을 **신규 36단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout·HOME/NuGet·빈 엔진 cache의 Release/MCP·실제 엔진,
새 Windows 교차 패키지·구조/무결성 검사·전체 ZIP 복원을 실행했다. 개발 실행과 최종 수를
합산하지 않으며 같은 검사 코드의 새 실행과 과거 결과 재사용을 구별한다.

- 이미 관측한 직접 소유 callee의 native `amount`에 저장된 별칭을 위치 ABI로 caller의
  `supplied`에 표시했다. native caller 인자·고정 return·함수/노드 ID·signature·arguments·
  outputs·정의 hash와 C# bytes를 유지한다. 실제 int 입력/반환 호출의 원래 결과10을 확인했다.
- 반복 열기·cold·다른 함수의 미저장 반환 표시명 보존을 확인했다. 다른 창 입력을
  암묵 저장하거나 아직 저장하지 않은 별칭을 관측 선언의 표시로 사용하지 않는다.
  잘못된 metadata는 원래 핀과 안내를 유지하고 자동 삭제/교체하지 않는다.
- 표시된 입력 핀의 기존 값 UI에서 native `supplied` 바인딩만7→8로 저장했다. Review 취소·
  편집 대상 graph의 Review 뒤 실제 물리 변경 거절·재검토/Confirm과 C# 원문 보존을 거쳐
  실제 결과11을 확인했다. 동료 callee draft 변경에 대한 기존 Save 거절과 입력/체크포인트
  보존도 검사했다. 새 저장/API 권한이나 native 계약을 만들지 않는다.
- 순수 조회는 id·타입·역할·반환 차이, malformed/알 수 없는 label과 caller 쪽 이름 충돌을
  구별한다. callee에서 유효한 별칭도 caller의 다른 native 이름과 충돌하면 기존 입출력
  쪽별 distinct 규칙을 적용한다. constructor/toString/__proto__의 자체 키를 검사했고,
  실제 UI의 별칭 없는 constructor도 JS 기본 속성으로 바뀌지 않았다.
- 기존 standalone 반환 표시명과 7/8행의 기존 alias/source/route 결합 UI를 새로 회귀했다.
  현재 실제3D 전송 정체·부분 POST 중 reload8회·단절·child/root·프로젝트 왕복·cold를 관찰했다.
  과거 간헐적 빈 화면의 원인은 여전히 미확정이며 이전 bootstrap 전체 검사를 합산하지 않는다.

개발 30단계의 실패 8건을 보존했다. typed import 누락/잘못된 blueprint
치환, 포트와 값 plug를 함께 찾은 locator, native가 요구하는 정식 import 별칭 대신 임의
별칭을 쓴 fixture, no-op route를 positive control로 쓴 가정, peer 편집의 선택 문맥 누락을
각각 바로잡았다. 단일 핀 저장은 기존 `argument` 요청을 사용하는데 `authorBatch`만 세었던
검사도 실제 요청·native ID·거절 응답을 확인하도록 바로잡았다. 제품 투영에서 callee-valid 별칭과 caller native 이름이 충돌하는 사례를
별도 순수 재현으로 확인했고 기존 per-side 검증을 재사용해 수정했다.

처음 final CAS fixture는 편집하지 않은 callee의 공백 변경까지 무조건 거절한다고 가정했다.
기존 `Changes`/`ConfirmReviewed`는 일반 변경의 실제 반영 파일을 선택하고 현재 물리 원본을
복사해 다시 컴파일한다. 편집 대상 graph의 원본 CAS를 검사하도록 바로잡았으며 Confirm
코드를 수정하거나 모든 읽기 의존성에 새 raw-byte lease를 추가하지 않았다. 원래 guarded
property/async/등록·공개 계약·copy의 별도 읽기 검증은 유지한다. 실패와 원문 근거를 보관했다.

구 Reference TYPE 거절·문자열 metadata의 [실제 바이너리 보관 근거](VALIDATION_V666_ARGUMENT_LABELS.md)는
개발 evidence에서 SHA를 다시 확인했다. 구 바이너리를 신규 실행한 것이 아니며 위 최종 수에
넣지 않았다. 새 view projection은 persisted 문법·Reference 지원을 소급 변경하지 않는다.
같은 게시 세대의 reader/authoring/runtime을 사용하고 ID·원문·profile을 보존하며 자동
migration/downgrade나 TYPE만으로 버전/데이터 손상을 단정하는 처리는 없다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 5b45f3bec2e265da5f221be9251d2e0f3ecea91a | 8ba5f5aa1d668987ace6cf469447de6bdbff001b94234dcaf0c3f291cd4c2ff9 | 54069723 |
| rollback | 88bd4c9303fb29581a4b41652e7d42bba563f876 | 385e7a602e363febcf717c0b10169b2f7056c281d35d62a01cdb7cc3dd1a28d7 | 54069068 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/99398b5019214ea298bbb010082c4681.json` · evidence SHA256 `87432ce186015c05f95e50d40042c5d8d54db39f9bbe210579a09b66cd6a9b4d`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/a2d3bd7f661f45da959660a4b405b1d5.json` · evidence SHA256 `e3a88392df3e70ddc032f2ba4a5b1e619b7dfcdf161714ac20ac2a485b64ddbf`.
두 관리 package와 증거를 SHA로 재확인했다. 승인된 latest/정상 rollback2세대 교대와 이번
소유 RAM 임시물 정리만 적용했다. 원래 checkout/main과 과거 비관리 자료/증거를 보존하며
퇴역한 세 번째 관리 ZIP 전체를 계속 보관한다고 주장하지 않는다. 여유 25337745408bytes
(23.60GiB)다.

다른 표시 문맥과 기존7행 forwarded/opaque 영향 source·다른 frame 결합, 기존8행 여러 함수의
명시 계약/본문·공유 caller closure는 [기존 유한 잔여](V666_CALL_PIN_LABELS.md)다. 이 표시 단위로
M11/M12/M4나7/8행 전체를 완료/재개하지 않는다. 실제 Windows/WebView2·물리 기기·OS IME·
GPU/audio·전체 UI 전수 검증은 별도다. 새 자격증명/외부 grant·라이브 AI/과금·main 변경은 없다.
