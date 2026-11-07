# v666 PDF 미리보기 검증

[닫힌 지원 경계](V7_RESOURCE_PDF.md)는 저장소 v666 PDF 원본 UI와 vendor를 사용한다.
제품 delta 기준 `8624c0ec0d26f4a771790b918aac5c5a89cf9846`,
최종 고정 source **e62d72ef27c774cfde708e0708bbfece2617f171**다. 후속 게시 커밋은 이 기록과 수용 표만 변경한다.
공개 실행/override 계약·원본 C#·프로젝트 읽기/저장 권한·Review→Confirm/CAS는 유지했다.

## 최종 신규 검사

총 **52단계, 신규 52·재사용 0**다. 주 실행 51단계는
LF 19·CRLF 19·패키지/복원/실패 수명 13단계다.
이와 별도로 같은 최종 패키지의 문서 간 소유 수명 검사1단계를 새로 실행했다.
과거 실행의 통과 결과를 최종 통과 수에 재사용하지 않았다.

두 Git checkout은 objects·NuGet·HOME·engine cache를 각각 독립시켜 restore/Release/
MCP/에디터를 새로 빌드했다. 원본 PDF.js main/worker/CMap/글꼴184개와 LICENSE4개,
vendor 바이트·LF/binary attributes·원본 CSS/controls·bundle pins를 대조했다.
native Open 변경은 count256→384와 opaque MIME 추가의 두 literal뿐임을 닫힌 guard로
확인한다. 파일4MiB·전체 raw/canonical32MiB·SHA·경로/링크·UTF-8 LF 규칙은 유지한다.
실제 native `test_web_ui_scope_revision_cancellation_disposal_and_pack_locality`에서
384개 허용·385개 거절·opaque CR/LF/NUL/FF 바이트 보존과 기존 SHA/크기/경로/권한/
비동기/취소/종료 경계를 양쪽에서 새로 검사했다.

Node는 canvas 크기 산술/고정된 font·CMap URL 정책의 실제 순수 함수를 검사했다.
이것을 PDF 표시나 Worker 실행의 증거로 대신하지 않았다. 실제 Linux 엔진/Chromium에서
PDF.js module Worker·ready handshake·port 연결·빨강/초록 PDF 픽셀·이전/다음·fit/200%
배율·실제 Korean CMap의 동일 출처 binary 요청을 확인했다. 글꼴 대체/모든 CJK glyph의
완전한 서식 재현을 검증한 것은 아니다. 공개 Liberation 글꼴을 넣은 PDF도 로컬 생성했다.
URI annotation 클릭과 PDF JavaScript는 동작하지 않았고 외부 PDF 요청/내용 편집은 없었다.
암호/손상·원래 viewport 초과·1,001페이지 거절과 명시 재시도, 두 창 quota/닫기 후 재사용,
실제 worker 메시지 보류·늦은 결과·10초 timer·강제 종료 후 복구를 확인했다.

cold engine에서 owner/ID/hash를 재관측해 새 Worker/픽셀을 만들었다. 실제 native 읽기
권한 실패/복구·Home 왕복·같은 namespace의 다른 실제 프로젝트 격리와 다른 입력/
원본 hash·저장 사본 불변을 확인했다. PDF byte/port/canvas/FontFace는 개인 배치에
저장하지 않는다. 기존 Office·이미지·텍스트 내용 편집/복구·readonly preview·이름·
다중 삭제·C# 본문 저장/Undo/취소/재시작/Review→Confirm/CAS 회귀도 최종 코드로 실행했다.
Office 접기/펼치기에서는 실제 native update 응답을 보류해도 DOM 가시성 이벤트만으로
복원됨을 확인했다. 이 검사는 초기 진입 `#app` 빈 화면의 원인 규명을 뜻하지 않는다.

## 재현한 구현 결함과 검사 수정

1. 첫 native 검사에는 예전257개 거절 기대값이 남아 있었다. 새384/385 경계를 유지하고
   기존 image count 거절도 새 한도에 맞췄다. 검사 입력 수정이며 제품 예외를 약화하지 않았다.
2. 비동기 Worker loader가 준비되기 전에 port를 바인딩해 첫 표시가 timeout되는 경로를
   고쳤다. 명시적 ready 신호 뒤에만 문서/port 연결을 시작하며 fake-worker fallback은 없다.
3. 실제 임베디드 문서의 종료 ACK를 보류하면 Worker13개가 모두 종료됐어도 FontFace가
   **0→2**로 남았다. 고정4.10.38에서 해당 transport의 fontLoader/filterFactory를 직접
   정리하는 adapter를 추가했고, 같은 실제 입력은 최종 **0→0**으로 복귀했다. vendor
   바이트는 바꾸지 않았으며 이 private adapter 의존성은 고정 버전/회귀에 명시한다.
4. Office 창을 빠르게 접기/펼치면 worker/document는 정리됐지만 native 상태 갱신이
   없을 때 빈 body가 남았다. 소유 창의 DOM 가시성 observer로 재관측하며 폐기 시
   observer도 해제한다. 실제 update 응답 보류 상태에서도 복원을 새로 통과했다.

모든 앞선 실패의 record/입력/로그/profile/manifest는 지속 보관했고 해당 실행이 소유한
임시 root만 종료/증거 보존 후 정리했다. 첫 네 실행은 최종 pass로 계산하지 않는다.

## 패키지·보관·소유 문서 간 회귀

Windows 교차 패키지 생성/구조 probe, ZIP CRC·전체 파일 SHA·디렉터리/모드 검증과
전체 복원본을 확인했다. 생성본과 복원본에서 실제 Linux 엔진/Chromium의 PDF·Office·
이미지·내용 편집 normal/lifecycle 검사를 새로 실행했다. Windows apphost/WebView2
실행과 구분한다. 복사 중 실패/UI 실패/변조 실패에서도 원본/런타임과 증거를 보존하는
기존 owned package 수명 검사가 통과했다.

- 주 record: `/workspace/artifacts/v536-verification-managed/runs/870f930387f74e64955988d5e7e9c77d.json`
- 주 증거 ZIP: `e37d4552379ce49883264bbab35c7bbc480cfa2748d4ab399c0cc37046e337e9` (4,405,796 bytes)
- 추가 소유 회귀 record: `/workspace/artifacts/v536-verification-managed/runs/cbc28e3a4a7d4dd19875031507bb557f.json`
- 추가 증거 ZIP: `0a6579ab82c6dafa91324b7cd369b4fcab68481f33733449ed84f17178cc5ff5`
- 추가 실제 FontFace 계수: `{'baseline': 0, 'first': 2, 'both': 4, 'surviving': 2, 'final': 0}`
- 최신 source: `e62d72ef27c774cfde708e0708bbfece2617f171`
- 최신 ZIP: `a5a52c6f7bd17d9416298a1fd5419357dfa21ca917c21e2d8329ce989697d1f8` (53,775,706 bytes)
- 최신 전체 manifest: `ae10f95530a94f626bc94b4f4184f9c72e1faa88ddd586d9b30663a9efa5d556`; 파일 2695·디렉터리 158
- 롤백 source: `6c1cae4ac1da3aa898e0f938f99a7b7bdec7a8d9`
- 롤백 ZIP: `f5358d814751ac79932a88e9b5ba9040322b9fe6d4f07cad593758ad8854c570` (51,946,281 bytes)
- 롤백 전체 manifest: `90fdbda710aeed8e1d01736bc166c8051a54ea233190bf7f52b3d18034f8114b`; 파일 2504·디렉터리 153

추가 회귀는 최신 패키지를 새 owned 공간에 전체 해시/모드 검증해 복원하고, 생성한
서로 다른 두 문서를 실제로 열었다. 하나의 진행 중 렌더/종료 응답을 보류해 강제
정리해도 나머지 문서의 글꼴·픽셀이 유지됐다. 남은 문서의 빠른 배율 변경 뒤에도
픽셀이 유지되고 마지막 닫기에서 FontFace 기준 수로 돌아왔다. product/compiler를
새로 빌드한 세 번째 checkout은 아니며 같은 검증 패키지에 새 입력을 실행한 검사다.
원래 source template와 집중 fixture/harness를 증거 ZIP에 포함했고 보관 index는 불변이다.

## 공간과 잔여

단위 시작 추가 peak 예산은148MiB(candidate56·증거20·source/Git8·안전64)다. 코드
작성 뒤 실행의 preflight144MiB·RAM 작업공간3GiB+안전512MiB·cgroup 추가7GiB+
안전1GiB를 유지했다. 주 실행 단계 샘플의 최소 디스크 여유 1,179,418,624 bytes,
cgroup peak 5,360,807,936 bytes다. 환경 전체 수치이며 앱 단독 peak가 아니다.
측정 당시 단위 누적 증가 18,702,336 bytes, 여유 1,171,324,928
bytes다. 최신/롤백/증거를 지속 검증하고 실행별 소유 임시물만 정리했다. 승인된
managed 최신/롤백 승격 외에 과거 원본·로그·캐시·패키지 삭제를 확대하지 않았다.

1MiB 초과/큰 파일·Office 편집·mesh/다른 원본 그림·설명 metadata와 기존 기타 진입 UI는
남는다. 암호 입력/새 편집/선택적 migration을 임의 필수 요구로 늘리지 않는다.
M4/M11/M12는 재개하지 않는다. 초기화 빈 화면은 원인 미확정이며 실제 Windows/모바일·
전체 UI·Space/Library 전달은 미검증이다. 기존 외부 Google Fonts CSS 참조도 기존 CSP가
계속 거절하며 PDF 때문에 CSP나 외부 접근을 추가 허용하지 않았다.
