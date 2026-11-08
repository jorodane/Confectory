# V8 원본 상위 해상도의 명시적4K 소프트웨어 출력

고정 v666 ZIP app.js::runPreviewResolutions의4K UHD3840×2160·DCI4K4096×2160·
1290×2796·QHD+1440×3200을 실제 소프트웨어 producer에 연결한다. 기존15개 메뉴·문구·
그룹·순서는 그대로이며 새로운 임의 해상도나 시연 scene을 추가하지 않는다. 원본 직접 입력은
8192px 상한이지만 이번 실제 profile의4096/8,847,360 예산을 넘는 custom 출력은 미지원으로
남긴다. 전체 custom 범위·GPU/물리 출력까지 완료로 세거나 고정8K 항목을 새로 만들지 않는다.

선택 팩의 Open4K(frameOwner)는 알려진 profile4다. 축4096·8,847,360픽셀·35,389,440 raw
RGBA8 bytes를 상한으로 하며 명시 ConfigureSize 뒤 RequestedSize를 다음 허용 프레임에서
소비한다. 기본/HD/FHD/QHD와 OpenConfigured의 기존 ID·입출력·profile0–3은 그대로이고
unknown5는 거절한다. 예제 examples/4k-output은64×36으로 시작한다. 사용자가 선택한 실제
요청 크기/완전한 bytes만 발행한다. 이동 연출/표시 완료가 작업 실행이나 Step의 조건이 아니다.

기존 CurrentUserOnly FrameControl·소유 handle/runtime/publisher·64개 size 요청·한 미결
sequence/ACK·취소/닫기/프로젝트/cold 수명을 재사용한다.45개 이하786432B raw 조각, 마지막
index44이며 전체 canonical base64url·metadata·SHA/길이/정수 cursor를 확인해야 신뢰 revision과
canvas를 교체한다. packet1,400,000B·RPC/관측2MiB·pipe I/O300ms는 늘리지 않는다.
기존 작은 profile의300ms 타이머 경로는 그대로다. 명시4K에서는 첫 읽기의 전체 elapsed를
포함하고 이후 각 Connect/Write/Read·종료 시간의 합을300ms에서 차감한다. 연결당25ms도
그대로이며 조각마다 새300ms를 주지 않는다. 사이의 native UTF8/JSON·metadata·전체SHA
CPU 처리는 I/O 예산과 구분한다. 누적 조각 지연이300ms를 넘는 실제 fixture의 거절을 검사한다.
전체 CPU 직렬화/해시·브라우저 decode를 포함한 wall-clock/FPS 보장을 뜻하지 않는다.
원래 작은 profile의 실제 전송 수·한도는 확대되지 않는다.

개인 등록의 동일 version1 JSON/ID·명령 영수증·프로젝트별CAS를4096/8,847,360까지 허용한다.
낮은 producer의 적용은 관측 max/maxPixels로 거절한다. 등록은 실행·캡처·더 큰 출력 권한을
주지 않는다. 이전 QHD reader는4K 항목이 포함된 전체 목록을 거절할 수 있으며 비우거나 자동
축소/이행하지 않는다. 작은/QHD 목록은 새 reader에서 그대로 읽는다. 새 Open4K symbol과
큰 전송/목록은 짝맞춘 provider/native reader/UI가 필요하며 구판의4K 지원을 주장하지 않는다.

검증은 독립 LF/CRLF·실제 native 소프트웨어 발행/소유·동일 스레드/복사·원자 revision,
45조각 고엔트로피/전체SHA·손상/혼합/부족/과다/잘못된 cap 거절, 실제 UHD/DCI/큰 세로
canvas·ACK, 반복/미결/응답 유실/늦은 입력·닫기/cold, 기존 QHD/FHD/HD/기본·등록CAS와
새 교차 패키지·전체 SHA/mode 복원·실패 수명을 포함한다. 개발과 최종 신규/재사용 근거는
최종 기록에서 구분한다. 생성 프로젝트/자산만 사용한다.

원본UI·HTML/CSS·기존 C# 원문/공개 override·부모외부/참조원본·권한·ReviewConfirm/CAS는
보존한다. 실제 GPU/화면 캡처·물리4K 모니터/Windows/WebView2·모바일/DPI/IME·물리오디오·
전체UI·Space/Library 전달은 미실행/미완료다. 초기 빈 #app·과거 cold 및 첫 출력 unavailable의
원인은 미확정으로 유지한다. 큰 Office 편집/백업/개인 초안 전송·4MiB 초과/총보관·실제
신원/권한 backend·종류 C#표현/사용중삭제 대응은 별도 기존 잔여다. 원본 text editor1MiB는
새 필수 확장으로 늘리지 않고 M11/M12/M4도 구체적 회귀 없이 다시 열지 않는다.
기존 환경·원본·SDK/Git·로그/프로필·증거와 main을 보존하며 승인된 소유 임시 수명과 최신/
롤백2세대 보관만 사용한다. 새 자격증명/실제 계정·접근권한·유료 호출·과거자료 정리는 없다.

최초 최종 실행의 기존 heartbeat 회귀는 픽셀 관측을2.7초 반복하며 매 응답을available로
가정한 곳에서1회 실패했다. 당시 거절 payload를 기록하지 않아 원인은 미확정이다. 관측은
기존 surface-unavailable 반환 계약이 있어 무중단 성공 보장과 heartbeat 갱신 금지를 구분한다.
검사는 같은2.7초 동안 성공 픽셀을 실제로 반복 확인하고2초 이후 성공도 요구한다. 오직
surface-unavailable만 기록해 허용하며 다른 거절은 실패한다. 중간 invoke 수 불변과 종료 후
실제 paused 제어 상태·foreign lease/view/handle·닫힌 소유 거절을 그대로 검사한다.

이 검사 보완 전 동결9aa90c19의 봉인된60개 통과 중, 제품/다른 검사·SDK/의존성/독립 checkout과
명령이 동일한39개만 별도 source-bound 증명으로 재사용할 수 있다. 실패·변경 heartbeat,
checkout/build/engine·boundary·예제 build·패키지/전체 복원은 새로 실행한다. 정확 probe/
harness SHA·전체 증거 manifest/CRC/SHA와 변경 SDK/제품 거절 guard를 검증하고 신규/재사용을
구분한다. 이 보완을 기존 빈 화면/첫 관측 원인 해결이나 native timer 완화로 간주하지 않는다.
