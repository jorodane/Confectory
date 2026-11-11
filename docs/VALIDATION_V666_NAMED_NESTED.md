# 공개 이름·native 본문·private 호출자 검증

제품 동결 `6ff8c0765d72f7664b64c76b803137f5401de6d0`의 [지원 범위](V666_NAMED_NESTED.md)를 **신규 38단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout·HOME/NuGet·빈 엔진 cache에서 Release/MCP·실제 엔진,
새 Windows 교차 패키지·구조/무결성·전체 ZIP 복원을 실행했다. 개발 결과와 합산하지 않는다.

- 게시89ca49e4에서 각 native 본문/공개 입력 이름 단일 후보와 실제 중첩 프로그램41은
  유효하지만 공동 후보만 거절되는 것을 재현했다. 기존 명시 C# 이름 모드와 실제 구현
  선택창에서 두 native 본문을 직접 선택·편집했다. 공동 Save 뒤 실제 실행은21이다.
- 정·역순 공동 후보와 원래 hash·단일 group을 검사했다. depth2와 형제 프레임의 동명
  qualified C# 기록·실제 CRLF/한글/emoji 원문, native 선언, 프레임별 계약/인자·지역값과
  정확64 값·노드 ID·실행선·출력은 유지하고 선택된 call의 명시 이름 대응만 갱신했다.
- 타입/역할/잘못된 이름 대응/native 선언, 위조·누락 qualified C#와 값 binding은 전체
  거절했다. copy/forwardCallerStorage/implementationContext/postCall의 기존 source
  경계도 유지한다. 기존 ref와 같은 계약 private caller, 직전 Blueprint/native 혼합
  후보를 새로 회귀했다. 새 필수 조합이나 C# 자동 재작성은 없다.
- 실제 UI 취소·Undo/Redo·미저장/저장 cold·checkpoint 쓰기 실패/복구·owner 경합과
  apply/settlement 응답 유실을 검사했다. 저장 성공 응답 지연 중 추가한 실제 설명은
  재시작 후에도 남았고 후속 명시 Save·Review 취소/Confirm은 새 설명과 결과21을 확인했다.
- version3 readGuards의 누락·잘못된 hash/path·관측 밖 경로·owner/version 변조는 전체
  거절했다. **후속 설명 Save 뒤에도** 정확한 guard와 group을 보존했다. Save 전 caller
  변경과 Review 뒤 header·중첩/형제 C#·graph 변경은 전체 Confirm을 막았다. peer와
  checkpoint를 유지하고 원문 복구·cold 후 새 Review/Confirm은 성공했다. 변경하지 않은
  caller header/C#의 bytes·inode·mode·mtime도 유지했다.
- 현재 실제3D의 전송 정체/부분 POST·reload8회·단절·child/root·프로젝트 왕복·cold와
  패키지 실패 수명을 검사했다. 과거 간헐 빈 #app 원인은 계속 미확정이다.

개발 18단계의 실패 2건과 원본 증거도 보존했다. 첫 UI 검사는 이미
존재하는 구현 선택창에서 편집할 native callee를 고르지 않은 fixture 문제였다. 실제
caller의 qualified C#도 나타나는 기존 선택창에서 정확한 본문을 선택하도록 수정했다.
또 후속 설명 Save 뒤 원문 복구/cold 재시도의 header 조회에서 아직 읽지 않은 caller
선언을 검증하려던 제품 결함을 확인했다. header 단계는 읽을 소유 선언을 식별하고,
이후 graph/prepare/validate와 마지막 source lease에서 전체 원문을 검증하도록 고쳤다.
이 둘을 같은 fixture 실패로 취급하지 않으며, 수정 후 실패 경로와 최종 코드를 새로 검증했다.

추가 readGuards가 없는 기존 단순 leaf 후보의 의미를 바꾸지 않는다. 이미 캡처한 named
native group과 실제 ordinary consumer graph만 후속 Save에 보존하며 새 live 기준으로
재배정하지 않는다. 기존64-member·240 read/write·2048 known source·Tree 예산, 원본과
override 계약·권한·Review/Confirm·CAS·authored layout은 유지한다.

구 Reference TYPE 거절과 optional 문자열 metadata의 [기존 바이너리 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는
개발 evidence에서 SHA만 다시 확인했다. 구 reader 신규 실행이 아닌 과거 증거 재사용이며
위 최종 단계 수와 별개다. 같은 게시 세대 reader/authoring/runtime을 사용하고 자동
migration/downgrade·소급 수정이나 원문/profile 삭제는 하지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 6ff8c0765d72f7664b64c76b803137f5401de6d0 | c7a433a7af800230a171bbd72d7930ebf1b9497dacf0382e4705658483052788 | 54080336 |
| rollback | 3c95b6657fe00ca373ad7e2235cd8b84e98ca504 | d8949b3d9a02c31e5895a858f4b1a4e62abee78382d2c168e04c05285be4c08b | 54073583 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/7ae9ab7e934f4be0a318f332a10160a3.json` · evidence SHA256 `3459f080bcf4847b8d85c0cf8aebbca7b1c311e1088238b8922367be0758829d`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/38a77e123d0e4377b667ec0dd18380c0.json` · evidence SHA256 `9d129213eec8b1024c423c52e20313ea196e24b3f947fe8fdfb31a9230dfb7cc`.
두 관리 package와 증거의 SHA를 재확인했다. 승인된 latest/정상 rollback2세대 교대와
이번 소유 RAM 임시물 정리만 적용했다. 원래 checkout/main·과거 비관리 자료와 증거는
보존하며 퇴역한 세 번째 관리 ZIP 전체를 계속 보관한다고 주장하지 않는다.
여유 25286037504bytes(23.55GiB)다.

고정7행 forwarded/opaque·다른 frame/import 계약·본문 closure와 고정8행의 위 단위 밖
실제 source 결합은 기존 유한 잔여다. 임의 조합을 필수로 늘리거나 M11/M12/M4를 다시
열지 않는다. 실제 Windows/WebView2·물리 기기·OS IME·GPU/audio·전체 UI 전수 검증은
Linux native/Chromium 자동화와 교차 패키징과 별도다. 새 자격증명/외부 grant·라이브
AI/과금·main 변경은 없다.
