# Run 직접 입력8192축 최종 검증

동결 `b810acbc4eb4ed4b93b6cdc1576975027de50b37`의 유효102단계(신규91·동일 입력 재사용11)를 통과했다. 개발/진단 결과를 최종 검사로 세지 않았다.
신규 단계별 분포는 `{"run": 1, "lf": 33, "crlf": 39, "windows": 2, "packaged": 7, "restored": 8, "package": 1}`다. [원본 근거·지원/보호·호환 경계](V8_RUN_CUSTOM_AXIS.md)를 따른다.

| 검사 | 실제 범위 |
|---|---|
| 독립 source | no-hardlinks LF/CRLF Git·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine. 고정 ZIP/hash·정확 제품 변경과 canonical bundle·이전 profile/layout/소유/CAS 대조 |
| 직접 출력 | 새 명시 OpenCustom/profile5의8192×1080/1080×8192 실제 RGBA·전체 SHA·정확45조각/index44. axis8193/area 초과·전체8192²·낮은 profile·같은 runtime cap 변경 거절 |
| 불완전 출력 | 혼합 publisher/revision/cap·틀린 SHA·누락/과다/비정규 base64url·누적 조각 I/O 지연 거절. 이전 신뢰 revision 유지·후속 정상 frame을 읽기만으로 복구 |
| UI 수명 | 원본15개 메뉴 보존·직접 적용/실제 canvas·한 요청/명시 Step·등록/초과 입력 보존·CAS/충돌/쓰기 실패/명령 영수증·응답 유실 뒤 늦은 입력·손상 조각 숨김/RO 복구·전송 중 닫기/늦은 slice·cold 새 idle lease |
| 회귀 | 기존4K/QHD/FHD/HD/기본 cap·소유/동일 스레드/복사/원자 revision·tail canonical bits·고정 메뉴·자동 크기/등록/오디오/bounds/rate/heartbeat |
| 패키지 | 새 Windows 교차 생성/구조·변조/의존성 확인. Linux engine으로 생성본과 전체 CRC/SHA/파일·디렉터리 mode 복원본의 직접 출력/조각 수명/실패 수명 검증 |

## 개발 결과와 호환성

기준03e81fea의 실제 UI/4K producer에서는8192×1080 적용을 거절하고 입력과64×36 실제 출력을
보존하며 size 명령0을 확인했다. 개발 managed19시도 중18통과·1회는 검사 실행기에 없는
`--filter` 옵션을 전달해 제품 검사가 시작되지 않았다. positional filter와 `--require-runtime`으로
새 프로필·기존4K/QHD native 검사를 실행해 통과했다. 오류 로그/초기·최종 source/입력·프로필/
스크린샷을 보존했다. 제품 오류나 역사적 초기 빈 화면 원인으로 표현하지 않는다.

원본 app.js의240–8192 직접 입력에 근거하며 새8K 고정 메뉴를 만들지 않았다. 총8,847,360픽셀,
raw35,389,440B·45조각·packet1,400,000B·RPC2MiB·connect25ms/누적 I/O300ms를 보존한다.
관측 소유/cap과 size ACK를 확인하기 전 UI가 실행을 바꾸지 않는다. 새 profile5는 사용자가
명시 선택해야 하며 기존 C# 원문을 다시 쓰거나 기존 profile0–4를 자동 확대하지 않는다.
개인 등록 version1/ID/프로젝트CAS는 같지만 구4K JS reader는8192축 항목 포함 목록을
거절할 수 있다. 실제 구 reader의 새 목록 거절과 작은/4K 목록 수용을 확인했다. 자동 이행/
비우기/축소는 없으며 새 producer/native/UI 조합이 필요하다.

이는 Linux 네이티브 소프트웨어 출력과 Chromium UI 검증이다. 실제 Windows/WebView2·
모바일/DPI/IME·GPU/물리8192 모니터·물리 오디오·전체UI·Space/Library는 미실행/미완료다.
초기 빈 화면 원인은 미확정이다. 전체8192²/더 큰 총출력 예산·4MiB 초과/총자료보관·실제
신원/권한 backend·종류 C#표현/사용중삭제 정책은 별도 기존 잔여다. M11/M12/M4는 닫힌다.

## 첫 최종 실패·진단과 제한된 재사용

첫 최종 record `/workspace/artifacts/v536-verification-managed/runs/45583957e9db4152a40dd1437c68bc7b.json`의22개 통과 뒤 기존4K Stop 전
재조회20회가 surface-unavailable로 끝났다. 당시 소유 frame7/paused 상태를 유지했지만
예외 원인을 기록하지 않아 정확한 거절 원인은 미확정이다. 진단 record `/workspace/artifacts/v536-verification-managed/runs/1fdc5df948c149b7a2d6749f85171122.json`는
소유 checkout에 예외 기록만 추가해 제품/검사 조건을 유지한 동일4K API를3회 통과했다.
그 실행에서는 기존 누적300ms I/O의 OperationCanceledException과 RO 정상 복구를 관측했다.
첫 실패에 같은 원인이 있었다거나 초기 빈 화면을 해결했다고 단정하지 않는다.

제품/검사는562814b7과 동일하다. 첫 실행의 직접 통과한 LF projection9개·native2개만
전체 manifest/CRC/SHA·동일 SDK/NuGet/config/RID·독립 checkout·정규화 명령을 대조해 재사용했다.
변경 SDK/제품을 실제 거절한 guard와 단계별 reused.json/source-bound proof를 보존했다.
실패 API·모든 checkout/build/engine/boundary·CRLF·패키지/전체 복원은 신규다. 재사용 flag
없는 전체 신규 suite도 유지한다. 기존 실패/진단 증거와 입력·프로필/로그를 모두 남겼다.

## 지속 보관과 자원

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/a0f79a339a1540b5b9393ec7b6d4d102.json`
- 최종 증거: `/workspace/artifacts/v536-verification-managed/runs/a0f79a339a1540b5b9393ec7b6d4d102.zip` (4,191,854B), SHA256 `e902b2c402c264725958fb5ac1a156ed452783a901d4e24df967fbd96a29ccd9`
- 개발 record: `/workspace/artifacts/v536-verification-managed/runs/d48913c48d9f4149b813ea2c4e92bb3b.json`, 증거 775,906B, SHA256 `0ca1c7c988a2aef79aa778638a055a9adef914cceacfd4b70557026845ed74aa`
- 승격 전 index는 최종 증거 package-index-before.json, 후 index는 `/workspace/artifacts/v536-verification-managed/runs/a0f79a339a1540b5b9393ec7b6d4d102.closing-index.json`, SHA256 `e8bcd2c5761dc6b7d849fcbc33ac221de1e80819603d13d6f3dde35ae32cc6c8`

| 보관 | source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | b810acbc4eb4ed4b93b6cdc1576975027de50b37 | 9af4e9209cf60ac41b5a1c9fca775cf0aae9cecae7230f58369cf216d6b0eb0b | 53,843,851 |
| rollback | 141f0b17ac58db3cbe70add8fb6acae43d7b0738 | 922d2ba97a3f919742a99a4041441f332b1682b0b09a17ed40639584ea7a7aba | 53,841,591 |

전체 복원·증거 봉인 뒤 원자 승격했다. 직전141f0b17을 rollback으로 보존하고 승인된 관리
2세대 수명으로 이전 rollback48242375 `1d7280076a4a4959a898925d842e7d5d1f2226e79534dc7dbc2665df0163a9ca`만 퇴역했다. 다른 기존 자료/
원본/로그/프로필/SDK/Git는 삭제하지 않았다. 개발·진단·첫 실패/최종의 네 소유 임시 root는 자식 종료·소유 확인과 지속
증거 무결성 검증 뒤 정리됐다. 원본 checkout과 main은 별도 게시 시점에도 확인한다.

단위 계획은 개발384MiB+최종512MiB+추가 archive56MiB+코드4MiB+별도 disk 안전64MiB=
1,069,547,520B였고, 진단384MiB+두 번째 최종512MiB를 추가해2,009,071,616B 계획과 실제 여유를 재확인했다. 기존 자료 삭제나 안전 여유 축소는 없었다. 최종 시작 전 필요한 추가 disk 666,894,336B를 확인했다.
RAM 작업공간4GiB+별도512MiB·추가 메모리9GiB+안전1GiB를 유지한다. 실제 증거는 개발/
최종 0.74/4.00MiB다.

단위 시작/현재 disk 여유 26,726,473,728/26,715,660,288B, 관측 순증가 10,813,440B다. 최종 시작
26,722,521,088B·단계 표본 최저 26,722,381,824B, 최종 cgroup 표본 peak 11,527,680,000B·
개발·진단·첫 실패 포함 peak 11,527,680,000B로 limit 17,179,869,184B 대비 여유 5,652,189,184B다.
tmpfs/컴파일러/cache를 포함한 표본이며 제품 단독 peak·절대 극값·향후 증가량 보장은 아니다.
