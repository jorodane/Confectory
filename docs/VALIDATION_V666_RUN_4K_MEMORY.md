# 명시4K 조각 디코딩 메모리 검증

동결 `52082e6bc065ae2155606946842ade4b7e044020`의 유효86단계(신규64·동일 입력 재사용22)을 통과했다. LF 신규16/유효38, CRLF 신규35/유효35,
나머지 {"run": 1, "windows": 2, "packaged": 4, "restored": 5, "package": 1}다.
개발/계측 결과는 최종 단계에 재사용하지 않았다. 제품·검사 입력이 같은 이전 source의 직접 통과22개만 별도 증명으로 재사용했다. [지원/호환 경계](V8_RUN_4K_MEMORY.md)를 따른다.

| 검사 | 실제 범위 |
|---|---|
| 독립 source | no-hardlinks LF/CRLF Git/HOME/NuGet·빈 engine cache·Release/MCP/Linux engine; 제품 변경1개와 원본 reference/기존 reader/공개 계약/UI/저장 원본 대조 |
| 실제 전송 | 고엔트로피4096×2160·35,389,440B/45조각·전체SHA, 인증/소유/순서/크기/누락/혼합/잘못된 alphabet·canonical·시간 예산 거절. 잘못된 세대2–11/13 각1번, 기존 신뢰값 보존과 정상12/14 read-only 복구 |
| tail | LF/CRLF 각각512×514·512×515의 실제 두 조각. 같은 raw로 decode되는 미사용 bit가0이 아닌 마지막 sextet을 거절. 신뢰1 보존/정상3 복구·invoke 불변. 생성본514/전체 복원본515 재검사 |
| UI/수명 | 원본15개 해상도와 실제4K/portrait 픽셀, preset 저장/재시작, 초과 입력 보존, accepted 응답 유실/read-only 재확인/늦은 입력, SHA 손상·닫는 중 늦은 조각·새 view/cold 분리. 생성한 프로젝트만 사용 |
| 회귀/구 reader | 4K/QHD/FHD/HD/기본/native 제어/heartbeat/소유/오디오·auto/bounds/rate·preset CAS·고정 메뉴. 이전 QHD JavaScript reader의4K 목록 거절/작은 목록 호환을 실제 실행 |
| 패키지 | 새 Windows 교차 패키지 구조/변조/의존성 거절 및 Linux engine 실제 실행, 생성본 UI/parts/wide/tail. CRC·전체파일SHA·파일/디렉터리 mode의 전체 복원 후 lifecycle/parts/wide/tail; 실패 수명과 소유 임시 정리 |

## 실제 할당 측정과 실패 증거

같은 독립 checkout/SDK/실제 native pipe/고정 입력 SHA
`87e3888a5133d006f422ce413117ea91a59a6228047fcf2231b8d32159e1042a`에서 개선 전후 각각 정상 세대1/12/14의3개 표본을 측정했다.
전체 native read의 프로세스 전체 GC 누적 할당 차이를 진단 JSON 파싱 전에 계산했다.
중앙값 988,323,112B →329,795,520B,
약 66.63% 감소다. concurrent 할당을 포함하고 peak/retained/FPS 측정은 아니다.
최대 raw 버퍼35,389,440B/char 버퍼1,048,580문자와 bounded packet/metadata 처리를 사용한다.
거대한 전체 UTF16 join/정규화/재인코딩을4K parts에서 없앴으며 작은 packet과0–3 profile은
기존 경로다. source/계측 SHA·원본/수정 .csbody·실행 스크립트/입력/로그는 개발 증거 ZIP에 있다.
계측은 제품/Git에 게시하지 않았다.

개발16시도 중15통과와 UI normal1회 실패를 모두 보존했다. 실패는 cold Play가 보인 직후
fixture가 이전 실행 lease의 cached row를 읽었다. 보존 traffic에는 이후 새 lease/idle/빈 handle가
도착했고 실제 preset/표시 저장도 정상이다. 제품은 변경하지 않고 새 native lease/idle/빈 handle/
lastCommand 없음 확인을 기다리게 했다. 수정 normal/lifecycle/parts가 모두 통과했고 최종86개는
이 수정된 검사와 최종 보관/복원으로 검증했다. 실패 source SHA·실패 HTML/스크린샷/traffic/프로필을 남겼다.
초기 빈 #app의 원인·수정으로 해석하지 않는다.

첫 최종 record `/workspace/artifacts/v536-verification-managed/runs/709171ce0fb6498e8746ae54b5212efc.json`는33개 통과 뒤 LF HD compatibility UI의 같은 cached
cold row 검사에서 실패했다. 그 증거에도 이후 새 native lease/idle/빈 handle가 도착했고,
제품은 그대로 유지한 채 HD normal/parts/lifecycle도 새 lease 관측을 기다리게 보완했다.
첫 실패 원문/traffic/프로필·스크린샷은 보존했다. 이전 단일 source01b63a75의 직접 통과22개만
전체 manifest/CRC/SHA와 정확한 SDK/NuGet/config/RID·LF no-hardlinks checkout·probe/harness
SHA·허용된 파일 변경·정규화한 동일 명령을 대조해 재사용했다. 이전 재사용 결과를 중복 세지
않는다. 변경/실패 HD, 모든 checkout/build/engine/boundary/예제·CRLF 전체·패키지/복원은
신규다. changed SDK/changed product 거절도 실제 실행했고 각 reused.json 및 source-bound
proof에 근거를 남겼다. 기본 reuse flag 없는 전체 신규 경로도 유지한다.

이번 신규 정상 관측의 bounded read-only 복구 기록은4개이며 최대
6회다. 실제 invoke 불변과 payload를 봉인했다. 재사용22개의 관측 trace는 첫 봉인본에 보관하며 이 신규 집계와 합치지 않는다.
이전 원인 미확정 transient/cold/빈 화면을 해결했다고 주장하지 않는다.

구 QHD reader의4K 목록 전체 거절은 기존 호환 경계다. version1/ID/CAS·저장 bytes를 바꾸거나
비우기/축소/자동 이행하지 않았다. 구 native 엔진은 이번에 재실행하지 않았다. 기존 producer와
공개/override 계약·권한/원본·ReviewConfirm/최종CAS·레이아웃은 그대로다.

## 보관과 자원

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/d40425cdd81143539ed5a48ce460907e.json`
- 증거: `/workspace/artifacts/v536-verification-managed/runs/d40425cdd81143539ed5a48ce460907e.zip` (2,459,616B), SHA256 `b40716a56fc1a531dfc3b37dbde2c00616aa13d6ff8e50b29113c319c1a4cab8`
- 개발/계측 record: `/workspace/artifacts/v536-verification-managed/runs/47d35dcf979f48b7a6a438e62c925b29.json`, 증거 SHA256 `aea8345f1d6e73e9f853b3fb630099c7d0a5d97dbce8f2c62ff3f023e1a6e18e`
- 승격 전 index는 최종 증거 내부 package-index-before.json, 승격 후 index는 `/workspace/artifacts/v536-verification-managed/runs/d40425cdd81143539ed5a48ce460907e.closing-index.json`, SHA256 `f5d3f801b6d3e5667751f73a7dda3667be36c9fbb0f1e5b53d40e04a75b61a55`

| 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | 52082e6bc065ae2155606946842ade4b7e044020 | a9d008d7c74f0d881e7a234a6a3ce72aece8fa54373304df2e499b6d8720b8a7 | 53,835,768 | 2726/158 |
| rollback | c661ae0457b269ca9c061ceb52f9d88e016f112b | 0dd5b1391ba72665985e8f99f68c65fd4f79a66e43cdc422d7c478e30a46327c | 53,834,452 | 2726/158 |

완전 복원·증거 봉인 뒤 원자 승격해 직전c661ae04를 rollback으로 유지한다. 승인된 관리2세대
수명으로만 이전 rollback a50c4103 `b41b452b8bb9a44f04a069d4428434de5e6f92c58c6e6b2961526a374ceebf64`를 퇴역했다. 다른 기존 산출물/원본·로그·
프로필·SDK/Git·사용자 자료는 추가 삭제하지 않았다. 개발/최종 root는 자식 종료·소유·지속 증거
검증 후 정리됐고 두 root 모두 없다. 전체파일 SHA/CRC/mode를 승격 후 다시 확인했다.

계획은 새 archive56MiB+증거192MiB+코드4MiB+별도 disk 안전64MiB로
331,350,016B를 요구했고 RAM 작업공간3GiB·추가 메모리9GiB+안전1GiB다.
단위 시작/종료 disk 여유29,175,324,672/29,160,845,312B·관측 순증가14,479,360B,
최종 시작/종료29,165,727,744/29,160,845,312B다. 신규 단계 표본 최저 disk29,165,629,440B,
최종 신규 cgroup 표본 peak8,853,639,168B, 개발/첫 실패 최종을 포함한 단위 전체 표본 peak8,853,639,168B·limit 여유8,326,230,016B다. 컴파일러/임시 RAM을
포함한 수치이며 decoder 단독 peak·절대 극값·향후 순증가 보장은 아니다.

큰 DOCX/XLSX 편집/백업/개인 초안 전송, 보관 범위와 실제 신원/권한 backend·종류 C#표현/
사용중삭제 대응, 현재4096/8,847,360px 예산 밖 custom은 기존 별도 잔여다. text editor 원본
1MiB 제한·정상 소유 거절·선택적 조합을 새 요구로 늘리지 않는다. M11/M12/M4는 구체적 회귀
없이 다시 열지 않는다. 실제 Windows/WebView2·모바일·DPI/IME·GPU/모니터/물리오디오·Office 앱·
전체 UI·Space/Library 전달은 미실행/미완료이며 이번 Linux 실행/교차 생성과 구분한다.
