# 정보 헤더와 C# 본문 결합 저장 검증

최종 runtime `464cb0c2c07b5b5cffeabe25d2112cc8451779b2`의 **신규43단계·재사용0**을 통과했다. 분포 `{"crlf": 16, "lf": 18, "restored": 4, "windows": 2, "package": 1, "header": 1, "packaged": 1}`.
[원래 수용 근거·지원·호환 경계](V666_HEADER_BODIES.md)를 따른다.

| 범위 | 실제 결과 |
|---|---|
| 게시본 재현 | 각 본문·owner 설명/아이콘 및 본문-only 그룹은 유효하고 원래 프로그램46 실행. 원본460px 창에서 네 입력의 한 Save만 거절되며 입력/checkpoint/원본 보존 |
| 원자 후보 | 같은 계약의 두 명시 본문과 owner 설명·아이콘을 한 후보로 합성. 역순 결과 동일. 중복 설명/아이콘·추가 키·과대 설명·잘못된 아이콘·구조/계약 변경7개 전체 거절 |
| 실제 UI | 기본/독립 창의 원래 구현 선택·코드 편집 취소·헤더/함수 Undo/Redo·미저장/저장 cold·Review 거절/새 Confirm·실제 프로그램26 확인. C# caller의 CRLF/Unicode/별칭·원문과 정확64 기본값 유지 |
| 수명/격리 | 쓰기 실패 뒤 네 입력/원본 checkpoint 유지와 재시도, 저장/결과 조회 응답 유실 뒤 cold receipt 확인·중복 적용 없음, peer 충돌·동일 namespace 프로젝트 왕복·취소를 새로 확인 |
| 늦은 입력 | 실제 Save 접수와 결과 전달 사이 editable 헤더에 새 설명 입력. 원래 네 입력만 저장하고 새 설명은 cold 뒤 보존. 재저장도 원래 readGuards 유지하며 새 Review/Confirm·실행26 |
| 후속 저장 | 설명과 아이콘의 두 후속 Save/cold는 같은 함수/body/manifest/owner footprint와 원래 해시 유지. Save 전 peer 변경은 checkpoint CAS 직전 거절. metadata-only receipt의 guards 누락·경로/해시/owner/version6개 변조 거절 |
| Review/최종 CAS | 첫 Save와 후속 Save 각각 cold 전후 caller 변경, Review 후 header/body/함수 변경을 거절. 전체 checkpoint/peer·본문 입력/원래 receipt 유지. 정확한 복구와 명시 새 Review/Confirm 후 실행20/26 |
| 호환/회귀 | 기존 본문-only native caller 흐름과 구 leaf/ordinary Blueprint의 빈 readGuards를 새로 실행. 공개/override 계약·원본 소유권·권한·레이아웃·receipt version3/최종 lease 유지 |
| 최종 패키지 | LF/CRLF no-hardlinks·독립 HOME/NuGet·Release/MCP·빈 엔진 cache에서 새로 검사. 새 Windows 교차 패키지 구조/해시·포함 Linux 엔진 UI·전체 ZIP CRC/SHA/파일/디렉터리 mode 복원·복원 CAS/후속 저장/응답 유실·실패 수명관리 통과 |

제품 변경은5파일이다. frontend/HTML/CSS/JS·공개/native ABI·code generation·
기존 parser/source compiler·권한·최종 Confirm source lease는 그대로다. 알려진 소유
헤더/함수의 관측과 기존 version3 원자 후보/receipt만 연결했다. 다음 표시 Save는
이미 저장한 본문 그룹의 해시를 상속하고 CAS 직전에 경로/링크/2MiB 예산과 실제
snapshot을 확인한다. 새 원본으로 재기준화하거나 다른 closure/권한을 만들지 않는다.

개발은36단계 중30통과·6실패를 보존했다. 초기 컴파일의 지역 변수 충돌1개,
owner 결과 위치·독립 입력 이후 Undo 보호·비동기 요청 접수 응답을 잘못 가정한
fixture3개를 각각 수정했다. 실제 제품 결함2개는 후속 설명 Save의63→0 readGuards
유실과, 해시 상속 후에도 Save 시점의 peer 변경 비교가 Review로 미뤄지는 경로였다.
해당 실패 후보는 Confirm하지 않았으며 최종 코드에서 후속 Save/Review/최종 CAS와
늦은 입력 UI를 통과했다. 초기에 통과한 UI는 최종 검사 수에 재사용하지 않았다.
기존 전체-map Undo의 새 독립 입력 보호를 약화하지 않았다.

초기 메모리 사전검사2회 차단과 정상 실행 중 workspace 소유 잠금의 재진입 거절도
별도 로그로 남겼다. 한정된 보관 ZIP의 read-only FD/hash/metadata 확인 후 파일별
캐시 조언만 사용했으며 전체 cache/메모리 예산을 바꾸거나 중복 빌드하지 않았다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 464cb0c2c07b5b5cffeabe25d2112cc8451779b2 | 4782033421f891e9f62e7d868e418896aa9e873bcd733c2ac052b9e26b3fb452 | 53,863,807 |
| rollback | 6a9b48d2af44eb4fa0227d80b164c24f17bcd164 | e7fd42884d7a717898bcdd979e065feb9679e26eba29ce703cda29ea9dbfe479 | 53,860,812 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/1d2cdb7105fd473cb80d8ee8996e7830.json`, evidence `d2d0799091acd390aa6f586cc49cf55565d10a934a66fc66333b2f07d838da45` (9,564,097B).
개발 evidence `739ee68e9e705959940a01ca81014eddb8a076bcfaeafe6eda71276db12a602e` (10,350,812B).
양쪽 evidence manifest와 보관 ZIP2개를 재검증했다. 시작 index `f3d0fe0b267cb538b137523324520475b69f70964bf8bc95d087d1d1f5ee0242`,
종료 sidecar `0faf5d85d555017712d28f6de1dfd61fd364529929e6af8eaf80c4a29fcc9ebf`. 최종 preflight 원본을 덮어쓰지 않고 개발 계획/실패와
캐시·원래 읽기 검증 유실 증거를 별도 이름으로 보존했다.

latest/rollback 두 ZIP만 승인된 관리 절차로 교대했다. 이전 rollback
`2897f3709cd44cf10c954ed9dd6a578dd421ec3d`의 관리 ZIP만 교체했고 과거 증거·사용자 데이터·원본 checkout은
유지했다. 개발/최종 RAM 작업공간은 evidence 봉인/소유 identity 확인 후 정리했다.
재생성 build outputs는 정확한 SHA 목록으로, 원문·checkpoint·실패 로그/화면은 archive에
보존했다. 이 단위의 새 owned bytecode만 해시 목록을 남긴 뒤 정리했다.

단위 시작 여유 25,836,576,768B, 마감 25,810,837,504B(24.0382GiB), 순증가
25,739,264B(24.5469MiB). 관측 최대 cgroup memory 9,389,961,216B,
최종 stage 최소 디스크 25,820,041,216B. 추가9GiB+safety1GiB·RAM4GiB+
reserve512MiB·최종 evidence512MiB의 기존 예산은 유지했다.

고정7/8/9행의 다른 실제 closure·고급 타입 선택/핀 표시명은 기존 잔여다. 가능한
타입/문맥 조합마다 요구를 추가하지 않는다. 신원/그룹 backend·종류 CLR/사용 중
항목 삭제 정책은 임의 확정하지 않으며 M11/M12/M4는 회귀 없이 다시 열지 않는다.

실제 검증은 Linux native 엔진·Chromium·생성한 격리 fixture다. 교차 Windows
패키지는 실제 Windows/WebView2 실행이 아니다. 모바일·물리 IME/GPU/audio·사용자
프로젝트·전체 UI·Space/Library 전달과 모든 구 reader 교환은 미검증이다. 초기 빈 화면
원인은 미확정이며, 과거 Save 클릭 요청 미발행의 간헐 원인도 이번 통과로 해결했다고
보지 않는다.
