# V6 한 번에 여러 자료 사본 보관

원본 v666 `app.js::importResourceFiles`는 선택한 File 전부를 같은 IndexedDB readwrite transaction에 넣은 뒤 목록에 반영한다. 이 단위도 기존 자료 추가/드롭·창 배치를 유지하고 활성 ProjectContext의 선택 전체를 한 native CommitPlan으로 보관한다. 순차 단일 저장으로 부분 성공을 만들지 않는다. Office 내용 편집이나 큰 파일 스트리밍을 지원한 것으로 표시하지 않는다.

독립 ProjectResources의 기존 `import {revision,command,item}`·`load`·`read` 계약과 `resources.v1.json` grammar는 유지한다. 추가 `import-many {revision,imports:[{command,item},...]}`는 같은 관측 revision의 명시 단일 import 의도들을 묶는다. 각 원래 ID·내용 SHA·command·원래 digest를 그대로 보관하고 반환의 `selectedIds`로 전체 선택을 표시한다. 별도 전역 배정/복제 정책이나 새 그룹 신원을 만들지 않는다.

선택은1–64개·합계1MiB, 기존 파일당1MiB·프로젝트 전체4MiB/64개 경계 안이다. `limits.importBatch`와 `limits.importBytes`로 공개한다. 기존 IPC2MiB와 native payload 제한은 올리지 않는다. 파일 bytes/hash/이름/ID·총량·전체 저장 형식을 모두 확인한 뒤 한 쓰기로 바꾸며 manifest·프로젝트 identity·삭제 기록·저장본의 최종 CAS를 유지한다. 폴더 첫 import 결합은 이번에 추가하지 않는다.

재시도는 제출한 모든 항목의 동일 영수증이 존재할 때만 무쓰기 확인한다. 기존/미보관 의도가 섞이면 전체를 거절하고, 다른 payload에 같은 command를 쓰거나 삭제된 import를 다시 살리지 않는다. 이미 확인된 의도 중 일부만 조회하는 것은 기존 개별 영수증 확인이며 새 전체 저장을 뜻하지 않는다. 이전 v1 reader/writer도 같은 항목과 영수증을 읽을 수 있다. 파일 이름은 경로가 아니며 동명 파일은 서로 다른 ID로 보관된다.

실패·충돌·응답 유실은 현재 창의 File 목록/bytes/동일 요청을 유지하고 명시 재시도·선택 입력 취소를 제공한다. 목록 새로 읽기가 오래된 기준을 자동 rebase하지 않는다. 선택 취소는 이미 보관된 사본의 삭제가 아니다. Home/다른 프로젝트·오래된 창 callback은 전송/표시 권한이 없으며, 실제 재시작은 미보관 파일을 자동 전송하지 않는다. File bytes·요청은 개인 presentation/Git에 저장하지 않는다. 아직 보관되지 않은 파일은 재시작 후 다시 직접 선택한다.

사용자 개인 폴더를 탐색하거나 외부 파일/URL을 자동 가져오지 않는다. 기존 본문·값·설명·source/override 계약·권한과 Review→Confirm은 유지한다. import는 프로젝트 자료 사본 보관이며 실행 권한 부여나 C# 확정이 아니다. 대형 import·현재 폴더 첫 import·배치 진입, 다른 원본 미리보기와 Office 편집은 고정 잔여다. 초기화 빈 화면은 원인 미확정이며 실제 Windows/모바일·전체 UI·Library/Space 전달은 별도 검증이다.
