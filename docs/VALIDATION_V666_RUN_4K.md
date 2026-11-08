# 원본 상위 Run 해상도의 명시4K 출력 검증

동결 c661ae0457b269ca9c061ceb52f9d88e016f112b의 유효80단계(신규33·동일 입력 재사용47)를 통과했다.
LF는 신규11/유효36, CRLF는 신규11/유효33이며
새 교차 패키지/전체 복원·실패 수명 검사는 전부 신규다. [원본·실제 지원·호환 경계](V8_RUN_4K.md)의
3840×2160·4096×2160·1290×2796·1440×3200 실제 RGBA를 기존15개 메뉴에 연결한다.
기존 UI/HTML/CSS/원문·공개 override·권한·ReviewConfirm/CAS와 기본/HD/FHD/QHD는 보존한다.

| 검증 | 실제 범위 |
|---|---|
| 독립 source | LF/CRLF no-hardlinks Git/HOME/NuGet·빈 engine cache·Release/MCP/Linux engine. 정확18개 제품 파일·canonical 자산/동일 HTML/CSS·원본15개 메뉴. LF 새 예제 직접 build |
| native/전송 | Open4K/profile4의4096/8847360·명시 Configure/실제 요청·소유/복사/revision·한도/unknown5 거절, 기존 profile 실제 실행. 고엔트로피35,389,440B RGBA·전체SHA·정확45조각/index44·metadata/canonical/길이/혼합/누락/과다·foreign/retired 거절 |
| I/O/복구 | 기존 profile의 legacy Read와300ms 타이머 경로 불변. 명시4K만 첫 읽기 전체 elapsed와 이후 실제 파이프 I/O의 합을300ms에서 차감·연결25ms/packet1400000B 유지.15ms 지연 조각의 누적 초과를 거절하고 신뢰 revision12 보존·정상14 읽기 복구·invoke 불변. 손상 세대2–11/13은 각각 한 번만 발행한 trace 검사 |
| 실제 UI | UHD/DCI4K·큰 세로2개 canvas 크기/producer 픽셀·size ACK, 기존15개 옵션 관측 cap으로 허용. 자동 Step/Resume 없음. 개인4K 등록/CAS·초과/늦은 크기/이름/chat 입력 보존·응답 유실 읽기 재확인·전송 중단·닫기/새 view/프로젝트/cold의 늦은 조각/폼 격리 |
| 회귀/호환 |4K/QHD/FHD/HD/wide/surface/resolution/preset8개 projection·RunSurface/Audio/WebUI/FrameControl/이력. 실제 QHD/FHD/HD/기본·private preset 쓰기 실패/충돌/receipt·auto/audio/bounds/rate와 원래 고정 메뉴 회귀. 구 QHD JavaScript reader의 큰 목록 거절/작은 목록 호환을 실제 실행 |
| 새 패키지/복원 | Windows 교차 생성·구조/변조/의존성 거절·Linux engine 실제 시작. 생성본4K normal/parts·wide, CRC/전체파일SHA/파일·디렉터리 mode 복원 뒤4K lifecycle/parts·wide. 실패 수명/소유 IPC·지속 증거 봉인 후 소유 임시 정리 |

개발 /workspace/artifacts/v536-verification-managed/runs/9bb7aebf150f4518b3a245d69556ad87.json는28시도 중23개 통과·5개 이전 실패를 보존했다. 별도 사전 projection은2회 중
1회 필수 command 누락으로 거절됐고 입력만 수정해 통과했다. 개발/진단은 최종80단계에
재사용하지 않았다. 이전 두 최종 실행의 동일한 직접 통과47개만 아래 별도 증명으로 재사용했다.
실패의 실제 원인과 수정은 다음과 같다.

- 최초 native 전체 전송은 성공했지만 일시정지 직후 관측이 거절됐다. 진단 복사본은
  조각12–32에서296–303ms에 취소되는 것을 기록했다. 원래 단일 deadline이 패킷 사이의
  native JSON 처리까지 포함했다.4K 경로에서 누적 I/O300ms를 분리했고 기존 profile 경로는
  byte 대조로 보존한다. 진단 source/SHA·실패/계측 로그와 제품 복구 source를 보관했고
  계측은 게시 제품에 없다. CPU 처리/브라우저 decode까지 포함한 전체 wall-clock/FPS를 보장하지 않는다.
- 수정 후 반복 중1회 일시적 unavailable을 즉시 성공으로 요구하던 API 검사가 멈췄다.
  이 거절 자체의 원인은 미확정이다. 기존 관측 계약과 같은20회/50ms 읽기만 재확인하며
  invoke 불변을 검사한다. 정상 반복3회가 통과했고 손상 세대는 재시도하지 않는다.
- 정상 복구 세대12도 일시적으로 거절될 수 있어 fixture가 정상1/12/14만 완료 cursor
  확인까지 유지하게 했다. 잘못된2–11/13은 매번 새 세대로 정확히 한 번 발행한 실제 파일
  trace로 확인한다. 그 뒤 누적 I/O 거절·정상 복구 반복3회가 통과했다.
- 세대 trace의 줄바꿈 escape를 잘못 작성해 생성 C#이 컴파일되지 않았고 실패 조회 중
  view_budget으로 종료했다. 초기 검사/생성 입력·로그를 보존하고 Environment.NewLine으로
  수정했다. 제품 결함과 구분한다. 이후 현재 UI normal/lifecycle/parts도 통과했다.

이전 최종 record /workspace/artifacts/v536-verification-managed/runs/ea11bcf39973482381082f377caa0b29.json의60개 통과 뒤 CRLF legacy heartbeat가
한 번 실패했다. 모든 픽셀 관측의 available=true를 요구한 지점이며 당시 거절 payload가 없어
원인은 미확정이다. 관측의 surface-unavailable 계약과 heartbeat 갱신 금지를 구분해, 같은
2.7초 동안 실제 픽셀 성공과2초 이후 성공·중간 invoke 불변·종료 후 실제 paused 상태를
검사한다. 다른 거절은 실패하며 foreign/닫힌 소유 거절도 유지한다. 변경 heartbeat는 LF/CRLF
보완 뒤 두 번째 실행f5fa1b47에서모두 새로 통과했고 이번에는 동일 입력 근거로 재사용했다.
최초 거절의 원인이나 빈 화면 해결을 주장하지 않는다. 그 직접 실행에서는 LF 55/55·CRLF 57/57회가 모두 available이었고, 마지막 성공은 각각
2.680초·2.663초였다. 중간 invoke 수는 불변이다. 원본 관측 JSON과 sourcef5fa1b47의
직접 실행/이번 재사용 연결은 동반 기록에 보존한다.

두 번째 최종 record /workspace/artifacts/v536-verification-managed/runs/a51394a06ccb436e887f6589e4f7608c.json는 신규29개·재사용39개를
통과한 뒤 기존 QHD API의 일시정지 직후 단일 관측이surface-unavailable이었다. 제품·기존
QHD/legacy 타이머는 같고 그 거절 원인은 미확정이다. QHD 검사도20회/50ms·read-only·invoke
불변으로 정상 프레임을 확인하도록 보완했고, 잘못된 데이터 세대나 명령은 재시도하지 않는다.
변경된 QHD 호환 검사는 LF/CRLF 모두 신규로 실행했다.

제품/native·다른 검사 입력과 SDK/의존성·독립 LF/CRLF가 동일한 직접 통과 결과만 두 원본
전체 manifest/CRC/SHA 검증 뒤 재사용했다. source9aa90c19에서38개(변경 QHD 검사는 제외),
sourcef5fa1b47에서직접 새로 통과한9개다. 두 번째 기록의 이전 재사용39개를 다시 셈하지 않는다. 정확 probe/harness SHA·허용된 변경 파일·정규화한
동일 명령을 확인하고 SDK/제품 변경 거절을 실제 검증했다. 실패/변경 검사와 모든 checkout/
build/engine/boundary/예제 build·패키지/복원은 신규다.4k-reuse-9aa90c19.json/4k-reuse-f5fa1b47.json과 각 reused.json에
이전 source/result/log와 연결 근거를 보존했다. 이전 실행 원본에 기록된 초기 관측 복구도
그 이전 봉인 증거에 남아 있으며 최대18회다. 이번 신규 관측의 횟수로 합치지 않는다.

이번 신규 초기/일시정지/정상 복구 관측에서 unavailable을 읽기로 복구한 기록은2개이며
단일 정상 복구의 최대 관측 거절은3회다.
각 observations.json에 횟수·실제 invoke 불변을 보존했다. 이 결과를 과거 빈 #app/cold 읽기의
원인이나 해결로 소급하지 않는다. 생성한 프로젝트/프로필/픽셀만 사용했고 실제 계정/권한·
자격증명/유료 호출·개인 파일 업로드는 없다. 실제4K canvas는 직접 확인했다.

등록 저장은 같은 version1 JSON·ID·프로젝트별CAS다. 구 QHD reader는4K 항목이 포함된
전체 목록을 거절할 수 있으며 비우거나 축소/이행하지 않는다. 구 native 엔진을 이번에 다시
실행한 것은 아니므로 그 호환을 주장하지 않는다. 기존 작은 목록/낮은 producer의 적용 한도는
유지한다. 원본 직접 입력8192px 중 현재4096/8847360 예산 밖은 미지원이며 전체 custom/GPU/
물리 출력까지 마감했다고 하지 않는다. 새로운 고정8K 항목·권한 정책은 추가하지 않는다.

## 보관·공간·미실행 경계

- record: /workspace/artifacts/v536-verification-managed/runs/548c030e04dd480387ece855256c5744.json
- 증거 ZIP: /workspace/artifacts/v536-verification-managed/runs/548c030e04dd480387ece855256c5744.zip, 1,674,532B, SHA256 0a8e666e8781a5c8a3c273b0cc098b013cb341b43873cc0fc92e58e1e1240f40
- 승격 전 index: 증거 ZIP의 package-index-before.json
- 승격 후 동반 index: /workspace/artifacts/v536-verification-managed/runs/548c030e04dd480387ece855256c5744.closing-index.json, SHA256 d99195d1fbb6f85fa8cd8668051d417dcc9ce4a1ffa043a010911a15b401f294

| 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | c661ae0457b269ca9c061ceb52f9d88e016f112b | 0dd5b1391ba72665985e8f99f68c65fd4f79a66e43cdc422d7c478e30a46327c | 53,834,452 | 2726/158 |
| rollback | a50c41033656052177543e93ad4e87cb52ffd35d | b41b452b8bb9a44f04a069d4428434de5e6f92c58c6e6b2961526a374ceebf64 | 53,832,355 | 2723/158 |

전체 복원/지속 증거 검증 후 원자 승격해 직전 정상a50c4103를 rollback으로 보존한다.
이전 관리 rollback86a52b25 8cc38a2d8c16e548686bd1049ae6e5b633c6c2ed267831efa50e9f927f5d7dd5만 승인된2세대 수명으로 퇴역했다.
다른 원본·기존 산출물/로그·프로필·SDK/Git·사용자 자료는 추가 정리하지 않았다. 개발/최종의
직접 소유 임시 작업공간만 자식 종료·소유권/지속 증거 확인 후 정리했다. 개발·이전 두 실패·
최종 네 실행 모두 root가 없음을 확인했다.

추가 디스크 331,350,016B(archive56MiB·증거192MiB·코드4MiB·별도 안전64MiB),
RAM 작업공간3GiB·추가 메모리7GiB+안전1GiB다. 최종 시작/종료 여유29,179,363,328/
29,175,468,032B·차이3,895,296B, 개발 포함 단위 시작/종료29,195,755,520/29,175,468,032B다.
이번 신규 단계 표본 최저 디스크29,179,293,696B·관측 cgroup peak
11,996,782,592B다. 절대 극값이나 다음 단위 순증가를 보장하지 않는다.

추가 메모리7GiB는 사전 추정이었고, 이번 전체 cgroup 표본은 시작3,148,029,952B에서
11,996,782,592B까지 증가해 추가8.24GiB로 추정보다 컸다.16GiB 한도에서 관측 peak의
잔여4.83GiB는 별도 안전1GiB보다 컸다. 이 표본은 producer 한 프로세스의 최대나
절대 극값이 아니며 다음 동일 규모 검증은 이 실측을 반영해 사전 메모리 예산을 다시 산정한다.
안전 여유를 낮추거나 기존 자료/증거를 삭제해 맞추지 않았다.


기존 환경/SDK10.0.401/seed·원본 checkout과 main을 보존한다. 마감 문서 후 코드/검사/tools가
동결과 같음을 확인해 work/current만 정상 게시한다. 큰 DOCX/XLSX 편집/백업/개인 초안 전송·
4MiB 초과/총보관·실제 신원/권한 backend·종류 C#표현/사용중삭제 대응은 기존 별도 잔여다.
원본 text editor1MiB 제한·정상 소유 거절·선택적 조합을 새 필수 확장으로 늘리지 않는다.
M11/M12/M4는 구체적 회귀 없이 다시 열지 않는다. 초기 빈 #app·과거 cold/일부 첫 관측의
원인은 미확정이다. 실제 Windows/WebView2·모바일·DPI/IME·GPU/모니터/물리오디오·Office 앱·
전체 UI·Space/Library 전달은 미실행/미완료이며 이번 Linux 자동화·교차 생성과 구분한다.
