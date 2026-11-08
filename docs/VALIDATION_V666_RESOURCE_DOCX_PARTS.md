# 큰 DOCX 편집·복원·개인 초안 최종 검증

동결 `48242375886376cf5d583d58f6cf1689724d0faa`의 신규 62단계를 통과했다. LF 27, CRLF 26,
나머지는 {"resource": 1, "windows": 2, "packaged": 2, "restored": 3, "package": 1}다.
최종 검사에 개발/과거 검사를 재사용하지 않았다(재사용0). [지원·원본·호환 경계](V7_RESOURCE_DOCX_PARTS.md)를 따른다.

| 검사 | 실제 범위 |
|---|---|
| 독립 source | no-hardlinks LF/CRLF Git·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine. 고정 ZIP/hash·정확10개 제품 변경·canonical bundle·불변 core/celem/cpack/원본 DOM/CSS/공개 계약 대조 |
| DOCX/ZIP | 실제 정상4MiB ZIP source/output, 기본1MiB·다른 Office 상한 유지. CRC·위험 entry/서명/매크로·보호된 문단·Word DOM/기존 XLSX DOM 회귀 |
| native 경계 | 생성4MiB 불투명 PK-signature bytes의 source/current/backup·private 조각/전체SHA·7MiB 전용 upload 최악 JSON escape. 이 fixture 자체는 유효 Office ZIP 증거가 아님 |
| 저장/보호 | import generation·project/source/private 최종CAS race·peer bytes·잘못된 snapshot/receipt·구 reader 거절·기본1MiB/import6M/RPC2MiB 유지. 수정 원본/backup은 명시 Save/복원만 변경 |
| 실제 UI | 유효 약2MiB DOCX 문단/표 편집·보호 거절·Save/복원/복원취소·cancel/닫기·Worker 늦은 결과·중복 요청·실패/충돌·새 입력·다른 프로젝트·cold 재시작 |
| 유실/손상 | private commit 응답 유실 뒤 정확한 read-only receipt, peer/손상 거절·사용자 재확인. 문서 Save 유실 후 명시 같은 command로 확인해 backup 중복 변경 방지. 늦은 조각은 닫힌/새 창에 반영하지 않음 |
| 회귀 | 기존 작은 DOCX/XLSX 편집·초안/미리보기, text 저장, 큰 Office preview·provider·WebUI scope/cancel/dispose. 최종 두 checkout에서 각각 실행 |
| 납품/수명 | 새 Windows 교차 패키지 구조/무결성/의존성 거절, 생성본 Linux engine 실제 UI normal/transport. CRC·전체파일SHA·파일/디렉터리 mode 전체 복원 후 lifecycle/transport·실패 수명/소유 임시 정리 |

## 개발 실패와 복구 근거

개발 managed37시도 중32통과·5실패를 전부 보존했다. 별도 Node2시도 중1통과/1실패도 남겼다.
개발에서 수정한 제품10개는 동결 제품과 일치하며 최종 전부 신규 검사로 재확인했다.

- 첫 cold private 조각은 실제 busy가3번 반환돼 기존 짧은 읽기 대기를 소진했다. 같은 기준의 busy에만20회/50ms bounded read-only 대기와 명시 재확인 UI를 연결했다. 프로젝트/창/원본 검증은 유지한다.
- 별도 공개 cold 미리보기 실패1건은 당시 payload가 없어 원인 미확정이다. 이후 같은 보존 입력의 진단은 통과했다. 입력/원본 불변을 확인하는 제한된 명시 read-only 재확인 흐름을 검사했으며, 원인이 해결됐다고 하지 않는다.
- 첫 transport 결합 assertion은 세부 조건의 근거가 없어 정확한 원인 미확정이다. private flush가 끝난 입력으로 확인하고 hash/손상 조건을 개별 기록하도록 검사만 보완한 뒤 같은 제품으로 통과했다. 제품의 입력 유실이나 flush 원인 해결로 단정하지 않는다.
- Node XLSX 경로1건은 존재하지 않는 mjs를 지정한 검사 문제였다. 실제 XLSX DOM 검사로 교정했다. Office native 비교1건은 새 optional cap만 명시적으로 분리하고 이전 필드 일치 검사를 유지해 통과했다.
- 별도 Node XML assertion은 같은149bytes의 ArrayBuffer/Uint8Array 표현 비교였다. 입력/실패/교정 로그를 보존하고 비교만 고쳤다.

로그·스크린샷·프로필·입력·실패와 최종 source SHA를 보관했다. compiler/cache 출력만 재생성 가능 목록과 전체 SHA를 남기고 해당 실행 소유 임시 root 수명으로 정리했다.
이전 초기 빈 #app이나 역사적 transient/cold 오류의 원인·해결로 소급하지 않는다.
최종 로그에서 cold 공개 읽기의 명시 read-only 재확인은 1개 검사에 기록됐다.
각 fixture는 그동안 sidecar bytes와 문서 Save 호출0을 확인하며, 최종 근거 경로/문구를 closing-facts.json에 남긴다.

## 호환성과 남은 범위

원래1MiB save-content·작은 v1 codec은 유지된다. 새 cap을 가진 DOCX만4MiB 편집을 사용하고,
내용 sidecar version2/format docx-v1과 private version2/docx-parts-v1을 명시한다. 기존 slot에
새 version을 두므로 구 reader가 거절한다. 과거본에서 새 자료가 사라진 것처럼 성공시키거나
자동 축소·비우기·이행하지 않는다. 실제 baseline3cf native bodies를 fixture에서 실행해 새
content/private 거절과 두 사본 보존을 확인했다. 과거 패키지를 실제 기기에서 실행한 검사는 아니다.
새 reader의 재개·전체 복원과 rollback ZIP 자체의 복원 가능성을 구 parser 호환과 구분한다.

현재64MiB/current+backup128MiB 전체 상한, immutable import4MiB·64개와 기존 권한/ProjectContext,
Review/Confirm 및 최종 원자 CAS를 유지한다. UI 표시/receipt는 새 접근 권한을 부여하지 않는다.
약2MiB UI의 미참조 고엔트로피 media와4MiB 경계 검사를 복잡한 Word 전체 서식/성능의 증거로 확대하지 않는다.
큰 XLSX 편집·4MiB 초과/보관량·신원/권한 backend·종류 C#표현/사용중삭제 대응·현재 예산 밖
custom Run 출력은 기존 별도 잔여다. 정상 거절과 선택적 조합은 새 필수 요구로 늘리지 않는다.
M11/M12/M4는 구체적 회귀 없이 다시 열지 않는다.

실제 Windows/WebView2·모바일·DPI/IME·Word/Office 앱·GPU/물리 오디오·전체 UI·Space/Library는
미실행/미완료다. Linux engine/Chromium 자동화와 Windows 교차 생성/전체 복원만 이번에 검사했다.

## 보관과 자원

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/15e7a9830c9d4e1aa8693e6184cc4974.json`
- 최종 증거: `/workspace/artifacts/v536-verification-managed/runs/15e7a9830c9d4e1aa8693e6184cc4974.zip` (462,344,800B), SHA256 `b8296a4fd63badcb199f23af66776de2529886cd6ffe8434e3e1a69afe20eeac`
- 개발 record: `/workspace/artifacts/v536-verification-managed/runs/422731cd846f45aaae77df2d7b763274.json`; 증거 466,736,854B, SHA256 `cb98a1505e615f32d85a7e1b357b35f4ef0cc8cb052a69359d55d6244f5f726e`
- 승격 전 index: 최종 증거 내부 package-index-before.json
- 승격 후 index: `/workspace/artifacts/v536-verification-managed/runs/15e7a9830c9d4e1aa8693e6184cc4974.closing-index.json`, SHA256 `d520c2b01ed1fb57caea27d5af63f2a25b6851532153283f206d0385a397401a`

| 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | 48242375886376cf5d583d58f6cf1689724d0faa | 1d7280076a4a4959a898925d842e7d5d1f2226e79534dc7dbc2665df0163a9ca | 53,841,952 | 2727/158 |
| rollback | 52082e6bc065ae2155606946842ade4b7e044020 | a9d008d7c74f0d881e7a234a6a3ce72aece8fa54373304df2e499b6d8720b8a7 | 53,835,768 | 2726/158 |

전체 복원·증거 봉인 뒤 원자 승격했다. 직전52082e6b를 rollback으로 유지하며 승인된 관리2세대
수명으로만 이전 rollback c661ae04 `0dd5b1391ba72665985e8f99f68c65fd4f79a66e43cdc422d7c478e30a46327c`를 퇴역했다. 다른 기존 자료/원본/로그/
프로필/SDK/Git는 삭제하지 않았다. 개발/최종 자식 종료와 소유·지속 증거 확인 후 두 임시 root를 정리했다.

개발 증거는 최초384MiB 예상보다 큰 약445.11MiB였다.
자료를 삭제하거나 안전 여유를 낮추지 않고 최종 증거 예산을768MiB로 상향했다. 최종 실제
증거는440.93MiB다. 새 패키지56MiB+증거768MiB+코드4MiB+별도
disk 안전64MiB = 935,329,792B를 최종 시작에 확인했다. 개발 비용과 별개다.
RAM 작업공간4GiB+별도512MiB, 추가 메모리9GiB+안전1GiB를 계획했다.

단위 시작/현재 disk 여유 29,160,701,952/28,226,531,328B, 관측 순증가 934,170,624B다.
최종 시작 28,691,623,936B, 최종 단계 표본 최저 28,691,521,536B다.
최종 신규 cgroup 표본 peak 11,706,535,936B, 개발을 포함한 managed 단계 표본 peak 11,706,535,936B,
limit 17,179,869,184B 대비 여유 5,473,333,248B다. tmpfs/컴파일러/
캐시를 포함하며 제품 단독 peak·절대 극값·향후 단위별 순증가 보장은 아니다.
