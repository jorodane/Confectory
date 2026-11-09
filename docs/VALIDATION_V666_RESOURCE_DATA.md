# 원본 자료 Data 보기 최종 검증

동결 `294ba7f12863214a88e6fad8e33ff395270cfe49`의 유효67단계(신규35·동일 근거 재사용32)를 통과했다. 개발 검사는 최종으로 다시
세지 않는다. 신규 단계 분포 `{"resource": 1, "lf": 7, "crlf": 7, "windows": 2, "packaged": 8, "restored": 9, "package": 1}`. [원본 근거·유한한 지원](V6_RESOURCE_DATA.md)을 따른다.

| 검사 | 실제 확인 |
|---|---|
| source | no-hardlinks LF/CRLF·독립 HOME/NuGet·빈 engine cache, Release/MCP/Linux engine. 고정 ZIP/SHA와 정확3개 UI 제품 파일. CSS/HTML·native/core/팩·공개/override ABI·권한/CAS·자료/private 형식 불변 |
| Data 표시 | 실제 native 종류/크기·Unicode 이름·폴더 크기 —·설명과 원본 행/버튼. readonly 필드의 기본 text 동작은 행 선택/열기/내부 drag가 되지 않음 |
| 사용자 흐름 | 첫 이름 선택·Ctrl 다중 선택, 단일 선택 후260ms 인라인 편집·Escape 취소·원자 alias 저장·ID/hash/원본 bytes 유지. 명시 문서 열기는 실제 저장 내용을 표시하고 선택 보존, 폴더 열기는 실제 하위로 진입. 이름 double-click은 열린 문서1개와 지연 rename 취소 |
| 수명/입력 | 새 검색/설명·Escape·폐기된 handler·창/프로젝트 수명은 지연 입력을 적용하지 않음. 새 Data 버튼/필드는 dirty 설명을 blur/제출하지 않으며 실제 cold에서 설명·미확정 이름과 기존 revision을 복원 |
| 실패/CAS | 실제 alias 파일 readonly Save 거절·원래 command/revision 유지·cold 자동 재생0·동일 요청 명시 재시도. 실제 동료 alias 변경 뒤 stale Save/cold/재시도 거절·입력만 취소하면 동료 값 보존. description 보호는 기존 sort/filter 회귀에서도 확인 |
| 영향 회귀 | 실제 layout handler의 timer 합치기·오래된 callback 거절·tree button drag 유지/새 입력·open drag 거절. 기존 정렬·keyboard·filter/Data cold/새 세대·parent receipt/최종 read race·layout·original bytes/pixel/download·WebUI scope/revision/cancel/dispose |
| package | 새 Windows 교차 생성/구조·의존성·무결성. 포함 Linux engine 생성본과 전체 CRC/SHA·파일/디렉터리 mode 복원본의 Data normal/lifecycle·기존 sort/keyboard/filter/parent/layout/original. 실패/예외 증거 보관 뒤 owned 임시물 정리 |

개발17 managed 단계는 모두 exit0이다. 게시 eda49871의 실제 Data 구조/컨트롤 누락을
baseline으로 보존했다. 코드 검토에서 일반 button 차단이 기존 계층 drag까지 거절할 수
있음을 찾아 명시 Data open/입력으로만 좁힌 뒤 단위 양방향/실제 layout 회귀를 통과했다.
이는 게시 전 보완이다. 로컬 단위 precheck의 undefined serial을 NaN으로 만든 fixture는
실제 selection API와 같이0부터 증가시키도록 고쳤고 최초 파일/이유도 증거에 보존했다.
개발 fixture·프로필·로그·스크린샷·final-inputs와 regenerable 출력 SHA 목록을 보관한다.

최종 초기 두 실행은 managed 작업공간/빌드 생성 전 메모리 사전 확인에서 각각80KiB,
616KiB 부족으로 종료됐다. 실제 종료와 source record0을 확인했다. 대기 bash의 RSS1848KiB를
관측하고 `exec`로 동일 Python 검증기/인자를 직접 실행해 대기 shell만 제거했다. 추가9GiB·
안전1GiB 예산은 그대로이며 첫 동결3873c63d의 성공 preflight cgroup은6,441,803,776B다. 두 실패 로그와
memory-preflight-recovery.json을 최종 증거에 보존했다. 기존 파일 삭제·전역 cache/allocator·
시스템 설정 변경·코드/검사 축소·중복 빌드나 환경 교체는 없었다.

첫 동결3873c63d의 실행은57개 통과 후 공통 restored-probe에서5초 안에 Codex 로그인
버튼이 나타나지 않아 중단됐다. 그때 비동기 connectionSetup 중 UI가 차단된 snapshot을
보존했고 초기 빈 화면과 같은 원인이라고 단정하지 않는다. 실패 record/evidence는 그대로
보존했고 원본 실패를 통과/재사용으로 세지 않았다. Data 제품 bytes는 그대로이며 새 source
`294ba7f12863214a88e6fad8e33ff395270cfe49`는 공통 probe의 준비 완료/진단과 엄격한 재사용 배선만 보완했다.

새 probe는 원래5초 관측을 저장한 뒤30초의 총 한도 안에서 실제 로그인 버튼과 선택한
Codex 작업의 완료를 요구한다. 요청 path·endpoint 이름·완료 시각만 기록하며 payload,
로그인/추론·외부 요청은 실행하지 않는다. 준비 진단 `[{'passed': True, 'elapsedMs': 2027.24, 'initialFiveSecondReady': True}, {'passed': True, 'elapsedMs': 3665.66, 'initialFiveSecondReady': True}]`를 보존했다.
이번 재검사가 통과해도 이전 일시 지연의 근본 원인이 해결됐다고 표현하지 않는다.

재사용32개는 동일 Data 제품/native/검사·SDK/NuGet·정규화한 호출의 LF16·CRLF16 소스
사실뿐이다. source-bound helper는 archive/manifest·개별 결과와 코드/검사 blob·CLI 인자를
대조하고 다른 제품 또는 SDK를 거절한다. 경계·빌드·패키지·실패한 공통 probe·복원은 모두
신규다. 실패 lifecycle이 후보 패키지를 owned 임시물로 회수했으므로 새 빌드/패키지 생성이
필요했다. 기존57개 통과와 새35개/재사용32개를 중복 합산하지 않는다. proof는 최종 archive의
resource-data-reuse-3873c63d.json이며 이전 archive SHA `255ac658eac1458915e893cdce757123af9ffb2a5a97c4279ad63cb593623b35`를 참조한다.

새 실패 증거 ZIP/manifest의 SHA/metadata를 확인하고 read-only FD의 POSIX_FADV_DONTNEED로
사용이 끝난 이 단위의 파일 읽기 캐시만 OS에 반납했다. 기록은 owned-evidence-read-cache.json이다.
파일 삭제·다른 기존 자료·전역 cache 설정·cgroup/allocator/안전/추가 메모리 예산 변경은 없다.
새 실행은6,442,037,248B에서 같은 전체 메모리 사전 확인을 통과한 뒤 원래32개 증거도 다시 검증했다.

정렬·필터·readonly metadata는 원본/권한·Review/Confirm/최종 CAS를 바꾸지 않는다.
현재 Data의 명시 파일 alias 저장·폴더 열기/표시 검증과 모든 타입/문맥/기기 조합의 전체
검증을 구별한다. M11/M12/M4 전체는 미실행이며 관련 제품 bytes 불변 대조와 영향 회귀를
실행했다. 선택적 조합이나 구 reader 자동 migration을 새 필수 항목으로 만들지 않는다.
새 저장 문법이 없고 기존 private 초안·일반 alias receipt의 호환/거절 의미를 유지한다.

실제 Windows/WebView2·모바일/기기 IME·GPU/물리 오디오·Office/OS 외부 앱·전체 UI·
Space/Library 전달은 미실행/미완료다. 초기 빈 화면의 원인은 미확정이다. 더 큰 보관·실제
신원/그룹 권한 backend·고급 함수 타입/핀 표시명·기존 정보 종류 C# 표현/사용중 삭제 정책은
별도다. 원본에 없는 mesh renderer나 새로운 타입/문맥 곱을 요구로 만들지 않는다.

## 지속 보관·자원

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 294ba7f12863214a88e6fad8e33ff395270cfe49 | a24d47ee07ef3ee7f27f827a4adba2d0348fba436559e3560833b24d667045e2 | 53,854,466 |
| rollback | f14deb1a5239d0bf92fc6ba458962269706ba2a0 | dfb439d876460abbc46e4091df6c8f64797021f1aeaf2da65384a65ba1d8e873 | 53,853,666 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/8973f85f446849ed97ef03a68f927b70.json`, evidence SHA `e32a44e0f3fe56ab0307bd0c4501a6947eeea40a5643337bacc396170003c888` (3,197,022B).
개발 evidence SHA `396aff0ff576c3de7564e30e20bd3ab88f0434880e9604086bf30062a0cccc5b` (947,980B).
양쪽 archive/전체 manifest를 검증했고 owned RAM root는 사라졌다. 이전 rollback만 기존
두 세대 정책에 따라 교체했고 다른 과거 자료·증거는 삭제하지 않았다. closing index는
`/workspace/artifacts/v536-verification-managed/runs/8973f85f446849ed97ef03a68f927b70.closing-index.json`, SHA `cd873da0999bcc0bd282175e2238a3b9fe1dbc9320f7b473cceec804f27979c7`다.

시작 df 여유 25,943,363,584B, 종료 25,920,147,456B (24.1400GiB), 순증가
23,216,128B (22.1406MiB). 표본 cgroup peak 10,283,548,672B는
limit 17,179,869,184B와 안전 1,073,741,824B 안이다. 디스크/메모리
예산을 낮추거나 시스템 cache 설정을 바꾸지 않았다. 게시/문서의 작은 후속 증가와 최종
원격/clean 확인은 scratch publication.json에 남긴다. main과 원본 작업폴더는 게시하지 않는다.
