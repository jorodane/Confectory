# v666 단일 큰 자료 보관 검증

최종 제품/검사 동결 `4ea7604d0e2a9da0d1bbc95b026fdb344aa4dc10`. 최종 **58단계(신규 27·재사용 31)**:
독립 LF 26·CRLF 23·owned IPC/새 패키지/전체 복원/실패 수명관리 9.
제품은 최초 동결 c04d15ff와 같다. 후속 두 커밋은 검사의 재개 브라우저 ID와 활성 프로젝트 바이트 대조 경로만 수정했다.
문서 마감은 제품/검사 코드를 바꾸지 않는다. 개발 실행과 선행 실패는 최종 수에 중복 합산하지 않는다.

[원본 근거·저장/호환/내용 읽기 경계](V6_RESOURCE_LARGE.md)를 따른다. 저장소 v666 ZIP
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`의 `importResourceFiles`
명시 File 사본/원자 보관에 연결했다. 기존 메뉴·카테고리/드롭 진입·레이아웃을 재사용한다.
파일당4MiB, 선택 전체/원본 보관4MiB·64개이며 내용 읽기·미리보기/편집·백업은 기존1MiB
범위다. 더 큰 사본의 정상 metadata-only 응답을 렌더링 성공이나 읽기 오류로 위장하지 않는다.

| 검사 | 확인한 실제 경계 |
|---|---|
| 독립 빌드 | no-hardlinks LF/CRLF Git objects·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine, 정확한 제품6파일·bundle hash·원본 File UI·공개 함수/권한/레이아웃 불변과 세 검증 분기 guard |
| 실제 별도 팩 소비자 | 단일/배치/폴더·명시 목적지·4MiB high-entropy 사본 전체 바이트/SHA/import receipt·같은6MiB 저장 상한; 큰 항목의 목록/read 결과는 bounded metadata이며 foreign/stale/id/path/비canonical/초과 입력은 거절 |
| 최종 CAS/실패 | 추출한 생산 Request/FileStream 실제 몸체에서 큰 파일의 single/batch 성공·manifest/identity/store/deletion 경합과 WriteAtomic 실패를 통제 주입; 원래 입력/peer 바이트 보존, 최종 검사 전 쓰기 없음 |
| 구버전 호환 | 실제24e639c 생산 Request로 기존 네1MiB 사본 전체 읽기; 1MiB 초과 사본이 있는 저장소의 구버전 load/read/import는 먼저 거절하고 원문을 비우거나 재작성하지 않음 |
| 실제 엔진 protocol | 동일 UTF-8/해시·청크와 명령/항목 ID·활성 ProjectContext를 보존, 미완성/변조/재사용/foreign·임의 target/plan 거절, 완료 영수증 재확인·Home/cold의 휘발 버퍼 분리 |
| 실제 큰 파일 UI | 폴더2MiB·두2MiB의4MiB 합계·root 단일4MiB, 정확한 bytes/ID/이름/설명·명시 삭제/cold 복원, 큰 미리보기의 제한 표시와 내용 편집의 쓰기 전 거절 |
| 중단/반복/응답 유실 | 실제 폴더 쓰기 거절/원자 롤백 후 같은 완료 버퍼 재확인, 수신/확정 응답 유실의 명시 재시도·늦은 검색/chat 보존, 닫기/Home/partial cold/no replay와 다른 실제 프로젝트 격리 |
| 기존 기능 회귀 | 작은 파일의 배치/목적지·내용 편집/백업/CAS/설명·SVG 표시/수명 및 WebUI scope/revision/취소/pack 경계; 실제 교차 패키지·전체 전개본의 큰 파일 정상/중단과 기존 내용/전송도 새 실행 |

큰 원본을 작은 내용으로 바꾸면 종전1MiB 백업 규칙을 넘길 수 있는 경로는 `save-content`에서
쓰기 전에 거절한다. 실제 UI/native 거절 뒤 resource 원문과 content sidecar 부재/목록 읽기를
확인했다. 미지원 원본을 자르거나 백업을 버리지 않는다. 기존 작은 내용의 저장/복원은 유지한다.
최종 CAS 경합은 실제 생산 몸체/OS 파일에 통제한 주입이며 외부 사용자 동시 실행이나 실제
Windows 기기 검증과 구분한다. 실제 브라우저 File 선택에는 생성한 테스트 자산만 사용했다.

변경한 native는 ProjectResources의 Request/Layout뿐이다. Core/targets·FileStream·ProjectManager·
EditorHome session/Resources·WebInvoke 권한/취소 경계·C# 사용자 원문·공개/override 시그니처·
Review→Confirm과 소스 CAS는 그대로다. 업로드 세션6,000,000B·청크1MiB·전역RPC2MiB와
저장6MiB·총원본4MiB/64개는 늘리지 않는다. root의 큰 File은 올바른 import-many 본문을 써서
기존 단일 import 본문을 batch 전송에 보내지 않는다. 미확정 File/bytes는 presentation에 넣지 않는다.
새 large `read`는 metadata와 명시적인 unavailable reason만 반환해 초과 RPC/미지원 편집을 막는다.
이 한계 확장은 기존 v1의 필드를 이행하거나 작은 저장소를 재작성하지 않는다. 큰 사본이 있는
프로젝트는 이전1MiB reader/writer로 열어 편집할 수 없으며 실제 구버전 거절을 검증했다.

변경 없는 Run backend/출력/자산에 대한 참고 기록 `/workspace/artifacts/v536-verification-managed/runs/69d34a616875406099cec7997534c916.json`의
ZIP/전체 manifest와 SDK/NuGet 입력 동일성·관련 source/bundle 불변을 확인했다. 이는 이번
신규/재사용 수에 넣지 않는다. M11/M12/M4를 확인된 회귀 없이 다시 열지 않는다.

재사용31개는 선행 동결의 LF19·CRLF12 통과 검사다. 제품과 해당 검사/fixture·SDK/NuGet·
정규화 명령·봉인 결과/전체 manifest의 동일성을 확인했다. 변경SDK·제품·미승인 fixture 소스를
거절하는 negative guard와 current-window-recovery-driver.py·current-window-reuse.json·각
재사용 결과를 최종 증거에 보존했다. 변경된 큰 파일 UI의 normal/lifecycle는 모두 새로 실행했고
실패 검사·빌드·패키지를 재사용하지 않았다. 선행 CRLF UI의 실패는 닫은 창 ID를 새로 연 뒤에도
사용한 검사 bookkeeping이었다. traffic에서 서로 다른 두 브라우저 ID와 보이는 현재 창/숨긴
옛 창을 확인하고 새 창 ID를 캡처하도록 수정했다. 두 번째 실행은 닫기/Home/cold 제품 경로를
통과한 뒤 프로젝트B 바이트를 A 저장소와 비교하는 helper의 StopIteration에서 멈췄다.
실제 활성 프로젝트의 저장소를 대조하도록 수정했다. 두 수정 모두 제품 변경이 아니다.
초기 빈 #app 원인을 고친 것으로 보지 않는다.

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/e45c7bfc10284eb881a2a82c88407302.json`
- 증거 ZIP SHA256: `ed499bf8e6e43a9dad245bc36dcb3c0752a2d8dce1febce336c94305a5b2ccd2` (2,864,837B)
- 개발 record: `/workspace/artifacts/v536-verification-managed/runs/c9157b025c424f1a9944ee1519dd67ff.json` (최종 수 제외)
- 선행 실패/중단 record: `/workspace/artifacts/v536-verification-managed/runs/f8064b81d1f44a4392177d10088c768e.json` / SHA256 `5e85814453e967e812118918578228b1434e90382107a118cc8edd5d2a5d3620` / crlf-resource-large-ui: exit 1; log /tmp/cv-5q54bohm/evidence/crlf-resource-large-ui.log.
- 선행 실패/중단 record: `/workspace/artifacts/v536-verification-managed/runs/1b1bbbe7b54445d89a2fb6e5280c1721.json` / SHA256 `0f735ee3834a56c9afb05dbe693ac8c5e4804834f2653add0dda42e8d44d83a3` / crlf-resource-large-ui: exit 1; log /tmp/cv-uusr8i6w/evidence/crlf-resource-large-ui.log.

| 지속 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `4ea7604d0e2a9da0d1bbc95b026fdb344aa4dc10` | `f07246a50ef5dd031e04337b266cf11d6880abc73a7bca2f00edc59a2a2b0834` | 53,816,885 | 2710/158 |
| rollback | `d23d6324a731a6558ccb2e6db694ca569984ce35` | `8ca5254ee138e342cb533ab8811c250a059a73cd7bb17c22878a592678ad89bb` | 53,815,396 | 2710/158 |

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.
latest manifest `d0d6a03699f1d6424daf1455da8a09d00b83915837c931de036839ed11e2f779`, rollback manifest `781a543da0e6fa363a618a4b11b98f1c6bdcef4dcac862ea8a25b85baa8cf479`.
최신 생성 패키지의 전체 압축복원/CRC/SHA/파일·디렉터리 mode 검증을 마치고, 직전 정상 HD
패키지를 rollback으로 남기는 기존 승인2세대 원자 승격만 사용했다. 검증 증거를 먼저 영속
보관한 뒤 소유 자식 종료·정확한 owned root 제거를 확인했다. 기존 원본/과거 자료·SDK/Git·
사용자 데이터·로그/프로필은 추가 삭제하지 않았다.

보관 확인 시점의 단위 순증가 25,886,720B (약 24.7MiB),
최종 실행 순증가 4,001,792B, 남은 여유 1,038,266,368B
(약 0.97GiB). 시작에 지속 최대384MiB+안전64MiB·임시3GiB·추가
메모리7GiB+안전1GiB를 확인했다. 최종 신규 단계의 표본 최소 디스크 여유 1,042,223,104B,
cgroup peak 7,426,478,080B는 모든 압축/승격 순간의 hard 최저/최대 측정이나 이후 단위
순증가 보장이 아니다.

남은 범위는4MiB 초과 파일·전체 보관량 확대·큰 내용의 분할 읽기/미리보기·다른 원본 지원 형식,
FHD/4K/GPU·물리 출력/오디오 장치, 실제 신원/멤버/권한 backend와 공유/다른 참여자 등이다.
mesh는 원본의 실제 renderer 근거 없이 설계하지 않는다. 기존 명시 ABI 제한이나 가능한 조합을
새 필수 항목으로 늘리지 않는다. 초기 빈 #app 원인은 미확정이다. Linux 엔진/Chromium·Windows
교차 생성/복원과 실제Windows/WebView2·모바일·DPI/IME·전체UI·Space/Library 전달을 구분하며
후자는 이번에 실행하지 않았다.
