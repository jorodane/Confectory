# V8 명시적 QHD 소프트웨어 출력

고정 v666 ZIP의 app.js::runPreviewResolutions에 있는 `QHD / 2K · 2560 × 1440`을
기존 Run 개발 메뉴의 PC·가로 select에 연결한다. 새로운 화면/모의 scene이나 자동 소스
변환이 아니라, 명시적 software producer의 실제 RGBA8과 크기 ACK를 연결하는 단위다.
기존 화면·실행/권한·Review→Confirm·최종 CAS·3D/권한 별도 팩과 이동 연출 규칙을 유지한다.

프로젝트는 선택 팩 `Confectory.RunSurface::OpenQHD(frameOwner)`를 직접 사용한다.
OpenProfile의 알려진 profile3이며 ConfigureSize를 첫 Present 전에 호출하고 RequestedSize의
실제 요청을 다음 허용 프레임에서 소비한다. 기존 Open/OpenHD/OpenFHD와 OpenConfigured의
공개 ID/입출력·각0/1/2 선택과 동작은 그대로다. 알 수 없는 profile은 거절한다.
예제 `examples/qhd-output`은 처음64×36으로 구성하고, 사용자가 Run 메뉴에서 요청한 크기의
완전한 RGBA8을 다음 프레임에 제출한다. 실제 작업/Step은 표시나 캐릭터 이동을 기다리지 않는다.

QHD는 축2560·3,686,400픽셀·14,745,600 raw bytes다. 기존 기본640/262144, HD1280/921600,
FHD1920/2073600 profile은 확대하지 않는다. 큰 실제 출력은 max/maxPixels의 정확한 쌍과
현재 owner/runtime/publisher 관측으로만 허용한다. 기존64개 size 요청/한 미결 command·
sequence/ACK·불변 크기 capability, 원래 실제 pixels의 SHA와 revision/반환 계약을 유지한다.
모든 크기가 원본 메뉴로 추가되는 것은 아니며 회전 QHD는 기존 직접 입력/개인 등록 범위다.
원본에 없는1440×2560 프리셋을 만들지 않는다. 다른 원본 해상도/상위 profile은 별도 잔여다.

CurrentUserOnly FrameControl의 handle/secret/request/frameRuntime을 그대로 재사용하며
새 socket/외부 grant/캡처 권한을 만들지 않는다. child packet1,400,000B·글로벌 RPC/관측2MiB·
파이프 I/O300ms는 그대로다. 원래786432B raw 조각·base64url/canonical/전체 metadata/SHA와
불변 snapshot을 사용하며, QHD는 최대19조각·마지막 index18이다. 읽기 cursor의 문법만18까지
확장하고 실제 저장된 전체 길이·소유·runtime/revision·part offset 범위로 다시 검증한다.
이전 작은 profile의 실제 조각 수가 증가하지 않는다. 마지막 조각·새 snapshot·Stop/종료의
단일 전송 수명과 한 불변 encoded 프레임/metadata만 복제하는 처리는 유지한다.

브라우저는 전체 픽셀/SHA가 맞을 때만 canvas를 교체한다. 손상/혼합/누락/잘못된 cap·소유권·
revision/size receipt가 마지막 신뢰 값이나 ACK를 바꾸지 않는다. 닫기/다른 view·프로젝트/
실행·늦은 slice/digest와 cold는 기존 token으로 격리한다. 읽기 재관측은 자동 Step/Resume나
mutation replay가 아니다. size 명령 응답 유실은 현재 owner의 명시 재확인만 사용하며 늦은
크기·등록명·chat 입력과 원본 C#을 보존한다. 300ms는 기존 파이프 I/O cancellation 예산이며
CPU 검증/직렬화까지 포함한 전체 wall-clock이나 실제 장치 FPS 보장이 아니다.

개인 QHD preset은 같은 version1 JSON/ID·영수증·프로젝트별 CAS에 저장한다. 새 reader는
작은 목록을 이행 없이 읽지만, 구1920 한도 reader는 QHD 항목이 있는 전체 목록을 거절할 수
있다. 데이터를 비우거나 자동 축소/이행하지 않는다. 기본/HD/FHD producer에서는 같은 목록을
읽어도 큰 항목의 적용은 실제 관측 cap으로 거절한다. 등록이나 화면 표시는 실행 권한·더 큰
producer 권한을 부여하지 않는다. OpenQHD symbol·큰 전송·새 preset은 짝맞춘 provider/native
reader/UI가 필요하며 구버전의 QHD 표시를 보장하지 않는다.

우선순위를 원본과 대조했다. `resource-edit.js`의 텍스트 editor는 원래1MiB를 명시 제한하므로
그 보호를 새 필수 대형 텍스트 편집 요구로 늘리지 않는다. DOCX/XLSX 원본 archive 편집은32MiB
범위가 있어 현재1MiB 초과의 편집·백업·개인 초안/재시작 전송은 실제 별도 잔여다. 현재4MiB
보관 경계와 기존2MiB RPC/원자 저장·입력 보존을 함께 다뤄야 하므로 이번 출력 단위와 섞지 않는다.

최종 LF/CRLF·native 실제 API/픽셀·중단/응답 유실/late input/cold·새 교차 패키지/전체 복원·
최신/롤백과 실패 수명관리는 별도 검증 기록에서 마감한다. 생성한 테스트 프로젝트만 사용한다.
기존 환경/SDK·원본·보관본/증거와 승인된 소유 임시 수명/두 세대 보관을 유지하고 main은 보존한다.
실제 계정/자격증명·유료 AI 호출·접근권한 확대·기존 자료 추가 삭제는 없다. 초기 빈 #app와 과거
cold 읽기의 원인은 미확정이며 실제 Windows/WebView2·모바일·DPI/IME·GPU/모니터 FPS·물리 오디오·
전체 UI·Space/Library 전달은 소프트웨어 자동화/교차 패키징과 구분한다.

개발의 높은 엔트로피 손상 fixture 첫 정상 읽기가 한 차례 surface-unavailable이었다.
동일 입력의 진단 복사본에서는 최초 정상·모든 손상 거절이 통과해 최초 원인은 미확정이다.
이 결과를 초기 빈 #app 원인이나 해결로 합치지 않는다. 기존 읽기 재관측 계약에 맞춰
최초 정상 snapshot은20회/50ms 안에서 읽기만으로 확인하며 invoke 수 불변을 검사한다.
fixture는 그 완료 cursor 확인 전까지 정상 generation1을 유지하고, 이후 원래 손상
각 generation2–11을 한 번씩 검사한다. 손상 세대의 재시도나 신뢰 revision 완화는 없다.
계측을 제거한 제품 경로에서3회 반복 손상 검사와 일반/응답 유실/중단 UI가 통과했다.
진단 소스/SHA·실패/초기 관측 기록과 제품 source 복구를 보존하고 최종에는 신규 검증만 쓴다.

[최종 신규73단계·보관·미실행 기록](VALIDATION_V666_RUN_QHD.md)을 따른다.
