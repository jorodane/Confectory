# 큰 텍스트 prefix 최종 검증

제품 구현 `7de5fb6a`, 최종 코드/검사 동결 `9588568e11a050e655b421aaee9832e781862414` 기준 **45단계 전부 신규 통과**.
개발 실행·기준 게시본 복구·선행 실패는 이 수에 합산하거나 재사용하지 않는다.
[지원 경계와 원본 근거](V7_RESOURCE_TEXT_PREFIX.md)를 따른다. 원본 v666의 첫1MiB만 표시하며
전체 큰 텍스트 전송이나 편집으로 확대하지 않는다.

| 검사 | 실제 확인 범위 |
|---|---|
| 독립 빌드/범위 | no-hardlinks LF/CRLF Git·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine, 실제 일곱 제품 파일·canonical asset SHA·관찰 endpoint 분리·세 suite 분기, public/override/권한/레이아웃/저장 문법 불변 |
| native 전체/최종 읽기 | 실제 생산 몸체로4MiB 전체SHA와 정확한1MiB prefix·prefixSHA·RPC 상한, 표시 밖 tail 변조·ID/전체hash/세대/revision/추가 필드 거절, 쓰기0회. manifest·identity·store·layout·파일/폴더명·설명·삭제이력·내용 sidecar의 최종 읽기 변경9곳을 통제 주입 |
| 호환/정체성 | 실제6a82895b reader의 기존 metadata-only 결과 동일성, 이름 변경 후 stale revision과 같은ID/hash 재가져오기 후 stale generation 거절, 기존1MiB 편집/백업 제한 유지 |
| 실제 엔진/Chromium | 생성한 실제 File 선택,4MiB 이하 합계의 큰 UTF8/BOM/CRLF·1MiB 경계에서 잘린 문자·UTF16LE의 정확한 표시 텍스트SHA, literal HTML·외부 요청 없음, binary 거절·readonly·legacy capability 없음·손상 prefix 거절/명시 재시도 |
| 수명/입력/소유 | header 전 readonly·prefix 대기 중 늦은 설명 보존/명시 저장, 오래된 표시revision 거절, 닫기/같은키 재열기의 늦은 실패, Home/cold/같은namespace 다른 프로젝트 왕복, durable presentation에 prefix payload·미결 읽기 없음 |
| 관련 회귀/납품 구조 | 작은 text preview·설명·내용 저장/복원/실패·응답유실/충돌·새입력 보존, 큰 사본 가져오기/편집거절·SVG·전송/권한 경계. 새 Windows 교차 패키지의 실제 Linux 엔진 UI, ZIP 전체SHA/CRC/파일·디렉터리mode/전체 복원본 UI와 실패 수명관리 |

native 경쟁은 실제 OS 파일/생산 몸체에 대한 통제 주입이며 외부 사용자 동시 실행으로 표현하지 않는다.
브라우저는 표시 prefix만 SHA 검증하고 전체 파일 SHA는 native가 확인한다. 개인 파일이나 외부 자료는
업로드하지 않았다. Core/targets·원본C#·celem/cpack·공개 override 계약과 Review→Confirm/쓰기CAS는
변경하지 않았다. 기존 M11/M12/M4를 미구현으로 다시 넣지 않는다.

## 복구와 선행 실패

같은 환경 연결 뒤 기존 작업 폴더는 초기 `work`/`b5ea38c3d7eec3eb20f170e68f0f4215b86b2aee`
상태였고 이전 미커밋 변경·SDK10·검증/패키지 경로를 찾지 못했다. 복구됐다고 주장하지 않는다.
그 폴더를 수정하지 않고 별도 `/workspace/Confectory-recovery-6a82895b`에 원격 게시본6a82895b를
받아 재구현했다. 공식10.0.401 SDK는 release metadata SHA512 대조 뒤 새 경로에 설치했고
기존 SDK8/setup 자료는 보존했다. 환경 생성/초기화/교체나 과거 자료 추가 삭제는 하지 않았다.

기준6a82895b의 복구 record `9a4524cdd08941729bb63d655a51a8b0`에서47단계가 통과한 뒤
작은 내용 편집의 CRLF cold 복구 검사가 실패했다. 앱/창은 존재했으나 읽기 오류와 명시 retry가
표시돼 저장결과 복구 버튼이 없었다. 최초 원인은 **미확정**이다. 이 실행의 실패 ZIP/SHA
`2b34f367e5962eb91fae94cbfc0bbc0d63dc66f5a462f5b62bb4b06f5f596f5e`를 보존했다.

기준 재생성 record `b36e04c12553499080a5054e137fa538`은 같은source/SDK/seed와 앞선47개
통과 결과의 봉인SHA를 확인한 뒤, 출력 재생성에 필요한 빌드와 실패 cold 경로의 읽기 응답 진단·
나머지 설명/가져오기·생성/복원 패키지까지15단계를 새로 통과했다. fixture에 관찰 로그만 더했고
제품을 고치거나 실패를 통과로 바꾸지 않았다. 진단 재실행과 이번 최종 관련 회귀가 통과해도
최초 실패 원인을 해결했다고 간주하지 않는다. 초기 빈 #app도 별도의 원인 미확정 잔여다.
기준 증거 ZIP SHA `5ba280b223fc44eac6807f72413c1fdf34b861f6f65571e1e169f03180d7a1f0`.

개발 record `838400ef48a445c799a59d5e29fd9673`의 첫 native race 검사는 주입용 내용 폴더가
없어 실패했다. fixture parent 생성만 고친 후9곳 전부 거절을 확인했다. 개발 UI normal/lifecycle는
통과했지만 최종 수에 포함하지 않는다. 마지막 header 사전검증/부분UTF8 경계는 이번 동결에서
새로 검사했다. private 작업공간 재개 driver의 worker_script 누락과 게시본 보관 대기 시간 초과는
검사 시작 전의 제어 문제였으며 제품 통과 증거로 사용하지 않았다. 보존된 이전 실행을 중복 게시하지 않았다.

## 지속 보관

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/af3beb128d8c473eb9d95efc943d58bb.json`
- 증거 ZIP SHA256: `3ee92b00d4e22813b416b1c7fd7fdc3641f3f5d2e3382a656206cb1ba9a3b834` (11,906,491B)
- index: `/workspace/artifacts/v536-verification-managed/packages/index.json`

| 보관본 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `9588568e11a050e655b421aaee9832e781862414` | `8f310ebfcddc4ad78f1d505bcd11521ba452d63059eff600dea2c42adeb1efbf` | 53,819,209 | 2711/158 |
| rollback | `6a82895b84c614cfe6710c564aae2d356c8d4603` | `19e7041d20d332e3f06f9c7317dbfa73774749a62b314e9e2c4b8fde8400a84f` | 53,821,961 | 2710/158 |

이 두 보관본은 현재 환경에서 새로 만든 것이다. 이전 환경의4ea7604/d23d632 보관 ZIP을 찾았거나
복구했다고 표현하지 않는다. 새 정상본의 전체 복원 검증과 증거 영속 보관 후 원자 승격했으며
각 실행이 생성한 임시 root·캐시·checkout만 자식 종료/소유권 검증 후 정리했다. 기존 과거 자료·
로그/프로필·원본·SDK/Git·사용자 자료는 추가 삭제하지 않았다. Git에는 코드·문서·검사만 게시한다.
문서 마감 뒤에도 패키지 source와 runtime/검사 bytes가 같은지 확인한다.

최종 preflight의 추가 디스크 예산 264,241,152B는 새 archive56MiB·
증거128MiB·코드4MiB와 **별도 안전64MiB**다. 임시RAM3GiB·추가 메모리7GiB+안전1GiB를
유지했고 안전 기준을 낮추지 않았다. 최종 실행 전/후 여유는 30,584,115,200/30,516,486,144B,
이 실행의 순증가는 67,629,056B다. 새 두 세대 보관의 bootstrap 증가를 정상 이후 단위의
순증가 보장으로 쓰지 않는다. SDK/별도 Git/기준 복구 준비 비용은 이 최종 실행 증감과 구분한다.
단계별 표본 최저 디스크 30,584,020,992B·관측 cgroup peak 6,025,519,104B는 모든 압축/승격 순간의
절대 최저/최대 측정이 아니다.

4MiB 초과·총 보관량 확대와 다른 rich 형식, 큰 내용 편집/백업, 실제 신원·멤버/권한 backend·공유,
FHD/4K/GPU/물리 출력·장치 등은 기존 미지원/미구현 경계다. 가능한 type/context 조합을 새 필수
항목으로 늘리지 않는다. 실제Windows/WebView2·모바일·DPI/IME·전체UI·Space/Library 전달은
실행하지 않았다. 환경 복구와 이번 한 단위의 완료를 전체 v666 완료로 표현하지 않는다.
