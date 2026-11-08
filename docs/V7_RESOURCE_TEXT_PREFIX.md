# 큰 텍스트의 앞부분 미리보기

기준은 저장소 `Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/resource-preview.js`다. 원본은
`blob.slice(0,1024*1024).arrayBuffer()`와 “파일의 앞부분 1 MB까지 표시합니다.”를
사용한다. 전체 큰 파일을 전송하거나 편집하는 요구로 확대하지 않는다.

기존 명시 File 사본의 파일당4MiB·전체4MiB/64개 범위 안에서 1MiB 초과 텍스트/코드의
첫1MiB를 원래 자료 창의 `<pre>`에 표시한다. UTF8·UTF16LE/BE BOM 선택, 줄바꿈과
불완전 마지막 문자의 TextDecoder 처리는 원본과 같다. HTML은 literal text이며 실행하지 않는다.
OBJ/GLTF의 원문 텍스트 표시는 mesh renderer 지원을 뜻하지 않는다.
이미지 kind·PDF·Office가 우선하며, 큰 rich/binary 자료는 기존 제한 안내를 유지한다.

`Layout.read`의 기존 unavailable/no-data 결과에 선택적인 prefix capability만 더한다.
`preview-text`는 ID·전체SHA256·생성세대·compound 표시 revision을 고정하고 전체 원본/영수증을
검증한 뒤 첫1MiB와 그SHA256·전체길이를 반환한다. manifest·identity·store·layout·이름·설명·
삭제이력·내용 sidecar의 최종 재검사를 유지한다. native가 전체 파일을 확인하고 브라우저는
정확히 표시할 prefix의 바이트/해시와 관찰 identity를 확인한다. 브라우저가 전체 큰 SHA를
직접 계산했다고 표현하지 않는다. 응답은 기존2MiB RPC 안에 들어가며 조각 전송은 추가하지 않는다.

EditorHome의 활성 ProjectContext·취소·관찰 전용 endpoint를 사용한다. 다른 프로젝트나
오래된 생성세대/revision을 자동 재기준하지 않는다. 닫기/Home/프로젝트 전환/재시작은 기존
preview token의 수명을 따른다. durable presentation에는 원문/prefix/미결 읽기를 저장하지 않는다.
내용 편집·백업의1MiB 제한, 원본C#·공개/override 계약·권한·Review→Confirm·쓰기CAS는 그대로다.

설명 필드는 검증된 header 전에는 readonly이고, header 뒤 prefix를 기다리는 동안에는
기존대로 편집할 수 있다. prefix 도착 시 metadata를 다시 bind하지 않아 더 늦은 설명 입력을
덮지 않는다. 오류는 사본을 변경하지 않고 명시적인 같은 항목 읽기 재시도를 제공한다.
capability가 없는 기존 backend의 metadata-only 결과도 계속 표시한다.

[최종 신규 검증·패키지/전체 복원·복구 기록](VALIDATION_V666_RESOURCE_TEXT_PREFIX.md)에서 새 검사와 선행 실패를 구분한다.
4MiB 초과/총 보관량 확대, 큰 내용 편집·백업과 다른 rich 형식, 실제 신원·멤버/권한 backend,
실제Windows/WebView2·모바일·DPI/IME/전체UI 및 Space/Library 전달은 이번 완료에 포함하지 않는다.
초기 빈 화면의 원인은 미확정이다.
