# v666 구현 기준과 고정 수용 목록

[일반 Blueprint 호출 카드의 핀 표시명](V666_CALL_PIN_LABELS.md)은 이미 관측한 직접 소유
callee의 명시 별칭을 기존 위치 ABI의 caller 핀 ID에 읽기 전용으로 표시한다. native 계약·
정의 hash·C#·권한·CAS를 유지하며 다른 표시 문맥과 고정7/8행의 실제 closure는 별도다.

[standalone 고정 반환 표시명](V666_STANDALONE_RETURN.md)은 같은 상세창·선택 metadata와
기존 void 보관 정책을 직접 소유 함수에 연결한다. 반환 ID·C# 계약·권한·CAS는 유지하며
다른 표시 문맥과 고정7/8행의 실제 source closure는 별도다.

[standalone 인자 표시명](V666_STANDALONE_LABELS.md)은 정보 카드 밖 기존 상세창의
표시/native 분리를 연결한다. 같은 계약의 owner 저장과 원문·권한·CAS 보호를 유지하고,
다른 표시 문맥·고정7/8행 전체·실제 기기/UI 완료로 합산하지 않는다.

[초기 module 로딩 실패 안내](V666_BOOTSTRAP_RECOVERY.md)는 재현된 빈 앱의 명시
재시도와 부분 화면 보존만 연결한다. 다른 표시·7/8행의 실제 source closure와
구 Reference reader 호환 범위는 그대로 구분하며 과거 간헐 빈 화면 원인은 미확정이다.

사용자가 2026-10-29에 승인한 저장소의 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`을 현재 UI 구현 기준으로 삼는다. ZIP SHA-256은 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`, 내부 버전은 666, Site 소스 commit은 `d6d8a63575a3d1addafc9ab0b558aa3fec600a46`이다. 최신 라이브 Site나 다른 버전을 자동 채택하지 않는다. 첨부 이름·크기는 일치하지만 Library 바이트 전송 실패로 첨부와 ZIP의 바이트 동일성은 미확정이다. 사용자가 main에도 있다고 지정한 이 저장소 ZIP을 사용한다.

v536 기록은 과거 검증 증거이며 기존 기능을 미구현으로 되돌리지 않는다. 속성·정보 함수 카드 이미지, 저장/실패/응답 유실·Undo·취소·cold·CAS·Review/Confirm의 기존 지원을 보존한다. 프로토타입의 브라우저 저장소·모의 Confirm·멤버 정책·Worker 연출은 실제 실행 권한이나 서버 보안의 증거가 아니다. 실제 계정·자격증명·접근권한 변경과 배포는 이번 구현 승인에 포함되지 않는다. 공개 override는 원본 입출력 계약을 유지하고 구현만 바꾸며, 독립 새 계약 복제는 필수 범위가 아니다.

## 정보 헤더 표시와 본문의 혼합 저장

고정 정보 편집8행의 [소유 헤더 설명·아이콘과 같은 계약 native 본문의 한 Save](V666_HEADER_BODIES.md)를 연결한다. 게시본의 실제 화면에서 네 입력의 결합 거절을 재현했고 기존 후보/CAS·version3 읽기 guard·cold Review를 공유한다. 새로운 공개/override 계약·권한·화면·문법은 없다. 타입/구조 변경 및 다른 원래 closure는 해당 고정 잔여로 유지하며 가능한 조합별 요구를 추가하지 않는다. 후속 표시 Save의 readGuards 유실과 Save 전 실제 비교 누락도 수정했다. 최종 **LF18·CRLF16·IPC1·패키지/전체 복원/실패 수명8, 신규43단계·재사용0**을 [마감 검증](VALIDATION_V666_HEADER_BODIES.md)했다.

## 현재 V3 소유 프로젝트의 3D 보기

관측된 pending 도구 I/O 뒤 상세 poll이 같은 잠금을 기다리는 경로는 [passive 갱신 후속](V3_WORKSPACE_IO_POLL.md)으로 수정하고 [신규44단계·재사용0](VALIDATION_V666_OFFICE_IO_POLL.md)를 마감했다. 일반 디스크 지연/모든 경합 시점·전체 UI의 완료와 구분한다.

[별도 표시 팩](V3_WORKSPACE_VIEW.md)에 원본 방/지도·실제 소유 선언·개인 카메라·기존
Browser 진입을 연결했다. 프로젝트 왕복/cold·늦은 응답/입력·WebGL 불가/변조 격리와
[최종 신규 35단계·재사용 0](VALIDATION_V666_OFFICE_VIEW.md)를 마감했다.
기존 공개 Worker의 8개 실제 상태와 Helper/대상·cold/철회 표시를 [상태 adapter](V3_WORKSPACE_WORKERS.md)에
연결하고 [최종 신규 34단계·재사용 0](VALIDATION_V666_OFFICE_WORKERS.md)를 마감했다.
개인 배치·확정/취소/지역 Undo와 root/child의 저장 격리는 [개인 배치](V3_PRIVATE_ARRANGEMENT.md)에
연결하고 [최종 신규 38단계·재사용 0](VALIDATION_V666_OFFICE_ARRANGEMENT.md)를 마감했다.
[실제 read/stage 완료 신호](V3_WORKSPACE_IO.md)를 명시 배정·현재 권한에 연결하고
[최종 신규 38단계·재사용 0](VALIDATION_V666_OFFICE_IO.md)를 마감했다.
도구 capability의 진행 신호/비차단 관측과 UI 소비는 [이번 기반](V3_WORKSPACE_ACTIVE_IO.md)에 연결했다. [최종 신규 34단계·재사용 7](VALIDATION_V666_OFFICE_ACTIVE_IO.md)를 마감했지만, 당시 미검증인 잠금 중 UI 전달은 [후속의 통제된 OS 읽기 검사](VALIDATION_V666_OFFICE_IO_POLL.md)로 관측된 pending 경로를 연결했다. 일반 OS I/O·모든 경합 시점/전체 UI 완료로 보지 않는다. 하위 Workspace의 다른 원본
조작과 전체 UI는 기존 지원 대조/검증 대상이며 가구 조합별 새 필수 기능으로 늘리지 않는다.
Run 영상/오디오 backend나 별도 권한 팩의 구현 완료를 뜻하지 않는다.

## 현재 V8 Run 소프트웨어 출력과 개발 메뉴

명시 producer의 요소 경계는 [픽셀과 원자 발행하는 선택 경계](V8_RUN_BOUNDS.md)로 연결한다.
원본 체크박스/점선 표시를 재사용했고 [최종 신규 50단계·재사용 0](VALIDATION_V666_RUN_BOUNDS.md)를 마감했다. GPU/기기 검증과 구분한다.

명시 소프트웨어 producer의 성공 발행 FPS는 [실제 출력 계측](V8_RUN_RATE.md)에 연결했다.
FrameControl 완료나 브라우저 조회·재그리기와 구분하며 GPU/모니터 표시 FPS는 잔여다.
[최종47단계(신규42·재사용5)](VALIDATION_V666_RUN_RATE.md)를 따르고, 초기화 간헐 빈 화면은 원인 미확정으로 유지한다.

원본10% 디버그 그리드는 [실제 영상 영역의 읽기 전용 표시](V8_RUN_GRID.md)에 연결했다. [최종 신규 44단계·재사용 0](VALIDATION_V666_RUN_GRID.md)를 마감했다. GPU/모니터 FPS 및 진행 중 I/O/큰 출력의 잔여와 구분한다.

현재 원본 PC640×360 선택과 축640/총262144픽셀의 실제 출력은 [픽셀 예산 보존 경계](V8_RUN_WIDE.md)로 연결했다. [최종 신규 55단계·보조 guard 2개 재사용](VALIDATION_V666_RUN_WIDE.md)를 마감했다. 이전512 provider의 관측/제한과 기존 Open의640 한도를 유지한다. 별도 명시 OpenHD의1280×720/720×1280/1024×768은 [HD profile](V8_RUN_HD.md)로 연결했고 [최종 검증](VALIDATION_V666_RUN_HD.md)에서 한계를 구분한다. 명시 FHD 가로/세로는 [FHD profile](V8_RUN_FHD.md)과 [신규69단계](VALIDATION_V666_RUN_FHD.md)로 마감했다. FHD를 넘는 출력/물리 장치는 기존 잔여다.

원본 개발 메뉴·디버그 선택은 [실제 Run 관측](V8_RUN_DEVELOPER.md)에 연결했다.
별도 선택 팩이 기존 소유 FrameControl 루프에 명시적으로 연결한 실제 RGBA 영상은
[소프트웨어 출력](V8_RUN_SOFTWARE_OUTPUT.md) 경계로 표시한다. 영상은 scope/소유자·
전체 SHA·순서를 전후 확인한 미보관 관측이며 ACK/heartbeat/실행 조건과 분리한다.
직접 출력하지 않는 기존 프로젝트는 미지원 표시를 유지한다. 실제 출력 크기만 읽으며
명시적으로 허용한 출력에는 [240–512 px 직접 크기 요청과 실제 프레임 확인](V8_RUN_RESOLUTION.md)을 연결한다. [최종 신규 54단계·재사용 0](VALIDATION_V666_RUN_RESOLUTION.md)를 마감했다. 현재 허용된 출력 범위의 프로젝트별 개인 preset 등록·선택·삭제는 [별도 CAS 저장과 실제 출력 적용](V8_RUN_PRESETS.md)에 연결한다. [최종 신규 37단계·재사용 0](VALIDATION_V666_RUN_PRESETS.md)를 마감했다. 현재 허용된 픽셀 예산의 창 영역에 대한 자동 맞춤은 [실제 창 영역/ACK 경계](V8_RUN_AUTO.md)와 [최종 신규 39단계·재사용 0](VALIDATION_V666_RUN_AUTO.md)로 마감했다. FHD profile을 넘는 대형 해상도·큰 surface·GPU/모니터 FPS·GPU/native Window 캡처는 기존 고정 잔여다. 오디오의 명시적 모노 PCM16/16kHz producer·소유 관측과 사용자 제스처/Off/수명 복구는 [현재 소프트웨어 미리듣기 경계](V8_RUN_AUDIO.md)와 [최종 검사 기록](VALIDATION_V666_RUN_AUDIO.md)에 연결한다. 다채널·장치/native sink·실시간 지연 및 물리 오디오 검증은 완료하지 않았다. [최종 신규 19단계·재사용 22](VALIDATION_V666_RUN_AUDIO.md)를 마감했다.
실제 Windows/모바일·전체 UI·Space/Library 전달은 이번 자동화 검증과 구분한다.
[최종 신규 44단계·재사용 0](VALIDATION_V666_RUN_SOFTWARE_OUTPUT.md)와 최신/롤백 보관 기록을 따른다.

## 현재 V6 프로젝트 자료 보관 기반

명시 File의 실제 프로젝트 사본 보관은 [독립 자산 팩·자료 탭](V6_RESOURCE_IMPORT.md)에 연결했다.
새 카테고리 생성·중첩 계층/제목 경로 탐색·파일/폴더의 내부 드래그 이동과 ProjectPack 복귀를
[별도 카테고리 목록의 원자 저장](V6_RESOURCE_LAYOUT.md)에 연결하고 **최종38단계(신규34·재사용4)**를
[검증](VALIDATION_V666_RESOURCE_LAYOUT.md)했다. 기존 파일 ID·바이트·import receipt와 원본/권한·Review→Confirm은 유지한다.
현재 파일당4MiB·전체4MiB/64개와 카테고리64개 경계다. 1MiB 초과 사본의 보관·제한된 metadata 읽기와 기존 내용 편집 경계는 [단일 큰 자료](V6_RESOURCE_LARGE.md)와 [최종 검증](VALIDATION_V666_RESOURCE_LARGE.md)을 따른다. [한 번에 여러 File 보관](V6_RESOURCE_BATCH.md)은 초기 선택 전체1MiB/64개를 한 원자 저장에 연결했고 현재 [선택 합계4MiB](V6_RESOURCE_TRANSFER.md)로 확장했으며 [최종51단계(전부 신규)](VALIDATION_V666_RESOURCE_BATCH.md)로 검증했다. [카테고리 첫 가져오기와 명시 폴더 File 드롭](V6_RESOURCE_DESTINATION.md)도 한 파일/배치 거래로 연결했고 [최종63단계(신규60·재사용3)](VALIDATION_V666_RESOURCE_DESTINATION.md)로 확인했다.
카테고리의 인라인 이름 변경·미확정/실패 입력 복원은 [별도 이름 metadata](V6_RESOURCE_FOLDER_NAMES.md)에 연결하고 [최종45단계(신규43·재사용2)](VALIDATION_V666_RESOURCE_FOLDER_NAMES.md)로 확인했다. 기존 topology/bytes·이전 v1 reader는 보존한다.
파일의 인라인 이름 변경과 열린 readonly 미리보기의 현재 이름은 [원본 사본을 보존하는 별도 metadata](V6_RESOURCE_FILE_NAMES.md)에 연결하고 [최종51단계(신규39·재사용12)](VALIDATION_V666_RESOURCE_FILE_NAMES.md)로 확인했다.
자료 텍스트·코드 내용 편집과 직전 저장 복원은 [원본 사본 보존·개인 입력 복구](V6_RESOURCE_CONTENT.md) 단위로 연결한다. [최종58단계(신규29·재사용29)](VALIDATION_V666_RESOURCE_CONTENT.md)로 LF/CRLF·실패/충돌/응답 유실·재시작·새 패키지/전체 복원과 수명 보관을 확인했다. 자료의 파일·카테고리 설명 및 이름+설명 검색은 [원본 metadata 흐름](V7_RESOURCE_DESCRIPTIONS.md)과 [신규57단계 검증](VALIDATION_V666_RESOURCE_DESCRIPTIONS.md)에 연결했다. 1MiB 이하 DOCX 문단·표 텍스트 편집/저장과 직전 내용 복원은 [원본 문단 편집 경계](V7_RESOURCE_DOCX.md) 및 [최종 검증](VALIDATION_V666_RESOURCE_DOCX.md)에 연결했다. 1MiB 이하 XLSX 셀 값 편집·워크시트 선택·저장/정확 복원은 [원본 셀 편집 경계](V7_RESOURCE_XLSX.md)와 [최종77단계(전부 신규)](VALIDATION_V666_RESOURCE_XLSX.md)에 연결했다. 선택 합계 4MiB는 [제한된 분할 전송](V6_RESOURCE_TRANSFER.md)으로 연결한다. 1MiB 초과 사본의 보관은 위 큰 자료 경계를 따르며 큰 텍스트는 [첫1MiB 관찰](V7_RESOURCE_TEXT_PREFIX.md), 큰 PNG/JPEG는 [전체 raster 관찰](V7_RESOURCE_RASTER_PARTS.md)을 따르며 다른 큰 형식은 별도 잔여다.
기존 텍스트/코드 읽기 전용 미리보기는 [완료한 V7 경계](V7_RESOURCE_TEXT_PREVIEW.md)를 따르며 다시 미구현으로 넣지 않는다. [정지 PNG/JPEG 미리보기](V7_RESOURCE_IMAGES.md)도 원본 contain 패널에 연결하고 [최종43단계(신규41·재사용2)](VALIDATION_V666_RESOURCE_IMAGES.md)로 실제 픽셀·읽기 실패/재시도·닫기/재시작·프로젝트 격리·새 패키지/전체 복원을 확인했다. DOCX·XLSX·PPTX·ODT의 제한된 내용/값 표시는 [Office 미리보기](V7_RESOURCE_OFFICE.md)와 [최종 검증](VALIDATION_V666_RESOURCE_OFFICE.md)에 연결했다. 1MiB 이하 PDF의 페이지·배율·실제 canvas/Worker 표시는 [PDF 단위](V7_RESOURCE_PDF.md)와 [신규52단계](VALIDATION_V666_RESOURCE_PDF.md)에 연결했다. Office 빠른 접기/펼치기 복원도 native 응답 없이 확인했다. DOCX 문단 편집의 현재 지원 경계는 위 후속을 따른다. XLSX 셀 값 편집은 [현재 지원](V7_RESOURCE_XLSX.md)과 [최종 검증](VALIDATION_V666_RESOURCE_XLSX.md)을 따른다. 1MiB 이하 정지 WebP의 손실/무손실·alpha 표시와 디코드/bitmap 수명은 [WebP 지원 경계](V7_RESOURCE_WEBP.md)와 [신규65단계](VALIDATION_V666_RESOURCE_WEBP.md)에 연결했다. 1MiB 이하 24/32비트 비압축 BMP의 실제 방향/행 padding·pixel과 사전 디코드 수명은 [BMP 경계](V7_RESOURCE_BMP.md)와 [최종 신규49단계](VALIDATION_V666_RESOURCE_BMP.md)로 연결했다. 1MiB 이하 GIF의 정지/제한 애니메이션·투명도·실제 compositor pixel·프레임 가중 lease는 [GIF 경계](V7_RESOURCE_GIF.md)와 [최종 신규57단계](VALIDATION_V666_RESOURCE_GIF.md)로 연결했다. 1MiB 이하 정지 AVIF의 기본 SDR8 색상/alpha·실제 sequence 크기·공유 표면 예산은 [AVIF 경계](V7_RESOURCE_AVIF.md)와 [최종 신규57단계](VALIDATION_V666_RESOURCE_AVIF.md)로 연결했다. 큰 파일과 다른 형식의 rich preview는 기존 잔여다.

## 현재 V9 3D 작업실 찾기

현재 공개된 직접 소유 3D 요소·Helper/Worker의 검색과 구역·카메라 이동은 [표시 팩의 검색 연결](V9_OFFICE_FINDER.md)을 따른다. 새 신원·권한/연락처 조회는 포함하지 않는다. [최종 46단계(신규41·동등 근거 재사용5)와 보관 증거](VALIDATION_V666_OFFICE_FINDER.md)는 기존 패널/본문 검색과 실제 native 상태의 경계를 구분한다.

## 기존 V9 모듈 직접 기능 이름 검색

원본의 직접 `methods[].name` 검색과 기존 native 모듈 인터페이스에서 표시하는 직접
`require` 이름의 누락을 게시 패키지로 재현했고 [소유 모듈 찾기](V9_FINDER_MODULES.md)에 연결했다.
[최종 33단계(신규 33·재사용 0)](VALIDATION_V666_FINDER_MODULES.md)를 통과했다.
상속/부모·외부 source 탐색과 새로운 관계/타입 조합을 필수 잔여로 늘리지 않는다.

## 현재 V2 검토 안내

실제 Review/Confirm의 영어 완료 안내·구어체 19개/24곳을 원본 문체와 native 의미 보존에 맞춰
[검토·확정 안내](V2_REVIEW_GUIDANCE.md)에 연결했다. 선택/고급 확인·compiler·최종 CAS는 유지한다.
[최종 35단계(신규 32·재사용 3)](VALIDATION_V666_REVIEW_GUIDANCE.md)를 통과했다.

## 현재 저장 복구 점검

초기화 중 읽지 않는 HTTP 클라이언트가 전체 host loop를 막고 단절 시 호스트를 종료시키는
결함은 [전송 수명 격리](V2_STARTUP_TRANSPORT.md)로 수정했다. 과거 간헐적 빈 `#app` 실패의
직접 원인은 미확정이며, controlled socket 정체의 재현과 구별한다. 최종37단계(신규32·재사용5)는
[이번 기록](VALIDATION_V666_STARTUP_TRANSPORT.md)을 따른다. 레이아웃/공개 API·원문·권한은 보존한다.

고급 선언 폼의 `현재 초안 다시 읽기`가 미적용 이름/계약 입력을 확인 없이 지우는 경로를
재현해 [명시 입력 버리기 확인과 재조회 보호](V2_DECLARATION_RELOAD.md)에 연결했고
[최종 39단계(신규 39·재사용 0)](VALIDATION_V666_DECLARATION_RELOAD.md)를 통과했다.
기존 취소/해제 의미와 exact Apply revision/hash는 보존하며, 실패·대상 변경·새 입력은 유지한다.

여러 일반 next 실행선을 편집한 뒤 저장 실패 시 입력 세 개가 사라지는 결함을
재현했고 [순수 실행선 묶음 복구](V2_ROUTE_GROUP_RECOVERY.md)에 연결했다.
[최종 검증](VALIDATION_V666_ROUTE_GROUP_RECOVERY.md)은 **LF 17·CRLF 17·패키지/전체 복원/실패 수명관리 8, 총 42단계(신규 42·재사용 0)** 통과했다. 기존 단일 실행선·표시명·Root 이름·반환 위치의 마감
범위를 다시 열지 않으며, 다른 혼합 저장/직접 배치는 재현 기반 조사 후보다.
조합마다 새 필수 항목을 추가하지 않는다. M11/M12/M4는 구체적 회귀 없이 재개하지 않는다.

## 현재 M11·M12·M4 경계

첫 생성 Save 전 소유 C#·값·표시·지역 핀/연결과 명시 Task 입력의 결합은 [현재 지원 경계](M4_ASYNC_FIRST_SAVE.md)를 따른다. 생성 전 Undo/취소/cold와 선언 자체의 미저장 복구를 다룬다. 공개 Root IO의 새 전역 생성 결합은 [첫 Confirm 전 IO 거래](M4_ASYNC_ROOT_IO.md)로 연결했다. 기존 원본·정보 owner·복수 계약의 공동 갱신 보호는 유지하며, 분기선 생성의 첫 Task 결합도 [후속 거래](M4_ASYNC_BRANCH_CREATION.md)에 연결했다. 최종 검증 수치는 [공개 IO 기록](VALIDATION_V666_ASYNC_ROOT_IO.md)과 [분기선 기록](VALIDATION_V666_ASYNC_BRANCH_CREATION.md)을 따른다.

직접 소유 내부 Task의 명시 전환·저장·실행은 [private 지원 경계](M4_ASYNC_PRIVATE.md)를 따른다. 연결된 내부 완료 실행선의 일반 결과 보존 동기 복귀는 마감했다. 첫 생성 Save 입력의 현재 지원/잔여는 위 경계를 따른다.

정보 자체 함수의 생성·배정 async 연결은 [직접 소유 경계](M4_ASYNC_INFORMATION.md)를 따른다. 검증 마감 수치는 해당 최종 기록에서 확정한다. 내부 Task는 위 private 경계를 따르고 첫 생성 Save 입력의 현재 지원/잔여는 위 경계를 따른다.

새 전역 함수/구현/graph/코드의 첫 Confirm 전 async 전환은 [생성 소유권 경계](M4_ASYNC_NEW_FUNCTION.md)를 따른다. 정보 소유 함수의 직접 생성/배정은 위 정보 소유 경계를 따르며 내부 Task와 첫 Save 입력은 위 현재 경계를 따른다.

새 ordinary C# 동작의 첫 Confirm 전 명시 async 전환은 [새 leaf 소유/저장 경계](M4_ASYNC_CREATING.md)를 따른다. 기존 직접 소유 Root에 생성 초안을 저장한 뒤 새 record의 missing CAS를 유지하며 메뉴·코드 편집·전체 Confirm으로 연결한다. 정보 소유 생성/배정과 private/internal Task는 위 지원 경계를 따른다. 첫 생성 Save의 코드/표시/값·지역 핀과 명시 Task 결합은 현재 경계에, 공개 Root IO 후속은 [새 전역 root 경계](M4_ASYNC_ROOT_IO.md)에 연결했다. 분기선 생성의 첫 Task 결합도 [후속 거래](M4_ASYNC_BRANCH_CREATION.md)에 연결했다.

아래 긴 표의 누적 문장은 각 당시 검증의 기록이다. 현재 잔여 판단은 [유한한 M12 마감표](M12_CLOSURE.md)를 우선한다. M11의 원래 소유 구현 편집은 마감했으며 구체적 회귀 없이 다시 열지 않는다. M12는 데이터 반환·소유 provider/target·일반 및 native 진입·공개/private 실행 계약 caller의 보존을 연결했고, 현재 실제 흐름의 마감 경계는 다음과 같다.

- ordinary IInvoke/native import·기존 NoBranch의 관측은 [검증 기록](VALIDATION_V666_ROOT_EXECUTION_OBSERVERS.md)을 따른다. 실제 공개 OriginalResult를 명시 wrapper로 연결하고 원본 계약의 전체 갱신 후보를 [wrapper 검증 기록](VALIDATION_V666_ROOT_EXECUTION_WRAPPERS.md)에 연결한다. 네 원래 흐름의 지원과 마감 근거는 다음과 같다.
- 같은 계약 copy·자식 소유 target의 전체 명시 갱신과 inherited-only 관측은 최종 검증까지 마감했다. [전체 갱신 기록](VALIDATION_V666_ROOT_EXECUTION_OWNED_UPDATES.md)에 신규/재사용과 환경 중단 복구 근거를 유지한다.
- 등록 외부 import·manifest·scope/포함 모듈의 읽기 전용 receipt도 저장·복원·Review·최종 CAS·실제 실행까지 마감했다. [최종 44단계와 패키지/복원 증거](VALIDATION_V666_ROOT_EXECUTION_IMPORTS.md)를 따른다. 네 원래 흐름으로 M12를 완료하며 조합별 새 잔여를 추가하지 않는다.

wrapper의 정상 stale 거절을 자동 변환 요구로, 비소유 부모/참조 쓰기나 override IO 변경을 미구현으로 늘리지 않는다. 새 타입·문맥 조합을 이 목록에 추가하지 않는다. M4의 직접 소유 ordinary 함수·동작/호출자의 명시적 Task 실행 기반은 [현재 지원 경계](M4_ASYNC.md)에 연결했다. 최종 신규 LF22·CRLF20·패키지/전체 복원/실패 수명관리8, 총50단계를 통과했다([검증·보관 기록](VALIDATION_V666_ASYNC_RUNTIME.md)). 직접 소유 ordinary Root의 원본 전환 메뉴·초안/원자 저장 연결은 [이번 지원 경계](M4_ASYNC_TRANSITION.md)를 따른다. 이 UI 단위의 [최종 신규 40단계·재사용 0](VALIDATION_V666_ASYNC_TRANSITION.md)을 마감했다. 지역 C# Result 완료 분기의 동기 복귀와 ordinary async Set 연동은 아래 후속에 연결했고, ordinary 공개 완료는 후속에 연결했고, async root 속성 편집은 [현재 단위](M4_ASYNC_PROPERTIES.md)로 연결했다. 기존 ordinary Root의 Result 없는 next 본문은 [원문/출력 보존 어댑터](M4_COMPLETION_ADAPTER.md)에 연결했다. 직접 소유하고 이미 Blueprint로 확정한 instance/native whole-body Root의 문맥 보존과 명시 전환은 [소유 whole-body 지원](M4_ASYNC_CONTEXT.md)에 연결했다. 직접 소유 내부 본문의 명시 전환은 위 private 지원 경계를 따르며, 연결된 private 완료 실행선의 일반 결과 보존 동기 복귀는 [private 지원 경계](M4_ASYNC_PRIVATE.md)에 연결하며, 첫 생성 Save 입력의 현재 지원/공개 Root 계약 잔여는 위 경계를 따른다. 동기 caller는 명시적으로 async로 바뀌기 전에는 오류로 거절한다. V2–V9와 기존 별도 UI/권한 backend·종류 C# 표현/사용 중 삭제 대응·실기기 검증의 남은 범위는 해당 고정 행을 따른다.

Workspace 확대 팝오버의 재개방·프로젝트 전환 후 폐기 콜백 보호는
[V1 수명 경계](V1_ZOOM_LIFETIME.md)로 연결한다. 기존 Blueprint 보호와 구분하고
독립 정보 편집 창의 모든 배율 문맥·실기기 미검증은 유지한다. [최종 31단계(신규 31·재사용 0)](VALIDATION_V666_ZOOM_LIFETIME.md)를 통과했다.

일반 Blueprint의 별도 viewport 읽기·확대 수명은 [현재 지원 경계](V1_NATIVE_ZOOM_LIFETIME.md)에
연결한다. Browser 갱신과 겹친 진입 읽기의 제한적 stale 재관측과 재개방/숨김/폐기 popup
보호를 다루며 source 저장·실행 계약은 미변경이다. [최종 31단계(신규 31·재사용 0)](VALIDATION_V666_NATIVE_ZOOM_LIFETIME.md)를 통과했다.

일반 Blueprint 읽기 중 창 닫기의 늦은 응답 경계는 [현재 지원 범위](V1_NATIVE_READ_CLOSE.md)에
연결한다. 기존 숨긴 창의 명시 재열기·현재 source 관측·private 배치와 권한을 보존한다.
[최종 29단계(신규 29·재사용 0)](VALIDATION_V666_NATIVE_READ_CLOSE.md)를 통과했다.

일반 Blueprint 설명의 Apply 중 원래 관측 값/같은 문자열로 돌아온 새 입력은
[현재 V2 보존 경계](V2_NATIVE_INTENT_LATE.md)에 연결한다. 입력 비활성화와 서버 basis/
CAS·명시 기준 재검토·공유 Undo를 유지하며 새 입력만 자동 폐기하지 않는다.
[최종 31단계(신규 31·재사용 0)](VALIDATION_V666_NATIVE_INTENT_LATE.md)를 통과했다.

## 기존 미완료 사용자 흐름

아래는 기존 27행/ABI 9행의 같은 흐름을 묶은 목록이다. ref/out·target·프레임의 가능한 조합마다 새 필수 행을 추가하지 않는다. 원본 ZIP의 `app.js`/`blueprint.js`에 대응하며 완료 조건은 해당 원본 조작의 정상 저장·원자 실패·명시 대응·입력 보존 및 영향 검증이다.

| 고정 흐름 | 실제 잔여와 종료 조건 |
|---|---|
| 자체 중첩 정의 | `renderObjectSchema`의 자체 compound 자식 추가/이름/타입/기본값/아이콘/삭제. named 정보의 값 편집은 이미 지원한다. 기존 qualified schema/소유 키 경로로 **새 자체 복합과 저장된 소유 복합의 하위 정의 편집 지원 단위를 마감**했다. 기본/독립 정보 창·객체에서 추가·이름·타입·기호/이미지·기본값·삭제, private Undo/Redo·Save/cold/Review/Confirm을 검증했다. 실패·충돌·응답 유실·저장 중 입력·별도 실제 프로젝트 cold 왕복을 집중 확인했고 최초 LF/CRLF·새 패키지/압축 복원 회귀 36단계가 통과했다. named 정보·부모·외부 정의는 복제하지 않는다. 기존 일반/named·참조 속성의 소유 복합 전환도 원본의 빈 복합 초기화 의미와 기존 팝오버의 명시 적용으로 연결했다. 정보/객체 private source·저장된 내부 자식, 배열 유지/축소와 오류/복구 집중 검증 및 **이번 전환의 최종 LF/CRLF·새 패키지·압축 복원 40단계**를 마감했다. [전환 지원/신규·재사용·미실행 검증](VALIDATION_V666_OWNED_CONVERSION.md). 연결된 public 정보의 정의는 원본 창에서 편집하고, 비호환 기존 소비자는 전체 미적용한다. 공개 override 계약 금지·독립 계약 복제 제외는 그대로다. 모든 참조/배열 타입 조합의 UI 검증 완료로 표시하지 않는다. [최초 저장/보호 검증 경계](VALIDATION_V666_OWNED_INFORMATION.md). |
| 나머지 실제 노출 아이콘 | 소유 graph 동작 카드의 기호·로컬 이미지를 기존 팝오버·private 입력·소유 후보/CAS로 연결했다. 일반/직접 private graph 및 same-contract copy의 root/private frame을 다루며, call/wrapper는 원본과 같이 readonly다. 공개 함수 정의·ABI·본문·외부 원본을 바꾸지 않는다. 집중 native/UI와 최종 LF/CRLF·새 패키지·압축 복원의 **49단계**가 통과했다. [아이콘 지원/검증·보관 경계](VALIDATION_V666_ACTION_ICONS.md). 분류·개념·모듈 헤더도 기존 팝오버·로컬 이미지와 metadata 전용 owner 거래에 연결했고 집중 UI/보호·프로젝트 왕복과 최종 LF/CRLF·새 교차 패키지·압축 복원 **57단계**를 마감했다. [헤더 범위/검증 기록](VALIDATION_V666_DECLARATION_ICONS.md). 모듈의 직접 요구 입력/out/반환과 기존 Set 편집이 지원하는 자체 출력에는 공통 팝오버·로컬 이미지·해제를 연결했다. 아이콘은 실행 ID/타입/순서/연결과 분리한다. 집중 보호 검사와 최종 **LF30·CRLF26·새 패키지/압축 복원/실패 수명관리14, 총70단계**가 통과했다. Set의 copy 초안·slot·private·conversion·결합 copy/호출 문맥은 기존 Set UI 미지원 경계로 유지하며 정상 금지로 확정하지 않는다. [지원/검증 경계](VALIDATION_V666_PIN_ICONS.md). 종류는 별도 nominal `enum` 정의와 미참조 항목의 생성·이름·순서·문자/이미지·해제·삭제를 연결했고 집중 기본/독립 창·cold·원자 실패·Review/Confirm을 확인했다. 최종 **LF34·CRLF29·새 교차 패키지/압축 복원/실패 수명관리16, 총79단계**가 통과했고 증거와 최신/롤백 두 패키지를 지속 보관했다. 이는 종류 정의·미참조 항목 편집의 완료이며 전체 종류 소비 흐름 완료는 아니다. [종류 정의 지원과 호환성](VALIDATION_V666_INFORMATION_ENUM.md). 속성의 종류 값/기본값은 owner+항목 ID 기반의 단일/배열 typed-data와 원본 드롭다운으로 연결했다. 정보/객체의 새 속성·기존 값·기본/독립 창·입력/Undo/취소/실패/충돌/응답 유실/프로젝트 왕복/cold/ReviewConfirm의 집중 검사와 최종 **LF37·CRLF31·새 패키지/전체 압축 복원/실패 수명관리18, 총86단계**가 통과했다. 기존 79단계도 다시 실행했으며 최신/롤백 두 패키지와 증거를 지속 보관했다. C# 표현은 결정하지 않으며 runtime property descriptor는 비지원/CLR 미지정을 유지한다. [종류 속성 값 지원·검증 경계](VALIDATION_V666_INFORMATION_ENUM_VALUES.md). 사용 중 ID 삭제는 현재 값/기본값이 무효가 되면 전체 거절한다. 소비자 삭제 대응 UI는 별도 잔여다. 종류 정의 전체 보관/복구는 기존 Browser 삭제·등록 보관 계약과 동일 ID 복구에 연결했다. 참조 중 정의는 값을 바꾸지 않고 보관을 차단하며 원문·초안·현재 입력을 보존한다. 집중 12개와 최종 **LF39·CRLF32·새 패키지/전체 복원/실패 수명 관리20, 총91단계**가 통과했고 증거·최신/롤백 두 패키지를 지속 보관했다. [보관/복구 지원·검증 경계](VALIDATION_V666_INFORMATION_ENUM_RETIREMENT.md). 원본 핸들러가 없는 함수 상세 핀이나 CSS가 숨긴 루트/모바일 핀은 추가하지 않는다. 종류의 숫자/C# 변환은 결정하지 않고 실행 분기 enum과 구분한다. 완료된 속성·정보 함수 카드 이미지는 제외한다. |
| copy의 영향 소스 결합 | 원본 계약 갱신이 실제 forwarded 부모/opaque·whole-body/import에 영향을 주는 경우 명시 본문·저장소·연결을 한 후보/CAS로 저장. ordinary Root/private·복수 호출·명시 target 지원을 중복 구현하지 않는다. 기존 A4–A6/7행에 한 번만 집계한다. |
| 여러 함수의 공유 호출자 결합 | [기존 로컬 import의 같은 계약 native 본문 그룹](V666_NATIVE_BODY_IMPORTS.md)을 연결했다. [기존 C# 호출자 원문을 보존한 그룹](V666_NATIVE_CALLERS.md)도 같은 계약으로 연결한다. 현재 지원한 직접 scalar·정의·ref/out·순열·계약 불변 본문 그룹 밖의 실제 private/wrapper/copy/상속/등록 소스 closure를 한 Save에 결합. 현재 순수 순열 보호는 구현 경계이며 영구 UX 금지가 아니다. |
| 함수 고급 타입 | 원본 타입 선택기의 정보·객체·기능 등 제공 타입을 native 함수 계약/호출자 검증에 연결. 속성의 typed datum 지원과 구별한다. |
| 핀 표시명 | 한글·공백 표시명과 생성 코드 식별자의 대응·저장·복원. 직접 소유 정보 카드의 입력/out은 [명시 표시명 편집](V666_ARGUMENT_LABELS.md)과 기존 이름 편집을 구분한다. 별도 영구 핀 ID 재설계를 이미 결정된 것으로 취급하지 않는다. |
| 실제 작업자 배지 B2 | 기존 `assignedNode`/지원 초안/변경 source와 실제 Helper/Worker 상태를 선언·폴더·헤더 범위에 표시. 3D 연출과 동일한 실제 상태를 사용하며 가짜 작업을 생성하지 않는다. **로컬 소유 활성 ProjectContext의 실제 배정·관측 변경/지원 초안, 고유 Helper 집계·팝오버·cold 읽기 연결 구현.** 실행 owner 부재는 확인 필요이며 다른 사용자/그룹의 권한 backend는 별도 팩 선행. [범위와 검증](VALIDATION_V666_WORKER_BADGES.md). |
| 비동기 M4 | 원본 async 전환/완료 분기를 실제 저장·호출·실행 계약에 연결. ref 입력 등 원본의 정상 거절을 유지한다. |
| 개별 C# 동작의 내부 흐름 M11 | 원본 내부 편집 진입에 대응하는 노드 단위 활성 구현·원문 보존·복구 거래. 임의의 C# 로직 추론은 요구하지 않는다. 저장된 직접 소유 Root 및 중첩 graph의 일반 next C#를 원문 보존 단일 내부 코드로 감싸는 미리보기/편집/Save를 연결했다. 중첩은 전체 frame/source binding·조상 왕복·혼합 profile을 보존하며 기존 엔진 예산을 적용한다. 이번 중첩 단위의 집중 보호 검사와 최종 **LF22·CRLF18·새 패키지/전체 복원/실패 수명관리8, 총48단계**가 통과했고 최신/롤백·증거를 지속 보관했다. 일반 ref/out은 바깥 저장소 배정·역할을 보존하는 native 전달로 연결했고, 집중 API/화면과 최종 **LF18·CRLF17·새 패키지/전체 복원/실패 수명관리8, 총43단계**가 통과했다. native 저장소·whole-body 문맥 11개도 양쪽에서 통과했으며 whole-body 노드의 private 전환 완료를 뜻하지 않는다. [저장소 지원/whole-body 경계](VALIDATION_V666_NODE_INTERNAL_STORAGE.md). 직접 소유 whole-body의 원래 Invoke/this·재귀·scoped import/source identity를 private 경로로 전달하는 연결도 추가했다. 원문 자동 재작성 없이 외부 계약·ref/out 저장소·원래 target을 유지한다. [whole-body 지원/검증](VALIDATION_V666_NODE_INTERNAL_CONTEXT.md). 이 단위의 최종 **LF23·CRLF20·새 패키지/전체 복원/실패 수명관리8, 총51단계**가 통과했고 최신/롤백과 증거를 지속 보관했다. 전체 M11 완료 아님. 직접 소유 실행 enum 선택기의 원문 보존 래핑·본문/helpers 편집·실행 결과 전달도 연결했다. [실행 분기 지원/검증](VALIDATION_V666_NODE_INTERNAL_BRANCHES.md). 이 단위는 최종 **LF27·CRLF22·새 패키지/전체 복원/실패 수명관리8, 총57단계**가 통과했으며 최신/롤백과 증거를 지속 보관했다. 내부 종료점의 기존 분기 ID 선택·연결·첫 미리보기/저장된 흐름의 원자 Save도 연결했다. [종료점 지원/검증](VALIDATION_V666_NODE_BRANCH_EXITS.md). 이 단위는 독립 **LF22·CRLF18** 통과 후 검사 helper 경로만 수정하여 동등 코드의 40단계를 재사용했고, 최종 source의 **새 준비6·패키지/전체 복원/실패 수명관리8**을 통과했다. 최신/롤백과 실패를 포함한 증거를 지속 보관했다. 저장된 same-contract copy의 단독 정보 배정·Root 일반 C# 내부 진입도 기존 소유 receipt와 원자 후보로 연결한다. [copy 지원/검증 경계](VALIDATION_V666_NODE_INTERNAL_COPY.md). 최종 소스의 **새 LF18·CRLF14·패키지/전체 복원/실패 수명관리8, 총40단계**를 통과하고 최신/롤백과 증거를 지속 보관했다. 저장된 단독 same-contract copy의 소유 중첩 graph 안 일반 C# 내부 진입도 정확한 frame/source binding과 기존 소유 receipt로 연결한다. [중첩 copy 지원/검증 경계](VALIDATION_V666_NODE_INTERNAL_COPY_NESTED.md). 최종 소스의 **새 LF21·CRLF17·패키지/전체 복원/실패 수명관리10, 총48단계**를 통과하고 집중 증거·최신/롤백을 지속 보관했다. 저장 copy의 일반 ref/out 내부 진입도 기존 caller/local 저장소와 out 역할을 보존하며 연결한다. [copy 저장소 지원/검증](VALIDATION_V666_NODE_INTERNAL_COPY_STORAGE.md). 최종 소스의 **새 LF18·CRLF16·패키지/전체 복원/실패 수명관리8, 총42단계**를 통과하고 집중 증거·최신/롤백을 지속 보관했다. 저장된 단독 배정 copy의 실행 enum 선택기 내부 진입·본문/helpers 편집도 기존 분기 전달과 소유 receipt에 연결한다. [copy 실행 분기 지원/검증](VALIDATION_V666_NODE_INTERNAL_COPY_BRANCHES.md). 최종 수정 코드의 **새 LF19·CRLF18·패키지/전체 복원/실패 수명관리8, 총45단계**를 통과하고 최신/롤백·증거를 지속 보관했다. 저장된 단독 배정 whole-body copy의 원문 보존 내부 진입도 기존 native context 전달에 연결한다. [whole-body copy 지원/검증](VALIDATION_V666_NODE_INTERNAL_COPY_CONTEXT.md). 최종 코드의 **새 LF19·CRLF19·패키지/전체 복원/실패 수명관리8, 총46단계**를 통과하고 최신/롤백·증거를 지속 보관했다. 새 copy의 Root next C# 내부 진입과 첫 Save/정보 배정도 기존 snapshot·receipt·원자 후보로 연결한다. [첫 Save 지원/검증](VALIDATION_V666_NODE_INTERNAL_COPY_CREATING.md). 최종 코드의 **새 LF19·CRLF19·패키지/전체 복원/실패 수명관리8, 총46단계**를 통과하고 최신/롤백·증거를 지속 보관했다. 새 copy의 기존 소유 중첩 frame 및 실행 selector 최초 전환도 같은 전체 경로/source binding과 원자 첫 Save/배정에 연결한다. [중첩/분기 최초 전환 지원·검증](VALIDATION_V666_NODE_INTERNAL_COPY_FRAMES.md). 최종 **LF20·CRLF19·새 교차 패키지/전체 복원/실패 수명관리8, 총47단계(새23·동등재사용24)**를 통과하고 증거·최신/롤백을 지속 보관했다. 지연 응답을 기다리던 검사 도우미의 추가 flush는 수정하고 새로 검증했으며 실패/중단도 따로 보존한다. call/wrapper·상속받기만 한 부모 본문은 원래 readonly/소유 보호이며 새 미구현으로 세지 않는다. 자식이 직접 선언한 own Blueprint target은 같은 공개 계약을 유지하며 M11 진입/편집/원자 저장을 지원한다. [override 소유 경계·검증](VALIDATION_V666_NODE_INTERNAL_OVERRIDE.md). 최종 동결 코드의 **신규 LF19·CRLF18·새 교차 패키지/전체 복원/실패 수명관리8, 총45단계**가 통과했고 집중 증거·최신/롤백 두 패키지를 지속 보관했다. 등록 외부 부모도 기존 등록 의존성의 헤더 관측·영수증·Save/Review/Confirm 재검증 및 최종 읽기 전용 CAS에 연결했다. [등록 부모·최종 CAS 지원/검증](VALIDATION_V666_NODE_INTERNAL_EXTERNAL_OVERRIDE.md). 최종 동결 코드의 **신규 LF22·CRLF21·새 교차 패키지/전체 복원/실패 수명관리8, 총51단계**를 통과하고 집중 실패 증거·최신/롤백 두 패키지를 지속 보관했다. 이로써 원래 고정 M11의 소유 구현 편집 범위를 마감하며 부모/참조 원본 직접 쓰기와 공개 override 계약 변경은 정상 거절이다. 실제 기기/전체 UI 검증과 다른 고정 행의 잔여는 별도로 유지한다. private graph 미지원 구형 profile의 자동 승격 거절은 호환성 보호이며 새 마이그레이션을 필수 잔여로 추가하지 않는다. [지원 경계](BLUEPRINT_NODE_INTERNAL_FLOW.md), [Root 최초 검증](VALIDATION_V666_NODE_INTERNAL_FLOW.md), [중첩 검증](VALIDATION_V666_NODE_INTERNAL_NESTED.md). |
| 루트 실행 분기 M12 | 루트 분기 추가·반환 배치와 호출자 분기를 원자 검증. 이미 지원된 노드 enum과 구별한다. **직접 소유한 동기 void 함수의 Blueprint target 전부·명시한 일반 직접 호출자들**를 공개 실행 metadata/별도 결과 인터페이스·반환 카드·호출자 분기 포트와 하나의 후보에 연결한다. 원래 C#·ordinary Invoke·ID/값·override 계약은 유지한다. 보존 원문/헤더와 관측 closure도 Save/Confirm의 읽기 CAS에 포함한다. 값 입력에 정수 out 하나가 있는 동기 void 계약도 기존 출력 카드/데이터 연결과 IInvoke를 보존하며 결과 enum과 함께 전달한다. 출력 발행 뒤 호출자 분기/다음 줄을 실행한다. 같은 그래프의 반복 호출·여러 호출자/target의 계약과 반환을 하나의 후보/CAS/Review 그룹으로 결합하며, 영향받는 모든 호출 위치와 다른 target 반환을 직접 지정한다. Blueprint 호출자가 없는 정의와 기존 C# IInvoke 소비자도 보존한다. Confirm 후 작은 그룹의 기준본 정착도 공통 검증으로 처리한다. 직접 소유 함수 계약의 정보(schema)에 단독 배정된 저장 same-contract copy에는 기존 공개 분기/None의 반환 선택·배치·연결을 readonly 정의와 분리해 연결했다. 관측 소스 전체의 원자 그룹과 읽기 receipt를 checkpoint/복원/Review/최종 CAS에 결합하며, 완료된 공개 루트 거래의 live metadata 수명도 같은 세션의 copy 생성/후속 편집과 구분한다. 이 후속 단위의 최종 **신규 LF23·CRLF19·새 교차 패키지/전체 복원/실패 수명관리6, 총48단계**가 통과했다. 최신/롤백과 증거를 지속 보관했다. [copy 반환 지원/검증](VALIDATION_V666_ROOT_EXECUTION_COPY.md). 새 정보(schema) copy의 미리보기에서도 같은 공개 분기/None 반환을 편집하고 생성·등록·배정과 첫 Save에 결합하도록 연결했다. 최초 관측 원문을 보존하며 미확정 copy의 후속 본문 영수증과 구분한다. 독립 창은 같은 소유자의 정확한 반환 계획만 전달한다. 이 첫 저장 단위의 최종 **신규 LF24·CRLF20·새 교차 패키지/전체 복원/실패 수명관리6, 총50단계**를 통과하고 증거·최신/정상 롤백을 지속 보관했다. [첫 저장 지원·검증 경계](VALIDATION_V666_ROOT_EXECUTION_COPY_CREATING.md). 자식이 직접 선언한 ordinary Blueprint target의 기존 공개 분기/None 반환을 동일 계약·원자 그룹에 연결했다. 상속된 Blueprint 실행은 선언 소유자의 원문을 사용하고 부모 본문 직접 편집은 거절한다. 이미 등록된 외부 부모는 readonly ancestry receipt와 최초 화면 dependency hash를 Save/복구/Review/최종 CAS에 결합한다. [자식 소유 반환 지원·검증](VALIDATION_V666_ROOT_EXECUTION_OVERRIDE.md). 이 단위의 최종 **신규 LF23·CRLF20·새 교차 패키지/전체 복원/실패 수명관리6, 총49단계**가 통과했고 최신/롤백과 증거를 지속 보관했다. 기존 직접 등록 외부 함수의 공개 분기/None도 정보(schema)에 명시 배정된 로컬 소유 ordinary provider에서 readonly 계약·헤더 관측과 원자 Save/최종 CAS로 연결한다. [등록 함수 반환 지원·검증](VALIDATION_V666_ROOT_EXECUTION_REGISTERED.md). 최종 **신규 LF16·CRLF14·패키지/전체 복원/실패 수명관리6, 총36단계**와 명시한 집중/변경 없는 native 재사용 근거를 보존했고 최신/롤백 보관을 마쳤다. 등록 외부 함수의 **저장된** public same-contract copy도 기존 분기/None 반환·명시 배정·readonly 헤더 receipt·원자 저장/최종 CAS에 연결했다. [저장 외부 copy 검증](VALIDATION_V666_ROOT_EXECUTION_REGISTERED_COPY.md). 최종 **신규 LF17·CRLF14·패키지/전체 복원/실패 수명관리6, 총37단계**와 명시한 집중 재사용 및 추가 native80개 신규 근거를 보존했고 최신/롤백 보관을 마쳤다. 새 외부 함수 copy의 미리보기/첫 Save도 기존 선택 origin·첫 관측 해시·생성/등록/배정·반환의 원자 거래로 연결했다. [외부 새 copy 검증](VALIDATION_V666_ROOT_EXECUTION_REGISTERED_CREATING.md). 최종 **LF19·CRLF16·패키지/전체 복원/실패 수명관리6, 총41단계(신규33·동등재사용8, native/소유 경계80개 포함)**와 집중 보호·원본 증거를 보존했고 최신/롤백 보관을 마쳤다. 나머지 원래 데이터/호출 문맥은 [유한한 M12 대조표](BLUEPRINT_ROOT_EXECUTION.md)에 남기며 공개 외부 계약 변경은 정상 readonly 보호다. 다른 직접 소유 함수 import가 있는 ordinary 본문·caller도 추가 계약을 변경 없는 관측 멤버로 결합한다. [본문 import 검증](VALIDATION_V666_ROOT_EXECUTION_PROVIDER_IMPORT.md). 최종 **신규 LF20·CRLF18·패키지/전체 복원/실패 수명관리6, 총44단계(native/소유 경계82개 포함)**와 집중 증거·최신/롤백을 지속 보관했다. [소유 복합 호출 검증](VALIDATION_V666_ROOT_EXECUTION_COMPOUND_OWNED.md). 최종 **신규 LF20·CRLF18·패키지/전체 복원/실패 수명관리6, 총44단계(native/소유 경계82개 포함)**와 집중 실패 증거·최신/롤백을 지속 보관했다. 중첩/private·등록 외부 import receipt·복수 provider 계약 변경은 현재 구현 경계이지 새 정상 금지 정책이 아니다. 이 확장 단위의 최종 **신규 LF21·CRLF18·새 교차 패키지/전체 복원/실패 수명관리6, 총45단계**를 마감하고 최신/롤백과 증거를 지속 보관했다. [복수 호출자/target 검증](VALIDATION_V666_ROOT_EXECUTION_CLOSURE.md). 후속 단위에서 동기 void의 typed out·복수 out·ref를 기존 전달 계약으로 연결한다. ordinary 비void 반환은 별도 경계다. [동기 데이터 전달 검증](VALIDATION_V666_ROOT_EXECUTION_DATA_VOID.md). 최종 **신규 LF20·CRLF18·패키지/전체 복원/실패 수명관리6, 총44단계(native/소유 경계82개 포함)**와 실패를 포함한 집중 증거·최신/롤백을 지속 보관했다. 정수 out 단위의 **신규 LF19·CRLF17·새 교차 패키지/전체 복원/실패 수명관리6, 총42단계**가 통과했고 증거·최신/정상 롤백을 지속 보관했다. [out 동시 반환 검증](VALIDATION_V666_ROOT_EXECUTION_OUT.md). [이번 지원 경계](BLUEPRINT_ROOT_EXECUTION.md). 최종 동결 코드의 **신규 LF18·CRLF16·새 교차 패키지/전체 복원/실패 수명관리6, 총40단계**가 통과했고 최신/정상 롤백·집중 및 최종 증거를 지속 보관했다. [최종 검증·보관 결과](VALIDATION_V666_ROOT_EXECUTION.md). 다른 원래 함수/호출 문맥 및 M4는 별도 잔여이며 전체 M12/UI 완료로 표시하지 않는다. |

## v666의 누적 변경

다음은 이번에 제외하지 않고 반영한 유한한 추가 수용 단위다. 각 단위는 기본/독립 창·프로젝트 경계·입력/취소·저장/재시작과 실제 관련 권한 검증으로 닫는다. 동일 화면의 모든 타입/target 순열을 별도 항목으로 늘리지 않는다.

| 단위·원본 근거 | 구현 범위·의존성·현재 상태 |
|---|---|
| V1 화면 확대: `clampCanvasZoom`, `createSteppedZoomWheel`, 두 zoom menu | Workspace/Blueprint 3.125–500%, 400/500 프리셋, 직접 입력/슬라이더/휠/터치, 중심/포인터 기준과 개인 화면 복원. source·실행 권한과 분리한다. **기본 화면 지원 구현·집중 검증 완료**. LF/CRLF·새 교차 패키지·압축 복원본에서 확대 8개 확인씩 통과했다. 새 배율의 독립 정보 창/프로젝트 전환 조작은 이번 집중 검사에서 별도 실행하지 않았으며 모든 문맥 완료로 표시하지 않는다. [검증 범위와 출처](VALIDATION_V666_CANVAS_ZOOM.md). |
| V2 안내 문체 | 원본의 바뀐 안내·오류·확인 문구를 실제 대응 화면에 적용. 오류 의미·거절·backend 원문 진단을 전역 문자열 치환으로 바꾸지 않는다. [C# 편집기 14개 문구/16개 표시 지점](V2_CODE_EDITOR_GUIDANCE.md)을 먼저 연결하고 [최종 31단계(신규 31·재사용 0)](VALIDATION_V666_CODE_EDITOR_GUIDANCE.md)를 통과했다. [값·연산식/핀 연결 안내 15개](V2_VALUE_GUIDANCE.md)와 직접 소유 root 값 전용 저장의 실패 입력 보존을 연결하고 [최종 33단계(신규 33·재사용 0)](VALIDATION_V666_VALUE_GUIDANCE.md)를 통과했다. [일반 설명 저장 복구·안내 11개/기존 13곳](V2_DESCRIPTION_RECOVERY.md)을 연결하고 [최종 42단계(신규 30·재사용 12)](VALIDATION_V666_DESCRIPTION_RECOVERY.md)를 통과했다. [일반 C# 본문 저장 복구·안내 6개/기존 8곳](V2_SOURCE_RECOVERY.md)을 연결하고 [최종 42단계(신규 42·재사용 0)](VALIDATION_V666_SOURCE_RECOVERY.md)를 통과했다. [일반 동작 표시명 저장 복구·공통 안내 3개/3곳](V2_NAME_RECOVERY.md)을 연결하고 [최종 42단계(신규 42·재사용 0)](VALIDATION_V666_NAME_RECOVERY.md)를 통과했다. [일반 next 실행선 저장 복구·연결 해제 안내 2개/2곳](V2_ROUTE_RECOVERY.md)을 연결하고 [최종 43단계(신규 43·재사용 0)](VALIDATION_V666_ROUTE_RECOVERY.md)를 통과했다. [기존 함수 시작점 저장 복구·저장 분리 안내 2개/3곳](V2_ENTRY_RECOVERY.md)을 연결하고 [최종 46단계(신규 46·재사용 0)](VALIDATION_V666_ENTRY_RECOVERY.md)를 통과했다. [기존 내보내기 값 저장 복구·저장 분리 안내 1개/1곳](V2_EXPORT_VALUE_RECOVERY.md)을 연결하고 [최종 47단계(신규 47·재사용 0)](VALIDATION_V666_EXPORT_VALUE_RECOVERY.md)를 통과했다. [기존 내보내기 출력 재배정 저장 복구·안내 2개/2곳](V2_EXPORT_BINDING_RECOVERY.md)을 연결하고 [최종 49단계(신규 49·재사용 0)](VALIDATION_V666_EXPORT_BINDING_RECOVERY.md)를 통과했다. [기존 root 반환 출력 핀 값 저장 복구](V2_ROOT_RETURN_RECOVERY.md)를 연결하고 [최종 51단계(신규 51·재사용 0)](VALIDATION_V666_ROOT_RETURN_RECOVERY.md)를 통과했다. [기존 export 노드 삭제 저장 복구](V2_EXPORT_REMOVAL_RECOVERY.md)를 연결하고 [최종 54단계(신규 54·재사용 0)](VALIDATION_V666_EXPORT_REMOVAL_RECOVERY.md)를 통과했다. [새 export 첫 저장 복구](V2_EXPORT_CREATION_RECOVERY.md)를 연결하고 [최종 56단계(신규 56·재사용 0)](VALIDATION_V666_EXPORT_CREATION_RECOVERY.md)를 통과했다. [root 반환 핀 표시 위치 저장 복구](V2_ROOT_OUTPUT_ORDER_RECOVERY.md)를 연결하고 [최종 58단계(신규 58·재사용 0)](VALIDATION_V666_ROOT_OUTPUT_ORDER_RECOVERY.md)를 통과했다. [root 입력 식별자 저장 복구](V2_ROOT_INPUT_NAME_RECOVERY.md)를 연결하고 [최종 60단계(신규 60·재사용 0)](VALIDATION_V666_ROOT_INPUT_NAME_RECOVERY.md)를 통과했다. [root 저장 뒤 일반 본문 저장 복원](V2_ROOT_FOLLOWUP_RECOVERY.md)을 연결하고 [최종 45단계(신규 40·재사용 5)](VALIDATION_V666_ROOT_FOLLOWUP_RECOVERY.md)를 통과했다. 다른 계약 편집·일반 검토·탐색/시스템 안내는 남으며, 미구현 V3–V9 안내는 해당 화면과 함께 적용한다. |
| V3 3D 작업실: `office.js`, `office-world.js`, `office-actors.js`, `voxel-character.js` | 기존 패널과 아이소메트릭 보기 전환, 프로젝트별 방·보관 설비·배치·카메라/추적, Helper/Worker 표시와 보관함→기존 Browser 진입. 실제 Worker 이벤트의 read/write/완료/중단을 즉시 표시한다. 사용자가 2026-10-29에 명시한 대로 캐릭터 이동은 시각적 연출뿐이다. 실제 작업 시작/실행은 도착·이동 애니메이션 완료를 기다리지 않으며 시각적 위치를 선행 조건·실행 잠금·스케줄로 사용하지 않는다. 실제 권한·검증·실행 조건은 그대로이고 6개 단말은 표시 자리다. 고정 로컬 자원/라이선스와 실제 소유 선언의 읽기 전용 방·지도·패널 전환/개인 카메라/Browser 진입은 [별도 표시 팩](V3_WORKSPACE_VIEW.md)으로 연결했고 [최종 신규 35단계](VALIDATION_V666_OFFICE_VIEW.md)를 마감했다. 기존 공개 Worker/Helper 상태는 [adapter](V3_WORKSPACE_WORKERS.md)와 [최종 검증](VALIDATION_V666_OFFICE_WORKERS.md)에 연결했다. 개인 배치 도구·확정 전 snapshot 분리·root/child owner 격리는 [개인 배치](V3_PRIVATE_ARRANGEMENT.md)와 [최종 검증](VALIDATION_V666_OFFICE_ARRANGEMENT.md)에 연결했다. [실제 read/stage 완료 신호](V3_WORKSPACE_IO.md)는 연결했다. 도구 read/inspect·초안 stage의 진행 신호/비차단 batch 관측과 UI 소비는 [부분 완료 경계](V3_WORKSPACE_ACTIVE_IO.md)에 연결했다. 관측된 pending I/O 중 상세 poll 경합은 [후속 검증](VALIDATION_V666_OFFICE_IO_POLL.md)으로 연결했다. 일반 디스크 지연/모든 경합 시점과 편집기 전체 UI는 미검증이며 provider 대기/최종 파일 쓰기를 추정하지 않는다. 하위 Workspace의 다른 원본 조작·전체 UI는 기존 지원 대조/검증 대상으로 구분하며 가구 조합별 새 필수 기능으로 늘리지 않는다. 개인 표시는 실행이나 권한의 근거가 아니다. |
| V4 프로젝트 멤버/조직: `members.js` 및 동봉 조직/권한/소유권 검사 | 원본 멤버·그룹·미배정 영역·계층/복수 소속, 공개 범위, 경로별 권한 트리, staged 변경/Undo/취소/소유권 제안 UI. native의 실제 신원/권한 source와 연결해야 하며 로컬 demo ACL을 서버 권한으로 채택하지 않는다. 현재 멤버/조직 backend 연결 미구현. 실제 계정/접근권한 변경은 이번 승인 밖이다. |
| V5 Agent 공유·대화 경계: `agents.js`, 관련 `app.js` 함수 | 실제 사용/관리 가능 상태와 Helper·사용자별 세션·철회·개인 이력 분리의 표시/기존 동작 연결. 새 자격증명 복제·실제 grant 확대는 하지 않는다. 기존 권한 source adapter가 선행하며 미구현이다. |
| V6 리소스 탐색: `resourceDatabase`, `renderResourceBrowser`, `setupResourceTree` | 프로젝트 자산의 폴더/검색/밀도·선택·이름·이동·삭제와 복구, 원래 drag/drop 진입. 실제 소유 자산·경로/권한·원자 변경/이력 저장이 선행한다. 사용자 개인 폴더를 임의 탐색/업로드하지 않는다. 활성 프로젝트의 명시 File 사본 보관·실제 metadata 목록/검색·표시 크기·선택/성공 보관본 복원 기반은 [독립 자산 팩](V6_RESOURCE_IMPORT.md)에 연결한다. 초기 단일 파일 공급자의 파일1MiB·전체4MiB/64개 지원과 실패 입력/재시도·소유 경계를 **최종44단계(신규26·재사용18)**로 확인했다. [신규/재사용·패키지/전체 복원·실기기/OS 드롭 한계](VALIDATION_V666_RESOURCE_IMPORT.md)를 구분한다. 카테고리 생성·중첩 계층/제목 경로·파일/폴더 drag 이동은 [별도 metadata 원자 저장](V6_RESOURCE_LAYOUT.md)과 [최종38단계(신규34·재사용4)](VALIDATION_V666_RESOURCE_LAYOUT.md)로 연결했다. 기존 bytes/ID/receipt는 보존한다. 카테고리 인라인 이름 변경은 [새 표시명과 입력 수명 경계](V6_RESOURCE_FOLDER_NAMES.md) 및 [최종45단계(신규43·재사용2)](VALIDATION_V666_RESOURCE_FOLDER_NAMES.md)로 연결했다. 파일 이름은 [현재 metadata와 readonly 미리보기 동기화](V6_RESOURCE_FILE_NAMES.md) 및 [최종51단계(신규39·재사용12)](VALIDATION_V666_RESOURCE_FILE_NAMES.md)로 연결했다. 파일 한 개의 확인 후 삭제·재시도·새 세대 보호는 [프로젝트 사본 삭제](V6_RESOURCE_FILE_DELETION.md) 및 [최종 59단계(신규52·재사용7)](VALIDATION_V666_RESOURCE_FILE_DELETION.md)로 연결했다. 카테고리와 하위 사본의 확인 후 일괄 삭제는 [원자 하위 삭제](V6_RESOURCE_FOLDER_DELETION.md) 및 [최종 66단계(신규58·재사용8)](VALIDATION_V666_RESOURCE_FOLDER_DELETION.md)로 연결했다. Ctrl/⌘·Shift 선택과 명시한 여러 대상의 원자 삭제는 [다중 선택 삭제](V6_RESOURCE_MULTI_DELETION.md) 및 [최종 75단계(신규70·재사용5)](VALIDATION_V666_RESOURCE_MULTI_DELETION.md)로 연결했다. 텍스트·코드 내용 편집과 직전 내용 복원은 [내용 sidecar/개인 입력 수명](V6_RESOURCE_CONTENT.md) 및 [최종58단계(신규29·재사용29)](VALIDATION_V666_RESOURCE_CONTENT.md)로 연결했다. [초기 선택 전체1MiB/64개 다중 가져오기](V6_RESOURCE_BATCH.md)는 항목별 v1 영수증과 한 CommitPlan/CAS에 연결하고 [최종51단계(전부 신규)](VALIDATION_V666_RESOURCE_BATCH.md)로 검증했다. [카테고리 첫 가져오기·가리킨 폴더 File 드롭](V6_RESOURCE_DESTINATION.md)은 같은 v1 원문/배치와 한 최종 CAS로 연결하고 [최종63단계(신규60·재사용3)](VALIDATION_V666_RESOURCE_DESTINATION.md)로 검증했다. 파일·카테고리 Data 설명과 이름+설명 검색은 [같은 metadata 저장](V7_RESOURCE_DESCRIPTIONS.md)과 [신규57단계](VALIDATION_V666_RESOURCE_DESCRIPTIONS.md)로 연결했다. DOCX 문단·표 텍스트 편집/저장·직전 내용 복원은 [원본 DOCX 흐름](V7_RESOURCE_DOCX.md)과 [최종 검증](VALIDATION_V666_RESOURCE_DOCX.md)에 연결했다. 1MiB 이하 XLSX 셀 값 편집·워크시트 선택·저장/정확 복원은 [원본 셀 편집 경계](V7_RESOURCE_XLSX.md)와 [최종77단계(전부 신규)](VALIDATION_V666_RESOURCE_XLSX.md)에 연결했다. 원본 빈 목록/카드 밖·ProjectPack 트리의 자료 추가/새 카테고리 메뉴는 [동일 원자 거래와 화면 수명](V6_RESOURCE_ENTRY.md)에 연결하고 [최종 신규41단계](VALIDATION_V666_RESOURCE_ENTRY.md)로 검증했다. 선택 합계 4MiB는 [제한된 분할 전송](V6_RESOURCE_TRANSFER.md)으로 연결한다. 파일당 1MiB 초과/전체 보관 예산 초과는 남으며 모든 V6 완료로 표시하지 않는다. |
| V7 리소스 미리보기·편집: `resource-preview.js`, `resource-edit.js` | 원본이 제공한 텍스트·이미지·PDF 등 미리보기와 지원하는 내용 편집/취소/저장. PDF/3D 등은 원본에서 제공한 보기 범위만 다루며 임의 편집 기능을 늘리지 않는다. 로컬 vendor·라이선스·읽기 권한·자산 수명·최종 CAS가 선행한다. 저장된 텍스트·코드 사본의 읽기 전용 창을 [첫 V7 경계](V7_RESOURCE_TEXT_PREVIEW.md)에 연결했고 **최종32단계(신규21·재사용11)**로 검증했다. [실제 관측/수명·기존 자료 보관·패키지/전체 복원 및 한계](VALIDATION_V666_RESOURCE_PREVIEW.md)를 구분한다. 텍스트·코드 내용 수정/저장·직전 내용 복원/복원 취소와 개인 입력 복구는 [내용 편집 단위](V6_RESOURCE_CONTENT.md) 및 [최종58단계](VALIDATION_V666_RESOURCE_CONTENT.md)로 연결했다. 1MiB 이하 정지 PNG·baseline/progressive JPEG의 실제 픽셀 표시는 [원본 contain 패널](V7_RESOURCE_IMAGES.md)과 [최종43단계(신규41·재사용2)](VALIDATION_V666_RESOURCE_IMAGES.md)로 연결했다. DOCX·XLSX·PPTX·ODT의 제한된 읽기 전용 내용/값을 [동일 출처 Worker](V7_RESOURCE_OFFICE.md)와 [최종 46단계(전부 신규)](VALIDATION_V666_RESOURCE_OFFICE.md)로 연결했다. 1MiB 이하 PDF 읽기 전용 페이지/배율을 [고정 renderer/자산](V7_RESOURCE_PDF.md)과 [최종52단계](VALIDATION_V666_RESOURCE_PDF.md)에 연결했다. 자료 설정 설명은 [원본 textarea·저장/입력 수명](V7_RESOURCE_DESCRIPTIONS.md)과 [최종57단계](VALIDATION_V666_RESOURCE_DESCRIPTIONS.md)로 연결했다. 1MiB 이하 DOCX 문단·표 텍스트 편집/취소·저장·직전 ZIP 복원은 [문단 편집·개인 입력/원본 보존](V7_RESOURCE_DOCX.md)과 [최종 검증](VALIDATION_V666_RESOURCE_DOCX.md)에 연결했다. 1MiB 이하 XLSX 셀 값 편집·취소/저장·정확 복원과 워크시트 선택은 [현재 경계](V7_RESOURCE_XLSX.md)와 [최종 검증](VALIDATION_V666_RESOURCE_XLSX.md)에 연결했다. 1MiB 이하 정지 WebP의 손실/무손실·alpha 표시와 디코드/bitmap 수명은 [WebP 지원 경계](V7_RESOURCE_WEBP.md)와 [신규65단계](VALIDATION_V666_RESOURCE_WEBP.md)에 연결했다. 1MiB 이하 24/32비트 비압축 BMP의 실제 방향/행 padding·pixel과 사전 디코드 수명은 [BMP 경계](V7_RESOURCE_BMP.md)와 [최종 신규49단계](VALIDATION_V666_RESOURCE_BMP.md)로 연결했다. 1MiB 이하 GIF의 정지/제한 애니메이션·투명도·실제 compositor pixel·프레임 가중 lease는 [GIF 경계](V7_RESOURCE_GIF.md)와 [최종 신규57단계](VALIDATION_V666_RESOURCE_GIF.md)로 연결했다. 1MiB 이하 정지 AVIF의 기본 SDR8 색상/alpha·실제 sequence 크기·공유 표면 예산은 [AVIF 경계](V7_RESOURCE_AVIF.md)와 [최종 신규57단계](VALIDATION_V666_RESOURCE_AVIF.md)로 연결했다. 큰 파일·다른 원본 그림 미리보기는 남으며 모의 렌더러로 완료 처리하지 않는다. mesh는 원본의 분류/필터만 확인됐고 실제 renderer 흐름이 없어 범위를 임의 설계하지 않는다. |
| V8 실행창 제어: `openRunViewport`, `setupRunDeveloperMenu` | 원본의 해상도/전체화면·소리·개발 표시 제어를 실제 Run 수명에 연결. 모의 scene/FPS를 native renderer 성공으로 쓰지 않는다. 기존 Run backend로 가능한 제어와 내장 renderer/오디오 backend 부재를 구별한다. 원본 개발 메뉴·debug 정보 선택은 [실제 Run 프레임 진단](V8_RUN_DEVELOPER.md)에 연결했고, 명시적 출력 팩이 제공한 실제 RGBA 영상과 읽기 전용 크기는 [소프트웨어 출력](V8_RUN_SOFTWARE_OUTPUT.md)으로 표시한다. 명시적으로 허용한 소프트웨어 출력의 직접 크기는 [크기 요청·실제 ACK](V8_RUN_RESOLUTION.md)로 연결한다. 명시적 PCM producer의 로컬 On/Off/테스트는 [현재 오디오 경계](V8_RUN_AUDIO.md)에 연결했다. 현재 허용된 출력 범위의 개인 등록/선택/삭제는 [preset 지원](V8_RUN_PRESETS.md)에 연결했다. 현재 허용된 픽셀 예산의 창 영역의 자동 맞춤은 [실제 출력/ACK](V8_RUN_AUTO.md)로 연결했다. 명시 FHD profile을 넘는 대형 해상도·큰 surface·GPU/모니터 FPS·GPU/native Window 캡처 및 native audio/장치/다채널은 미지원이다. 원본의 실행창 최대화·복원을 [실제 Run 표시 경계](V8_RUN_FULLSCREEN.md)에 연결한다. 문서/플로팅·CSS/native 전체 화면·Esc/닫기·지연 응답·프로젝트/재시작을 기존 Run 소유권과 분리했고 [최종 LF 13·CRLF 13·새 패키지/전체 복원/IPC·실패 수명관리 9, 총 35단계(신규 35·재사용 0)](VALIDATION_V666_RUN_FULLSCREEN.md)를 통과했다. 원본 요소 경계는 [실제 픽셀의 선택 경계](V8_RUN_BOUNDS.md)로 연결했고 [신규 50단계](VALIDATION_V666_RUN_BOUNDS.md)를 마감했다. 원본10% 그리드는 [실제 영상 표시](V8_RUN_GRID.md)로 연결했고, 고정 대형 해상도·GPU·물리 오디오 제어는 별도 backend 선행 잔여이며 모의 기능으로 채우지 않는다. |
| V9 찾기·참여자 탐색: `openWorkspaceFinder`, 참여자/연락처 관련 함수 | 현재 프로젝트의 원본 찾기/관련 요소 이동과 멤버·Helper 프로필/연락처/대화 진입. 실제 보이는 범위와 신원·대화 권한을 사용한다. 프로젝트 검색 버블의 요소/배치 글자·현재 허용 선언 이름/종류 이동은 [이번 V9 경계](V9_WORKSPACE_FINDER.md)로 연결했고 [최종 LF 14·CRLF 13·새 패키지/전체 복원/실패 수명관리 9, 총 36단계(신규 36·재사용 0)](VALIDATION_V666_WORKSPACE_FINDER.md)를 통과했다. 기존 배치 Ctrl+F는 유지한다. 배치하지 않은 소유 선언의 설명·Browser Data 값은 [기존 읽기 기반 검색](V9_FINDER_CONTENT.md)으로 연결했고 [최종 39단계(신규 39·재사용 0)](VALIDATION_V666_FINDER_CONTENT.md)를 통과했다. 직접 소유한 필드·함수 서명·종류 항목 이름은 [정의 구조 검색](V9_FINDER_DEFINITIONS.md)으로 연결했고 [최종 43단계(신규 43·재사용 0)](VALIDATION_V666_FINDER_DEFINITIONS.md)를 통과했다. 직접 등록한 소유 C# target 본문은 [대상별 검색·정확한 원문 열기](V9_FINDER_BODIES.md)에 연결했고 [최종 55단계(신규 55·재사용 0)](VALIDATION_V666_FINDER_BODIES.md)를 통과했다. 필터 밖 변경·Undo/Redo도 열린 색인에 반영하고 stale receipt·미적용 원문 입력을 보호한다. 소유 정보의 typed JSON 기본값은 [정확한 Unicode·값 검색](V9_FINDER_DEFAULTS.md)으로 연결했고 [최종 61단계(신규 61·재사용 0)](VALIDATION_V666_FINDER_DEFAULTS.md)를 통과했다. 원본 helper/저장 구조 실행 대조에서 깊은 graph 노드·코드는 원래 깊이 밖이므로 새 필수 전체 탐색으로 늘리지 않는다. 보존 원문 등 다른 실제 얕은 텍스트는 구체적 원본 근거와 재현으로 판단한다. 3D 구역 바로가기·직접 소유 요소와 이미 공개된 Helper/Worker 상태의 검색·선택/따라가기는 [표시 팩의 office 검색](V9_OFFICE_FINDER.md)에 연결했다. 실제 배정 대기/작업 중/재시작 확인 필요 상태와 기존 패널/본문 검색·입력 보호를 [최종 검증](VALIDATION_V666_OFFICE_FINDER.md)으로 구분한다. 다른 참가자·신원/연락처/대화는 V4/V5 실제 가시성·권한 backend의 별도 잔여이며 새 외부 메시지 전송 권한을 만들지 않는다. |

raw+저장 copy ABI/다중 target/Set-property/독립 properties+copy의 넓은 혼합 저장은 기존 명시적 지원 제한이다. 정상 보호와 혼합 미구현을 구별하며 이번 목록의 자동 조합 확장으로 만들지 않는다. Helper의 실제 ‘설명으로 작성’과 AI 이미지·협의/shared Confirm·내장 renderer backend는 별도 기존 후속이다. 실제 Windows/WebView2·모바일 기기·DPI/IME·Space/Library 전달은 교차 패키징과 별개로 미검증이다.

## 사용자 확정 팩 경계

2026-10-29 사용자 지시에 따라 **3D Workspace와 권한 부여·관리는 서로 다른 팩**으로 구현한다. 에디터 본체에 두 구현을 직접 결합하지 않는다. 기존 namespace-qualified 계약 ID·명시 provider/팩 연결과 소유 검증을 사용하며, 아직 없는 로더/모드 정책 전체를 새로 만드는 범위로 확대하지 않는다. 팩을 문서에 나눴다는 이유로 실제 구현·권한 검증 완료로 표시하지 않는다.

- 3D Workspace 팩은 실제 프로젝트/Helper/Worker 상태를 읽고 위치·카메라·선택·연출을 표시한다. 이동 완료는 작업 시작/실행 조건·잠금·스케줄이 아니다. 표시 팩이 비활성화되어도 실제 작업과 권한 검사는 유지한다. 실제 작업 제어가 필요하면 기존 에디터/실행 계약을 통해 다시 검증하며 3D 위치가 권한이나 작업 완료의 근거가 되지 않는다.
- 권한 팩은 권한 관리 UI와 실제 작업 허용 판단을 연결한다. 판정은 현재 프로젝트·실제 신원/소유/권한 source를 사용하고 기존 실행 경계·CAS/Review/Confirm 검증을 우회하지 않는다. 권한 팩이 없거나 판정을 확인할 수 없다고 무조건 허용하지 않는다. 기존 검증된 권한 경계는 계속 유지하며 새 허용 판정이 필요한 작업은 명확히 거절한다. 실제 계정 설정·외부 접근권한 변경은 이번 요청 밖이다.
- 에디터는 두 팩의 명시된 계약을 연결하는 어댑터를 제공한다. 3D 팩에 권한 판정/작업 스케줄러를 소유시키거나 권한 팩에 3D renderer를 필수 의존성으로 두지 않는다. 현재 확대 단위는 두 팩의 구현/권한과 독립적이다.


## M12 데이터 반환 후속 경계

직접 소유 ordinary Root의 비void 반환값과 공개 분기는 원래 Invoke·C#·데이터 연결을 유지하는 별도 생성 캡처로 함께 전달한다. [이번 지원·검증과 유한한 잔여](VALIDATION_V666_ROOT_EXECUTION_NONVOID.md)를 기준으로 copy/자식·등록외부 데이터 흐름, 중첩/private·외부 import 관측, 여러 직접 소유 provider의 원자 계약 갱신을 구별한다. 임의 타입/문맥 곱을 새 필수 목록으로 만들지 않는다. M4 호환 정책은 사용자 결정으로 확정됐다: 호출자가 명시적으로 async로 바뀌기 전에는 호환되지 않는 호출을 오류로 거절하고 자동 대기/자동 변환을 하지 않는다. 실제 async 저장·호출·완료 구현은 남아 있다.

비void 동결 코드의 최종 **신규 LF21·CRLF18·패키지/전체 복원/실패 수명관리6, 총45단계(Core/runtime·소유 경계86개 포함)**가 통과했고 집중 실패·최종 증거 및 최신/정상 롤백을 지속 보관했다. [최종 결과](VALIDATION_V666_ROOT_EXECUTION_NONVOID.md).


M12 ordinary 비void 데이터 반환의 기존 소유 흐름(저장/새 copy·자식 직접 본문·등록 외부 함수의 local provider와 저장/새 copy)을 같은 실행 선택·데이터 보존 검증에 연결한다. [지원과 검증 범위](VALIDATION_V666_PUBLIC_RETURN_DATA.md). 남은 M12는 중첩/private/native·외부 import의 실제 호출 계약 결합과 여러 직접 소유 provider의 완전한 명시 대응이다. 정상 예약 이름/소유권 거절이나 구형 자동 migration은 새 필수 항목이 아니다.

ordinary 소유/등록 데이터 반환의 최종 **신규 LF20·CRLF19·패키지/전체 복원/실패 수명관리6, 총45단계(반환 계약/runtime·소유 경계36개 포함)**가 통과했고 최신/롤백·집중/최종 증거를 지속 보존했다. [결과와 경계](VALIDATION_V666_PUBLIC_RETURN_DATA.md).

같은 함수의 여러 직접 소유 ordinary provider·각 target·실제 직접 caller를 전체 명시 대응에 연결한다. 실행 provider의 기존 scoped 배정은 변경하지 않고 다른 provider의 import도 readonly 최종 CAS 관측에 포함한다. [이번 범위와 검증](VALIDATION_V666_ROOT_EXECUTION_PROVIDERS.md). 남은 공개 계약 결합은 중첩/private/native와 등록 외부 import의 실제 caller/provider closure다. 기존 copy provenance가 포함되는 공개 계약 갱신도 같은 경계 대조에 묶고, 완료한 본문 반환 편집이나 독립 새 계약 복제와 구별한다.

여러 직접 소유 provider의 최종 **신규 LF20·CRLF18·패키지/전체 복원/실패 수명관리6, 총44단계(반환/runtime·소유 경계36개 포함)**가 통과했고 증거·최신/롤백을 지속 보관했다. [결과와 경계](VALIDATION_V666_ROOT_EXECUTION_PROVIDERS.md).

소유 ordinary switch-profile private caller도 물리 Root+전체 node 경로로 명시 대응하고 local frame의 반환/실행선만 갱신한다. 재귀적인 leaf 원문 관측과 body target을 같은 후보/CAS/Review 그룹에 유지한다. [중첩 호출 경계와 검증](VALIDATION_V666_ROOT_EXECUTION_NESTED.md).

소유 private caller 결합의 최종 **총45단계(신규39·동등재사용6; LF21·CRLF18·패키지/복원6, 계약/runtime·소유 경계36개 중 신규18·재사용18 포함)**가 통과했고 증거·최신/롤백을 지속 보관했다. [결과와 실제 경계](VALIDATION_V666_ROOT_EXECUTION_NESTED.md).


기존 branch-capable native whole-body의 공개 실행 진입을 원래 instance Invoke/this·재귀/scoped import/소스 위치와 분리해 연결하고 scope object·import 함수의 읽기 관측을 같은 CAS/Review 그룹에 보존했다. 최종 동결 코드의 **신규 LF19·CRLF16·새 패키지/전체 복원/실패 수명관리6, 총41단계**가 모두 통과했다(계약/runtime·소유 경계 38개 포함, 재사용 0). [지원·증거](VALIDATION_V666_ROOT_EXECUTION_NATIVE.md)와 [M12의 유한한 실제 흐름·종료 조건](M12_CLOSURE.md)을 기준으로 남은 caller 계약·copy/자식·등록 import를 구분한다. M4의 확정된 동기 caller 오류 정책과 실제 async 구현, 원래 V2–V9/UI 후속 및 기기 검증은 이 단위로 완료되지 않는다.


피호출자의 공개 분기 갱신 중 호출자 자신이 가진 공개 Root 분기·반환 데이터·readonly 선언을 보존하고, 원래 반환 카드에 연결하는 흐름을 마감했다. 최종 LF19·CRLF16·새 패키지/전체 복원/실패 수명관리6, **총41단계(신규37·동등 근거 재사용4)**가 통과했다. 재사용은 소스/SDK 입력이 동일한 Core 직접 검사 38개에만 해당하며 변경된 후보/API/UI·빌드·패키지는 신규다. [지원·검증·재사용 근거](VALIDATION_V666_ROOT_EXECUTION_CALLER.md). 남은 M12는 [유한한 종료 표](M12_CLOSURE.md)의 private forwarding/postCall 실제 영향, 같은 계약 copy·자식 전체 갱신과 등록 import 경계이며 임의 조합을 새 필수 행으로 늘리지 않는다.


기존 private 실행 frame·그 분기 영역 안의 callee 공개 계약 갱신을 연결했다. caller의 source/enum/서명/owner/종료점과 원래 `17`·out `10`·부모 분기/연속 실행을 보존한다. 최종 LF19·CRLF16·새 패키지/전체 복원/실패 수명관리6, **총41단계(신규33·동등 근거 재사용8)**가 통과했다. 재사용 Core 직접 검사38개 및 경합 경로 수리에 영향 없는 기존 LF 4단계와, 신규 충돌·CRLF API/UI·빌드·패키지 검사를 구분하고 [지원·증거·실제 경계](VALIDATION_V666_ROOT_EXECUTION_FORWARDING.md)에 기록했다. 이후 [유한한 M12 표](M12_CLOSURE.md)의 실제 소비자 관측/명시 wrapper 계약, 같은 계약 copy·자식 전체 갱신과 등록 import를 마감하며 조합별 필수 항목을 새로 만들지 않는다.


ordinary IInvoke/native import와 legacy NoBranch wrapper를 공개 계약 갱신의 읽기 관측·생성 receipt 갱신에 연결했다. 원래 profile·C#·IO·source identity·scope/자체 분기를 보존하고 실제 public caller만 명시 대응한다. 최종 **LF20·CRLF16·새 패키지/전체 복원/실패 수명관리6, 총42단계(신규38·동등 재사용4)**가 통과했다. [정확한 지원·신규/재사용 근거·증거와 잔여](VALIDATION_V666_ROOT_EXECUTION_OBSERVERS.md)를 따른다. wrapper의 실제 공개 OriginalResult 명시 연결과 copy/자식·등록 외부의 전체 갱신은 유한한 M12 표에 유지한다.


직접 소유 Root caller의 공개 OriginalResult wrapper·기존 데이터 ABI와 원본 계약의 전체 명시 wrapper 선택을 연결했다. legacy NoBranch adapter·원문·ID·자체 enum/연결은 보존한다. 최종 **LF20·CRLF16·새 패키지/전체 복원/실패 수명관리6, 총42단계(신규42·재사용0)**가 통과했다. [정확한 지원/검증/호환/증거](VALIDATION_V666_ROOT_EXECUTION_WRAPPERS.md)를 따른다. 남은 M12는 같은 계약 copy·자식 본문이 포함된 정의 전체 갱신과 등록 외부 readonly import 관측 두 흐름이다.


같은 공개 계약 copy·직접 자식 target과 inherited-only 관측을 전체 명시 반환/호출자 갱신·checkpoint/Review/최종 CAS에 연결했다. 원문/IO·donor provenance·부모 소유권·기존 화면을 보존한다. 최종 **LF19·CRLF16·패키지/전체 복원/실패 수명관리6, 총41단계(신규28·동등 재사용13)**가 통과했다. [범위·중단 복구·신규/재사용 증거와 잔여](VALIDATION_V666_ROOT_EXECUTION_OWNED_UPDATES.md)를 따른다. 유한한 남은 M12는 등록 외부 import/manifest/scope의 readonly 관측 결합이다. M4 및 고정 UI/실기기 검증은 별도다.


## M4 완료의 일반 분기 복귀 후속

직접 소유 ordinary root 안의 기존 C# Result 동작은 완료의 literal 포트/연결과 원문을 보존하는 일반 지역 분기로 전환하고 같은 ID로 async 재활성화한다. UI 표시명과 C# 식별자를 분리한다. async ordinary root의 Set 계획도 기존 소유/타입/원자 검증을 재사용한다. [정확한 경계](M4_ASYNC_TRANSITION.md).

유한한 M4 후속은 **공개 함수·호출자의 완료 일반분기 어댑터**, **Result 없는 next/native/whole-body 원문 보존 어댑터**, **새/내부 소유 본문과 실제 보조 편집 통합**이다. 앞선 지역 Result 지원과 Set 지원을 다시 잔여로 세지 않는다. 정상 비소유/override/ref/실제 await 거절 및 선택적 legacy 자동 변환은 새 필수 조합이 아니다. M11/M12는 닫힌 상태를 유지한다. V2–V9와 별도 팩·backend/종류 호환성 결정, 실제 기기·전체 UI·Space 전달은 기존 별도 잔여다.

완료 일반 분기·ordinary async Set의 동결 코드 `a24e3e2`를 신규 47단계(재사용 0)로 검증하고 최신/롤백 및 전체 증거를 보관했다. [최종 검증 기록](VALIDATION_V666_ASYNC_COMPLETION.md).


## M4 공개 함수 완료 후속

직접 소유한 기존 ordinary 함수/Blueprint target·직접 Blueprint 호출자의 완료를 같은 ID·값·literal 연결의 일반 공개 Result로 전환한다. C#·IO·지역 Result를 보존하며 기존 반환 카드의 명시 선택/이름 편집과 async 재활성화에 연결한다. [정확한 경계와 호환성](M4_PUBLIC_COMPLETION.md). Root 전환·실제 호출자 전체 관측과 final CAS를 유지하고, 재시작의 무관한 lazy body와 필수 importing body 누락을 구분한다.

다음 M4 흐름은 Result 없는 소유 next/native/whole-body 본문의 원문/출력 보존 어댑터, 새/내부 소유 본문의 명시 전환, property 보조 편집이다. 완료한 ordinary 공개 완료/지역 Result/Set을 다시 조합별 잔여로 추가하지 않는다. M11/M12는 관련 회귀를 제외하면 닫힌 상태를 유지하며 V2–V9·팩/backend·종류 호환성 및 실제 기기/전체 UI/Space 전달은 기존 별도 잔여다.

공개 완료의 최종 동결 `262f1a5`를 신규 52단계(재사용 0)로 검증하고 최신/롤백·전체 증거를 보관했다. [최종 검증 기록](VALIDATION_V666_PUBLIC_COMPLETION.md).

## M4 속성 편집 후속

기존 직접 소유 async root의 속성 검색·receiver/소비 연결·필드 쓰기를 원래 속성 UI와 propertyPlan 후보에 연결한다. 전환 가능 여부와 현재 async 시계 표시를 분리하며 프로젝트 관측을 최종 CAS까지 유지한다. 물리 원본 관측과 저장 응답 후보 해시를 분리해 후속 C# 편집·재시작을 허용하고, 전체 Confirm 뒤 관측을 종료해 반복 저장을 유지한다. [정확한 경계와 검증 계획](M4_ASYNC_PROPERTIES.md). 기존 Result 없는 본문 어댑터와 새/내부 소유 본문 전환은 남고, 기존 copy/slot/private 보호를 새 조합 요구로 확대하지 않는다. 최종 검증 수치는 종료 기록에서 확정한다.

속성 편집·관측/CAS의 최종 동결 `e4c0646`를 신규 48단계(재사용 0)로 검증하고 최신/롤백·전체 증거를 보관했다. [최종 검증 기록](VALIDATION_V666_ASYNC_PROPERTIES.md).

## M4 Result 없는 ordinary 동작 후속

기존 직접 소유 Root의 next 동작은 void/native 반환·out·원문/helper/source marker와 완료 ID/연결을 보존하는 별도 지역 선택기로 동기 복귀한다. 기본 None과 명시 완료 선택을 구별하고, 확정 후 원문/선택기 편집도 전체 관측·원자 저장·Review/최종 CAS에 연결한다. 창 숨김에서 팝업 입력을 보존하고 원래 본문 문맥으로 재진입하는 cold 복원을 검증한다. [정확한 지원·호환성과 유한한 후속](M4_COMPLETION_ADAPTER.md)을 따른다. 최종 LF/CRLF·패키지/전체 복원 수치는 종료 검증 기록에서 확정한다.

Result 없는 ordinary 동작 완료 어댑터의 최종 동결 `76f9837`은 **신규 39·동일 근거 재사용 9, 총 48단계**를 통과했다. 새 LF/CRLF 빌드·모든 UI·교차 패키지/전체 복원/실패 수명관리는 신규이며 [출처·실패 수정·정확한 재사용·보관 기록](VALIDATION_V666_COMPLETION_ADAPTER.md)에 경계를 유지한다. 다음 M4는 instance/native whole-body 문맥 및 새/내부 소유 본문 전환이며, 기존 완료 범위를 조합별 잔여로 다시 늘리지 않는다.

## M4 소유 whole-body 함수 후속

직접 소유하고 이미 Blueprint로 전환·확정한 native whole-body Root의 명시적 함수 async 전환을 연결한다. 원래 같은 클래스의 Invoke/this·직접 재귀/scoped import·소스 위치/CRLF·native 반환/out을 보존하고 동기 호출자의 오류와 별도 명시 전환을 유지한다. [정확한 경계와 유한한 종료 조건](M4_ASYNC_CONTEXT.md)을 따른다. 새/직접 소유 내부 본문 전환은 남으며 자동 원문 async 재작성·비소유/override/ref/구형 자동 migration은 새 요구로 추가하지 않는다. 최종 검증 수치는 종료 기록에서 확정한다.

소유 native Root async 전환의 최종 동결 `b3fa243`를 신규 42단계(재사용 0, LF/CRLF Core 각 18개 포함)로 검증하고 새 패키지/전체 복원과 최신/rollback·전체 증거를 보관했다. [정확한 검증·수정·호환/잔여](VALIDATION_V666_ASYNC_CONTEXT.md)를 따른다. 새/직접 소유 내부 본문의 명시 전환과 기존 고정 UI/backend/기기 잔여는 유지한다.

새 ordinary leaf의 첫 Confirm 전 async 전환을 총 45단계(LF/CRLF·새 패키지/전체 복원·실패 수명관리; 신규 39, 동일 입력 재사용 6)로 검증했다. [정확한 지원/실패·보관·유한 잔여](VALIDATION_V666_ASYNC_CREATING.md)를 따른다.

새 전역 함수의 첫 Confirm 전 async 생성 흐름은 신규 본 검사 48단계와 강제 포함 컴파일 보완 3단계를 통과했다(재사용 0). [지원 경계·증거·유한 잔여](VALIDATION_V666_ASYNC_NEW_FUNCTION.md)를 따른다.

정보 자체 함수의 직접 생성/배정 async 흐름은 최종 신규 51단계(재사용 0)를 통과했다. [지원·실패 수정·검증·보관과 유한 잔여](VALIDATION_V666_ASYNC_INFORMATION.md)를 따른다. M4 내부 Task·첫 생성 Save 전 입력 결합은 남는다.

내부 Task 기본 흐름의 최종 신규 55단계(재사용 0)와 실제 잔여를 [최종 기록](VALIDATION_V666_ASYNC_PRIVATE.md)에 마감했다. 연결된 내부 완료 분기 보존 동기 복귀와 첫 생성 Save 전 입력 결합은 남는다.

연결된 private Task 완료선은 같은 marker/선·native 반환/out을 보존하는 일반 결과로 동기 복귀하고, 기존 반환 카드에서 명시 선택한다. 기본 None과 완료 선택을 구별하며 공개 IO·원문을 바꾸지 않는다. 첫 생성 Save 전 입력 결합은 별도 유한한 M4 잔여다.

연결된 private 완료선의 일반 결과 복귀를 최종 신규 **57단계(재사용 0)**로 검증하고 새 패키지/전체 복원·최신/롤백·증거를 보관했다. [최종 결과](VALIDATION_V666_ASYNC_PRIVATE_RETURNS.md). 남은 유한한 M4는 첫 생성 Save 전 입력 결합이다.

## M4 첫 생성 Save 입력 결합 후속

새 전역/정보 소유 함수와 새 ordinary 동작 및 기존 직접 소유 내부 본문에서 C#·표시/값·지역 핀/연결과 명시 Task를 기존 원자 후보에 결합한다. 선언 자체가 아직 checkpoint되지 않은 전역 함수도 같은 소유 프로젝트/등록/원문/checkpoint의 정확한 일치로만 메모리 복구한다. [지원/미지원·유한한 후속](M4_ASYNC_FIRST_SAVE.md)과 [최종 검증 기록](VALIDATION_V666_ASYNC_FIRST_SAVE.md)을 따른다. 공개 Root 핀 계약의 새 전역 생성 후속은 [정확한 root IO 경계](M4_ASYNC_ROOT_IO.md)에서 연결했다. 이미 있는 원본·owner·복수 계약의 공동 갱신 보호는 유지한다. V2–V9와 기존 팩/backend·종류 결정·실기기/전체 UI/Space 전달은 그대로 구분한다.

첫 생성 Save의 직렬 소유 입력 결합은 최종 **68단계(신규 32·동등 근거 재사용 36)**로 검증했다. [당시 검증·지속 보관·후속 두 거래](VALIDATION_V666_ASYNC_FIRST_SAVE.md)를 따른다. 당시 남긴 공개 Root IO는 아래 후속으로 연결했고, 분기 실행선에서 만드는 새 동작의 첫 Task 결합도 아래 후속으로 연결했다. 정상 보호나 타입 조합을 새 목록으로 늘리지 않는다.

## M4 첫 Confirm 전 공개 IO 결합

새 직접 소유 전역 함수의 단일 구현/target에서 원본 공개 IO·값/연결과 명시 Task를 첫 원자 후보에 결합하고, Confirm 전 명시 재편집을 같은 생성 증명으로 다룬다. [정확한 경계](M4_ASYNC_ROOT_IO.md)와 [최종 검증 기록](VALIDATION_V666_ASYNC_ROOT_IO.md)을 따른다. 분기선에 만든 새 동작의 첫 Task 결합은 [후속](M4_ASYNC_BRANCH_CREATION.md)으로 연결했다. M11/M12는 닫힌 상태를 유지하고 기존 팩/backend/기기 잔여는 별도로 구분한다.

첫 Confirm 전 새 전역 root의 공개 IO 결합은 최종 **50단계(신규 50·재사용 0)**로 검증하고 최신/롤백과 증거를 지속 보관했다. [실제 지원·실패 수정·보관·후속](VALIDATION_V666_ASYNC_ROOT_IO.md)을 따른다. 분기선 새 동작의 첫 Task 결합도 아래 후속으로 연결했고 기타 고정 잔여를 완료로 계산하지 않는다.

## M4 분기선 새 동작 첫 Task 결합

완료/결과 분기선에 만든 직접 소유 ordinary 동작의 명시 C#·Task·연결을 첫 저장 후보로 연결한다. 기존 분기 ID·영역·목적지와 출력→완료→결과→연속 실행을 보존하며 새 권한/실행 계약은 추가하지 않는다. [정확한 지원](M4_ASYNC_BRANCH_CREATION.md)과 [최종 검증 기록](VALIDATION_V666_ASYNC_BRANCH_CREATION.md)을 따른다. 개발 중 성공/실패 근거와 최종 LF/CRLF·패키지/전체 복원 통과를 구분해 기록한다.

분기선 새 동작의 첫 Task 결합은 최종 **47단계(신규 47·재사용 0)**로 검증했다. [정확한 실행/실패/보관/한계](VALIDATION_V666_ASYNC_BRANCH_CREATION.md)를 따른다. 이로써 앞서 남긴 첫 생성 Save의 두 원래 결합 흐름을 마감하며 정상 보호나 선택적 조합을 새 필수 잔여로 늘리지 않는다. 기타 고정 UI/팩/backend/종류 결정·실기기 검증은 별도다.

## V2 C# 편집 안내 후속

지정한 14개 문구/16개 표시 지점만 v666 문체로 연결하고 소스 byte 차이의 허용 목록을 검증했다. 최종 **LF 12·CRLF 12·새 패키지/전체 복원/실패 수명관리 7, 총 31단계(신규 31·재사용 0)**를 통과했다. [실제 compiler Confirm·거절/입력 보존·실행·보관·검증 한계](VALIDATION_V666_CODE_EDITOR_GUIDANCE.md)를 따른다. 다른 V2 노출 화면과 V3–V9/팩/backend·종류 결정·실기기 검증은 고정 잔여로 유지하며 새 조합을 추가하지 않는다.

## V2 값·연산/핀 안내와 실패 입력 보존

지정 안내 15개와 직접 소유 root code 인자 전용 원자 저장 진입을 연결했다. 실제 발견한 레거시 Save의 쓰기 실패 입력 손실을 수정하고 기존 권한·원본/계약·Review/Confirm 경계를 보존했다. 최종 **LF 13·CRLF 13·패키지/전체 복원/실패 수명관리 7, 총 33단계(신규 33·재사용 0)**를 통과했다. [정확한 API/UI/실행 범위·개발 실패·보관·한계](VALIDATION_V666_VALUE_GUIDANCE.md)를 따른다. V2의 다른 계약/일반 저장/검토/탐색/시스템 안내와 다른 레거시 일반 Save의 입력 보존 확인·V3–V9/팩/backend·종류 결정·실제 기기/전체 UI/Space는 별도 잔여다.

## V2 일반 설명 저장 실패 복구 후속

직접 소유 root code intent와 함수 description-only Save·기존 Blueprint 진입의 재현된 입력 손실을 기존 원자 후보/CAS/receipt에 연결한다. 공유 Undo와 intent의 C# 재검토 의미를 보존한다. [정확한 범위·미수정 레거시 후보](V2_DESCRIPTION_RECOVERY.md)와 [개발/최종 검증 상태](VALIDATION_V666_DESCRIPTION_RECOVERY.md)를 따른다. 최종 **LF 17·CRLF 17·패키지/전체 복원/실패 수명관리 8, 총 42단계(신규 30·재사용 12)**를 통과했다. 다른 레거시 일반 Save와 V2 후속·실기기/전체 UI/Space는 별도 잔여다.

## V2 일반 C# 본문 저장 실패 복구 후속

직접 소유 ordinary root code source의 재현된 쓰기 실패 입력 손실을 기존 원자 후보/CAS/receipt와 공유 Undo에 연결한다. 기존 property source 관측 검증과 원문·권한·Review/Confirm 경계를 보존한다. [이번 범위·남은 레거시 후보](V2_SOURCE_RECOVERY.md)와 [검증 상태](VALIDATION_V666_SOURCE_RECOVERY.md)를 따른다. 최종 **LF 17·CRLF 17·패키지/전체 복원/실패 수명관리 8, 총 42단계(신규 42·재사용 0)**를 통과했다. 다른 레거시 일반 Save와 V2 후속·실기기/전체 UI/Space는 별도 잔여다.

## V2 일반 동작 표시명 저장 실패 복구 후속

직접 소유 ordinary root code 하나의 기존 compact 이름 입력을 원자 후보·CAS·receipt·공유 Undo와 연결한다. ID·C# 원문/계약·핀·연결과 권한을 보존한다. [지원 경계](V2_NAME_RECOVERY.md)와 [검증 상태](VALIDATION_V666_NAME_RECOVERY.md)를 따른다. 최종 **LF 16·CRLF 18·패키지/전체 복원/실패 수명관리 8, 총 42단계(신규 42·재사용 0)**를 통과했다. 다른 일반 Save 점검과 V2 후속·실기기/전체 UI/Space는 별도 잔여다.

## V2 일반 다음 실행선 저장 실패 복구 후속

직접 소유 ordinary root code 하나의 기존 next 목적지 입력을 원자 후보·CAS·receipt·공유 Undo와 연결한다. C# bytes·ID·핀/계약·다른 연결과 권한을 보존하며 명시한 실행 변화만 반영한다. [지원 경계](V2_ROUTE_RECOVERY.md)와 [검증 상태](VALIDATION_V666_ROUTE_RECOVERY.md)를 따른다. 최종 **LF 17·CRLF 18·패키지/전체 복원/실패 수명관리 8, 총 43단계(신규 43·재사용 0)**를 통과했다. 다른 일반 Save 점검과 V2 후속·실기기/전체 UI/Space는 별도 잔여다.

## V2 기존 함수 시작점 저장 실패 복구 후속

기존 직접 소유 root의 단일 entry 입력을 원자 후보·CAS·receipt·공유 Undo와 연결한다. 공개/override 계약·C# bytes·ID·다른 연결과 권한을 보존하고 명시한 시작 선택만 반영한다. [지원 경계](V2_ENTRY_RECOVERY.md)와 [검증 상태](VALIDATION_V666_ENTRY_RECOVERY.md)를 따른다. 최종 **LF 18·CRLF 20·패키지/전체 복원/실패 수명관리 8, 총 46단계(신규 46·재사용 0)**를 통과했다. root 핀/export·혼합 계약 등 다른 일반 Save 점검과 V2 후속·실기기/전체 UI/Space는 별도 잔여다.

## V2 기존 내보내기 값 저장 실패 복구 후속

기존 직접 소유 root의 단일 export 값만 원자 후보·CAS·receipt·공유 Undo와 연결한다. 기존 outputNodes 검증·공개/override 계약·C# bytes·ID·연결·권한을 보존한다. [지원 범위](V2_EXPORT_VALUE_RECOVERY.md)와 [검증 기록](VALIDATION_V666_EXPORT_VALUE_RECOVERY.md)을 따른다. 최종 **LF 19·CRLF 20·패키지/전체 복원/실패 수명관리 8, 총 47단계(신규 47·재사용 0)**를 통과했다. root 핀·export 구조·혼합 계약 Save와 V2 후속·실기기/전체 UI/Space는 별도 잔여다.

## V2 기존 내보내기 출력 재배정 저장 실패 복구 후속

기존 직접 소유 root의 단일 export 출력 재배정을 원자 후보·CAS·receipt·공유 Undo와 연결한다. 기존 outputNodes 검증·값·공개/override 계약·C# bytes·ID·연결·권한을 보존한다. [지원 범위](V2_EXPORT_BINDING_RECOVERY.md)와 [검증 기록](VALIDATION_V666_EXPORT_BINDING_RECOVERY.md)을 따른다. 최종 **LF 20·CRLF 21·패키지/전체 복원/실패 수명관리 8, 총 49단계(신규 49·재사용 0)**를 통과했다. root 핀·export 생성삭제/구조 혼합·혼합 계약 Save와 V2 후속·실기기/전체 UI/Space는 별도 잔여다.

## V2 기존 root 반환 출력 핀 값 저장 실패 복구 후속

기존 직접 소유 ordinary nonvoid root의 단일 반환 값만 원자 후보·CAS·receipt·공유 Undo와 연결한다. 공개 핀 정의/타입/순서·override 계약·C# bytes·ID·다른 연결·권한을 보존한다. [지원 범위](V2_ROOT_RETURN_RECOVERY.md)와 [검증 기록](VALIDATION_V666_ROOT_RETURN_RECOVERY.md)을 따른다. 최종 **LF 21·CRLF 22·패키지/전체 복원/실패 수명관리 8, 총 51단계(신규 51·재사용 0)**를 통과했다. root 핀 정의·export 생성삭제/구조 혼합·혼합 계약 Save와 V2 후속·실기기/전체 UI/Space는 별도 잔여다.

## V2 기존 내보내기 노드 삭제 저장 실패 복구 후속

기존 직접 소유 root의 단일 export 삭제를 원자 후보·CAS·receipt·공유 Undo와 연결한다. 기존 실행선 우회·profile의 out 기본값·남은 출력·공개/override 계약·C# bytes·ID·권한을 보존한다. [지원 범위](V2_EXPORT_REMOVAL_RECOVERY.md)와 [검증 상태](VALIDATION_V666_EXPORT_REMOVAL_RECOVERY.md)를 따른다. 최종 **LF 23·CRLF 23·패키지/전체 복원/실패 수명관리 8, 총 54단계(신규 54·재사용 0)**를 통과했다. root 핀 정의·export 생성/구조 혼합·혼합 계약 Save와 V2 후속·실기기/전체 UI/Space는 별도 잔여다.

## V2 새 내보내기·값·수동 실행선 첫 저장 복구 후속

직접 소유 root에서 기존 선언 출력에 export 하나를 만들고 값을 입력하며 ordinary code의 기존 next 목적지 사이를 수동 연결하는 네 입력을 원자 후보·CAS·receipt·공유 Undo와 연결한다. 원래 ID·출력/override 계약·C# bytes·남은 값/연결·권한과 기존 거절 경계를 보존한다. [지원 범위](V2_EXPORT_CREATION_RECOVERY.md)와 [검증 상태](VALIDATION_V666_EXPORT_CREATION_RECOVERY.md)를 따른다. 최종 **LF 24·CRLF 24·패키지/전체 복원/실패 수명관리 8, 총 56단계(신규 56·재사용 0)**를 통과했다. root 핀 정의·다른 생성/구조 혼합·혼합 계약 Save 및 직접 배치 점검과 V2 후속·실기기/전체 UI/Space는 별도 잔여다.

## V2 root 반환 핀 표시 위치 저장 실패 복구 후속

직접 소유 동기 root에서 out 둘의 상대 순서를 보존한 반환 핀 위치 선택을 원자 후보·CAS·receipt·공유 Undo와 연결한다. args/반환 타입·실제 C# 호출 계약·원문/ID/값/연결·부모/외부 원본·권한과 기존 root 검증/Review→Confirm을 보존한다. [지원 범위](V2_ROOT_OUTPUT_ORDER_RECOVERY.md)와 [검증 상태](VALIDATION_V666_ROOT_OUTPUT_ORDER_RECOVERY.md)를 따른다. 최종 **LF 25·CRLF 25·패키지/전체 복원/실패 수명관리 8, 총 58단계(신규 58·재사용 0)**를 통과했다. 다른 root 핀 정의·혼합 계약 Save·직접 배치 점검과 V2 후속·실기기/전체 UI/Space는 별도 잔여다.

## V2 root 입력 식별자 저장 실패 복구 후속

직접 소유 동기 root의 값 입력 하나를 기존 명시 remap으로 이름 변경하는 Save를 원자 후보·CAS·receipt·공유 Undo에 연결한다. 타입·위치·mode·반환 및 위치 기반 호출 계약·C# bytes·원래 node ID/연결·부모/외부 원본·권한·Review→Confirm을 보존한다. [지원 범위](V2_ROOT_INPUT_NAME_RECOVERY.md)와 [검증 상태](VALIDATION_V666_ROOT_INPUT_NAME_RECOVERY.md)를 따른다. 최종 **LF 26·CRLF 26·패키지/전체 복원/실패 수명관리 8, 총 60단계(신규 60·재사용 0)**를 통과했다. 다른 root 정의·혼합 계약 Save·직접 배치 점검과 V2 후속·실기기/전체 UI/Space는 별도 잔여다.

## V2 root 정의 저장 뒤 일반 본문 저장 복원 후속

이미 저장한 zero-dirty root 묶음에서 일반 C# source Save의 durable receipt가 바뀌어도 기존 함수·구현·그래프 멤버를 함께 보관한다. 새 편집/receipt·그룹 재구성·권한을 허용하지 않으며 원래 소유/계약/Restore/Review→Confirm/CAS/Undo와 UI를 보존한다. [지원 범위](V2_ROOT_FOLLOWUP_RECOVERY.md)와 [검증 상태](VALIDATION_V666_ROOT_FOLLOWUP_RECOVERY.md)를 따른다. 최종 **LF 18·CRLF 19·패키지/전체 복원/실패 수명관리 8, 총 45단계(신규 40·재사용 5)**를 통과했다. 다른 root 정의·혼합 계약 Save·직접 배치 점검과 V2 후속·실기기/전체 UI/Space는 별도 잔여다.

동일 흐름에서 cold revision만 달라진 개인 본문을 저장하는 동안 생긴 늦은 입력도 복구한다. 직접 소유한 단일 일반 source에서 정확한 성공 receipt·같은 캡처 입력·전체 소스 ID/해시가 확인돼야 새 기준에 연결한다. 다른 원본/입력이나 copy·비소유·혼합 계약으로 편집 범위를 넓히지 않는다.

## V2 새 일반 동작 직접 배치 첫 저장 복구

기존 root 그래프의 원래 다음 줄에 새 일반 void 동작 하나를 명시 삽입하는 생성·이름·설명·본문·두 실행선의 첫 Save를 원자 후보/receipt와 닫힌 미적용 기준 관측에 연결했다. **최종 LF 17·CRLF 16·패키지/전체 복원/실패 수명관리 8, 총 41단계(신규 34·재사용 7)**를 통과했다. 생성의 기존 `OWNERSHIP_CHANGED` 이력 경계와 이후 별도 본문 공유 이력을 구분해 보존한다. 공개 계약·native 권한·원본 C#·Review→Confirm·최종 CAS·기존 레이아웃은 유지한다. [지원 경계](V2_DIRECT_CREATION_RECOVERY.md)와 [검증 상태](VALIDATION_V666_DIRECT_CREATION_RECOVERY.md)를 따른다. 다른 root·혼합 계약·직접 배치 점검 후보와 기존 고정 잔여는 넓히지 않는다.

## V2 기존 동작 표시명·본문 함께 저장 복구

직접 소유 root의 같은 일반 next code 노드에서 표시명과 C# 본문을 함께 Save하는 두 입력의 유실을 재현했다. 정확한 두 편집을 원자 후보·ownedSource receipt·공유 이력과 늦은 두 입력의 출처 보존에 연결했다. **최종 LF 18·CRLF 17·패키지/전체 복원/실패 수명관리 8, 총 43단계(신규 20·재사용 23)**를 통과했다. 기존 계약/권한/원본/레이아웃과 Review→Confirm·최종 CAS를 보존한다. [지원 경계](V2_TEXT_PAIR_RECOVERY.md)와 [검증 기록](VALIDATION_V666_TEXT_PAIR_RECOVERY.md)을 따른다. 다른 root·혼합 계약·직접 배치 형태는 별도 점검 후보이며 새 필수 조합으로 늘리지 않는다.

## V2 여러 값 입력 중 하나의 이름 저장 복구

원래 노출된 root 입력 이름 편집에서 입력이 둘 이상일 때 재현된 실패 유실을 같은 원자 후보·receipt·공유 이력으로 연결한다. 기존 1–64개 값 입력 중 하나의 이름만 명시 remap으로 바꾸며, 다른 입력·위치 기반 계약·C# bytes·원본/권한/레이아웃·Review→Confirm/CAS를 보존한다. **최종 LF 17·CRLF 17·패키지/전체 복원/실패 수명관리 8, 총 42단계(신규 42·재사용 0)**를 통과했다. [정확한 지원 경계](V2_ROOT_VALUE_RENAME_RECOVERY.md)와 [검증 기록](VALIDATION_V666_ROOT_VALUE_RENAME_RECOVERY.md)을 따른다. 다른 root·혼합 계약·직접 배치는 재현 기반 점검 후보이며 조합별 새 필수 항목이 아니다.

## V2 같은 동작의 이름·설명·본문 함께 저장 복구

같은 직접 소유 ordinary root code/next 노드의 세 텍스트 입력이 쓰기 실패 뒤 유실되는 것을 재현했다. 이름·설명·본문 중 중복 없는 2–3개를 기존 원자 후보·receipt·공유 이력과 정확한 origin의 늦은 입력 복구에 연결했다. **최종 LF 17·CRLF 17·패키지/전체 복원/실패 수명관리 8, 총 42단계(신규 42·재사용 0)**를 통과했다. 기존 원문·계약·권한·레이아웃·Review→Confirm/CAS는 보존한다. [닫힌 범위](V2_NODE_TEXT_RECOVERY.md)와 [검증 기록](VALIDATION_V666_NODE_TEXT_RECOVERY.md)을 따른다. 다른 편집 종류나 조합을 새 필수 작업으로 추가하지 않는다.

## V2 기존 위치 기반 계약을 유지한 root 반환 핀 위치 저장 복구

같은 반환 표시 이동에서 값 입력 하나·out 셋인 root의 쓰기 실패 입력 유실을 재현했다.
기존 1–64개 전체 매개변수와 out 상대 순서·반환 타입이 동일한 반환 핀 표시 이동을
기존 원자 저장/receipt에 연결한다. 이미 마감한 out 둘 경로와 원문/계약/권한/레이아웃·
Review→Confirm/CAS는 보존한다. out 상대 순서 변경은 실제 ABI 변경이므로 계속 거절하며
새 필수 마이그레이션으로 늘리지 않는다. [닫힌 범위](V2_ROOT_RETURN_POSITION_RECOVERY.md)와
[검증 기록](VALIDATION_V666_ROOT_RETURN_POSITION_RECOVERY.md)을 따른다. 최종 **LF 17·CRLF 17·패키지/전체 복원/실패 수명관리 8, 총 42단계(신규 42·재사용 0)**를 통과했다.

## V2 기존 일반 동작 여러 개의 표시명 저장 복구

같은 직접 소유 root의 기존 code/next 동작 둘의 제목을 바꾸고 Save 쓰기를 실패시켰을 때
두 입력이 사라지는 것을 재현했다. 기존 2–64개 batch 예산 내의 서로 다른 기존 노드
표시명만 원자 후보/ownedRename receipt/공유 이력으로 연결한다. C#/계약/ID/값/연결·
권한·원본 레이아웃·Review→Confirm/CAS는 보존하며 다른 필드/계약 조합을 새로 허용하지
않는다. [닫힌 범위](V2_NODE_NAMES_RECOVERY.md)와
[검증 기록](VALIDATION_V666_NODE_NAMES_RECOVERY.md)을 따른다. 최종 **LF 17·CRLF 17·패키지/전체 복원/실패 수명관리 8, 총 42단계(신규 42·재사용 0)**를 통과했다.

## V2 void root 값 입력 이름 저장 복구

반환값이 없는 직접 소유 동기 함수의 기존 값 입력 이름 하나를 바꾸고 Save 쓰기를
실패시켰을 때 개인 계획이 사라지는 것을 재현했다. 기존 1–64개 값 입력/단일 명시
remap 경계를 void에도 연결하며 원래 반환 void와 출력 없음·위치 기반 호출 계약을
유지한다. nonvoid 지원·C#/원본·권한·레이아웃·Review→Confirm/CAS는 그대로다.
[닫힌 범위](V2_ROOT_VOID_NAME_RECOVERY.md)와
[검증 기록](VALIDATION_V666_ROOT_VOID_NAME_RECOVERY.md)을 따른다. 최종 **LF 17·CRLF 17·패키지/전체 복원/실패 수명관리 8, 총 42단계(신규 42·재사용 0)**를 통과했다.

## V6 선택 합계 4MiB 전송

기존 전체 보관 예산 내에서 파일당1MiB인 여러 명시 File을 합계4MiB까지 한 원자 저장에 연결한다. [범위와 저장/취소/재시도 수명](V6_RESOURCE_TRANSFER.md)을 따르며 과거 선택1MiB 검증은 당시 기록이다. 단일1MiB 초과 파일과 다른 형식 미리보기는 별도 잔여다.
최종 **61단계(신규61·재사용0)**의 [독립 checkout/패키지/복원·수명 검증](VALIDATION_V666_RESOURCE_TRANSFER.md)을 통과했다.

## V7 GIF 표시 후속

원본 GIF 그림의 정지·제한된 애니메이션을 기존 contain 패널에 연결한다. [프레임 가중 예산·원본 bytes·decoder 수명 경계](V7_RESOURCE_GIF.md)를 따르며 단일 큰 파일·다른 형식/전체 UI와 구분한다.
최종 **57단계(신규57·재사용0)**를 마감했다. [검증·지속 보관 기록](VALIDATION_V666_RESOURCE_GIF.md).

## V7 정지 AVIF 후속

원본 AVIF 그림의 기본 SDR8 색상/alpha를 기존 contain 화면에 연결한다. [항목/실제 sequence 크기·공유 표면 예산·native decoder 경계](V7_RESOURCE_AVIF.md)를 따르며 큰 파일·SVG·전체 UI와 구분한다.
최종 **57단계(신규57·재사용0)**를 마감했다. [검증·지속 보관 기록](VALIDATION_V666_RESOURCE_AVIF.md).

## V7 자체 포함 정지 SVG 후속

원본 이미지 분류의 SVG와 기존 그림 창을 [제한된 정지 SVG 표시](V7_RESOURCE_SVG.md)로 연결한다. 기존 보관 사본/ID/hash/읽기 권한과 native 저장·CAS는 바꾸지 않는다. 일반 raster와 공유한 픽셀 예산, XML 파싱 전 DTD 거절, 자체 포함 도형·경로·그라데이션·클리핑·텍스트와 실제 격리 이미지 디코딩을 사용한다. 외부 참조·script/style/animation/filter 및 지원 예산 밖의 SVG는 안전한 표시 거절이며 원본 사본은 남긴다. SVG 표준 전체나 편집 지원으로 확대하지 않는다. [최종 검사/한계](VALIDATION_V666_RESOURCE_SVG.md)는 동결 코드의 결과로 마감한다. 큰 파일·권한 backend·HD/물리 출력 및 초기 빈 화면 원인 미확정은 기존 잔여로 유지한다.
최종 **60단계(신규24·재사용36)**를 마감했다. [검증·지속 보관과 미실행 경계](VALIDATION_V666_RESOURCE_SVG.md).

## V8 명시적 HD 출력 후속

원본 Run 메뉴의1280×720·720×1280·1024×768을 [명시적 HD software profile](V8_RUN_HD.md)에 연결한다. 기존 Open의640/262144픽셀 기본값·공개 signature·실행 권한은 유지한다. OpenHD와 ConfigureSize/RequestedSize를 직접 선택한 프로젝트만 새921600픽셀 한도를 사용한다. 전역 RPC/pipe 한도를 늘리지 않고 소유 프레임의 불변 조각·전체 SHA 확인 뒤에 표시하며, size ACK/Step/작업 진행과 표시 완료를 분리한다. 큰 preset의 paired reader 제한을 보존하고 source/override/ReviewConfirm/CAS와 늦은 입력·닫기·cold를 보호한다. [최종 검증과 보관](VALIDATION_V666_RUN_HD.md)에서 신규/재사용과 실제 기기 미실행을 구분한다. FHD/4K·GPU/물리 출력·장치, 큰 파일/신원·권한 backend 및 초기 빈 화면 원인 미확정은 기존 잔여다.
최종 **65단계(신규35·동일성 확인 재사용30)**를 마감했다. [HD 검증·보관/미실행 기록](VALIDATION_V666_RUN_HD.md).

## V6 단일 큰 자료 보관 후속

원본의 명시 File 사본 보관을 [파일당4MiB·기존 전체4MiB의 경계](V6_RESOURCE_LARGE.md)로 연결한다. root/폴더의 기존 청크·원자 저장과 ID/영수증·최종CAS를 재사용한다. 기본 큰 read는 metadata-only이며 텍스트/코드의 첫1MiB는 [후속 prefix 관찰](V7_RESOURCE_TEXT_PREFIX.md)로 표시한다. 큰 rich 형식은 제한 안내로 구분한다. 큰 원본의 내용 편집/백업은 쓰기 전에 거절한다. 큰 사본을 가진 저장소의 구버전 reader/writer 비호환을 숨기지 않으며 작은 기존 자료는 이행하지 않는다. 검증·보관 결과는 [해당 기록](VALIDATION_V666_RESOURCE_LARGE.md)에서 확정한다. 4MiB 초과/총 보관량 확대·다른 rich 형식과 실제 권한 backend·기기 검증은 기존 잔여다.
최종 **58단계(신규27·재사용31)**를 마감했다. [큰 자료 검증·호환/보관·미실행 기록](VALIDATION_V666_RESOURCE_LARGE.md).

### 큰 텍스트 prefix 관찰 연결

4MiB까지 보관된 텍스트/코드의 첫1MiB를 [원본 prefix 흐름](V7_RESOURCE_TEXT_PREFIX.md)에
연결한다. 전체 큰 파일 전송/편집으로 확대하지 않는다. native 전체SHA·최종 의존성 검사와
브라우저 prefixSHA·생성세대/표시revision 검증을 구분하고 기존 metadata-only fallback을
유지한다. 큰 rich preview·내용편집/백업과4MiB 초과/총 보관량 확대는 기존 미지원 경계다.
M11/M12/M4는 회귀 근거 없이 다시 열지 않는다. 초기 빈 화면 원인은 미확정이고 실제 기기·
전체UI·신원/멤버/권한 backend는 미완료다. 이번 환경 복구 후 역사적 검증 ZIP/패키지는
현재 파일시스템에서 찾지 못했으며, 별도 체크아웃에서 재생성한 증거/보관본과 구분한다.

위 prefix 단위는 동결 `9588568e`의 [최종 신규45단계](VALIDATION_V666_RESOURCE_TEXT_PREFIX.md)로 마감했다. 선행 게시본 cold 읽기 실패1회는 재실행 통과와 구분해 원인 미확정으로 남긴다.

### 큰 PNG/JPEG의 원래 그림 패널 연결

원본 image 분기의1MiB 초과 사본 누락을 [PNG/JPEG 조각 관찰](V7_RESOURCE_RASTER_PARTS.md)에
연결한다. 기존 파일/합계4MiB·저장 v1·공개/override 계약과 pixel/lease 예산은 유지하며
whole hash 확인 뒤 기존 contain renderer를 사용한다. 별도 `imagePreview` capability로 이전
텍스트 `preview`와 metadata-only 호환성을 보존한다. 생성한 큰 PNG/JPEG·정확4MiB의 실제 픽셀,
변조/stale/중단·설명 입력·삭제/Home/cold/다른 프로젝트와 관련 작은 형식/텍스트 회귀를 검증한다.
큰 WebP/BMP/GIF/AVIF/SVG·문서 및4MiB 초과/보관량 확대, 신원/권한 backend·공유·기기/전체UI는
이 단위의 완료로 표현하지 않는다. 초기 빈 #app와 앞선 cold 읽기1회 원인은 미확정이다.

큰 PNG/JPEG는 동결 `a91bd900`의 [신규61단계](VALIDATION_V666_RESOURCE_RASTER_PARTS.md)와 새 교차 패키지/전체 복원·최신/롤백 보관으로 마감했다. 큰 다른 형식·기기/권한 backend 잔여와 선행 미확정 원인을 구분한다.


## V8 명시적 FHD 후속

원본1920×1080·1080×1920을 [명시 FHD 출력](V8_RUN_FHD.md)에 연결한다. 기존
Open/OpenHD의 공개 시그니처·실제 한도/소유권과 레이아웃·실행/권한·ReviewConfirm/CAS는
유지한다. FHD provider의 실제 pixels/size ACK·인증된 최대11개 조각·전체 SHA를 확인하며
Step/표시/3D 이동은 분리한다. 개인 FHD preset은 같은 JSON/receipt/CAS지만 구 reader의
한도 거절을 숨기지 않는다. QHD/4K/FHD+·GPU/물리 출력·기기/전체UI 및 초기 빈 화면의
미확정 원인은 별도 잔여다. M11/M12/M4는 구체적 회귀 없이 다시 열지 않는다.

FHD는 동결 `47262dc1`의 [총69단계(신규69·재사용0)](VALIDATION_V666_RUN_FHD.md)와 새 교차 패키지/전체 복원·최신/롤백 보관으로 마감했다. 이후 원본 해상도와 실기기/전체 UI·권한 backend의 잔여는 유지한다.

## V7 큰 PDF 후속

기존 보관1–4MiB PDF의 전체 조각/SHA 관찰을 [원본 PDF 페이지·배율 흐름](V7_RESOURCE_PDF_PARTS.md)에 연결한다. 기본 작은 PDF와 PNG/JPEG·텍스트, 원본 UI·쓰기/권한·ReviewConfirm/CAS는 유지한다. 실제 renderer/worker·수명 및 최종 LF/CRLF·새 패키지/전체 복원 결과는 해당 검증 기록에서 마감한다. 큰 다른 형식/내용 편집·4MiB 초과와 신원/권한·실기기/전체 UI·초기 빈 화면 원인 미확정은 구분한다.

큰 PDF는 동결 `d8279712`의 [신규51단계·재사용0](VALIDATION_V666_RESOURCE_PDF_PARTS.md)와 새 교차 패키지/전체 복원·최신/롤백 보관으로 마감했다. 큰 다른 형식·신원/권한·실기기/전체 UI와 초기 빈 화면 원인 미확정은 별도다.

## V7 큰 Office 후속

이미 보관한1–4MiB DOCX/XLSX/PPTX/ODT의 내용/워크시트 미리보기를 [기존 ZIP/XML 예산을 보존한 전용 관찰](V7_RESOURCE_OFFICE_PARTS.md)에 연결한다. 큰 문서는 읽기 전용이며 작은 DOCX/XLSX 편집·내용/백업·권한·ReviewConfirm/CAS와 원본 레이아웃은 유지한다. 최종 LF/CRLF·관련 회귀·새 패키지/전체 복원 및 보관 결과는 해당 검증 기록으로 마감한다. 큰 편집/다른 그림·4MiB 초과와 실제 신원·실기기/전체 UI·초기 빈 화면 원인 미확정은 구분한다.

큰 Office는 동결 61a72f55의 [신규61단계·재사용0](VALIDATION_V666_RESOURCE_OFFICE_PARTS.md)와 새 교차 패키지/전체 복원·최신/롤백 보관으로 마감했다. 큰 편집/다른 그림·신원/권한·실기기/전체 UI·초기 빈 화면 원인 미확정은 구분한다.

## V7 큰 BMP 후속

이미 보관한1MiB 초과–4MiB BMP를 [원래 형식/픽셀·디코더 수명의 그림 패널](V7_RESOURCE_BMP_PARTS.md)에 연결한다. 기존 조각/전체SHA·최종 관측과 저장·권한·원본UI/CAS는 유지한다. 큰 WebP/GIF/AVIF/SVG·내용 편집/백업·4MiB 초과와 실제 신원/권한 backend·실기기/전체 UI·초기 빈 화면 원인 미확정은 별도 잔여다.

큰 BMP는 동결 f4208fa3의 [신규57단계·재사용0](VALIDATION_V666_RESOURCE_BMP_PARTS.md)와 새 교차 패키지/전체 복원·최신/롤백 보관으로 마감했다. 큰 다른 그림·편집/권한 backend·실기기/전체 UI·초기 빈 화면 원인 미확정은 구분한다.

## V7 큰 정지 WebP 후속

이미 보관한1MiB 초과–4MiB 정지 WebP를 [기존 형식·실제 bitmap 수명·픽셀 예산의 그림 패널](V7_RESOURCE_WEBP_PARTS.md)에 연결한다. 조각/전체SHA·최종 관측과 원본UI·권한·저장/CAS는 유지한다. 큰 GIF/AVIF/SVG·내용 편집/백업·4MiB 초과, 실제 신원/권한 backend·실기기/전체 UI·초기 빈 화면의 미확정 원인은 별도다.

큰 정지 WebP는 동결 ec7cb80a의 [신규61단계·재사용0](VALIDATION_V666_RESOURCE_WEBP_PARTS.md)와 새 교차 패키지/전체 복원·최신/롤백 보관으로 마감했다. 큰 다른 그림·편집/권한 backend·실기기/전체 UI·초기 빈 화면 원인 미확정은 구분한다.

## V7 큰 GIF 후속

이미 보관한1MiB 초과–4MiB GIF를 [기존 정지/제한 애니메이션·가중 픽셀·수명의 그림 패널](V7_RESOURCE_GIF_PARTS.md)에 연결한다. 조각/전체SHA·최종 관측과 원본UI·권한·저장/CAS는 유지한다. 큰 AVIF/SVG·편집/백업·4MiB 초과와 실제 신원/권한 backend·실기기/전체 UI·초기 빈 화면의 미확정 원인은 별도다.

큰 GIF는 동결 e96f6e06의 [신규61단계·재사용0](VALIDATION_V666_RESOURCE_GIF_PARTS.md)와 새 교차 패키지/전체 복원·최신/롤백 보관으로 마감했다. 큰 다른 그림·편집/권한 backend·실기기/전체 UI·초기 빈 화면 원인 미확정은 구분한다.

## V7 큰 정지 AVIF 후속

이미 보관한1MiB 초과–4MiB 정지 AVIF를 [기존 profile·alpha/픽셀·수명의 그림 패널](V7_RESOURCE_AVIF_PARTS.md)에 연결한다. 조각/전체SHA·최종 관측과 원본UI·권한·저장/CAS는 유지한다. 큰 SVG·편집/백업·4MiB 초과와 실제 신원/권한 backend·실기기/전체 UI·초기 빈 화면의 미확정 원인은 별도다.

큰 정지 AVIF는 동결 82444451의 [신규63단계·재사용0](VALIDATION_V666_RESOURCE_AVIF_PARTS.md)와 새 교차 패키지/전체 복원·최신/롤백 보관으로 마감했다. 큰 SVG·편집/권한 backend·실기기/전체 UI·초기 빈 화면 원인 미확정은 구분한다.

## V7 큰 정지 SVG 후속

이미 보관한256KiB 초과–4MiB 정지 SVG를 [기존 geometry·권한·격리 수명의 그림 패널](V7_RESOURCE_SVG_PARTS.md)에 연결한다.1MiB 초과는 기존 조각/전체SHA 관측을 사용하고, 큰 XML 주석·markup를 파싱 전에 제한한다. 원본UI·소유 데이터·권한·저장/CAS는 유지한다. 큰 편집/백업·4MiB 초과와 실제 신원/권한 backend·실기기/전체 UI·초기 빈 화면의 미확정 원인은 별도다.

큰 정지 SVG는 동결 d94ee5e9의 [신규65단계·재사용0](VALIDATION_V666_RESOURCE_SVG_PARTS.md)와 새 교차 패키지/전체 복원·최신/롤백 보관으로 마감했다. 큰 편집/백업·보관량/권한 backend·실기기/전체 UI·초기 빈 화면 원인 미확정은 구분한다.

## V8 명시적 QHD 후속

원본의 `QHD / 2K · 2560 × 1440`을 [명시 QHD 출력](V8_RUN_QHD.md)에 연결한다. 기본/HD/FHD·원래 소유/권한·실제 크기 ACK·packet/RPC/파이프 I/O 예산과 레이아웃을 유지한다. 같은 private preset의 구 reader 한도와 새 OpenQHD/큰 전송의 paired-version 요구를 구분한다. 원본 텍스트 editor의1MiB 제한은 유지하며, 큰 DOCX/XLSX 편집·백업/개인 초안 전송과 다른 상위 출력·실기기/권한 backend는 별도 잔여다.

QHD는 동결 86a52b25의 [신규73단계·재사용0](VALIDATION_V666_RUN_QHD.md)와 새 교차 패키지/전체 복원·최신/롤백 보관으로 마감했다. 상위 출력/큰 Office 편집·신원/권한 backend·실기기/전체 UI·초기 거절/빈 화면의 원인 미확정은 구분한다.

## 원본 고정 Run 메뉴의 유한한 마감 단위

[원본15개 해상도 메뉴](V8_RUN_RESOLUTIONS.md)를 기존 관측 max/maxPixels에 연결한다.
시네마·FHD+ 등 현재 QHD로 가능한4개를 실제 출력에 연결하고,4K와 축/픽셀 초과4개는
표시하되 거절한다. 이 메뉴 단위와 상위 실제 출력 backend 잔여를 구분하며 임의 새 profile이나
해상도마다 별도 필수 조합을 늘리지 않는다. 기존 M11/M12/M4 완료와 원본/권한/CAS를 유지한다.

원본15개 고정 Run 메뉴는 동결 a50c4103의 [신규79단계·재사용0](VALIDATION_V666_RUN_RESOLUTIONS.md)와 새 교차 패키지/전체 복원·최신/롤백 보관으로 마감했다. 실제 상위 출력/4K backend와 나머지 Office/저장/신원 권한·실기기/전체 UI·원인 미확정 빈 화면은 별도다.

## V8 상위 원본 해상도의 실제 소프트웨어 출력

원본15개 고정 메뉴의 남은 UHD/DCI4K·1290×2796·1440×3200을 [명시 Open4K/profile4](V8_RUN_4K.md)에 연결한다. 기본/HD/FHD/QHD·관측/소유/ACK/packet/RPC/I/O 예산·UI를 보존한다. 실제 물리/GPU 지원과 큰 Office·저장·신원 권한 및 미확정 빈 화면 잔여를 구분한다. 최종 신규/재사용·보관/호환성은 검증 기록에서 마감한다.

원본 고정15개 메뉴의 실제 소프트웨어 출력은 동결 c661ae04의 [유효80단계(신규33·재사용47)](VALIDATION_V666_RUN_4K.md)와 새 교차 패키지/전체 복원·최신/롤백으로 명시4K까지 연결했다. 전체8192 custom·GPU/물리장치·큰Office/보관/실제신원·권한 backend와 원인 미확정 빈 화면은 별도다.

## V8 명시4K 관측 메모리

실제4K 관측의 전체 인코딩 문자열 중복을 [조각별 디코딩](V8_RUN_4K_MEMORY.md)으로 줄인다.
UI·프로필/공개 계약·저장 형식/구 reader 정책·SHA/소유·원자 게시와 기존 안전 경계를 유지한다.
이는 측정된 자원 사용 개선이며 새 타입/해상도 조합을 필수 잔여로 추가하지 않는다.
큰Office 편집/백업/초안 전송, 보관 범위·실제 신원/권한 backend·기존 종류 정책,
현재 예산 밖의 custom 출력과 실기기·전체 UI/초기 빈 화면 원인 미확정은 별도다.

4K 메모리는 동결 52082e6b의 [유효86단계(신규64·동일 입력 재사용22)](VALIDATION_V666_RUN_4K_MEMORY.md)와 새 패키지/전체 복원으로 검증했다. 할당량 중앙값 약66.63% 감소이며 전체 cgroup peak와 구분한다. 기존 구 reader 거절/작은 목록 호환·원본/권한/CAS와 별도 잔여는 유지한다.

## V7 큰 DOCX 편집 후속

기존4MiB 보관 사본의 [문단 편집·직전 내용 복원·조각 private 입력](V7_RESOURCE_DOCX_PARTS.md)을
연결한다. 원본 레이아웃·문단/표/보호 필드와 기본1MiB·RPC2MiB·import/실행/권한·최종CAS를
보존한다. 새 content/private 형식의 구 reader 거절과 원본 보존을 검증하며 자동 이행하지 않는다.
최종 LF/CRLF·생성/전체 복원·보관/실패 증거는 후속 검증 기록에서 마감한다. 큰 XLSX 편집·
전체 보관 확대·권한 backend·실기기/전체 UI 및 원인 미확정 초기 빈 화면은 별도다.

큰 DOCX 편집/복원/private 초안은 동결 48242375의 [신규62단계·재사용0](VALIDATION_V666_RESOURCE_DOCX_PARTS.md), 새 교차 패키지와 전체 복원으로 검증했다. 기본1MiB/다른 Office 제한·원본/권한/CAS·구 reader 명시 거절과 별도 고정 잔여를 유지한다. 초기 빈 화면과 공개 cold 실패 원인은 미확정이며 실제 기기/Office 앱/전체UI 완료가 아니다.

## V7 큰 XLSX 편집 후속

기존4MiB 보관 사본의 [셀 편집·직전 내용 복원·조각 private 입력](V7_RESOURCE_XLSX_PARTS.md)을 연결한다. 원본 시트/수식/보호/병합·문체/레이아웃과 기본1MiB·RPC2MiB·import/권한·최종CAS, 완료된 DOCX를 보존한다. 새 XLSX content format/private codec의 구 reader 거절과 원본 보존을 검증하며 자동 이행하지 않는다. 최종 독립 LF/CRLF·새 패키지/전체 복원·실패/보관 증거에서 마감한다. 보관 확대/권한 backend·실기기/전체UI 및 초기 빈 화면 원인 미확정은 별도다.

큰 XLSX 편집/복원/private 초안은 동결 141f0b17의 [유효70단계·신규28/동일 입력 재사용42](VALIDATION_V666_RESOURCE_XLSX_PARTS.md), 새 패키지·전체 복원으로 검증했다. 작은 XLSX/기존 DOCX·원본/권한/CAS와 구 reader 명시 거절을 보존한다. 초기 빈 화면 원인은 미확정이고 실제 기기/Office 앱/전체UI 완료가 아니다.

## V8 직접 입력8192축의 명시 출력

원본 `app.js`의240–8192 직접 입력을 [OpenCustom/profile5](V8_RUN_CUSTOM_AXIS.md)에
연결한다. 총8,847,360픽셀·45조각·기존 packet/RPC/I/O/메모리 예산과 profile0–4·원본15개
메뉴·권한/소유/CAS를 유지한다. 새 등록값의 구4K reader 거절/작은 목록 호환을 명시한다.
최종 검사/보관은 검증 기록에서 마감한다. 전체8192²/물리 출력·4MiB 초과/총보관·신원/권한
backend·종류 정책·실기기/전체UI 및 원인 미확정 초기 빈 화면은 별도다.

직접 입력8192축은 동결 b810acbc의 [유효102단계·신규91/동일 입력 재사용11](VALIDATION_V666_RUN_CUSTOM_AXIS.md), 새 패키지/전체 복원으로 검증했다. 총 픽셀 예산·기존 프로필/원본 메뉴/권한/CAS와 구 reader 거절·작은 목록 호환을 보존한다. 전체8192²/물리 출력과 기존 별도 잔여·미확정 초기 빈 화면을 완료로 세지 않는다.

## V6 누적 자료 사본 보관

원본의 명시 File 축적을 [누적8MiB 저장 경계](V6_RESOURCE_TOTAL.md)에 연결한다. 파일당/
선택4MiB·64개·RPC/업로드·원자 CommitPlan은 유지한다. 기존 v1은 재작성하지 않고 명시
추가가4MiB를 넘는 후보만 v2로 승격한다. 구 reader 거절/기존 v1 호환·원본/권한/CAS를
검증하며 더 큰 파일/일반 보관 확대와 실제 신원/권한·종류 정책·실기기/전체UI는 별도다.

누적8MiB 보관은 동결 a505ab74의 [신규82단계·재사용0](VALIDATION_V666_RESOURCE_TOTAL.md), 새 교차 패키지/전체 복원으로 검증했다. 기존 파일/선택4MiB·v1 호환과 v2 구 reader 거절·원본/권한/CAS를 보존한다. 더 큰 저장·신원/권한·종류 정책·실기기/전체UI와 미확정 빈 화면은 별도다.

## V7 자료 원본 파일 열기

원본 파일 메뉴의 [현재 저장본 전체 열기](V7_RESOURCE_ORIGINAL.md)를 연결한다.
최초 import/개인 초안/OS 경로와 구분하고 기존 파일당4MiB·누적8MiB·관측/권한/저장/CAS와
레이아웃을 유지한다. 새 창의 active MIME 무해화·SHA/최종 재관측·지연 응답/취소를 검증한다.
최종 LF/CRLF·새 패키지/전체 복원·보관 기록에서 이 유한한 메뉴 흐름을 마감한다.
상위 카테고리 열기·큰 보관/실제 신원 권한·종류 정책·실기기/전체 UI·초기 빈 화면 원인 미확정은 별도다.

원본 파일 열기는 동결 ec88e8d6의 [신규53단계·재사용0](VALIDATION_V666_RESOURCE_ORIGINAL.md), 새 교차 패키지와 전체 복원으로 검증했다. 마지막 저장본/개인 초안·원본/권한/CAS·기존 크기 예산을 보존한다. 상위 카테고리 열기 및 기존 별도 잔여·미확정 초기 빈 화면·실기기/전체UI는 구분한다.

## V7 자료 상위 카테고리 열기

원본의 [독립 상위 카테고리 창](V7_RESOURCE_PARENT.md)을 파일/카테고리/root에 연결한다.
현재 위치·선택·포커스와 기준 트리·기존 복제/복원을 유지하고 순수 metadata 관측을 마지막에
재확인한다. 원본 창의 검색/입력·실제 소유/권한·저장/CAS는 보존한다. 기존 cold 검색 표시
결함도 저장된 입력을 폐기하지 않고 수정한다. 최종 독립/패키지/전체 복원·보관 기록에서 마감한다.

상위 카테고리 열기는 동결 d872b05e의 [신규49단계·재사용0](VALIDATION_V666_RESOURCE_PARENT.md), 새 교차 패키지와 전체 복원으로 검증했다. 독립 root/선택/포커스·원본 입력/권한/CAS와 현재 key 기반 복원을 보존한다. 더 큰 보관/신원 권한·종류 정책·미확정 초기 빈 화면·실기기/전체UI는 별도다.

## V6 자료 종류 필터

원본 정렬 앞의 [자료 종류 다섯 선택지](V6_RESOURCE_KIND_FILTER.md)를 현재 폴더·검색·정렬에
연결한다. 카테고리 유지·숨겨진 선택 해제·창별 private 복원과 기존 입력/권한/CAS를 보존한다.
메시 필터가 새 mesh renderer를 뜻하지 않는다. 최종 독립/패키지/전체 복원·보관 기록에서 마감한다.

자료 종류 필터와 같은 세대의 Data 설명 cold 재결합은 동결 5e3ec519의 [신규57단계·재사용0](VALIDATION_V666_RESOURCE_KIND_FILTER.md), 새 교차 패키지와 전체 복원으로 검증했다. 원래 입력/revision·pending receipt/새 세대·프로젝트 격리와 native 권한/CAS를 보존한다. 더 큰 보관/신원 권한·종류 정책·미확정 초기 빈 화면·실기기/전체UI는 별도다.

## V6 자료 탐색 키보드

원본의 [다섯 목록 단축키](V6_RESOURCE_KEYBOARD.md)를 기존 native 열기·이름·삭제 확인
경로에 연결한다. 보이는 선택·입력/IME·미확정 요청·늦은 확인/창 수명과 원본/권한/CAS를
보존한다. 최종 독립/새 패키지/전체 복원·보관 검증으로 이 유한한 흐름을 마감한다.

다섯 자료 목록 단축키는 동결 2a81b552의 [신규57단계·재사용0](VALIDATION_V666_RESOURCE_KEYBOARD.md), 새 교차 패키지와 전체 복원으로 검증했다. 실제 실패/재시도/cold/CAS·자료 body의 Delete 전파 경계와 기존 원본/권한/입력을 보존한다. 더 큰 보관/신원 권한·정보 종류 정책·미확정 초기 빈 화면·실기기/전체UI는 별도다.


## V6 자료 정렬 입력 보호

원본 네 정렬의 [미확정 입력·메뉴 수명](V6_RESOURCE_SORT.md)을 기존 표시 상태에 연결한다. 게시본에서 실제 재현된 설명 blur 저장과 이전 메뉴의 새 선택 덮어쓰기를 수정하며 native 원본/권한/CAS와 기존 레이아웃·저장 형식을 보존한다. 독립 LF/CRLF·새 패키지/전체 복원 및 보관 결과에서 마감한다. 기존 큰 보관/backend·종류 정책·미확정 초기 빈 화면·실기기/전체UI 잔여는 유지한다.

자료 정렬의 입력·이전 메뉴 보호는 동결 f14deb1a의 [신규61단계·재사용0](VALIDATION_V666_RESOURCE_SORT.md), 새 교차 패키지/전체 복원과 최신/롤백 보관으로 마감했다. 기존 원본/권한/CAS·표시/저장 호환을 보존하며 고정 backend/종류 정책·미확정 초기 빈 화면·실기기/전체UI 잔여는 별도다.


## V6 원본 자료 Data 행

원본의 [종류·크기·명시 열기와 이름 버튼](V6_RESOURCE_DATA.md)을 현재 native metadata와 기존 인라인 편집에 연결한다. 원본 CSS·설명 입력/미확정 저장·권한/CAS·private 복원을 보존한다. 독립 LF/CRLF·새 패키지/전체 복원과 보관 기록으로 마감한다. 기존 큰 보관/backend·종류 정책·초기 빈 화면 원인 미확정·실기기/전체UI는 별도다.

원본 자료 Data 행/이름·열기의 입력 보호는 동결 294ba7f1의 [유효67단계·신규35/재사용32](VALIDATION_V666_RESOURCE_DATA.md), 새 교차 패키지/전체 복원과 최신/롤백 보관으로 마감했다. 기존 원본/권한/CAS·표시/저장 호환을 보존하며 고정 backend/종류 정책·미확정 초기 빈 화면·실기기/전체UI 잔여는 별도다.


## V6 모든 자료 목록의 파일명 활성화

원본 Compact/Preview의 [선택 후 이름 재클릭](V6_RESOURCE_NAME.md)을 이미 검증된 공통 Data 이름 처리에 연결한다. 기존 태그/배치·F2/우클릭·원문·권한/CAS·미확정 저장과 cold 복구를 보존한다. 독립 LF/CRLF·새 패키지/전체 복원 및 최신/롤백 검증으로 마감하며 기존 고정 backend/정책/미확정 원인·실기기 잔여는 유지한다.

Compact/Preview/Data 파일명 활성화는 동결 11b38f1a의 [신규50단계·재사용0](VALIDATION_V666_RESOURCE_NAME.md), 새 교차 패키지/전체 복원과 최신/롤백 보관으로 마감했다. 원본/권한/CAS·표시/저장 호환과 고정 backend/정책·미확정 원인·실기기/전체UI 잔여를 보존한다.


## 고정 혼합 저장: 기존 값 이름과 본문

[직접 소유 ordinary root의 별칭 이름·연결과 C# 본문 하나](V536_ALIAS_SOURCE_SAVE.md)를 같은 후보/CAS에 연결한다. 기존 Unicode 표시명/ID/소비자·명시 본문과 공개/override 계약·원본/권한을 보존한다. 고정 혼합 저장의 한 흐름이며 M11/M12/M4를 다시 열거나 모든 타입/문맥 조합을 추가하지 않는다. 독립 LF/CRLF·새 패키지/전체 복원·최신/롤백과 입력/실패 수명관리로 마감한다.

직접 소유 root의 기존 값 이름/연결과 C# 본문 하나의 결합 저장은 동결 3897515c의 [신규39단계·재사용0](VALIDATION_V666_ALIAS_SOURCE.md), 새 패키지/전체 복원과 최신/롤백 보관으로 마감했다. 그 밖의 고정 혼합 저장·권한/종류 정책·미확정 원인·실기기/전체UI 잔여는 유지한다.

## 고정 혼합 저장: 기존 값 이름과 일반 next 실행선

[직접 소유 동기 root의 기존 값 이름·소비자와 명시 next 실행선 묶음](V536_ALIAS_ROUTES_SAVE.md)을 한 후보/CAS에 연결한다. 게시본의 실제 공동 Save 거절을 재현한 흐름이며 기존 값 이름+C# 본문·순수 실행선 지원을 보존한다. 원래 코드 바이트·저장소/노드/핀 identity·계약·권한과 Review/Confirm을 유지한다. 다른 문맥의 가능한 조합을 새 필수 항목으로 늘리거나 M11/M12/M4를 재개하지 않는다. 최종 독립 검사·패키지/복원·보관 결과로 마감한다.

기존 값 이름·소비자와 일반 next 실행선의 결합 저장은 동결 047a71fa의 [신규40단계·재사용0](VALIDATION_V666_ALIAS_ROUTES.md), 새 패키지/전체 복원과 최신/롤백 보관으로 마감했다. 나머지 고정 혼합 계약·backend/정책·실기기/전체UI 및 미확정 초기 빈 화면은 유지한다.

## V2 공통 함수 상세창의 IME 취소 키

[상세창·타입 검색의 IME Escape 보호](V2_SIGNATURE_IME.md)는 조합 취소와 편집 전체 취소를 구별한다. 게시본의 실제 DOM 이벤트로 입력 유실을 재현했고 두 공통 Escape 처리만 기존 guard에 맞췄다. 일반 Escape·명시 닫기/취소/저장·owner/창 수명·레이아웃과 native 계약/권한/CAS를 보존한다. 실제 OS IME와 자동화 이벤트를 구분하며 독립 LF/CRLF·패키지/전체 복원·보관 기록에서 마감한다. 핀 표시명/고급 ABI 정책과 초기 빈 화면 원인 미확정은 별도다.

공통 함수 상세창·타입 검색의 조합 취소 Escape 입력 보호는 동결 ecb47f0a의 [신규29단계·재사용0](VALIDATION_V666_SIGNATURE_IME.md), 새 패키지/전체 복원과 최신/롤백 보관으로 마감했다. 실제 OS IME/전체UI·시작 자원 표본 두 개의 증거 수집 한계·핀 표시명/ABI 및 기존 backend/종류 정책·미확정 초기 빈 화면은 구분해 남긴다.

## V2 공통 아이콘 창의 조합 취소 키

[기호·선택 이미지의 IME Escape 보호](V2_GLYPH_IME.md)는 원래 미적용 팝오버 복사본을 조합 취소 키에서 보존한다. 게시본의 네 실제 DOM 이벤트 사례를 재현했으며 공통 listener 한 곳만 기존 guard에 맞춘다. 일반 Escape/닫기/적용·이미지 수명·native 원본/권한/CAS/저장 문법·기존 레이아웃을 보존한다. 실제 OS IME와 자동화 이벤트를 구분하고 독립 LF/CRLF·새 패키지/전체 복원·보관 검증으로 마감한다. 기존 고정 잔여를 가능한 조합별로 늘리지 않는다.

공통 아이콘 창의 조합 취소 Escape 입력 보호는 동결 fe3d35dd의 [신규29단계·재사용0](VALIDATION_V666_GLYPH_IME.md), 새 패키지/전체 복원과 최신/롤백 보관으로 마감했다. 기호/생성 이미지의 미적용 입력·명시 저장과 원본/권한/CAS를 보존하며 실제 OS IME/전체UI·기존 계약/backend/정책 잔여 및 초기 빈 화면 원인 미확정은 구분한다.


기존 로컬 helper를 호출하는 여러 직접 소유 C# 본문을 한 Save에 결합하는 경계는
[V666_NATIVE_BODY_IMPORTS.md](V666_NATIVE_BODY_IMPORTS.md)를 따른다. 원래 ABI/import/caller를 유지하고,
이미 관측한 소유 원문을 기존 version3 readGuards와 최종 lease에 연결한다.

기존 로컬 import의 여러 C# 본문 저장은 최종 **신규13·동등재사용25, 유효38단계**로 검증했다.
[실패·보관·유한 잔여](VALIDATION_V666_BODY_IMPORTS.md)를 따르며 전체8행 완료로 세지 않는다.

기존 C# 호출자를 보존한 여러 본문 저장은 최종 **신규41단계·재사용0**을 통과했다.
[실제 수용·실패/미확정·보관·잔여](VALIDATION_V666_NATIVE_CALLERS.md)를 따른다.


[정보 함수 고정 반환 슬롯 표시명](V666_RETURN_LABEL.md)은 원래 상세창 이름칸과
선택 metadata를 연결한다. `return` ID·C# ABI/원문·호출 연결을 유지하며, 일반 인자/out
이름의 계약 의미는 바꾸지 않는다. 9행 전체/고급 정보·참조 실행 표현과 다른 실제
closure를 완료로 세지 않으며 신규36단계·재사용0의 [확정 검증·보관](VALIDATION_V666_RETURN_LABEL.md)을 마쳤다.


[기존 일반 호출자 보존](V666_RETAINED_CALLERS.md)은 고정8행의 같은 계약 native
본문 공동 저장을 기존 code/local caller에 연결한다. 변경 없는 코드 기록은 원래
바이트를 유지하고 caller source는 기존 읽기 CAS로 보호한다. 전체8행/다른 closure나
고급 타입 표현을 완료로 세지 않으며 신규34단계·동등 재사용7, 유효41단계의 [확정 검증·보관](VALIDATION_V666_RETAINED_CALLERS.md)을 마쳤다.


[기존 호출자의 실행 분기 보존](V666_RETAINED_BRANCHES.md)은 같은 계약의 직접 소유
native 본문 공동 저장에서 기존 ordinary code branch/switch를 읽기 의존성으로
유지한다. 실행 분기 ID·값·연결·종료점·C# 원문과 public/override 계약·권한·UI를
바꾸지 않는다. copy/forward/wrapper 및 다른 실제 ABI closure·고급 타입 선택은
기존 잔여이며 경우의 수별 새 필수로 늘리지 않는다. [신규41단계·재사용0의 확정 검증·보관](VALIDATION_V666_RETAINED_BRANCHES.md)을 마쳤다.


[명시 검토한 플랫폼별 C# 본문 공동 저장](V666_MULTITARGET_BODIES.md)은 같은 계약의
직접 소유 함수 여러 개에서 기존 native target을 각각 선택·편집하는8행 흐름이다.
원래 target/핀/호출 연결·C# 원문·권한과64-member Review/최종 CAS를 보존한다.
모든 영향 target의 명시 검토와 source 전체 관측을 요구하며 자동 복제·미검토 승인은
하지 않는다. 고급 타입 선택·다른 실제 ABI/source closure는 기존 잔여다.
[신규42단계·재사용0의 확정 검증·보관](VALIDATION_V666_MULTITARGET_BODIES.md)을 마쳤다.


[기존 중첩 호출자 보존](V666_RETAINED_NESTED.md)은 고정8행의 같은 계약 native
본문 공동 저장에서 기존 private graph와 qualified C#·형제/지역값을 읽기 의존성으로
유지한다. 원래 계약·원문 바이트·실행 연결·권한·레이아웃과 최종 CAS를 보존한다.
다른 실제 ABI/source closure와9행의 표시명·고급 타입 선택은 기존 잔여다.
[신규42단계·재사용0의 확정 검증·보관](VALIDATION_V666_RETAINED_NESTED.md)을 마쳤다.


[기존 호출 후처리 보존](V666_RETAINED_WRAPPERS.md)은 고정8행의 같은 계약 native
본문 공동 저장에서 기존 serial After·enum wrapper C#/helpers·출력/실행 계약을 유지한다.
wrapper만 있는 호출자도 원래 source 전체의 읽기 CAS와 조립 C# 컴파일에 포함한다.
다른 실제 ABI/source closure와9행의 표시명·고급 타입 결정은 기존 잔여다.
[신규43단계·재사용0의 확정 검증·보관](VALIDATION_V666_RETAINED_WRAPPERS.md)을 마쳤다.


[기존 소유 복사본 호출자 보존](V666_RETAINED_COPIES.md)은 고정8행의 같은 계약 native
본문 공동 저장에서 이미 단독 배정된 local copy의 원래 receipt와 source를 유지한다.
내부 후보에 저장된 명시 함수 설명의 해시만 검증된 overlay로 연결하며 실파일 기준을
재설정하지 않는다. 정보별 C# 구조체 생성은 사용자 결정으로 확정됐고 세부 참조/스키마
호환 정책은 별도다. 다른 실제 source/ABI closure·9행·전체 UI를 완료로 세지 않는다.
[신규43단계·재사용0의 확정 검증·보관](VALIDATION_V666_RETAINED_COPIES.md)을 마쳤다.


정보 정의별 C# 타입은 사용자 결정에 따라 **별도 struct**로 생성한다. [첫 생성·컴파일
기반](V666_INFORMATION_STRUCTS.md)은 단일 기본형 필드/상속·빈 정보의 nominal 값 타입,
native 함수 입력·반환·실제 링크와 동일 계약 본문 저장의 스키마 source/CAS를 연결한다.
표시명은 정체성을 바꾸지 않고 필드 변경은 의존 산출물을 갱신한다. 기존 객체 ID 참조를
값 복사로 바꾸지 않으며 타입 선택 UI·복합/reference/종류·고급 Blueprint 대응은 같은9행의
후속 범위다. 구 parser 제한과 원문/권한/override 보호는 위 문서를 따른다.
이 정보 구조체 단위의 [신규40단계·재사용0 검증·보관](VALIDATION_V666_INFORMATION_STRUCTS.md)을 마쳤다.


[단일 복합 정보 구조체](V666_INFORMATION_COMPOUND.md)는 기존9행의 값 포함을 자식
struct 전체 closure·전이 shape·pack compiler/link 참조와 같은 본문 저장/CAS에 연결한다.
primitive v1의 생성 source/hash와 정보 ID별 CLR 이름은 유지한다. 구 v1 compiler의 명시
거절/원문 보존과 구 parser 경계를 구별하며 자동 migration은 만들지 않는다. 타입 선택 UI,
reference/종류 등은 같은 잔여다. 사용자는 종류는 C# enum, 모듈은 C# interface로 확정했다.
종류의 기존 항목 ID 안정성을 숫자 연결에서도 유지하며 표현 선택을 다시 묻지 않는다.
이 복합 정보 단위의 [신규44단계·재사용0 검증·보관](VALIDATION_V666_INFORMATION_COMPOUND.md)을 마쳤다.


[종류 enum·모듈 interface 연결](V666_NAMED_CLR.md)은 고정9행의 native 타입 생성을
확장한다. 종류는 항목 ID와 영구 int32 예약표를 분리하고 이름/순서 변경에 안정적이다.
기존 v1은 명시 준비/항목 저장에서만 v2로 전환하며 구 reader 제한을 안내한다. 단일
종류 필드와 enum/interface 함수 입출력·같은 계약 본문 저장/CAS를 연결한다. 모듈의
첫 interface는 동기 기본형/배열 요구 계약이며 default를 자동 선택/실행하지 않는다.
타입 선택 UI·살아 있는 reference 접근/수명·multiple/함수 필드·고급 Blueprint 대응과
모듈의 고급 요구 계약은 같은 고정9행 잔여다. [신규47단계·재사용0 검증·보관](VALIDATION_V666_NAMED_CLR.md)을 마쳤다.


[모듈의 nominal 요구 계약](V666_MODULE_NOMINAL.md)은 고정9행에서 정보 struct·종류 enum·
다른 interface를 요구 메서드의 원래 입력/반환/ref/out에 투영하고 전체 타입 의존성을
추적한다. primitive-only module source/profile/hash는 유지한다. 깊은 정보 변경과 요구
모듈 자체의 dependency 검사를 같은 생성·본문 후보·최종 CAS에 연결한다. 함수 타입 선택
UI 전체와 살아 있는 참조 접근을 완료로 세지 않는다. async/공개 실행 요구·CLR interface
상속/upcast·선택 타입 순환은 명시 지원 경계이며 조합별 migration 요구를 추가하지 않는다.
[신규22·동등 재사용23 검증·보관](VALIDATION_V666_MODULE_NOMINAL.md)을 마쳤다.

후속 [함수 상세 native 타입 선택](V666_FUNCTION_NATIVE_TYPES.md)은 직접 소유 정보의
새 함수 첫 계약에 지원 nominal 타입/배열을 연결한다. 기존 상세창의 검색/다중 선택을
재사용하고 정의 초안과 디스크 원본, 등록 manifest를 별도 확인하며 최종 source lease에
읽기 증거를 유지한다. 전체 고급 타입 UI·live reference·module async/분기 완료로 합산하지 않는다.

이 한정 범위의 [최종 신규41단계·재사용0 검증/보관](VALIDATION_V666_FUNCTION_NATIVE_TYPES.md)을 마쳤다.
정보 소유 새 함수의 native 타입 선택과 보호 초안 v2에 해당하며, 기존 연결 고급 ABI UI·live reference·
module async/공개 실행 계약 및 실제 기기/전체 UI 수용은 합산 완료하지 않는다.

후속 [기존 정보 기능의 native 타입 전환](V666_EXISTING_NATIVE_TYPES.md)은 구현·호출·요구
계약이 없는 직접 소유 동기 기능의 입력/out/반환·배열을 기존 상세창에 연결한다.
사용처 부재와 원본 읽기 증거를 Save/Review/최종 CAS에 결부하며, 첫 구현은 전환
Confirm 뒤에 작성한다. Confirm 후 같은 세션의 저장이 오래된 receipt를 상속해 거절되던
결함도 수정한다. 연결된 nominal ABI 대응·live reference·module async/공개 실행 계약과
실제 기기/전체 UI는 같은 고정 잔여이며 새 선택 조합을 필수 목록으로 늘리지 않는다.

이 한정 범위의 [최종 신규45단계·재사용0 검증/보관](VALIDATION_V666_EXISTING_NATIVE_TYPES.md)을 마쳤다.

후속 [C# 구현·호출자 native 타입 전환](V666_CONNECTED_NATIVE_TYPES.md)은 직접 소유 일반
동기 기능과 일반 C# 구현·직접 호출자의 고급 타입 선택을 기존 명시 본문 대응에 연결한다.
모든 영향 본문을 한 후보/Review/CAS에 묶고, 선택한 등록 외부 타입은 읽기 전용 컴파일
사전에 전달한다. 수락된 본문 계획을 늦은 이름 Save가 다시 제출하지 않도록 정산한다.
Blueprint/상속·비소유 전환, 살아 있는 참조와 module async/공개 실행 요구는 같은9행 잔여다.

이 한정 범위의 [최종 신규45단계·재사용0 검증/보관](VALIDATION_V666_CONNECTED_NATIVE_TYPES.md)을 마쳤다.

후속 [직접 Blueprint 호출자의 고급 타입 입력](V666_BLUEPRINT_NATIVE_INPUTS.md)은 같은9행의
기존 caller 입력을 명시적으로 선택해 native 계약과 본문 계획을 원자 저장한다. 원본 좌표·ID·
실행/반환 연결·공개 계약·소유/권한·최종 CAS와 기존 C# 호출자 경로를 유지한다.
Blueprint 구현 entry/출력·live reference·module async/공개 실행 요구는 기존 유한 잔여다.

이 한정 범위의 [최종 신규45단계·재사용0 검증과 보관](VALIDATION_V666_BLUEPRINT_NATIVE_INPUTS.md)을 마쳤다.

후속 [직접 Blueprint 구현의 고급 entry·반환 전환](V666_BLUEPRINT_NATIVE_ENTRY.md)은
같은9행에서 기존 call/export 그래프의 정확한 입력·writer/exit 선택과 명시 C# 호출자를
한 후보/Review/최종 CAS에 연결한다. 원래 ID·좌표·경로·계약·권한과 명시 계획 밖의 C# bytes를 보존한다.
code/whole-body/private 대응·live reference·module async/공개 실행 결과는 기존 유한 잔여다.

이 한정 범위의 [최종 신규45단계·재사용0 검증과 보관](VALIDATION_V666_BLUEPRINT_NATIVE_ENTRY.md)을 마쳤다.

후속 [일반 C# 노드 보존과 고급 root 계약 전환](V666_RETAINED_NATIVE_CODE.md)은 같은9행의
고정 C# 노드 서명·source/helpers/import를 보존하며 명시 입력 재연결·writer/exit와 C# 호출자
계획을 한 후보/Review/최종 CAS에 연결한다. 원래 코드 record는 다시 쓰지 않고 읽기 증거로
보호한다. 노드 자체 ABI·private/whole-body·live reference·module async/공개 실행 결과는
기존 유한 잔여다. 원래 ID·연결·권한·레이아웃과 구 reader 제한을 유지한다.

이 한정 범위의 [최종 신규45단계·재사용0 검증과 보관](VALIDATION_V666_RETAINED_NATIVE_CODE.md)을 마쳤다.

후속 [단일 코드 whole-body의 명시 고급 ABI 전환](V666_NATIVE_WHOLE.md)은 같은9행에서
고급 입출력과 실제 C# 매개변수·본문·일반 호출자를 한 후보/Review/CAS에 연결한다.
원래 보관 C# 파일·문맥 identity·노드/반환 배치·권한·구 reader 경계를 보존하며,
원본 물리 헤더의 읽기 증거와 새 후보의 compiler 검증을 분리한다. 독립 code/private/retained
문맥·live reference·module async/실행 결과는 기존 유한 잔여다.

이 한정 범위의 [최종 신규45단계·재사용0 검증과 보관](VALIDATION_V666_NATIVE_WHOLE.md)을 마쳤다.

후속 [기존 독립 노드·지역값을 보존하는 whole-body 고급 ABI](V666_NATIVE_RETAINED.md)는
같은9행에서 한 소유 문맥의 native 서명·본문·호출자와 명시 root 출력 교체를 연결한다.
독립 C# code/helpers bytes·mtime, 정확한 local·실행선·원본·권한을 유지한다. 다른 소비자가
남는 이전 출력의 해제는 기존 backend와 UI에서 계속 거절한다. 독립 code/private ABI,
live reference·module async/실행 결과는 기존 유한 잔여다.

이 한정 범위의 [최종45단계(신규34·동등 재사용11) 검증과 보관](VALIDATION_V666_NATIVE_RETAINED.md)을 마쳤다.

후속 [일반 C# 노드의 관측된 고급 매개변수 타입](V666_NATIVE_PARAMETERS.md)은 같은9행에서
현재 frame/노드 타입 선택과 한 노드의 명시 대응·바인딩·본문을 원자 checkpoint에 연결한다.
소유 root와 독립 소유 함수 private frame이 범위이며, 정보 슬롯 private 진입·공개/override/
copy/receiver 계약은 기존 보호를 유지한다. 저장 실패 시 순차 적용으로 입력이 사라지던
결함을 수정하고 기존 source/receipt/CAS·원래 배치와 원본 계약을 보존한다. 다른 기존 ABI
문맥·live reference·module async/실행 결과는 같은 유한 잔여다.

이 한정 범위의 [최종46단계(신규41·동등 재사용5) 검증과 보관](VALIDATION_V666_NATIVE_PARAMETERS.md)을 마쳤다.

후속 [정보 구조체의 여러 값 필드](V666_INFORMATION_ARRAYS.md)는 같은 고정9행의 기존
single/multiple 값 계약을 C# 배열 생성에 연결한다. primitive·중첩 정보·종류 배열과
기존 동기 모듈의 정보 값 전달을 다루며 기존 단일 값 생성 원문/hash를 보존한다.
본문 Save의 native 타입 관측 영수증을 Review의 읽기 범위에 재검증해 합치는 결함도
수정한다. reference/함수 필드, 살아 있는 객체 접근과 모듈 async/공개 실행 계약은
여전히 별도 잔여다. 생성/reader 호환성과 최종 검증은 해당 문서의 한정 경계를 따른다.

이 한정 범위의 [최종 신규46단계·재사용0 검증과 보관](VALIDATION_V666_INFORMATION_ARRAYS.md)을 마쳤다.

후속 [실제 객체의 종류 값 Read/Set](V666_LIVE_ENUM.md)은 고정9행에서 호출자가 명시적으로
제공한 enum 값·배열을 기존 checked property 경로에 연결한다. 선언 ID 조회·기본값 생성·
provider 선택이나 mutable enum ref를 추가하지 않는다. 기존 primitive/reference와
숫자 매핑 없는 종류의 거절, 원문·권한·원자 저장·Review/CAS를 유지한다. 나머지 정보 참조,
function/compound 필드와 module async·공개 실행 결과는 별도 잔여다.

이 한정 범위의 [최종42단계(신규26·재사용16) 검증과 보관](VALIDATION_V666_LIVE_ENUM.md)을 마쳤다.

후속 [실제 객체의 compound 값 접근](V666_LIVE_COMPOUND.md)은 같은9행에서 기존
native struct 값·배열을 정확한 타입/전이 구조와 얕은 값 복사에 연결한다. 깊은 원본의
관측·최종 CAS와 기존 참조/함수의 별도 계약을 보존하며 실제 기기·전체 UI 완료로 세지 않는다.

이 한정 범위의 [최종 신규42단계·재사용0 검증과 보관](VALIDATION_V666_LIVE_COMPOUND.md)을 마쳤다.

모듈 require의 공개 실행·async 계약은 [module flow 지원 경계](V666_MODULE_FLOW.md)에
따라 기존 함수 결과 타입·nominal identity·동기 caller 오류 정책에 연결한다. provider
선택·원문 재작성·권한 확대는 없다. 최종 동결 및 보관/게시 결과는
[검증 기록](VALIDATION_V666_MODULE_FLOW.md)에 구분한다. 정보 참조 bridge/수명과
reference/function 필드는 별도 잔여이며 실제 기기/전체 UI 완료를 합산하지 않는다.

이 한정 범위의 [최종 신규 38단계·재사용 0 검증과 보관](VALIDATION_V666_MODULE_FLOW.md)을 마쳤다.

고정 정보9행의 [native 함수 필드](V666_FUNCTION_FIELDS.md)는 기존 함수 interface와
호출자가 명시한 handle을 정보 struct/배열에 담는다. provider 선택이나 선언 ID의 자동
실행 변환은 없으며 실제 수명·source CAS·최종 패키지 결과는
[전용 검증 기록](VALIDATION_V666_FUNCTION_FIELDS.md)으로 구분한다.

이 한정 범위의 [최종 신규 24단계·동등 재사용 14단계·총 38단계 검증과 보관](VALIDATION_V666_FUNCTION_FIELDS.md)을 마쳤다.


고정 정보9행의 [live 함수 속성](V666_LIVE_FUNCTIONS.md)은 호출자가 제공한 실제
IInvoke/IAsyncInvoke handle을 기존 object/object[]·Create/Read/Set 및 property 노드에
연결한다. ID 조회나 provider 선택 없이 원래 계약·수명·권한·본문 및 최종 CAS를 유지한다.
새 함수 descriptor는 구 accessor의 지원 범위가 아니며 자동 migration은 하지 않는다.
객체 참조 bridge/reference 필드·명시적 인스턴스 binding은 같은 유한 잔여로 유지하며
검증·보관 결과는 [전용 기록](VALIDATION_V666_LIVE_FUNCTIONS.md)으로 구분한다.

이 한정 범위의 [최종 신규 42단계·재사용 0 검증과 보관](VALIDATION_V666_LIVE_FUNCTIONS.md)을 마쳤다.


고정 정보9행의 [실제 인스턴스 bridge](V666_REFERENCE_BRIDGE.md)는 호출자가 제공한
ObjectModel 인스턴스를 명시적 정보 계약에 연결하고 같은 handle과 실제 owner를 반환한다.
값 복사·ref 셀 교체·ID 조회·권한 확대는 없다. 정보별 native reference ABI/struct의 reference
필드와 타입 선택 연결은 같은 유한 잔여이며 이번 runtime bridge와 구분한다. 검증·보관은
[전용 기록](VALIDATION_V666_REFERENCE_BRIDGE.md)을 따른다.

이 한정 범위의 [최종 신규 42단계·재사용 0 검증과 보관](VALIDATION_V666_REFERENCE_BRIDGE.md)을 마쳤다.

정보별 [typed reference ABI·필드·타입 선택](V666_TYPED_REFERENCES.md)은 정보 값과
실제 handle의 참조를 별도 struct로 유지하고 명시적인 binding과 원래 source/권한/CAS를
사용한다. 기존 descriptor나 C# 원문을 자동 승격하지 않으며 새 reader가 필요한 범위를
구분한다. 최종 검사는 [전용 기록](VALIDATION_V666_TYPED_REFERENCES.md)을 따른다.

이 한정 범위의 [최종 신규 49단계·재사용 0 검증과 보관](VALIDATION_V666_TYPED_REFERENCES.md)을 마쳤다.

이 한정 표시 단위의 [최종 신규 41단계·재사용0 검증과 보관](VALIDATION_V666_ARGUMENT_LABELS.md)을 마쳤다.

이 초기 로딩 실패 단위의 [최종 신규 37단계·재사용0 검증과 보관](VALIDATION_V666_BOOTSTRAP_RECOVERY.md)을 마쳤다.

이 standalone 표시 단위의 [최종 신규 41단계·재사용0 검증과 보관](VALIDATION_V666_STANDALONE_LABELS.md)을 마쳤다.

이 반환 표시 단위의 [최종 신규 39단계·재사용0 검증과 보관](VALIDATION_V666_STANDALONE_RETURN.md)을 마쳤다.

이 호출 핀 표시 단위의 [최종 신규 36단계·재사용0 검증과 보관](VALIDATION_V666_CALL_PIN_LABELS.md)을 마쳤다.

[이미 관측한 함수 호출 표시](V666_OBSERVED_CALL_LABELS.md)는 saved Blueprint의 공통 읽기 경계에서 정확한 owned 함수 관측과 기존 위치 ABI를 사용한다. private·After·slot을 표시만의 금지 조건으로 삼지 않으며 snapshot/외부 읽기/계약 편집 권한은 확장하지 않는다. 고정7/8행의 실제 계약·본문 closure와 기기·전체 UI 잔여는 별도다.

이 관측 호출 표시 단위의 [최종 신규 36단계·재사용0 검증과 보관](VALIDATION_V666_OBSERVED_CALL_LABELS.md)을 마쳤다.

[명시 값 입력 이름과 native 본문 공동 저장](V666_NAMED_BODY_GROUP.md)은 원래 위치별 타입·역할·수·반환과 native 선언을 유지하고, 여러 함수의 직접 본문 편집과 공개 값 입력 C# 이름 대응을 한 후보/공유 caller에 연결한다. 고정7/8행의 다른 실제 closure와 구 reader·기기·전체 UI 잔여는 별도다.

이 명시 이름·본문 공동 저장 단위의 [최종 신규 37단계·재사용0 검증과 보관](VALIDATION_V666_NAMED_BODY_GROUP.md)을 마쳤다.

[Blueprint 이름 계약과 native 본문 혼합 저장](V666_MIXED_FUNCTION_BODIES.md)은 각각 유효한 두 원래 편집을 공유 caller와 한 후보/CAS에 결합한다. scalar·직접 소유·단일 import-free 구현과 일반 caller 범위이며, 기존7/8행의 다른 source closure 및 기기/전체 UI 잔여와 구별한다.

이 Blueprint 계약·native 본문 혼합 저장 단위의 [최종 신규 37단계·재사용0 검증과 보관](VALIDATION_V666_MIXED_FUNCTION_BODIES.md)을 마쳤다.

[공개 입력 이름·native 본문과 private 호출자](V666_NAMED_NESTED.md)는 기존8행의 명시 계약/본문 그룹을 ordinary owned private frame에 연결한다. 원래 frame 계약·지역값·qualified C# 원문과 version3 읽기 CAS를 유지하고 다른 forwarded/opaque/import closure는 같은 유한 잔여로 둔다.

이 공개 이름·native 본문과 private 호출자 단위의 [최종 신규 38단계·재사용0 검증과 보관](VALIDATION_V666_NAMED_NESTED.md)을 마쳤다.

[공개 입력 이름·native 본문과 로컬 import](V666_NAMED_IMPORTS.md)는 기존8행의 명시 계약/본문 그룹에서 이미 관측한 로컬 helper를 읽기 전용으로 보존한다. 원래 helper 계약·별칭·C# 원문과 version3 읽기 CAS를 유지하고 다른 forwarded/opaque·원래 source closure는 같은 유한 잔여로 둔다.

이 공개 이름·native 본문과 로컬 import 단위의 [최종 신규 28·재사용 10·총 38단계 검증과 보관](VALIDATION_V666_NAMED_IMPORTS.md)을 마쳤다.

[기존 forwarded/opaque 호출 원본](V666_RETAINED_FORWARDING.md)은 기존7/8행의 계약 불변 native 본문 저장을 전달/private graph와 opaque C# 읽기 문맥에 연결한다. 원래 import 위치 표기와 source/definition hash·조립 컴파일·readGuards/CAS를 유지한다. 실제 계약 변경과 다른 원래 source closure, 기기/전체 UI 잔여는 별도다.

이 같은 계약 forwarded/opaque 원본 보존 단위의 [최종 신규 39·재사용0 검증과 보관](VALIDATION_V666_RETAINED_FORWARDING.md)을 마쳤다.

[공개 입력 이름·native 본문과 전달 호출자](V666_NAMED_FORWARDING.md)는 고정7/8행의 위치별 명시 값 이름 대응을 기존 전달 graph/call에 연결한다. 부모/형제 계약·저장 바인딩·qualified C#와 원래 source/readGuards/CAS를 보존하며 opaque/code source 계획·다른 ABI 및 기기/전체 UI 잔여는 구별한다.

이 명시 공개 입력 이름·native 본문과 전달 호출자 단위의 [최종 신규 40·재사용0 검증과 보관](VALIDATION_V666_NAMED_FORWARDING.md)을 마쳤다.

[명시 native 입력 타입·본문 공동 저장](V666_NATIVE_INPUTS.md)은 고정7/8행의 직접 소유 동기 scalar 입력 교체를 여러 함수와 공유 직접 Blueprint caller에 연결한다. 새 값·원래 연결 해제·C# 선언/본문을 직접 선택하고 기존 receipt/readGuards·Review/Confirm·원래 CAS를 유지한다. 역할·출력 구조·opaque 계획·다른 원본 의존성과 reader/기기/전체 UI 잔여는 구별한다.

이 명시 native 입력 타입·본문 공동 저장 단위의 [최종 신규 39·재사용0 검증과 보관](VALIDATION_V666_NATIVE_INPUTS.md)을 마쳤다.

[명시 native 반환·본문·기존 출력 대응 공동 저장](V666_NATIVE_RETURNS.md)은 고정7/8행에서 두 함수의 scalar 반환 변경과 직접 C# 본문, 기존 소비의 호환 out 대응을 한 후보/CAS에 연결한다. 입력과 out 계약·ID는 유지하고 기존 receipt/readGuards·Review/Confirm을 보존한다. 역할·out/void 정의·opaque/private 계획·다른 원본 의존성 및 reader/기기/전체 UI 잔여는 구별한다.

이 명시 native 반환·본문·출력 대응 단위의 [최종 신규 39·재사용0 검증과 보관](VALIDATION_V666_NATIVE_RETURNS.md)을 마쳤다.

[명시 native 반환 삭제·void 본문·기존 out 대응 공동 저장](V666_NATIVE_VOID.md)은 고정7/8행에서 여러 직접 소유 C# 함수의 반환 삭제와 본문, 이전 소비의 호환 out 대응을 한 후보/CAS에 결합한다. 입력/out 계약과 원래 receipt/readGuards·Review/Confirm을 유지한다. 역할·out 정의·역방향 void→값·opaque/private 계획·다른 원본 의존성 및 reader/기기/전체 UI 잔여는 구별한다.

이 명시 native 반환 삭제·void 본문·출력 대응 단위의 [최종 신규 39·재사용0 검증과 보관](VALIDATION_V666_NATIVE_VOID.md)을 마쳤다.

[명시 native void→반환 추가·본문 공동 저장](V666_NATIVE_RETURN_CREATE.md)은 고정7/8행에서 여러 직접 소유 C# 함수에 scalar 반환과 본문을 추가하는 후보를 한 Save/CAS에 결합한다. 기존 입력/out 계약·바인딩과 receipt/readGuards·Review/Confirm을 유지하며 새 반환을 자동 연결하지 않는다. 역할·out/입출력 정의·opaque/private 계획·다른 원본 의존성과 reader/기기/전체 UI 잔여는 구별한다.

이 명시 native void→반환 추가 단위의 [최종 신규 39·재사용0 검증과 보관](VALIDATION_V666_NATIVE_RETURN_CREATE.md)을 마쳤다.

[명시 native out 타입·본문·소비자 공동 저장](V666_NATIVE_OUTPUTS.md)은 기존 출력 타입 선택과 모든 원래 소비자의 명시 호환 반환 대응을 여러 native 함수의 한 Save/CAS에 결합하는 단위다. 값 입력·역할·수·반환 타입·원본 소유권·권한·Review/Confirm을 유지하며, 역할/구조 변경·opaque/private 명시 계획·다른 원본 의존성 및 reader/기기/전체 UI 잔여는 별도다.

이 명시 native out 타입·본문 단위의 [최종 신규 40·재사용0 검증과 보관](VALIDATION_V666_NATIVE_OUTPUTS.md)을 마쳤다.

[명시 native out 삭제·본문·소비자 공동 저장](V666_NATIVE_OUT_REMOVAL.md)은 기존 출력 삭제 UI와 모든 원래 소비자의 명시 호환 반환 대응을 여러 native 함수의 한 Save/CAS에 결합하는 단위다. 남은 계약·원본 소유권·권한·후속 저장 보호·Review/Confirm을 유지하며 역할/추가·다른 구조 변경·opaque/private 계획·다른 원본 의존성은 별도 잔여다.

이 명시 native out 삭제·본문 단위의 [최종 신규 41·재사용0 검증과 보관](VALIDATION_V666_NATIVE_OUT_REMOVAL.md)을 마쳤다.

[명시 native out 추가·본문 공동 저장](V666_NATIVE_OUT_ADDITION.md)은 기존 출력 추가 UI와 새 out의 직접 C# 할당을 여러 native 함수의 한 Save/CAS에 결합하는 단위다. 원래 계약·소비자 연결·소유권·권한·후속 저장 보호·Review/Confirm을 유지하고 새 기본값/바인딩을 추정하지 않는다. 역할·다른 구조 결합·opaque/private 계획·다른 원본 의존성은 별도 잔여다.

이 명시 native out 추가·본문 단위의 [최종 신규 41·재사용0 검증과 보관](VALIDATION_V666_NATIVE_OUT_ADDITION.md)을 마쳤다.

### 원래 native C# 값→out 역할 · 고정7/8행

[명시 역할 전환과 공동 저장](V666_NATIVE_VALUE_OUT.md)은 기존 C# 매개변수 창과 정확한 caller 입력 해제를 연결한다. 이름·타입·수·순서·반환·원문과 소유권을 유지하며 새 out은 자동 연결하지 않는다. 검증 결과는 별도 기록한다. 다른 역할/입출력 정의·opaque/private 명시 계획·선택 native 의존성 결합은 같은 유한 잔여다.

이 값→out 명시 역할·본문 단위의 [최종 신규 43·재사용0 검증과 보관](VALIDATION_V666_NATIVE_VALUE_OUT.md)을 마쳤다.

### 원래 native C# out→값 역할 · 고정7/8행

[명시 out→값 전환](V666_NATIVE_OUT_VALUE.md)은 새 리터럴 입력과 사라지는 out 소비자의 호환 반환 대응을 기존 C#·호출 계약 창에서 선택한다. 기존 입력/out·C# 원문·receipt/readGuards·Review/Confirm·CAS와 소유권을 유지한다. ref/다른 정의 결합·opaque/private 계획·다른 원본 의존성은 같은 고정 잔여다.

이 out→값 명시 역할·본문 단위의 [최종 신규 43·재사용0 검증과 보관](VALIDATION_V666_NATIVE_OUT_VALUE.md)을 마쳤다.

### 원래 native C# ref→out 역할 · 고정7/8행

[명시 ref→out 전환](V666_NATIVE_REF_OUT.md)은 기존 저장소 연결의 정확한 해제와 새 out의 비자동 연결을 기존 C#·호출 계약 창에서 선택한다. caller 자체의 ref 계약과 C# 원문·receipt/readGuards·Review/Confirm·CAS를 유지하며 실제 저장소 갱신 차이를 검증한다. 다른 ref 방향/정의 결합·opaque/private 계획·원본 의존성은 같은 고정 잔여다.

이 ref→out 명시 역할·본문 단위의 [최종 신규 43·재사용0 검증과 보관](VALIDATION_V666_NATIVE_REF_OUT.md)을 마쳤다.

[명시 native ref→값과 공유 caller](V666_NATIVE_REF_VALUE.md)는 원래 입력 바인딩을 값으로 읽고 callee 쓰기의 caller 전달을 제거하는 역할·본문 공동 저장 단위다. 원문·caller 자체 계약·출력 identity·source CAS를 보존한다. 값/out→ref·입력 정의·opaque/private 계획·원본 의존성 결합 및 reader/기기/전체 UI 잔여는 구별한다.

이 ref→값 명시 역할·본문 단위의 [최종 신규 43·재사용0 검증과 보관](VALIDATION_V666_NATIVE_REF_VALUE.md)을 마쳤다.

[명시 native 값→ref와 공유 caller](V666_NATIVE_VALUE_REF.md)는 실제 기존 입력 저장소를 직접 선택해 쓰기 전달을 추가하는 역할·본문 공동 저장 단위다. caller 자체 ABI·원문·출력 identity·CAS를 보존하고 리터럴/임시 ref 셀을 만들지 않는다. out→ref·입력 정의·opaque/private 계획·원본 의존성 및 reader/기기/전체 UI 잔여는 구별한다.

이 값→ref 명시 역할·본문 단위의 [최종 신규 46·재사용0 검증과 보관](VALIDATION_V666_NATIVE_VALUE_REF.md)을 마쳤다.

[명시 native out→ref와 기존 caller ref 출처](V666_NATIVE_OUT_REF.md)는 원래 선언된 scalar ref 입력을 직접 선택하고 기존 out 소비자를 호환 반환에 명시 대응하는 공동 저장 단위다. ref 출처 선언도 read/CAS 원본으로 유지한다. 입력 정의 변경·opaque/private 계획·원본 의존성 및 reader/기기/전체 UI 잔여를 구별하며 제한된 역할 방향 지원을 전체 계약 완성으로 표현하지 않는다.

이 out→ref 명시 역할·본문 단위의 [최종 신규 46·재사용0 검증과 보관](VALIDATION_V666_NATIVE_OUT_REF.md)을 마쳤다.

[명시 native 값 입력 추가·본문·공유 caller](V666_NATIVE_INPUT_ADDITION.md)는 기존 public/native 매개변수와 caller 바인딩·출력·ABI를 유지하며 새 입력의 명시 값과 직접 작성한 본문을 공동 저장하는 단위다. 원문은 자동 변환하지 않는다. 입력 삭제/다른 정의 결합·opaque/private 계획·원본 의존성과 reader/기기/전체 UI 잔여는 구별한다.

이 값 입력 추가·본문 단위의 [최종 신규 46·재사용0 검증과 보관](VALIDATION_V666_NATIVE_INPUT_ADDITION.md)을 마쳤다.

[명시 native 값 입력 삭제·본문·공유 caller 공동 저장](V666_NATIVE_INPUT_REMOVAL.md)은 남는 원래 native 별칭·입력/출력 연결을 유지하고 삭제한 원래 바인딩을 정확히 명시 해제한다. 원래 source/readGuards·후속 Save·Review/Confirm·CAS를 보존하며 다른 명시 계약 결합·opaque/private 계획·원본 의존성 및 reader/기기/전체 UI 잔여는 구별한다.

이 값 입력 삭제·본문 단위의 [최종 신규 46·재사용0 검증과 보관](VALIDATION_V666_NATIVE_INPUT_REMOVAL.md)을 마쳤다.

[명시 native 입력 삭제·추가·본문·공유 caller 공동 저장](V666_NATIVE_INPUT_DEFINITIONS.md)은 같은 함수의 기존 입력 해제와 새 값 선택을 원래 증거·한 후보/CAS로 결합한다. 남는 native 별칭·입력/출력 연결과 후속 Save·Review/Confirm·CAS를 보존하며 다른 복합 계약/opaque/private·원본 의존성 및 reader/기기/전체 UI 잔여는 구별한다.

이 입력 삭제·추가·본문 단위의 [최종 신규 46·재사용0 검증과 보관](VALIDATION_V666_NATIVE_INPUT_DEFINITIONS.md)을 마쳤다.

[명시 native 입력 정의·타입·본문 공동 저장](V666_NATIVE_INPUT_MIX.md)은 같은 함수의 입력 삭제/추가와 scalar 타입 선택을 명시 값·원래 해제·공유 caller 및 한 후보/CAS에 연결한다. 원래 source/readGuards·후속 Save·Review/Confirm과 caller ABI·출력·경로를 유지하며 다른 복합 계약/opaque/private·원본 의존성과 reader/기기/전체 UI 잔여는 구별한다.
