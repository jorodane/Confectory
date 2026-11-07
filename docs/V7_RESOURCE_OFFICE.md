# V7 Office 내용 미리보기

기준은 저장소 v666 ZIP의 `Confectory-v666/dist/resource-preview.js`와 `style.css`다.
DOCX의 문단·간단한 텍스트 서식/표, XLSX의 워크시트 선택·저장된 값, PPTX의
슬라이드 텍스트, ODT 문단을 원본의 자료 창 안에 표시한다. 문서를 편집·저장하지 않는다.
수식은 계산하지 않으며 캐시 값이 없으면 수식 자체를 텍스트로 표시한다.

활성 ProjectContext의 기존 읽기 권한·ID·SHA·canonical base64 검증을 통과한 사본만
사용한다. 파일명/자료 metadata와 원문을 바꾸지 않으며 기존 text/image 편집, native
저장 계약·CAS·Review→Confirm·부모/외부 보호에는 변경이 없다. 새 업로드·외부 링크
조회·Office 앱 실행·매크로/스크립트 실행은 하지 않는다.

원래 1MiB 사본 읽기 제한을 유지한다. 전용 동일 출처 module Worker에서 표준 ZIP의
stored/DEFLATE만 처리한다. 최대 1,024개 directory entry, 선택 XML 64개·각 2MiB·합계
4MiB, 5초 deadline이며 ZIP64/분할/암호화/심볼릭 링크/경로 위장/중복/겹친 entry/
CRC·길이 불일치는 거절한다. 필요한 XML만 메모리에서 해제하며 디스크에 전개하지 않는다.
이름·local/central header와 선택 내용 CRC를 확인하나 미사용 항목 내용까지 인증하는
일반 ZIP 무결성 도구는 아니다. Worker/stream 미지원 환경은 실패 안내와 재시도를 제공한다.

원본은 fflate 0.8.2를 사용한다. 그 버전의 ZIP64 문제에 대한
[공개 advisory](https://github.com/advisories/GHSA-px8p-9vwx-vf98)를 확인했고 vendor를
복사하지 않았다. [표준 Compression Streams](https://compression.spec.whatwg.org/)와
[ZIP 형식](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT)을 기준으로
제한된 reader를 사용한다. DTD/entity는 거절하고 XML을 HTML로 삽입하지 않는다.
최대 50,000 XML node·깊이64·문자524,288, 표시 DOM 20,000개·문자524,288을 제한하며
원본처럼 문단/슬라이드/시트 수와 표 200행·30열을 제한한다. 서식 재현은 완전하지 않다.

활성 Office 창은 최대4개다. 닫기·접기·프로젝트/Home 전환·이름/관측 세대 변경·실패에서
Worker를 종료하고 XML/DOM 참조를 버린다. 늦은 응답은 현재 소유 세대에만 표시한다.
개인 레이아웃에는 기존 owner/ID/hash만 남으며 ZIP/XML·Worker는 지속 저장하지 않는다.
재시도는 같은 사본을 다시 권한 확인해 읽고, 원래 사용자의 다른 입력은 보존한다.

큰 파일/부분 읽기·Office 편집·PDF/mesh/다른 이미지 형식과 원래 기타 자료 기능은
별도 잔여다. 레거시 DOC/XLS/PPT나 암호 문서는 이 reader의 필수 지원 조합으로
확대하지 않는다. 실제 Windows/WebView2·모바일·전체 UI·Space 전달은 자동화 검사와 구분한다.

후속 DOCX 문단·표 텍스트 편집은 [DOCX 지원 경계](V7_RESOURCE_DOCX.md)와
[별도 최종 검증](VALIDATION_V666_RESOURCE_DOCX.md)을 따른다. 위 읽기 전용 검증은
당시 미리보기 단위의 기록이며 XLSX 편집은 아직 남는다.
