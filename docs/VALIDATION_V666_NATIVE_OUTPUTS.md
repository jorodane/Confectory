# 명시 native out 타입 공동 저장 검증

제품 동결 `56465896ba241f64ae2d7c09fe7c333e4067bc9f`의 [지원 범위](V666_NATIVE_OUTPUTS.md)를 **최종 신규 40단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout·격리 HOME/NuGet·빈 엔진 cache의 Release/MCP·실제 Linux 엔진,
새 Windows 교차 패키지·구조/무결성·전체 ZIP 복원을 실행했다. 확인한 기존 NuGet seed를
각 격리 환경에 복사해 restore했다. 개발과 최종 단계 수는 합산하지 않는다.

- 게시 d4a147ab에서 원래 실행38과 각 단일 out long→double/본문/기존 소비자의 명시 return
  대응은 유효하지만 공동 후보만 거절되는 것을 재현했다. 기존 상세창에서 count 타입과
  호출 계약을 직접 선택하고 C# 선언·본문을 검토한다. 입력·역할·수·순서·반환 타입은 유지한다.
- 같은 임시 Main 원문으로 실제 생성된 두 IInvoke의 CLR 반환/out 타입과 값을 확인했다.
  원래 long40/out long34, 변경 후 long34/out double1.25이며 caller는 전후38이다.
  첫 old count를 쓰던 둘째 amount와 둘째 old count를 쓰던 caller 반환만 직접 선택한
  compatible long return으로 대응한다. 새 count 값은 직접 작성한 `count=real`이다.
  암묵 숫자 변환·새 바인딩·C# 자동 재작성이나 제품 코드 생성의 reflection 대체는 없다.
- 단일·정역순 공동 후보·원래 쓰기 hash·한 그룹을 검증했다. 역할·반환/입력 타입·이름·수,
  잘못되거나 누락된 out 교체 mapping, 본문/호출 계획 누락·stale hash·잘못된 native 선언,
  out을 할당하지 않는 C#, 호환되지 않은 출력 대응·새 입력·caller hash·문맥 삽입의
  19개 fault는 전체 거절했다. 기존 입력 타입·void→반환 추가·forwarded/opaque 보존·
  ref·private 이름·로컬 import 회귀도 최종 코드에서 새로 실행했다.
- 기존 상세창의 타입·출력 대응·본문 UI에서 취소·Undo/Redo·미저장/저장 cold·checkpoint
  실패/재시도·owner 경합·Save/settlement 응답 유실을 확인했다. 실제 trusted Save의
  활성화/거절과 복원을 검증하며 이미 발행된 명령을 임의 재실행하지 않았다.
- 후속 정보/함수 설명 Save는 새 out ABI·본문·caller 그룹과 version3 readGuards를 유지했다.
  guard 전체/일부 누락·hash/path·관측 밖 경로·owner/version·implementation proof 누락을
  거절했다. Save 전 helper 선언 변경과 Review 뒤 helper 선언·본문/caller graph/선택 native
  본문·선언의5경로 변경은 Confirm 전체 거절이었다. peer·checkpoint·원래 receipt와 입력을
  유지했고 정확한 복원·cold 뒤 새 Review/Confirm은 실제 반환/out·실행38을 확인했다.
  편집하지 않은 helper의 bytes·inode·mode·mtime도 유지했다.
- 성공 Save 응답 지연 중 추가한 실제 설명은 반복 Save가 비활성인 동안 남고 cold에서
  복원됐다. 후속 명시 Save·Review 취소·새 Confirm·cold는 새 out 계약·두 본문과 설명을
  함께 보존했다. 새 package와 전체 복원본에서도 저장·응답 유실·늦은 입력·실행을 확인했다.
- 현재3D 전송의 정체/부분 POST·reload8회·단절·child/root·프로젝트 왕복/cold와 package
  실패 수명을 검사했다. 과거 간헐 빈 #app의 원인을 확정한 증거로 세지 않는다.

개발은 23시도 중 22통과·해결된 UI 실패1건이다. 최초 공동 guard가 null 교체만
허용했으나 실제 화면은 `count→count` identity를 보냈다. 기존 단일 후보가 이 대응을 받아들이는
진단 증거와 최초 실패 요청·코드를 보존했다. 공동 guard를 기존 두 대응 형식에 맞춰 수정하고
별도 corrected 빌드·후보·UI 검증을 통과했다. 최종은 현재 동결 코드에서 전부 새로 실행했다. [구 Reference reader 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는 해시를
대조해 개발 증거에 보관한 과거 증거 재사용이며 이번 최종 수에 포함하지 않는다.
새 그룹의 저장·재검토는 같은 게시 세대 도구 기준이며 이전 authoring 세대의 새 그룹
재편집/검토 호환은 주장하지 않는다. 새 문법·자동 migration/downgrade·기존 profile 삭제는 없다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 56465896ba241f64ae2d7c09fe7c333e4067bc9f | 2e22e37e9e06d144a04a7764696f0dfa17ea1e9ca36e7fbe4e798de370a20b26 | 54085083 |
| rollback | 2cf25620296635f88ab48d47fcff9b5e77516201 | 50ad7b70ae209a07be42d4d1069222c71ba1c4ed1622a8716f4fecd319da36ce | 54083942 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/4d8b276b8765445d94dc0edbd2ff5aa9.json` · evidence SHA256 `742412b2cc1d70d59d30ec65885fb6ec47ccc14a19fff3a561b8652c59889367`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/48a21bca5296407ab67d081406f5d8bb.json` · evidence SHA256 `e79b01c0b33e605a6fc021c9bdf72dff1dba0a93e571cb266a906647de48029f`.
두 관리 package와 증거 SHA를 다시 대조했다. 기존 latest/직전 정상 rollback2세대 교대와
이번 소유 RAM 임시물 정리만 적용했다. 원래 checkout/main·비관리 자료·과거 증거는 유지한다.
퇴역한 세 번째 관리 ZIP 전체의 보존은 주장하지 않는다. 여유 25148891136bytes(23.42GiB)다.

역할 전환 UI·out 추가삭제/입출력 정의 변경, opaque/private 명시 C# 계획, 선택 native callee
사이 의존성과 다른 원래 import/등록 외부 관측 결합은 같은 고정7/8행 잔여다. 조합별 migration을
새 필수로 늘리거나 M11/M12/M4를 회귀 없이 다시 열지 않는다. 부모/외부 직접 편집 거절은
원래 소유권 보호다.64-member Review·240 source checks·2048 known source 예산, 권한·override
계약·authored layout·Review/Confirm·최종 CAS를 유지했다. 실제 Windows/WebView2·물리 기기·
IME·GPU/audio·전체 UI 전수 검증은 수행하지 않았다. 새 credential/grant·라이브 AI/과금·main 변경은 없다.
