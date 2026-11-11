# standalone 고정 반환 표시명 검증

제품 동결 `88bd4c9303fb29581a4b41652e7d42bba563f876`의 [지원 범위](V666_STANDALONE_RETURN.md)를 **신규 39단계·재사용0·실패0**으로 검증했다.
독립 no-hardlinks Git 객체·HOME/NuGet·빈 엔진 cache의 LF/CRLF Release/MCP·실제 엔진,
새 Windows 교차 패키지와 구조/무결성 검사·전체 ZIP 복원을 실행했다. 기존 테스트 코드의
새 실행과 과거 결과의 재사용을 구분하며 개발 검사를 최종 수에 합산하지 않는다.

- 실제 standalone 상세창의 고정 반환 이름칸, 같은 카드 표시, 빈 입력 거절·취소·로컬
  Undo/Redo·cold·저장 이력 Undo/Redo·기본값 초기화/metadata 제거와 다시 저장을 검사했다.
  반환과 설명을 한 owner 후보/CAS로 저장하고 고정 반환/함수/인자 ID·타입·역할·연결과
  원래 C# bytes를 보존했다. native 후보는 인자 표시명·설명·아이콘까지4개를 결합했다.
- 실제 체크포인트 쓰기 실패·명시 재시도·peer 체크포인트 충돌·cold를 검사했다. 실제
  native apply 접수 뒤 응답 유실과 늦은 새 이름 입력은 receipt와 새 cell을 구별했다.
  복원 후 이전 apply를 재실행하지 않고 새로운 입력만 한 번 저장했다.
- Review 취소, Review 뒤 physical peer 원문 변경의 최종 CAS 거절, 원문 복구 뒤 새
  Review/Confirm과 원래 C# 결과10을 검사했다. 입력/반환 int인 한 함수의 실제 실행
  표본이며 모든 타입/문맥의 실행이나 void 전환 실행 전수를 뜻하지 않는다.
- native 순수 후보에서 잘못된 길이/control/빈 값·추가/중복/과다 cell·잘못된 owner/kind를
  거절했다. 기존 helper의 trim·기본값 제거, 명시적인 잘못된 metadata 교체와 void 보관을
  검사했다. native 서명과 새 표시 변경의 동시 UI 제출은 popup 입력을 유지하며 거절했다.
  자동 C# 치환·인자/반환 대응·서명 migration을 추가하지 않는다.
- 같은 코드의 standalone 인자 표시명 및 정보 카드 반환 표시명 저장/실행을 새로 회귀
  검사했다. 실제3D 전송 정체·부분 POST 중 reload8회, 단절·child/root·프로젝트 왕복·cold를
  관찰했다. 과거 간헐적인 빈 화면 원인은 여전히 미확정이다. 이전 bootstrap 실패37단계
  전체를 이번에 재실행/재사용했다고 합산하지 않는다.

개발 18단계의 실패2건을 보존했다. 첫 fixture는 Python 비교식의 공백 누락으로
제품 실행 전에 실패했다. 잘못된 metadata fixture는 선언 끝의 newline을 닫는 brace로
잘못 취급해 SYNTAX가 발생했다. 올바른 선언으로 해당 native 검사만 다시 실행했고 제품
코드는 이 두 실패 때문에 변경하지 않았다. 개발 단계 `dev-standalone-return-normal`은
실제 command에 기록된 기존 인자 표시명 회귀다. 전용 반환 UI와 구분해 보존했다.

[기존 구 reader 비교](VALIDATION_V666_ARGUMENT_LABELS.md)의 최종/개발 evidence SHA를
읽기 전용으로 재확인하고 실제 pretyped TYPE 거절 및 이전 문자열 metadata 보존 로그를
확인했다. 구 바이너리를 새로 실행한 것은 아니며 최종 신규 수에 넣지 않았다. optional
표시 metadata 호환과 새로운 `Confectory.Reference.*` 타입 지원은 별개다. 같은 게시 세대의
reader/authoring/runtime을 사용하고 원문·ID·profile을 유지한다. 자동 downgrade나 TYPE만으로
버전/데이터 손상 판정, 구 설치본의 소급 수정은 없다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 88bd4c9303fb29581a4b41652e7d42bba563f876 | 385e7a602e363febcf717c0b10169b2f7056c281d35d62a01cdb7cc3dd1a28d7 | 54069068 |
| rollback | 462f9ac50112c260af2934e7bdea4731948d0b94 | 0dfb32b2a20d1c8d32b642ae25222d3efcb9ccdcfe71a4b2468e497130622b18 | 54069010 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/d1feb18fd6014218956409fbb3cc9506.json` · evidence SHA256 `7e2304a47e265804f4f2dbb06c72ad9ac5a7145addb2e518f6aede45106fcb91`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/5dcfb102a04240f6b2774361d5b70788.json` · evidence SHA256 `bf4684456ab03c86701d89e5843be0356156d88934e2382d8e9cc3e627cddf6e`.
증거와 두 관리 package를 SHA로 재확인했다. 기존 승인된 latest/정상 rollback2세대 교대와
이번 소유 RAM 임시물 정리만 적용했다. 과거 비관리 자료·원래 checkout/main을 보존하며
교대된 세 번째 관리 package 전체도 계속 보관한다고 주장하지 않는다. 여유 25349509120bytes
(23.61GiB)다.

다른 표시 문맥과 고정7행 forwarded/opaque source closure, 고정8행 여러 함수의 실제
계약/본문·공유 caller closure는 [유한 잔여](V666_STANDALONE_RETURN.md)에 유지한다.
완료된 M11/M12/M4를 다시 열지 않는다. 실제 Windows/WebView2·물리 기기·OS IME·GPU/audio·
전체 UI는 미검증이다. 새 자격증명/외부 grant·라이브 AI/과금·main 변경은 없다.
