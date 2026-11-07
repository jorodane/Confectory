# v666 Office 내용 미리보기 검증

지원 경계는 [V7_RESOURCE_OFFICE.md](V7_RESOURCE_OFFICE.md), 제품 delta 기준은
`4d24a25d38fb536f068d9b76f2be277a1a06553b`다. 최종 고정 source는 **6c1cae4ac1da3aa898e0f938f99a7b7bdec7a8d9**다.
후속 커밋은 이 기록과 수용 표만 변경하며 최종 코드/검사와 패키지의 출처를 유지한다.

## 신규 검사와 범위

총 **46단계, 신규 46·재사용 0**가 통과했다.
주 검증 45단계와 추가 writer 호환성 1단계를 구분한다.
LF 17단계·CRLF 17단계는 독립 Git objects/checkout·NuGet·HOME·cache에서 restore,
Release/MCP 및 에디터 엔진을 새로 빌드했다. 바뀌지 않은 native 선언/헤더 구조,
6개 제품 파일과 v666 원본 ZIP·기존 CSS·bundle의 LF canonical SHA도 확인했다.

Node에서 실제 native DEFLATE stream/CRC와 표준 ZIP/data descriptor를 확인하고
손상·길이/CRC 불일치·암호화·경로 위장·중복·ZIP64·초과 예산을 거절했다.
별도의 Worker quota/deadline/retire 단위 검사는 명시적으로 가짜 Worker/timer/DOM을
사용한 수명 검사다. 이것을 실제 문서 표시의 증거로 사용하지 않았다.

실제 Linux 엔진과 Chromium의 기존 CSP에서 동일 출처 module Worker를 실행했다.
생성한 DOCX의 문단/표/굵기/HTML 문자, XLSX의 캐시/공유문자/boolean/수식 텍스트와
반복 시트 전환, PPTX 숫자 순서와 ODT 문단을 확인했다. 4개 창 제한 뒤 닫기/명시
재시도, 손상/DTD·외부 entity/ZIP64/CRC 거절, 실제 Worker 결과 지연과 닫기/다시 열기,
접기/펴기, 5초 초과 뒤 늦은 결과 무시와 재시도를 확인했다. 실제 native 읽기 권한
실패/복구, cold engine 재시작, Home 왕복과 같은 namespace의 다른 실제 프로젝트
격리를 확인했다. 원본 사본·C#·다른 입력은 유지됐고 Office 내용 sidecar 쓰기는 없었다.

기존 이미지 실제 픽셀/URL 수명, 텍스트 내용 편집/복구, readonly preview, 인라인
이름 변경, 다중 삭제, C# 본문 실패 복구 UI는 최종 코드로 새로 검사했다.
Office는 읽기 전용이며 새 저장/Review/Confirm/CAS 경로를 추가하지 않았다. 기존
저장 보호의 관련 회귀 통과와 모든 실제 저장 경로/전원 차단을 검증했다는 주장은 구분한다.

## 패키지와 증거

패키지·전체 복원·실패 수명관리 **11단계**도 신규다. Windows
교차 패키지 생성/구조 probe와 전체 파일 SHA·CRC·모드 검증 후 전체 전개본을
검사했다. 생성본과 복원본 모두에서 실제 Linux 엔진/Chromium Office·이미지·내용
편집 정상/수명 UI를 실행했다. Windows apphost/WebView2 실행 증거는 아니다.

- 실행 record: `/workspace/artifacts/v536-verification-managed/runs/ab5c98d129e8498aadca515ea09057e2.json`
- 증거 ZIP: `8dd92d966e106f7f4d773d9a3eb344482f87804da79e0b5dcb507718be9ac8b1` (3,671,919 bytes)
- 최신 source: `6c1cae4ac1da3aa898e0f938f99a7b7bdec7a8d9`
- 최신 ZIP: `f5358d814751ac79932a88e9b5ba9040322b9fe6d4f07cad593758ad8854c570` (51,946,281 bytes)
- 최신 전체 manifest: `90fdbda710aeed8e1d01736bc166c8051a54ea233190bf7f52b3d18034f8114b`; 파일 2504·디렉터리 153
- 롤백 source: `6fdb09f1e9996836bfb844915c12bf6a46104603`
- 롤백 ZIP: `de42bdea3f8aff8a2f552669d9f7f22161672c3a649c9fc4459ac318c228b3a4` (51,938,486 bytes)
- 롤백 전체 manifest: `235130ae639c98db5b0966cf53351add20ddb2efc276b2eff07d4e1f34c55d55`; 파일 2501·디렉터리 153

첫 실행은 모든 형식 표시/시트 검사를 통과한 뒤, 뒤쪽 DOCX 창의 닫기 버튼을
다른 PPTX 창이 가려 Playwright click이 시간 초과했다. 제품 코드는 바꾸지 않고
기존 자료 Browser에서 이미 열린 창을 다시 선택한 뒤 닫는 순서로 검사만 수정했다.
해당 실패 ZIP/입력/로그는 지속 보관했고 자식 종료 뒤 해당 실행 소유 임시물만 정리했다.
최종 실행은 이 수정된 순서로 처음부터 통과했고 실패 실행의 통과 검사를 재사용하지 않았다.
이는 기존 간헐적 초기 빈 화면의 원인 규명/수정을 뜻하지 않는다.

## 일반 writer 컨테이너 호환성

별도 추가1단계에서 새 최신 패키지를 다시 전체 SHA/모드 복원한 뒤, 실제 설치된
python-docx/openpyxl/python-pptx로 로컬 생성한 DOCX/XLSX/PPTX와 stdlib로 만든
저장 방식 mimetype/manifest를 포함한 ODT 컨테이너를 같은 native/browser 정상 검사에
사용했다. 문서 표시·시트/수식·한도/거절·지연/정리까지 통과했다. 원래 최소 ZIP/XML
검사를 이 결과로 대체하지 않는다. 라이브러리를 설치/다운로드하거나 개인 파일을 읽지
않았다. 실제 MS Office/LibreOffice 앱에서 생성/실행한 증거는 아니다.

- 추가 record: `/workspace/artifacts/v536-verification-managed/runs/09ab2edfefdb44a8aa27b9d94689781a.json`
- 추가 증거 ZIP: `18644f498971c500765ad81afa27cc1d5d3cc38b6392402190bd343081333219`
- 실제 writer 버전: `{'python-docx': '1.2.0', 'openpyxl': '3.1.5', 'python-pptx': '1.0.2'}`
- 원래 최종 UI template SHA: `94e35a975f6d197701869139081104291ee7c746384451d2309fe618cf555a68`
- 동일 패키지 출처/해시와 보관 index 불변을 확인했고 이 실행 소유 임시물도 정리했다.

## 저장공간과 미검증

사전 디스크 추가 예산 144MiB(안전64MiB 포함), RAM 작업공간3GiB와 안전512MiB,
cgroup 추가7GiB와 안전1GiB를 유지했다. 최종 실행 단계 샘플의 최소 디스크 여유
1,195,524,096 bytes, cgroup peak 5,282,643,968 bytes다. cgroup 값은 환경
전체 사용량이며 앱 단독 RAM 수치가 아니다. 이번 단위 누적 순증가
7,364,608 bytes(실패 증거/코드/로그 포함), 측정 당시 남은 공간
1,190,113,280 bytes다. 지속 최신/롤백 두 패키지와 증거를 전체 해시로
검증한 뒤 주 검증/실패/추가 호환성 실행 소유 임시 root를 정리했다. 과거 자료 추가 삭제는 하지 않았다.

큰 파일·선택 예산 초과, Office 편집, PDF/mesh/다른 원본 이미지, 설명 metadata와
남은 원본 진입 UI는 잔여다. M4/M11/M12를 다시 잔여로 넣지 않는다. 초기화 빈 화면은
원인 미확정이다. 실제 Windows/모바일 기기·전체 UI·Space/Library 전달은 미검증이다.
