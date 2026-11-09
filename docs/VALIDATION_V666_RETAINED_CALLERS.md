# 기존 일반 호출자와 native 본문 공동 저장 검증

최종 runtime `7938a4f01e6331cd980e4397fbba66fc3ffc0ea8`의 **신규34단계·동등 재사용7, 유효41단계**를 통과했다. 분포 `{"crlf": 17, "lf": 16, "restored": 3, "windows": 2, "package": 1, "retained": 1, "packaged": 1}`.
[원래8행 수용 근거·지원·호환 경계](V666_RETAINED_CALLERS.md)를 따른다.

| 범위 | 실제 결과 |
|---|---|
| 게시본 재현 | 두 native 편집 각각과 원래 프로그램41은 유효. 일반 caller의 code/locals가 있는 공동 후보와 원래460px UI Save만 거절. 원본/입력 유지 |
| 후보/소유권 | 역순에도 같은 후보. 선택 본문2개만 변경하고 caller graph·코드 기록·header·local ID·edges·정확64 값을 보존. copy/private/forward/wrapper/분기5개는 기존대로 거절 |
| source 보존 | 의미가 같은 caller JSON을 재직렬화해 쓰던 결함을 수정. 변경 없는 definition hash/코드 기록은 원래 바이트를 사용하고 쓰기 footprint에 넣지 않음 |
| 읽기 CAS | callee import/native caller 없는 leaf에서도 caller graph/코드/header를 version3 readGuards로 보존. Save 전 peer 변경 전체 거절. Review 후 세 source 변경 각각 최종 Confirm 거절과 checkpoint·peer 보존 |
| cold Review | 저장 뒤 code/locals를 제거한 유효한 caller graph도 빈 legacy scope로 재해석하지 않고 거절. 정확 복구·새 Review 후 허용. 원래 receipt와 두 본문 입력 유지 |
| 증거 변조 | readGuards 전체/일부 누락·나쁜 hash·경로 이탈·추가 source·잘못된 owner/version7개 거절. 새 writes나 원본 해시 재기준화 없음 |
| 실제 UI/수명 | 기본/독립 창의 C# 편집 취소·Undo/Redo·미저장/저장 cold·Review 취소/Confirm. checkpoint 실패 재시도, 응답/조회 유실 뒤 중복 적용 없는 복구, peer 충돌·프로젝트 왕복·취소. 실제 변경 프로그램21 실행 |
| 늦은 입력 | 두 본문 Save 중 새 owner 설명 입력을 cold 뒤 보존. 다음 명시 Save도 원래 전체 읽기 해시 유지. 새 Review/Confirm으로 설명과 본문 저장 후 caller 원문과 실행21 확인 |
| 호환/회귀 | 구 leaf/단순 caller 빈 readGuards의 cold/Review/Confirm·실행20과 기존 native caller 원문/CAS는 동일 backend 입력의 봉인 증거로 재사용. 완료된 반환 표시명 UI는 최종 코드에서 새로 검증 |
| 패키지/복원 | 독립 LF/CRLF no-hardlinks·HOME/NuGet·Release/MCP·빈 cache 엔진. 새 Windows 교차 패키지 구조/무결성, 포함 Linux 엔진 UI, 전체 ZIP CRC/SHA·파일/디렉터리 mode 복원, 복원 CAS/응답 유실 및 실패 수명관리 통과 |

제품7파일은 순수 후보·source 관측/cold graph 읽기와 같은 소유 source의 새 설명
proof를 연결한다. 변경한 JS의 canonical bundle hash도 갱신했다. UI 배치/HTML/CSS·
native/public/override 계약·C# 의미·권한·최종 source lease는
바꾸지 않는다. caller 코드/지역값은 수정 대상이 아니다. 기존240 source·2MiB 경로/
링크 읽기 예산과 Review→Confirm·원자 checkpoint CAS를 유지한다.

개발23단계 중19통과·4실패를 보존했다. 실제 제품 결함2개 중 첫째는 의미가 같은 caller
코드 기록 JSON의 불필요한 재직렬화/쓰기였다. 해당 후보는 Confirm하지 않았다.
둘째는 본문-only 저장 중 처음 입력한 설명이 이전 revision에 남아 후속 Save를 막는
결함이었다. 같은 owner text hash와 settled receipt를 확인한 경우에만 기존 설명 proof를
연결해 수정했다. owner peer 변경은 그대로 거절한다. fixture2개는 caller graph를
바꾸고 header를 snapshot 비교에서 제외한 오류와20ms마다 임시 view를 만들어 정상
retired-view 한도를 넘은 polling이었다. 제외 경로와 관측 간격만 고치고 host 예산은
유지했다. 두 실제 실패 후보는 Confirm하지 않았으며 원본/입력을 보존했다. 개발 결과는
최종 검사에 재사용하지 않았다. 첫 최종 실행은31통과 뒤 포인터 충돌 경고 관측1개가
시간 초과됐으며, 저장 요청 발행은 없고 두 입력은 보존됐다. 원인은 미확정이다.
키보드 관측도 시간 초과돼 별도 증거를 보존했다. 이후 기존 버튼의 pointerdown과
release 사이에 peer 갱신을 넣어 노드가 제거·재생성되고 저장이 발행되지 않는
경로를 고정 재현했다. 같은 프로젝트/요소/종류의 갱신에서만 action 노드와 현재
handler를 유지해 stale 입력 거절을 확인했다. 프로젝트/요소가 바뀌면 노드를 교체해
이전 gesture를 새 대상에 옮기지 않는다. 활성화 재현 개발9단계를 모두 통과했다. native backend·자료 adapter의
바이트·SDK/NuGet·독립 EOL·실행 명령이 같은7개 사실만 봉인 archive와
대조해 재사용했다. 실패·미실행·빌드·패키지는 재사용하지 않았다. 새34단계와 함께
유효41단계를 구성한다. 초기 개발/두 번째 최종 실행/활성화 재현 준비의 메모리 사전검사 각1회 차단을 보존했다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 7938a4f01e6331cd980e4397fbba66fc3ffc0ea8 | 94d6d4670a8d25a38c1c09b73bc5a44a47ab9de526d1bcbdece5a4af4b25c5a9 | 53,867,355 |
| rollback | dcf4cf7b82a3d6f84515a4b921dfb17dcce62c94 | dac9103fb29d20cc42cafa105204f95662a636253c53c0bdb8b249dce45ac82b | 53,865,648 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/bbb43586faf641309f0e5e87e2383a4b.json`, evidence `3122d85b2d36be8ef06e69c4b79d993f0b070aec131e989eb0eba7a714453804` (8,122,842B).
개발 evidence `53cc390af9df2abc1dfebf7672981e94e1430763632624fb1067776cb0453b81` (4,259,645B).
활성화 재현 evidence `c4e940cc06b02793e337c8924899ff82272851685961115c3445b2c3d0589640` (1,401,173B).
첫/두 번째 최종 실패 evidence `f505427343d1a4df3a318de30bda4676a07174759a3beccfe12337649c54b7be`, `80f4faaebfec48e215d3f12fa1c4a797dead3b650c943479fb91874dce52dc31`도 봉인 상태로 유지했다.
양쪽 manifest와 보관 ZIP2개를 재검증했다. 시작 index `c41ac48d31e2a4c49516fe98a1b9439be6674b184c009f6ef26de7e813eddac7`,
종료 sidecar `c937f87a241f8dc1f4768a4f11dc1854084e51e3b1d0f3be7a6b78811264d7bd`. 최종 preflight 원본은 그대로 두고 개발 계획/실패와
증거를 별도 이름으로 보존했다. 정확 SHA·크기·inode/mode/mtime이 같은 관리 ZIP에서
read-only FD 파일별 cache 조언만 사용했으며 전체 cache나 예산은 바꾸지 않았다.

latest/rollback 두 관리 ZIP만 승인된 보관 절차로 교대했다. 이전 rollback
`464cb0c2c07b5b5cffeabe25d2112cc8451779b2`의 관리 ZIP만 교체하고 과거 evidence·사용자 원본과 기존
checkout을 보존했다. 개발/최종 RAM 작업공간은 evidence 봉인·소유 identity 확인 뒤
정리했다. 재생성 build 출력은 해시 목록을 남기고 원문·checkpoint·실패 로그/화면은
archive에 유지했다. 이 단위의 새 owned bytecode만 별도 해시 증거로 정리했다.

시작 여유 25,796,755,456B, 마감 25,769,725,952B(23.9999GiB), 순증가 27,029,504B.
최대 관측 cgroup memory 9,490,989,056B, 최종 stage 최소 디스크 25,777,848,320B.
추가 cgroup 메모리9GiB+안전1GiB·RAM 임시파일4GiB+파일시스템 여유512MiB·
디스크 안전64MiB·최종 evidence512MiB의 기존 사전검사 예산을 유지했다.
위 memory 수치는 cgroup 전체 사용량이며 RAM 임시파일 예산과 구분한다.

8행의 다른 실제 ABI/closure 결합과 7행 source 영향, 9행 일반 입력/out 표시명·
정보/참조/외부 타입 실행 통합은 기존 잔여다. 고급 핀의 공통 값/참조 타입 대 정보별
C# 타입 생성 선택은 답변 대기이며 임의 확정하지 않았다. 신원/그룹 backend·종류
CLR/사용 중 삭제 정책과 M11/M12/M4의 완료 범위를 섞거나 새 조합별 요구를 추가하지 않는다.

검증은 Linux native 엔진·Chromium·격리 생성 fixture다. 교차 패키지는 실제 Windows/
WebView2 실행이 아니다. 실제 모바일·물리 IME/GPU/audio·사용자 프로젝트·전체 UI·
Space/Library 전달과 모든 구 reader 교환은 미검증이다. 초기 빈 화면 원인과 과거
Save 클릭 요청 미발행의 간헐 원인도 이번 통과로 해결됐다고 보지 않는다.
