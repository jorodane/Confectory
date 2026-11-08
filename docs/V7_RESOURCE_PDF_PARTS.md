# 큰 PDF 읽기 전용 미리보기

현재 저장소 v666 ZIP의 `dist/resource-preview.js::loadPdf`와 기존 페이지·배율·canvas
화면을 사용한다. 원본은64MiB 사전 검사 뒤 전체 PDF bytes를 renderer에 전달한다.
이번 단위는 **이미 보관 가능한1MiB 초과–4MiB PDF 사본**의 미리보기 누락을 닫는다.
기존 명시 File 가져오기/전체4MiB/64개, 작은 PDF/다른 형식과 원본 레이아웃은 유지한다.
원본 PDF 편집·외부 파일 열기·첨부/링크/폼 실행·암호 입력 기능은 추가하지 않는다.

큰 `read`는 원래 `encoding:unavailable`/제한 reason과 metadata를 유지하고, document
kind·PDF 이름/MIME·`%PDF-` signature가 맞을 때만 선택 필드 `pdfPreview`를 추가한다.
기존 `preview`/`imagePreview` 필드의 의미를 바꾸지 않는다. capability가 없는 이전
backend나 UI는 같은 metadata-only 표시를 유지하며 저장 형식 이행/재작성은 없다.
signature는 완전한 PDF 인증이 아니며 실제 decoder가 실패하면 사본 보존·명시 재시도를 쓴다.

새 관찰 전용 `readProjectResourcePDFPart`/`Layout.preview-pdf-part`는 현재 project/ID·
전체SHA·import generation·compound display revision과 정수 part만 받는다. 고정1MiB씩
최대 네 조각이며 마지막 길이는 남은 bytes다. 각 요청은 현재 전체 보관본의 길이·canonical
encoding·SHA와 manifest/identity/store/layout/이름/설명/삭제/내용 sidecar의 최종 읽기를
다시 검사한다. path·다른 project·누락/범위 밖 part·변경된 기준과 mutation/image lane은
거절한다. cache/lease로 오래된 bytes를 새 기준으로 위장하지 않는다. 공개 함수/override
계약·실제 권한과2MiB RPC·저장/전송/내용 편집·백업1MiB/CommitPlan·최종 쓰기CAS는 유지한다.

브라우저는 header/각 조각의 item·revision·순서·offset/길이·canonical base64·조각 SHA와
전체 SHA를 모두 확인한 뒤에만 기존 PDF document/Worker를 만든다. header 뒤 metadata를
다시 bind하지 않아 조각 대기 중의 새 설명 입력을 보존한다. busy만 같은 기준으로 제한
재관측하며 실패한 mutation을 자동 replay하지 않는다. 닫기·Home/프로젝트 변경·같은 창
재열기·cold는 조각/hash 도착마다 owner token을 검사해 늦은 응답의 Worker 생성을 막는다.
접힌 창은 document를 만들지 않고 다시 보일 때 새로 읽는다. bytes/미결 transfer/Worker는
개인 presentation에 저장하지 않는다. 기존 source·값·설명·Undo·Review→Confirm도 보존한다.

renderer는 기본1MiB 한도를 유지하며 검증한 큰 경로만 명시4MiB로 opt-in한다. vendor
4.10.38의188개 bytes/고지, 실제 module Worker/CMap/font의 동일 출처 fetch 제한과
`isEvalSupported:false`·XFA/annotation 비활성화·scripting layer 없음은 그대로다.
기존 최대2문서·1000페이지·viewport/canvas/pixel·10초 타이머·500ms 종료/FontFace 정리
규칙도 유지한다. 입력/canvas 한도는 PDF.js 내부 디코딩 전체 메모리/CPU의 하드 한도가
아니며 큰 복잡한 문서의 완전 재현을 보장하지 않는다. [기존 PDF 경계](V7_RESOURCE_PDF.md)를 따른다.
기존 반입본에 대한 [2024 공지](https://github.com/mozilla/pdf.js/security/advisories/GHSA-wgrm-67xf-hhpq)와
[2026 공지](https://github.com/mozilla/pdf.js/security/advisories/GHSA-hq66-cqwq-w95j)의 명시 버전 범위를
다시 확인했으며 library bytes를 임의 갱신하지 않았다. 모든 취약점 부재를 주장하지 않는다.

생성한 유효 PDF(큰 미참조 binary stream과 실제 빨강/초록 두 페이지), 손상 사본과4MiB
경계 자료만 사용한다. native 실제 본문/최종 읽기 race는 통제된 fixture이며 UI의 실제
PDF.js Worker/canvas 검증과 구분한다. LF/CRLF·중단/지연/같은 창·Home/다른 project/cold·
실패/손상/명시 retry, 작은 PDF·큰 PNG/JPEG·텍스트/내용 편집 회귀와 새 교차 패키지/전체
복원은 최종 source에서 마감한다. 신규/재사용과 최신/롤백·증거/소유 임시물 수명은 최종
검증 기록에서 확정한다. 기존 원본/로그/프로필/SDK/Git·사용자 자료를 추가로 정리하지 않는다.

큰 Office/다른 그림 형식·큰 내용 편집/백업과4MiB 초과/총 보관량 확대, QHD/4K/FHD+·
GPU/물리 장치, 실제 신원/권한 backend는 별도 잔여다. mesh renderer를 임의 설계하지 않는다.
M11/M12/M4는 구체적 회귀 없이 다시 열지 않는다. 초기 빈 #app 원인은 미확정이다.
실제 Windows/WebView2·모바일·DPI/IME·물리 오디오·전체 UI·Space/Library 전달은 이번
Linux native/Chromium 자동화 및 교차 패키지 생성·복원과 구분한다.

[최종 신규51단계·지속 보관·미실행 기록](VALIDATION_V666_RESOURCE_PDF_PARTS.md)을 따른다.
