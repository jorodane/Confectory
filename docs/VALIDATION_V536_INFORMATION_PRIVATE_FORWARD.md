# 부모 private 계약·branch/switch·enum 저장 검증

범위는 [고정 5행](V536_I5_6_NESTED_SCOPE.md)의 직접 소유 private 계층이다. 이전 게시 `1554bf2`의 결과와 이번 결과를 합산하지 않는다. 원본 v536 레이아웃·CSS·권한·사용자 C# 원문과 명시 Review/Confirm 경계는 유지한다. 계정 로그인·유료 AI·사용자 프로젝트 실행 없이 격리 fixture만 사용한다.

## 실제 연결

- 부모 계약과 바깥 입력·출력, 각 private 자식 출력은 원본 호출 대응창의 별도 행에서 명시 선택한다. 깊이 2의 직결 전달과 추가 code·수식·live alias·계산 반환을 같은 후보/CAS로 처리한다. 각 frame의 입력/출력 namespace를 구별하며 동명 leaf·다른 형제·정확한 64비트 값·원문을 보존한다.
- private branch/switch C#의 고정 native 경계와 switch Result enum을 유지하고, 사용자가 작성한 본문·helpers를 같은 owner 후보에 넣어 실제 조립 C#으로 검증한다. 자동 C# 재작성은 하지 않는다.
- 별도 private enum Script의 포트 이름·순서/값과 본문·helpers는 물리 root checkpoint 하나에 저장한다. 원래 private graph/node/source·정의/source 해시를 journal·저장·settled receipt에 결부한다. scope/copy/slot 권한을 확대하지 않는다.
- `Schema unavailable`은 실제 스키마 요청 실패와 구별했다. 함수 선택 상태에서 이전 정보창의 배경 복원이 null schema를 렌더하려는 표시였다. 현재 schema·draft·layout ID가 맞을 때만 복원하며, 기존 입력을 보존하고 실제 정보 재열기로 복원되는지 확인한다. 실제 사용자 요청의 실패를 성공으로 바꾸지 않는다.

## 검사와 수정 해석

실제 API와 기본/독립 창에서 저장·Undo/Redo·취소·장치 오류·동시 변경·응답/receipt 유실·프로젝트 전환·재시작·Review 취소/재검토·명시 Confirm을 확인한다. 누락된 부모/자식 선택·잘못된 qualified 경로·낡은 해시·사용 중인 출력 해제·계산 입력/별칭 유실·C# 오류는 전체 미적용이다. 기존 계약의 본문만 바꿀 때 불필요한 부모 계약 갱신을 요구하지 않는 회귀도 포함한다.

private enum 응답 유실 뒤 재시작 시, 이미 완료된 저장의 receipt 조회보다 오래된 입력 proof 검사가 먼저 실행되는 복구 결함을 수정했다. 최초 private 바인딩이 있는 같은 graph의 보관 요청만 기존 결과 조회 경로로 보내고, 서버가 원래 receipt와 현재 소스 closure를 확인한 경우에만 입력을 정리한다. 모르는 결과나 다른 편집자의 변경은 성공으로 치환하지 않는다.

새 내부 자식 출력의 명시 선택을 기존 "공개 출력 변경 없음" UI 가드가 잘못 거절한 결함을 수정했다. 해당 새 행만 별도 취급하며 서버의 exact type·사용처·전체 후보 검증은 유지한다. 초기 API fixture의 없는 `leaf_id`, 예상 거절 응답의 누락된 `result` 색인은 fixture 오류로 수정했다. 계산 반환을 사용자가 다른 호환 출력으로 명시 이동한 정상 후보를 실패로 기대한 추가 검사도 원래 의미에 맞게 바로잡았다. 이 오류들을 보호 완화나 제품 성공으로 세지 않는다.

집중 결과는 **58 check**다(순수 후보 10·실제 API 14·실제 렌더러 26·영향 회귀 8). 실패 후 같은 검사를 재실행한 횟수나 이전 게시 단위를 합산하지 않았다. [선별 근거](evidence/v536-information-private-forward/focused-checks.json), [수동 본문](evidence/v536-information-private-forward/manual-body.png), [기존 대응창](evidence/v536-information-private-forward/private-mapping.png), [모바일 폭 private enum](evidence/v536-information-private-forward/private-enum-mobile.png) 및 [원본 구조/CSS 근거](evidence/v536-information-private-forward/layout-evidence.json)를 남긴다. Native Release는 경고·오류 0건이고 Linux 빌드 stderr는 0이다. clean checkout 및 패키지 기동 검사는 별도 재현 결과로 기록한다.

## 완료 경계

현재 부모 전달 지원은 frame마다 forwarded 자식 하나인 직접 소유 계층이다. 같은 private frame의 여러 forwarded 자식 계약 동시 변경은 미구현이며, 기존 설계의 후속 구현이다. 계산에 필요한 새 값/저장소를 추정하거나 공유/부모/donor를 수정하지 않는다. copy/등록 receipt·여러 함수 공유 caller·고급 타입/표시명은 기존 7~9행이다. 이번 단위와 5행 전체/I5-6/v536 전체 완료를 구별한다. 실제 Windows apphost/WebView2·모바일 기기 실행과 Library 전달은 미검증이다.

Windows x64 교차 패키지의 manifest 2,340개(자기 manifest 포함 실제 2,341개) 해시와 production source 8개·Native/Core DLL 2개의 바이트가 모두 일치한다([기록](evidence/v536-information-private-forward/package-bytes.json)). manifest SHA-256은 `bf29992873e928727cc8ebd9d4e6c240ef31d9a3fb33ced58f10c7c818136768`이다. 패키지는 로컬 산출물이며 전달 성공을 의미하지 않는다.

## clean checkout·패키지 마감

검증한 실행 소스는 `9c6fd9fa3ed3f1b9c3314c9dd1ea74a607eaafda`다. 깨끗한 checkout의 Native Release는 경고·오류 0건, Linux 빌드 stderr는 0이다. 추가 계산이 있는 부모 계약 API 3건과 private enum 저장 실패·응답 유실·재시작·Confirm 화면 3건을 재현했다([기록](evidence/v536-information-private-forward/clean-checks.json)). 집중 58건과 별개인 재현 6건이며 기능 수에 중복 합산하지 않는다.

실제 Git retained CRLF/속성 pull과 fresh LF에서 74개 리소스를 기동하고 content/encoding/BOM/binary/budget 변조를 거절했다([기록](evidence/v536-information-private-forward/resource-checks.json)). 원래 working tree 바이트를 보존했다.

패키지의 managed 엔진을 SDK 없는 격리 runtime·별도 작업 디렉터리에서 기동하여 74개 리소스와 최소 로그인 화면, 누락/변조 의존성 거절, fixture 프로필/명시 override 보존을 확인했다([기록](evidence/v536-information-private-forward/package-probe.json)). Windows x64 교차 패키지 경로는 `/workspace/artifacts/v536-information-private-forward/Windows-x64/Confectory.exe`다. 실제 Windows apphost/WebView2·실제 모바일 기기는 실행하지 않았다. 계정 로그인·추론·사용자 프로젝트 실행과 Library 전달도 수행하지 않았다.

후속 마감 커밋은 검증 문서·증거만 추가하며 위 실행 소스와 동등하다. 이번 직접 소유 부모 계약/branch·switch/private enum 지원 단위를 마감한다. 같은 frame의 여러 forwarded 자식은 5행에 남아 있으므로 5행 전체·I5-6·v536 전체 완료로 처리하지 않는다.

후속 여러 forwarded 자식/연결된 부모 합성은 [VALIDATION_V536_INFORMATION_MULTI_FORWARD.md](VALIDATION_V536_INFORMATION_MULTI_FORWARD.md)에서 마감한다. 위 단일 자식 제한은 이 문서의 이전 게시 시점 기록이며 현재 지원 경계는 V536_I5_6_NESTED_SCOPE.md를 따른다.
