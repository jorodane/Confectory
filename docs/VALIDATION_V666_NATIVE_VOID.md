# 명시 native 반환 삭제·void 본문·출력 대응 검증

제품 동결 `b4906f6a7ad40875c677e21e6731843363de65a8`의 [지원 범위](V666_NATIVE_VOID.md)를 **신규 39단계·재사용0·최종 실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout·격리 HOME/NuGet·빈 엔진 cache의 Release/MCP·실제 Linux 엔진,
새 Windows 교차 패키지·구조/무결성·전체 ZIP 복원을 실행했다. 검증한 기존 NuGet seed를 각
격리 환경으로 복사한 뒤 restore했다. 개발과 최종 수는 합산하지 않는다.

- 게시16672b90에서 단일 반환/본문/출력 대응 후보와 원래 실행50은 유효하지만 공동 후보만
  거절됨을 재현했다. 두 반환을 삭제해 void로 직접 선택하고 이전 long 소비를 기존 out
  count로 명시 대응한다. 새 native 선언·본문은 직접 편집하며 입력·out 계약/ID/순서와 선은 유지한다.
- 원래부터 작성한 같은 임시 Main 원문이 실제 생성된 두 provider의 IInvoke 반환 타입·값·out 값을
  검사한다. 원래 long40/out34, 변경 후 void/null과 out38/34를 확인했고 공유 caller는 실행42다.
  caller의 둘째 amount와 최종 long 반환만 명시 count에 대응한다. 생산 코드의 원본을 reflection으로
  수정하거나 자동 C# 치환·숫자 변환을 추가하지 않는다.
- 단일·정역순 공동 후보·원래 쓰기 hash·한 그룹을 확인했다. 역할·입력 타입/이름·수 변경,
  잘못된 args 대응, 누락/오래된 본문·호출 계획, 잘못된 native 선언, void에서 반환값을 돌려주거나 out을 할당하지 않는 C# 코드,
  비호환 반환 대응·out identity 변경·새 입력·caller hash·문맥 삽입은 전체 거절했다.
  직전 native scalar 반환 변경, forwarded/opaque 보존·ref·private 전달 이름과 로컬 import 회귀도 새로 검사했다.
- 기존 상세창의 반환 타입 선택·출력 대응·본문 편집에서 취소·세 단계 Undo/Redo·미저장/저장 cold·
  checkpoint 쓰기 실패/재시도·owner 경합·Save/settlement 응답 유실을 확인했다. 실제 trusted Save
  활성화와 거절을 확인하며 이미 발행된 명령을 임의 재실행하지 않는다.
- 후속 정보/함수 설명 Save는 새 void ABI·본문·caller 그룹과 동일 version3 readGuards를 유지했다.
  guard 전체/일부 누락·hash/path·관측 밖 경로·owner/version·implementation proof 누락을 거절했다.
  Save 전 helper 선언 변경과 Review 뒤 helper 선언·본문, caller graph, 선택 native 본문·선언의
  5개 경로 변경은 Confirm 전체 거절이었다. peer·checkpoint·원래 receipt를 보존하고 정확한 복원·
  cold 뒤 새 Review/Confirm은 실제 ABI/반환/out 값과 실행42를 확인했다. 편집하지 않은 helper의
  bytes·inode·mode·mtime도 유지했다.
- 성공 Save 응답 지연 중 추가한 실제 설명은 반복 Save가 비활성인 동안 남았고 cold에서 복원됐다.
  후속 명시 Save가 원래 guard를 유지했으며 Review 취소·새 Confirm·cold는 설명·새 반환과 두 본문을
  함께 보존했다. 새 package와 전체 복원에서도 실제 저장·응답 유실·늦은 입력과 실행을 확인했다.
- 현재3D 전송의 정체/부분 POST·reload8회·단절·child/root·프로젝트 왕복/cold와 package 실패 수명을
  검사했다. 이는 과거 간헐 빈 #app의 원인을 확정한 증거가 아니다.

개발 16단계는 모두 통과했으며 개발 실패는0건이다. 범위 선정 중 완료한 동일
게시본의 baseline bootstrap은 기존 기록을 이어 사용해 중복 build/workspace를 만들지 않았다.
반환 삭제는 기존 UI와 단일 검증을 재사용하며, 직접 native 역할 전환 UI는 별도 잔여로 남긴다.
최종은 현재 동결 코드에서
전부 새로 실행했다. [구 Reference reader 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는 해시를 확인해
개발 증거에 보관한 과거 증거 재사용이며 이번 최종 단계 수에 포함하지 않는다. 새 조합의 저장·
재검토는 동일 게시 세대 도구로 검증했으며 이전 authoring 세대의 새 그룹 재편집/검토 호환은
주장하지 않는다. 새 문법·자동 migration/downgrade·기존 profile 삭제는 없다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | b4906f6a7ad40875c677e21e6731843363de65a8 | 8e130b12a7ff027269f9215bcc02bd640323132dc6b46178893e4c225a28d0d2 | 54083958 |
| rollback | 39583e77fa0e55f7d4bbcb0be72399af387fefbb | 0733db48b32386e304199aea18f236abca4682eb388bdd763ad7bf9f3da499c8 | 54083855 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/e9abc8bc0d6d4bd28dca42587822ce8a.json` · evidence SHA256 `e7e0a1f3fe6a8def1d5f340a83e461e503f806e4d8871e01511621dc068a33ae`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/5d96cd2cdc5a475a8fb7633d9f82d4a3.json` · evidence SHA256 `b69154738596312d75388ba9bfdda2c501299b0c4de413a13758100c75c930a7`.
두 관리 package와 증거 SHA를 다시 확인했다. 기존 latest/직전 정상 rollback2세대 교대와 이번
소유 RAM 임시물 정리만 적용했다. 원래 checkout/main·비관리 자료·과거 증거는 유지한다.
퇴역한 세 번째 관리 ZIP 전체의 보존은 주장하지 않는다. 여유 25180282880bytes(23.45GiB)다.

역할·out/입출력 정의 변경과 역방향 void→값, opaque/private C# 명시 계획, 선택 native callee 사이 의존성 및
다른 원래 import/등록 외부 관측 결합은 같은 고정7/8행 잔여다. 선택 조합이나 migration을 새 필수로
늘리지 않고 M11/M12/M4를 다시 열지 않는다. 부모/외부 직접 편집 거절은 원래 소유권 보호다.
64-member Review·240 source checks·2048 known source 예산, 권한·override 계약·authored layout·
Review/Confirm·최종 CAS를 유지했다. 실제 Windows/WebView2·물리 기기·IME·GPU/audio·전체 UI 전수
검증은 수행하지 않았다. 새 credential/grant·라이브 AI/과금·main 변경은 없다.
