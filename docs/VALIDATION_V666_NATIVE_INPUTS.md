# 명시 native 입력 타입·본문 검증

제품 동결 `dd11b88ed8ad034f9e3e7c4e9ec2fd781d238176`의 [지원 범위](V666_NATIVE_INPUTS.md)를 **신규 39단계·재사용0·최종 실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout·격리 HOME/NuGet·빈 엔진 cache의 Release/MCP·실제 Linux 엔진,
새 Windows 교차 패키지·구조/무결성·전체 ZIP 복원을 실행했다. NuGet은 검증한 기존 seed를
각 격리 환경으로 복사한 뒤 restore했다. 개발과 최종 수는 합산하지 않는다.

- 게시8436cb7에서 각각의 명시 타입/본문/호출 후보는 유효하지만 공동 후보만 거절됨을 재현했다.
  원래 프로그램70, 새 string 값/원래 연결 해제/수동 native 선언·본문 편집 뒤 프로그램21을
  실제 실행했다. 유지된 두 번째 count가 첫 번째 결과를 소비한다. 자동 C# 치환·타입 변환은 없다.
- 단일·정역순 공동 후보, 원래 쓰기 hash와 한 그룹을 확인했다. 역할·반환·이름·입력 수 변경,
  잘못된 대응, 누락/오래된 본문·호출 계획, 잘못된 native 선언·C# 코드·JSON 값·연결 해제와
  문맥 삽입은 전체 거절했다. 기존 forwarded/opaque 보존, ordinary caller 거절·ref·private 이름
  대응·로컬 import의 적용 가능한 회귀도 새로 검사했다.
- 기존 상세창의 타입 선택·호출 값·연결 해제·native 본문 편집에서 취소·세 단계 Undo/Redo·
  미저장/저장 cold·checkpoint 쓰기 실패/재시도·owner 경합·Save/settlement 응답 유실을 확인했다.
  실제 trusted Save 활성화와 거절을 확인하며 이미 발행된 명령을 임의 재실행하지 않는다.
- 후속 정보 설명 및 함수 설명 Save는 새 ABI·본문·caller 그룹과 같은 version3 readGuards를
  보존했다. 전체/일부 guard 누락·hash/path·관측 밖 경로·owner/version·implementation proof
  누락을 거절했다. Save 전 helper 선언 변경과 Review 뒤 helper 선언·본문, caller graph,
  선택 native 본문·선언의5개 경로 변경은 Confirm 전체 거절이었다. peer·checkpoint·원래 receipt를
  보존하고 정확한 복원·cold 뒤 새 Review/Confirm은 실행21로 성공했다. 편집하지 않은 helper의
  bytes·inode·mode·mtime도 유지했다.
- 성공 Save 응답을 지연하는 동안 들어온 실제 설명 입력은 반복 Save가 비활성인 동안 남았고,
  cold에서 복원됐다. 후속 명시 Save는 원래 guard를 유지했고 Review 취소·새 Confirm·cold는
  설명과 새 입력 계약·두 본문을 함께 보존했다.
- 현재3D 전송의 정체/부분 POST·reload8회·단절·child/root·프로젝트 왕복/cold와 패키지 실패 수명을
  검사했다. 이는 과거 간헐 빈 #app의 원인을 확정한 증거가 아니다.

개발은 총 22단계 시도 중3건의 검사기 실패가 있었다. 첫 fixture의 export 루프가
import alias를 덮어써 제품 실행 전에 실패했다. 두 UI 시도는 Undo 횟수를1/2로 가정했으며
보관한 trace가 타입·호출 대응·본문의3단계를 입증했다. 검사기를 수정하고 정상 UI를 통과했다.
제품 Undo를 변경하지 않았다. 최종은 현재 동결 코드와 수정한 검사에서 전부 새로 실행했다.
[구 Reference reader 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는 해시를 확인해 개발 증거에
보관한 과거 증거 재사용이며 이번 최종 단계 수에 포함하지 않는다. 같은 게시 세대 도구를
사용하며 자동 migration/downgrade·기존 profile 삭제나 새 ABI 문법은 없다. 새 조합의 저장·재검토는
동일 게시 세대 도구로 검증했으며 이전 authoring 세대의 새 그룹 재편집/검토 호환은 주장하지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | dd11b88ed8ad034f9e3e7c4e9ec2fd781d238176 | 47c487670187fb38628024811ec3135c7a4b10990e83da8b268db9f2679c4d07 | 54079996 |
| rollback | 59a2820bede5b8d2bd36f82dba3d37c8db34d750 | 74248d6eb7a19682ac147c26b358b47139ed1373c75239a166e88b9f59d1e9fa | 54077176 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/6c7af3d658b440f69f7cc00ce93315da.json` · evidence SHA256 `3569027d6d203e0e9958b41fa28bed58074b982879f1cc005b3c9f4e18712a39`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/4c6138e4989b4b7a84f9a25056a7604f.json` · evidence SHA256 `bc56cc8d5e322aec044f353589ccef6ebcdea9c6d9ab6a3e45c8d12abee0b471`.
두 관리 package와 증거 SHA를 다시 확인했다. 기존 latest/직전 정상 rollback2세대 교대와
이번 소유 RAM 임시물 정리만 적용했다. 원래 checkout/main·비관리 자료·과거 증거는 유지한다.
퇴역한 세 번째 관리 ZIP 전체의 보존은 주장하지 않는다. 여유 25212129280bytes(23.48GiB)다.

역할·반환/출력·입출력 수 변경, opaque/private C# 명시 계획, 선택 native callee 간 의존성 및
다른 원래 import/등록 외부 관측 결합은 같은 고정7/8행 잔여다. 선택 조합이나 migration을
새 필수로 늘리지 않고 M11/M12/M4를 다시 열지 않는다. 부모/외부 직접 편집 거절은 원래
소유권 보호다.64-member Review·240 source checks·2048 known source 예산, 권한·override
계약·authored layout·Review/Confirm·최종 CAS를 유지했다. 실제 Windows/WebView2·물리 기기·
IME·GPU/audio·전체 UI 전수 검증은 수행하지 않았다. 새 credential/grant·라이브 AI/과금·main 변경은 없다.
