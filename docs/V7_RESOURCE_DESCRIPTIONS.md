# V666 자료 설명

기준: 저장소의 `reference/site-ui/Confectory-Editor-Prototype-v666.zip` 내부
`Confectory-v666/dist/app.js`의 `data-resource-description`, 자료 설정의
`aria-label="자료 설명"` 및 `resourceItems` 이름+설명 검색이다.

Data 표시의 파일·카테고리 설명 입력과 자료 미리보기 설정의 6행 textarea를
연결한다. 원본 maxlength 1000 UTF-16 단위를 적용하며 줄바꿈·공백·문자열은
그대로 보존한다. NUL 등 줄바꿈/탭 외 제어문자는 거부한다. 기존 현재 폴더
검색은 이름과 설명을 함께 검사한다. 파일 이름·ID·내용·MIME·해시·원본
경로·부모·계약·권한은 설명 편집으로 변경하지 않는다.

선택적 `.confectory/resource-descriptions.v1.json`은 프로젝트/manifest,
대상 ID와 생성 세대, 값과 마지막 정규화 요청/해시 영수증을 보관한다.
파일 세대는 기존 import command, 폴더 세대는 create command의 SHA256이다.
최대 128개/2MiB이고 미생성 시 기존 revision 계산은 그대로다. 모든 Layout
변경은 설명 sidecar의 존재/해시도 최종 CommitPlan에서 검사한다. 자료 삭제는
해당 설명과 값이 담긴 영수증도 같은 원자 저장에서 제거한다. 미확정 입력의
대상이 삭제/재생성되면 별도 읽기 전용 복구 입력으로 보존하고 현재 자료에
적용하지 않는다. 명시 취소 전까지 복사해 둘 수 있다. 재사용 ID는
이전 설명을 물려받지 않는다. 삭제 정책·원본 파일 접근권한을 확장하지 않는다.

입력과 정확한 pending 요청은 기존 프로젝트별 비공개 presentation에 보존한다.
native mutation 전에 해당 presentation을 내구 저장한다. 실패/응답 유실은
같은 command로만 명시 재확인하며 외부 변경 위에 자동 재기준하지 않는다.
자기 성공 영수증만 확인한 후 추가 입력은 별도 변경으로 유지한다. 입력 취소는
현재 보관 상태를 확인하고 private 입력만 지운다. 재시작은 자동 저장하지 않는다.
자료 metadata는 기존 이름 편집처럼 직접 저장하며 소스의 Review→Confirm,
권한 판단 및 Undo 체계를 바꾸지 않는다. 이미 저장한 metadata를 입력 취소로
되돌린다고 약속하지 않는다. 원본 blur/change 저장 의미를 유지한다.

과거 실행본은 새 sidecar를 읽지 않고 새 CAS/삭제 시 제거를 보장하지 않는다.
새 설명을 작성한 프로젝트를 과거 롤백 실행본으로 편집하는 것은 지원하지
않는다. 기존 sidecar 없는 프로젝트는 별도 이행이나 재작성 없이 읽는다.

남은 V7: 큰 파일 전송/보관, Office 내용 편집, mesh 등 실제 지원 범위 대조와
기타 고정 수용 목록. PDF/Office 미리보기·내용 복구·폴더/삭제 등 완료 기능은
잔여로 되돌리지 않는다. 간헐적 초기화 빈 화면은 원인 미확정이다. 실제 Windows/
WebView2·모바일 기기, 전체 UI 및 Space/Library 전달은 별도 검증/전달 범위다.
