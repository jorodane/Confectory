# Blueprint 계약·native 본문 혼합 저장 검증

제품 동결 `3c95b6657fe00ca373ad7e2235cd8b84e98ca504`의 [지원 범위](V666_MIXED_FUNCTION_BODIES.md)를 **신규 37단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout·HOME/NuGet·빈 엔진 cache의 Release/MCP·실제 엔진,
새 Windows 교차 패키지·구조/무결성·전체 ZIP 복원을 실행했다. 개발과 최종 수는 합산하지 않는다.

- 게시74694344에서 Blueprint 값 입력 이름 변경과 별도 native 본문 편집은 각각 유효하지만
  공동 후보만 거절되는 것을 재현했다. 원래 실제 프로그램 결과40도 확인했다.
- 기존 상세창의 명시 C# 이름 모드에서 Blueprint amount→leftAmount를 대응하고 다른 함수의
  native 본문만 직접 편집했다. Blueprint C# 원문과 code 핀·native 선언, 함수/본문/노드 ID·
  기존 공유 caller 값·실행선·출력 소비자를 유지한다. 한 Save·cold·Review 취소/Confirm 뒤
  실제 결과30을 확인했다. C# 이름과 별도 표시 이름 metadata를 혼동하지 않는다.
- 정·역순 후보와 원래 hash·한 후보를 검사했다. 타입/역할/순서/출력 변경, 잘못된 remap,
  native 선언 변경, 위조/누락 본문 hash/path/필드, C# 컴파일·보호 경계와 겹치는 ID는 전체
  미적용이었다. body 계획 전체를 제거하면 기존 유효한 이름 편집만 준비하고 본문 쓰기를
  추측하지 않는다. 기존 caller 지역값 문맥은 단일 후보/원래 실행40이 유효해도 새 혼합
  그룹 범위 밖으로 보존·거절한다. 기존 ref와 직전 native 이름·본문 후보도 새로 회귀했다.
- UI 취소·Undo/Redo·미저장/저장 cold, 실제 checkpoint 쓰기 실패·복구, 동료 owner 경합,
  apply/settlement 응답 유실과 중복 apply 없는 재시작 복구를 검사했다. 지연 성공 응답 중
  추가한 실제 설명 입력은 보존됐고 후속 명시 Save·Review 취소/Confirm도 실제 결과30이었다.
- API receipt와 편집 대상 원래 write CAS를 검사했다. Save 전 caller 변경, Review 뒤 편집
  caller graph/native 본문 변경 및 호환되지 않는 현재 caller 헤더는 전체 거절했다. 원본·
  peer·checkpoint를 보존하고 복원/cold 후 새 Review/Confirm은 성공했다. native 선언·다른
  C#/변경하지 않은 헤더의 bytes·inode·mode·mtime도 유지했다.
- 저장된 caller는 기존 읽기 전용 projection으로 현재 관측한 leftAmount 핀 이름을 전달했다.
  같은 native signature와 checkpoint를 유지하고 추가 쓰기·C# 실행이 없었다.
- 현재 실제3D 전송 정체·부분 POST 중 reload8회·단절·child/root·프로젝트 왕복·cold와
  패키지 실패 수명을 새로 검사했다. 과거 간헐 빈 화면 원인은 계속 미확정이다.

개발 20단계의 실패 2건은 보존했다. scaffold C# 기록의0값 placeholder
정의 hash를 그대로 사용한 fixture는 실제 canonical node definition으로 수정했다. 또 본문
계획 전체 제거를 실패라고 기대했지만 이는 기존 유효한 이름-only 편집이다. 남아 있는 본문
계획의 필수 필드 누락으로 negative를 수정하고, 전체 제거의 정상 경로도 별도 positive로 확인했다.
이 두 fixture 수정으로 제품 거절/권한 정책을 바꾸지 않았다.

기존 단순 ordinary/leaf 문맥의 추가 readGuards는 비어 있을 수 있다. 이번 단위는 실제 편집
파일의 원래 CAS와 현재 물리 원본의 재검증/컴파일을 유지하며 모든 미편집 원본의 공백까지
새 raw-byte lease로 묶지 않았다. 추가 관측 closure가 필요한 private/whole/wrapper/import/
외부 문맥을 암묵 포함하지 않는다. 기존 보호와 지원 경계는 그대로다.

구 Reference TYPE 거절·optional 문자열 metadata의 [보관 바이너리 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는
개발 evidence에서 SHA를 다시 확인했다. 구 reader 신규 실행이 아닌 과거 증거 재사용이며 위
최종 단계 수와 분리한다. 같은 게시 세대 reader/authoring/runtime을 사용하고 소급 수정·자동
migration/downgrade·원문/profile 삭제나 TYPE만으로 버전/손상을 단정하는 처리는 없다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 3c95b6657fe00ca373ad7e2235cd8b84e98ca504 | d8949b3d9a02c31e5895a858f4b1a4e62abee78382d2c168e04c05285be4c08b | 54073583 |
| rollback | b3fb8f1e827d81e21783add5a1677774bcb59a6d | 1a563958960b59025277f14b8be7c6ae7afab4e41728e7b045a7862fa916c250 | 54070915 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/1824000d29a542119b31ec7f26d913f8.json` · evidence SHA256 `5c16358feae6574f6b8a38bec5b2a3600cb6eb71c4fd188ae0a1f8a938e38db4`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/ef1c88f00fb84e77a8e36ccdcda6b62c.json` · evidence SHA256 `5b8e3e5ccfb99e9fe86a5f8f294d120436ff44df32c4602378438d6b135b1d0d`.
두 관리 package와 증거의 SHA를 재확인했다. 승인된 latest/정상 rollback2세대 교대와 이번 소유
RAM 임시물 정리만 적용했다. 원래 checkout/main·과거 비관리 자료와 증거는 보존하며 퇴역한
세 번째 관리 ZIP 전체를 계속 보관한다고 주장하지 않는다. 여유 25301291008bytes(23.56GiB)다.

고정7행 forwarded/opaque·다른 frame 계약/본문 closure와 고정8행의 위 단위 밖 명시 계약/본문·
공유 caller/import 결합은 기존 유한 잔여다. 모든 조합을 새 필수로 늘리거나 M11/M12/M4를 다시
열지 않는다. 실제 Windows/WebView2·물리 기기·OS IME·GPU/audio·전체 UI 전수 검증은 별도다.
새 자격증명/외부 grant·라이브 AI/과금·main 변경은 없다.
