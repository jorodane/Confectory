# v666 XLSX 셀 값 편집

저장소 v666 ZIP의 `resource-edit.js` 워크시트 선택·셀 textarea·값 타입·수식 캐시/
재계산 속성·직전 내용 복원 흐름을 연결한다. 원래 `resource-sheet-editor`와
`resource-sheet-cell` CSS, 기존 미리보기 패널과 설정 배치를 유지한다.
1MiB 이하 프로젝트 사본에서 셀 값만 수정하며 XLSX 수식 실행·서식/시트/병합 구조
편집·Office 앱 실행·큰 파일 지원은 이 단위가 아니다.

공식 XLSX MIME 또는 `.xlsx` 이름의 빈/binary/ZIP MIME만 편집한다. 기존 File 소유권/
ProjectContext/읽기·쓰기 검증과 opaque byte 저장 API를 유지한다. 원본 import·ID·이름·
설명·부모/외부 원본·C#·공개/override 계약은 바꾸지 않는다. 최종 Layout CAS와 동일
command 영수증으로 저장하며, 기존 current/backup을 정확한 ZIP 바이트로 복원/복원 취소한다.

원본과 같이 최대30개 워크시트, 앞200개 존재하는 행·30열의 값을 표시한다. 빈 시트는
A1을 표시하고 같은 화면 안의 빈 셀을 생성한다. 수식 셀·배열/공유 수식 범위·보호 시트·
병합 영역의 덮인 셀은 읽기 전용이며 저장 단계에서도 재확인한다. 표/차트 시트나 임의
경로를 새로 지원하지 않는다. 기존 미리보기와 같은 `xl/worksheets/sheetN.xml`의 등록된
내부 workbook 관계만 사용하며 외부 관계는 탐색하지 않는다.

원본의 값 변환을 유지한다. 기존 shared/inline/string은 텍스트로 남고, 기존 숫자와
새 숫자는 유한 Number로 기록한다. 새 셀의 `001`은 텍스트다. 기존 boolean의 true/false는
boolean으로 보관한다. 그 밖의 입력과 `=...`는 inline 문자열이며 수식으로 실행하지 않는다.
수식과 병합·styles·shared strings·관계·기타 ZIP 항목을 유지한다. 원본과 같이 수식의
오래된 v 캐시를 제거하고 workbook의 `fullCalcOnLoad=1`, `forceFullCalc=1`, `calcMode=auto`를
설정해 원본 프로그램의 재계산을 요청한다. 실제 Excel 계산 결과로 표현하지 않는다.
수정된 시트·수식 캐시가 있던 시트·workbook XML만 다시 압축하고, 다른 local header/
압축 데이터/descriptor 및 새 offset 외 central metadata는 그대로 보존한다.

기존 DOCX 컨트롤러/ZIP writer를 공통으로 사용하며 DOCX 거절/보존 경계도 유지한다.
모든 ZIP 항목 CRC, 항목8MiB·합계16MiB, XML당2MiB·합계4MiB/64parts,
DOM node50,000·깊이64·문자524,288과 표시 node20,000을 제한한다. UTF-8 XML을 읽으며
DTD/entity·불일치 구조·서명/매크로·ZIP64/암호화/경로 위장/불투명 record는 거절한다.
각 Worker5초 응답 제한·DOCX와 합계2개 editor, 세대/접기/닫기/프로젝트 전환에서 종료와
늦은 응답 무시를 유지한다. hard CPU 상한으로 표현하지 않는다.

비공개 초안은 additive `xlsx-v1` codec, 원래 ZIP과 compact `c:sheetIndex:cellRef` 변화로
보관한다. sheetIndex는 같은 hash/generation의 고정 workbook에서 해석하므로 다른
프로젝트/새 파일에 묵시 대응하지 않는다. 최대4,096개 변화·합계98,304 UTF-16 단위로
기존2MiB 전송·4MiB private 기록 예산을 유지한다. 한도를 넘으면 입력을 화면에 유지하고
저장/이탈을 차단해 길이나 개수를 줄이도록 안내한다. 동일 pending bytes의 명시 재확인,
압축/저장 중 새 입력의 분리, 실패/재시작 입력 보존·자동 Save 없음·취소를 재사용한다.
구버전 private parser는 새 codec을 읽지 못하므로 XLSX 초안이 있는 상태를 과거 패키지로
편집하는 것은 지원하지 않는다. 이 제한을 자동 이행이나 원본 수정으로 숨기지 않는다.

형식 근거는 Microsoft의 [셀 타입](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.spreadsheet.cellvalues)과
[재계산 속성](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.spreadsheet.calculationproperties.forcefullcalculation)을 함께 따른다.
실제 Windows/WebView2·모바일·Excel 앱/전체 UI·Space/Library 전달과 자동화/교차패키징은
구분한다. 초기화 빈 화면은 원인 미확정 잔여이며 다른 원본 형식/mesh 범위를 임의 설계하지 않는다.

원래 값으로 되돌린 변경 없는 Save는 프로젝트 내용·직전 복원본·영수증을 바꾸지 않는다.
그 확인 중 들어온 새 입력은 별도 변화로 유지한다. [최종 검증과 보관·한계](VALIDATION_V666_RESOURCE_XLSX.md)를 따른다.
