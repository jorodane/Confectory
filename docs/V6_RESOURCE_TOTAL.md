# V6 명시 자료 사본의 누적8MiB 보관

고정 v666 ZIP `app.js::importResourceFiles`/`resourceDatabase`는 명시적으로 선택한 File을
프로젝트 ID에 사본으로 축적한다. 현재 공급자의 누적4MiB 제한 때문에 이미4MiB를 보관한
프로젝트는 두 번째 적격 File을 추가할 수 없다. 원본이8MiB를 지정한 것은 아니다. 이번
실행 예산은 파일당/선택 합계4MiB·64개·세션 전송6,000,000B와 원자 CommitPlan16MiB를
유지하면서 두4MiB 사본을 실제 저장·재시작·관리하는 누적8MiB 경계다. 더 큰 파일/총보관의
일반 blob 저장을 완료하거나 용량마다 새 필수 조합을 추가한 것으로 세지 않는다.

기존 소유 `.confectory/resources.v1.json` 경로·필드/ID/immutable import 영수증은 유지한다.
새 reader는 version1의 누적4MiB/직렬화6MiB를 그대로 검증한다. 읽기·작은 명시 저장은 v1을
재작성하지 않는다. 명시 import의 검증된 후보가4MiB를 넘을 때만 version2를 기록한다.
version2는 누적8MiB·직렬화12MiB이며 삭제 뒤 작아져도 자동 v1 축소/이행하지 않는다.
구 reader는 version2 load/read/write를 거절하며 원본을 비우거나 재작성하지 않는다.
예전 reader로 새 저장소를 편집할 수 있다고 표시하지 않는다. 실제 사용 전 짝맞춘 버전이 필요하다.

카테고리/내용/삭제 등 Layout의 원본 catalog 관측만12MiB bounded snapshot으로 연결한다.
각 내용/백업/preview/private 초안·전체 active64MiB/두 사본128MiB·삭제 영수증은 별도 기존
한도를 유지한다. 한 번의 import4MiB, 파일4MiB, 전체 항목64, 폴더64, RPC2MiB/조각1MiB와
관측 응답 metadata는 그대로다. API/공개 override/C# 원문·권한·Review/Confirm은 바뀌지 않는다.
새 계정/외부 경로/원본 파일의 이동·삭제나 새로운 접근 권한을 부여하지 않는다.

파일 추가와 폴더 배치는 하나의 기존 준비/CommitPlan·최종 manifest/identity/store/deletion
CAS에서 확정한다. 승격도 그 거래의 일부다. 실패/충돌 시 기존 v1/v2와 입력/peer bytes를
보존하고 같은 요청으로만 명시 재확인한다. 원래 UI·메뉴·문체·File 선택은 유지한다. v2의
파일/폴더 삭제는 명시 선택한 프로젝트 사본만 제거하고 기존 content/private 수명을 따른다.
응답 유실·취소/닫기/Home/cold가 미확정 업로드를 자동 확정하거나 재전송하지 않는다.

검증은 기준4MiB 거절, 독립 provider의 고엔트로피 두4MiB/정확8MiB bytes·ID/영수증·초과,
실제 pre-CommitPlan manifest/identity/store/deletion 경합·write 실패/원자 rollback,
실제 구 reader의 v2 거절/v1 호환·위조 v1 거절, UI 폴더/삭제/명시 retry/응답 유실/늦은
입력/닫기/프로젝트/cold, 기존 import/layout/content/DOCX/XLSX를 포함한다. 최종 독립
LF/CRLF·새 교차 패키지/전체 SHA/mode 복원·실패 수명 및 신규/재사용은 후속 기록에서 확정한다.
생성한 File만 사용하며 개인 파일이나 외부 자료를 업로드하지 않는다.

실제 Windows/WebView2·모바일/OS 파일 드롭·Office 앱·물리 오디오/GPU·전체UI·Library/
Space 전달은 별도 미실행/미완료다. 초기 빈 화면 및 역사적4K 재조회 실패 원인은 미확정이다.
더 큰 파일/총보관·실제 신원/권한 backend·종류 C#표현/사용중삭제 정책·전체8192² 출력과
실기기 검증은 기존 잔여이며 M11/M12/M4는 구체적 회귀 없이 다시 열지 않는다.

개발 중 기존 삭제 CAS fixture는 이미 존재하던 설명 sidecar 최종 의존성을 기대 목록에
넣지 않아 정상 거래를 거절했다. 기준65d8f298 본문에서도 같은 실패를 확인했고 제품은
그대로 두었다. File/Folder fixture에 실제 설명 의존성과 해당 peer race를 추가해 기존
4/5개 write rollback·원본/peer 보존 조건을 유지한다. 수정 전 프로그램/진단을 보존한다.
큰 DOCX/XLSX 회귀는 별도4MiB 원본을 추가한 실제 v2 누적 catalog에서 편집/백업/private
복구를 수행하고, 전체 불변 원본 catalog를 매 단계 대조한다. 기존 작은 catalog 검사도 유지한다.
