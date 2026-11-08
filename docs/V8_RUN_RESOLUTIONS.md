# V8 원본 고정 Run 해상도 메뉴

저장소의 고정 v666 ZIP(SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)
`Confectory-v666/dist/app.js::runPreviewResolutions/runResolutionOptions`를 기준으로 한다.
PC·가로6개, 시네마2개, 휴대폰·세로7개 총15개의 원래 값·문구·순서를 기존 select에 연결한다.
원본에 없는1440×2560 같은 새 항목은 추가하지 않는다. 기존 자동/개인 등록/직접 입력을 보존한다.

| 현재 실제 producer | 고정 항목의 허용 범위 |
|---|---|
| 기본/HD/FHD | 관측한 기존 max/maxPixels로 판정하며 자동 확대하지 않음 |
| 명시 QHD | 기존7개와2048×1080·1080×2340·1080×2400·1179×2556을 허용 |
| 현재 어떤 profile에서도 초과 | 3840×2160·4096×2160·1290×2796·1440×3200을 표시하되 선택 불가 |

1290×2796은 총픽셀이 QHD 예산 안이어도 축2560을 초과하므로 거절한다. 고정 메뉴 표시나
개인 등록은 큰 출력·캡처·실행 권한을 부여하지 않는다. 선택은 기존 현재 owner/runtime/publisher,
미결 명령/sequence/ACK, max/maxPixels 양쪽 검증을 그대로 거친다. disabled 항목을 강제로
선택한 이벤트와 대기 중 중복도 같은 검증으로 새 명령을 발행하지 않는다. 알 수 없는 문자열을
새 크기 명령으로 해석하지 않는다. 실제 producer가 다음 허용 프레임에 요청을 소비해야 ACK하며
메뉴가 자동 Step/Resume/동기 대기·소스 변환을 만들지 않는다.

제품 파일은 run-windows.js와 canonical WebBundle 기록2개뿐이다. 새 native profile/ID·공개
실행/override 계약·네이티브/RPC/파이프 예산·권한/원본/CAS/ReviewConfirm·HTML/CSS/자산 수를
바꾸지 않는다. 메뉴 선택은 기존 transient 표시 상태이며 재시작으로 live lease/frame/명령을
복원하지 않는다. 개인 등록은 기존 version1/프로젝트별 CAS를 유지한다. QHD를 쓰는 프로젝트와
개인 목록의 구버전 제한은 V8_RUN_QHD.md대로이며 이번에는 새로운 저장 형식을 만들지 않는다.

최종 검증은 독립 LF/CRLF, 실제 생성 producer와 소프트웨어 canvas, 각 profile의 허용/거절,
미결/반복/응답 유실/늦은 입력/닫기/새 view/cold, 새 교차 패키지·CRC/전체 SHA/mode 복원과
실패 수명관리를 포함한다. 개발·최종 신규/재사용 근거는 최종 검증 기록에 구분한다. 생성한
프로젝트/프로필만 사용하고 실제 계정/자격증명·유료 호출·접근권한 확대를 하지 않는다.

이 단위의 완료 기준은 원래15개 메뉴와 현재 실제 provider별 선택/거절이며, 모든4K 화면의
렌더러를 구현했다고 하지 않는다. 상위 실제 출력/4K·큰 DOCX/XLSX 편집/백업/개인 초안 전송·
4MiB 초과/총보관·실제 신원/권한 backend·종류 C#표현/사용중삭제 대응은 별도 기존 잔여다.
M11/M12/M4는 구체적 회귀 없이 다시 열지 않는다. 원본 text editor의1MiB 제한도 새 누락으로
늘리지 않는다. 초기 빈 #app·과거 cold 읽기·첫 QHD 관측 unavailable의 원인은 미확정이다.
실제 Windows/WebView2·모바일·DPI/IME·GPU/모니터/물리 오디오·Office 앱·전체 UI·Space/Library
전달은 이번 Linux 소프트웨어 자동화/교차 패키징과 구분한다. main과 원본/백업/증거를 보존하며
승인된 소유 임시 수명관리·검증된 최신/롤백2세대 보관만 사용한다.
