# 큰 Office 읽기 전용 미리보기 검증

동결 61a72f553cbb7462f2474990e9cf0e78f86d62bf의 신규61단계·재사용0을 통과했다.
LF 26·CRLF 26와 나머지 새 패키지/복원/수명 검사다.
[원본 흐름과 닫힌 지원 경계](V7_RESOURCE_OFFICE_PARTS.md)를 따른다. 이미 보관한1–4MiB
DOCX/XLSX/PPTX/ODT의 완전한 bytes/SHA를 확인한 뒤 기존 실제 ZIP/XML Worker·DOM에 연결했다.
원본 C#·값·공개/override 계약·권한·원본 레이아웃·Review→Confirm/최종CAS는 보존한다.

| 검증 | 실제 범위 |
|---|---|
| 독립 source | LF/CRLF no-hardlinks Git/HOME/NuGet·빈 engine cache, Release/MCP/Linux engine. 정확10개 제품 파일·canonical assets·같은 HTML/CSS. 기존 native write/content/backup·공개 celem/cpack·권한과 PDF/그림/텍스트/Run/FHD 보호 |
| transport 정책 | 4MiB 근처4개 조각·짧은 마지막 조각, exact project/item/hash/import/display/format·순서·offset/길이·canonical base64·각/전체 SHA.28개 malformed/stale/tampered 거절, busy만 제한 재관측·최종 전체 digest 중 owner 폐기 거절 |
| 실제 ZIP/편집 보호 | 네 형식의 실제 stored/DEFLATE ZIP에서 큰 media는 전개하지 않고 필요한 XML만 표시. 정확4MiB/초과·알 수 없는 opt-in 거절. 기본1MiB와 archive 편집 mode는4MiB opt-in을 거절. 기존2MiB/XML·전체4MiB/64 XML·디렉터리1024·CRC/길이/ZIP64/경로/중복/겹침 거절 유지. 기존 DOCX ZIP writer의 독립 Python CRC·미수정 record/metadata 보존도 새로 확인 |
| native 최종 읽기 | 전체4MiB 조각/SHA·store 무변경, 이전89d77344 reader와 metadata-only 동일성/새 operation 거절. rename·같은 ID/hash 재import 세대·tail 변조·잘못된 fields/parts·manifest/identity/store/layout/이름/설명/삭제/content sidecar 최종 읽기 race 거절. 기존 PDF 실제 final-read 본문도 별도 실행 |
| 실제 UI/API | 큰 DOCX heading/서식/표·문자 그대로 표시, XLSX 캐시값/boolean/수식 literal·반복 sheet 선택, PPTX 숫자 순서·ODT 문단, 정확4MiB workbook 실제 DOM. 큰 문서는 edit/restore 컨트롤 없이 읽기 전용. native 큰 save-content/restore-content도 쓰기 전에 거절 |
| 실패·수명 | dedicated observation의 foreign/stale/path/누락·실수/문자 part·mutation/image/PDF lane 거절. malformed/legacy cap·혼합/손상 part·원본 tail 변조는 Worker 생성 전 거절하고 명시 retry로 복구. 대기 중 새 설명 보존·저장 뒤 old basis 거절. 큰 DTD/entity ZIP 실패/재시도·외부 조회 없음 |
| 중단/격리 | accepted part 대기 중 close/reopen·접기/unfold·Home/다른 project·cold의 늦은 응답 격리, native read 권한 거절·복구와 다른 입력/원본 보존. presentation에 ZIP/XML/partial transfer/Worker 없음 |
| 관련 회귀 | 기존 작은 Office 실제 module Worker/4-view quota/DTD·CRC·ZIP64·5초 deadline·접기/해제. 작은 DOCX·XLSX 실제 편집/저장/변화 없는 Save·실패/응답 유실·늦은 입력·백업/복원/cold. 기존 큰 PDF·PNG/JPEG·일반 내용 편집의 실제 회귀. FHD의 변경 없는 source와 [이전69단계](VALIDATION_V666_RUN_FHD.md) 근거는 유지하며 이번 신규 수에 더하지 않음 |
| 패키지/전체 복원 | 새 Windows 교차 생성·구조/probe, 그 안의 실제 Linux 엔진/큰 Office normal·작은 XLSX 편집. ZIP CRC·전체 파일SHA·파일/디렉터리 mode 복원 후 큰 Office lifecycle·작은 DOCX 편집/cold. 실패 수명관리와 증거 봉인 후 소유 checkout/cache/build 종료·정리 |

개발 기록 /workspace/artifacts/v536-verification-managed/runs/42235ff2f9d04e51bdcb020fb024b193.json의 15단계는 기존 게시본에서 큰 Office 제한 안내와
작은 Office 정상 표시를 재현한 뒤 overlay의 unit/native·실제 UI를 확인했다. 한 normal
실패는 생성한 자료가 하나 남았을 때 기존 단일 삭제 메뉴 대신 다중 선택 이름을 기다린
검사 선택자 오류였다. 원래 제품 코드를 바꾸지 않고 단일 선택 분기만 수정한 normal/lifecycle가
통과했다. 실패 로그와 전후 검사 source/SHA를 보존하고 최종 신규 수에 합산/재사용하지 않았다.
최종 LF source의 실제4MiB 워크북 화면(4194304B·문자 literal/2/TRUE)과 읽기 전용·셀 값·시트 전환도 직접 확인했다. 생성 ZIP은 큰
미참조 무작위 media와 작은 실제 XML이므로 복잡한 문서 전체의 서식/성능/메모리 증거가 아니다.
native race는 통제된 fixture, Compression Streams/Worker/DOM과 native 엔진은 실제 실행이다.

선택 officePreview와 관찰 lane만 추가했다. 기존1MiB read·저장v1·파일/전체4MiB/64개,
2MiB RPC·기존 image/PDF/text capability와 실제 권한·원자 저장/최종CAS를 유지한다.
이전 backend/UI의 capability 없음은 원래 metadata-only 안내다. PK signature는 완전한
문서 인증이 아니다. 미사용 media까지 CRC 검증하는 일반 ZIP 도구가 아니며 전체 bytes의
SHA와 구조/선택 XML 검사도 구분한다. 큰 DOCX/XLSX를 편집기에 연결하지 않고 기존 작은
편집/private/backup/복원/변화 없는 Save를 보존한다. 입력/선택 전개/DOM/5초 deadline은
모든 경우의 hard CPU·전체 프로세스 메모리 상한이나 Office 앱 호환 보장이 아니다.

## 지속 보관과 공간

- 최종 record: /workspace/artifacts/v536-verification-managed/runs/f483d15527a241a799ed6c4e1d528816.json
- 증거 ZIP: /workspace/artifacts/v536-verification-managed/runs/f483d15527a241a799ed6c4e1d528816.zip, 91,532,009B, SHA256 1be105cf68283a6194692e6fb557251a23017c9f0c0069131eea9308f067241b
- 승격 전 index: 증거 ZIP의 package-index-before.json
- 승격 후 동반 index: /workspace/artifacts/v536-verification-managed/runs/f483d15527a241a799ed6c4e1d528816.closing-index.json, SHA256 e9ffb2e7d9cecf08618f22af261682eafb010c36eb0dcec23f63c943cc999672

| 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `61a72f553cbb7462f2474990e9cf0e78f86d62bf` | `d6bf5702fd96c7013467645673643cb1b3bd863613a7b62fb529d9ac502fb7ce` | 53,830,263 | 2720/158 |
| rollback | `d8279712afa0e7ddfed48f45854d0c06d48294c6` | `deed66a9cb3bc0a0a3d4d9bb13955f690b42d8780ba1316393e50450eedc4923` | 53,827,311 | 2719/158 |

새 전체 복원과 지속 증거를 검증한 뒤 원자 승격했다. 직전 정상d8279712를 rollback으로
보존하고 이전 관리 rollback47262dc1 3c84f7d4b3671fb074930680f12422da67856d6cfc5e459b7c194fa527363b6d만 승인된2세대 수명으로 퇴역했다.
rollback은 같은 ZIP SHA·전체 manifest·이전 전체 복원 근거를 유지하고 이번에는 구버전
엔진 자체를 다시 실행하지 않았다. 다른 기존 원본·과거 로그/프로필·SDK/Git·사용자 자료는
추가 정리하지 않았다. 실행이 직접 만든 임시물만 자식 종료/소유권·지속 증거 확인 후 정리했다.

추가 디스크 264,241,152B(archive56MiB·증거128MiB·코드4MiB와 별도
안전64MiB), RAM 작업공간3GiB·추가 메모리7GiB+안전1GiB를 유지했다. 최종 시작/종료 여유
30,211,051,520/30,116,851,712B, 표본 차이 94,199,808B다. 개발 포함 단위
시작/종료는 30,249,672,704/30,116,851,712B다. 최종 단계 표본 최저 디스크 30,210,957,312B,
관측 cgroup peak 6,249,099,264B다. 모든 순간의 절대 극값이나
이후 고정 증가량 보장이 아니며 안전 기준을 낮추거나 증거를 버려 맞추지 않았다.

기존 환경·SDK10.0.401/seed·원본 checkout과 main을 유지한다. 마지막 문서 마감 뒤에도
runtime/검사/tools가 동결 source와 같은지 확인하고 work/current에 정상 게시한다.
큰 다른 그림·내용/Office 편집·백업·4MiB 초과/총 보관 확대, 실제 신원/권한 backend와
QHD/4K/FHD+·GPU/장치는 기존 잔여다. 임의 mesh/타입 조합·권한 정책을 추가하지 않는다.
초기 빈 #app 원인은 미확정이며 M11/M12/M4를 구체적 회귀 없이 다시 열지 않는다.
실제 Windows/WebView2·모바일·DPI/IME·Office 앱 호환·물리 오디오·전체 UI·Space/Library는 미실행/미완료다.
