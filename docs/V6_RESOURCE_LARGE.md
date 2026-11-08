# V6 단일 자료의 4MiB 사본 보관

저장소 v666 `dist/app.js::importResourceFiles`의 명시 File 사본을 기존 메뉴와
폴더/드롭 경로에서 보관한다. 파일당 제한을 1MiB에서 4MiB로 넓히며 선택 합계와
전체 원본 보관은 기존 4MiB/64개 그대로다. 무제한 파일이나 총 보관량 확장이 아니다.
원본 파일/부모/외부 경로를 받거나 이동·삭제하지 않는다.

1MiB 초과의 단일 root File도 기존 import-many 형태로 보낸다. 원래 입력·항목/명령 ID·
목적지·revision을 유지한 UTF-8 JSON/SHA와 세션당 최대 6,000,000B 버퍼, 1MiB 청크를
재사용한다. 전역 RPC 2MiB, 필드/원본 검사, 최종 CommitPlan/CAS를 늘리거나 우회하지
않는다. 전체 바이트가 검증되기 전에는 파일이나 폴더 배치를 쓰지 않는다. 실패/응답 유실은
같은 요청으로만 명시 재확인하며 새 revision으로 자동 재기준하지 않는다. 취소/닫기/Home/
재시작은 미확정 입력과 성공 보관본을 구별한다. File/전송 본문은 presentation에 저장하지 않는다.

원본 저장은 동일한 `.confectory/resources.v1.json` 필드/ID/import receipt와 6MiB 파일 상한을
유지한다. 새 reader는 모든 저장 바이트의 길이·canonical base64·SHA와 명시 원본/identity를
검사한다. **1MiB 초과 사본이 있는 저장소는 이전 1MiB reader/writer와 호환되지 않는다.**
구버전은 목록/읽기/쓰기 전에 거절하며 비우거나 재작성하지 않아야 한다. 작은 파일만 있는
기존 저장소는 이행·재작성 없이 읽는다. 구버전으로 새 큰 파일을 편집할 수 있다고 표시하지 않는다.

보관과 내용 읽기의 한도는 다르다. `limits.fileBytes=4194304`, `readFileBytes=1048576`이다.
큰 항목의 `read`는 검증된 metadata와 `encoding:"unavailable"`,
`reason:"resource_preview_file_budget"`를 반환하며 `data`를 포함하지 않는다. 기존 작은
파일의 base64url 응답은 유지한다. public 함수 시그니처/권한과 기존 RPC 응답 한도를 유지한다.
큰 파일 미리보기 창은 보관됨/내용 미지원 범위를 표시하고 이름·설명은 기존 metadata로
연결한다. 이름 변경·이동·확인 후 삭제·성공 보관본의 cold 복원은 같은 ID와 바이트를 유지한다.
내용 미리보기/텍스트·Office 편집/백업은 계속 1MiB 범위다. 큰 원본을 작은 새 내용으로
바꿔 백업 상한을 넘기는 경로는 **쓰기 전에 거절**한다. 보관 성공을 렌더링 성공으로 표시하지 않는다.

기존 C# 원문·공개/override 계약·권한·Review→Confirm/source CAS·모델/전송 수명을 유지한다.
큰 파일의 내용 다운로드/분할 미리보기, 전체 보관량 확대와 4MiB 초과 파일은 별도 잔여다.
생성한 테스트 자산으로만 검증한다. 실제 Windows/WebView2/모바일·OS 파일 드롭·전체 UI·
Space/Library 전달은 교차 패키지/Chromium 검증과 구분한다. 초기 빈 #app 원인은 미확정이다.

[최종 검증·보관 기록](VALIDATION_V666_RESOURCE_LARGE.md).
