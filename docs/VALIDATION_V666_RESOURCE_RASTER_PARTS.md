# 큰 PNG/JPEG 조각 관찰 검증

동결 `a91bd900a22256647351810e8e6868a83e9540d2` 기준 **신규61단계·재사용0**을 통과했다.
[원본 요구/지원·호환 경계](V7_RESOURCE_RASTER_PARTS.md)에 따라 이미 보관 가능한1MiB 초과–4MiB 이하
PNG/JPEG만 원래 contain 패널에 연결한다. 저장/전역RPC·업로드 상한이나 픽셀·lease 예산은
늘리지 않는다. 원본C#·공개/override 계약·권한·Review→Confirm·최종 쓰기CAS는 보존한다.

| 검사 | 확인한 실제 경계 |
|---|---|
| 독립 빌드·범위 | no-hardlinks LF/CRLF Git·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine, 아홉 제품 파일/canonical asset SHA·관찰 전용 endpoint·세 검증 분기. Layout의 모든 writer suffix와 Request/Core/targets·원래 renderer/레이아웃·텍스트 prefix byte 불변 |
| native 전체/최종 읽기 | 실제 제품 코드로4MiB 네 조각/전체SHA·offset/length·응답1.5MB 미만, legacy73f5f63e read 결과(선택 imagePreview 제외) 동일성·구 reader의 새op 거절, ID/hash/generation/revision/part/type/extra path 거절. 표시 밖 tail 변조와 최종 의존성9곳의 통제 경합에서 쓰기0회/원래 요청 보존 |
| 조립/디코드 예산 | 26개 malformed/stale/tampered 거절, 마지막 짧은 조각·혼합세대·조각SHA가 맞아도 틀린 전체SHA 거절, 순서/offset/길이·canonical base64. retirement 뒤 후속 요청 없음, busy만 최대3회 동일 basis 재시도. PNG/JPEG encoded4MiB/초과 거절과 기존16MP/한 변16384·합계33MP/다른 형식1MiB 그대로 |
| 실제 File/픽셀 | 생성한 >1MiB PNG와 JPEG의 실제 File 사본→native 관찰→원래 img. PNG 전체RGBA SHA 일치, JPEG 자연 크기/표본RGBA(Pillow 기준 각RGB 오차3 이하), contain·readonly·내용 편집 없음. 정확4MiB 유효 PNG가 네 조각 뒤 원래 전체 픽셀로 표시됨 |
| 중단/손상/입력 | malformed capability·변조/혼합 later part·whole tail 변조·과도한 dimensions는 decoder/URL 전 거절 또는 명시 retry. 마지막 조각/전체SHA 전 URL0, 기다리는 새 설명을 덮지 않고 명시 저장. Home·같은키 close/open의 늦은 응답·확인 삭제 후 후속 part 없음·cold·동일namespace 다른 프로젝트 왕복·생성/해제 URL 균형 |
| 관련 회귀/패키지 | 작은 PNG/JPEG/progressive/EXIF·URL/lease, 각 기존 WebP/BMP/GIF/AVIF 구조/예산, 실제 SVG/GIF·큰 import/내용 저장·설명/텍스트 prefix. 초안/미확정 읽기의 첫 busy 통제 주입과 같은 목표 제한 재시도, write failure/응답 유실·cold·프로젝트 왕복 복구. 새 Windows 교차 패키지의 실제 Linux 엔진 UI, 전체 ZIP CRC/SHA/파일·디렉터리mode 복원본 UI와 실패 수명관리 |

native race는 생산 몸체/실제 OS 파일의 통제 주입이며 외부 사용자 동시 실행으로 표현하지 않는다.
signature/metadata reader는 완전한 codec/파일 인증기가 아니다. 실제 decoder 실패가 남을 수
있으며 원래 사본을 바꾸지 않는다. 브라우저는 모든 조각과 전체SHA를 확인한 뒤 decoder/Blob을
만든다. 개인 파일/외부 이미지·URL이나 실계정·AI 자격증명/유료호출은 사용하지 않았다.
현재 환경 연결/정책 적용, SDK10.0.401과 seed·최종 소스/패키지 출처를 확인했다.
기존 `/workspace/Confectory`의 work/b5ea38c 상태와 main은 변경하지 않는다.

## 개발/선행 실패 구분

개발 record `/workspace/artifacts/v536-verification-managed/runs/1a111489713245d99a54d66968ccc329.json`
에서 Node 검사 후 새 C# fixture의 loop `data`와 뒤의 local `data`가 충돌해 compile이 실패했다.
fixture 이름을 `partData`로만 바꾸고 네 조각/전체 SHA·9개 최종 읽기 거절을 통과했다. 제품
수정으로 실패를 숨기지 않는다. 개발 UI normal/lifecycle와 추가 maximum 검사는 통과했지만
이번 최종 수에 포함하거나 재사용하지 않았다. 생성된 4MiB 실제 PNG 스크린샷도 직접 확인했다.

이번 최초 최종 실행 record58a99f1ccf724d70a2356722d7c145a2의 신규56단계는
통과했지만 `restored-resource-content`가 실패해 패키지를 승격하지 않았다. 프로젝트 왕복에서
`readResourceContentDraft`의 실제 `busy` 응답을 확인했고, 생성한 개인 초안10문자는 증거에
그대로 보존돼 있었다. 원본 사본의 손상이나 초기 빈 #app와 같은 문제로 단정하지 않는다.
동결1a2dd917의 새 단위 검사로 첫 busy 뒤 중단을 재현하고, 같은 초안/미확정 요청 읽기에만
최대3회/50ms 재시도를 더했다. 재시도 전후 활성 창/current project를 확인하며 다른 오류와
owner 불일치는 거절한다. mutation 재실행·자동 저장/rebase·저장 정책은 바꾸지 않았다.
두 번째 실행05629679의 신규52단계 통과 뒤 내용 lifecycle은 제한된3회 busy를 모두
소진해 기존 ‘다시 확인’이 남았다. native `Observation`의 비차단 execution admission과 실제
busy 응답을 대조했고, 자동 복원을 무한 기다린 검사와 구분했다. 제품 코드는 dd2d3800에서
추가로 바꾸지 않았으며, 검사만 마지막3회가 동일 endpoint/동일 project/id의 busy인지 확인한
후 기존 버튼을 한 번 누르도록 했다. 다른 실패에 일반 재시도를 하여 숨기지 않는다. 별도
페이지에서3회 busy를 통제 주입해 거절 상한과 명시 복구 전후 사본·개인 요청 bytes 불변을
강제로 검증했다. 두 실패 실행 모두 패키지 승격/게시 전에 중단됐고 증거를 보존했다.

최종 source LF lifecycle/CRLF normal와 전체 복원 lifecycle에서 각 페이지의 첫 해당 읽기를
busy로 통제 주입하여 같은 입력의 재관찰, 실제 원문/미확정 요청·새 입력/cold/다른 project
복구를 확인했다. 무한 busy 최대3회, 다른 오류1회, 대기/응답 후 retirement 거절은 Node로
확인했다. 이 통합 회귀는 그림 실패로 바꾸어 표현하지 않는다. 공유 content asset이 바뀌어
최종 독립 빌드/그림 회귀/패키지·복원까지 다시 실행했고, 실패 단계/개발 검사를 재사용하지 않았다.

이전 게시본의 초기 빈 #app 및 작은 내용의 cold 읽기 실패1회 원인은 **미확정**이다.
이번 관련 cold 회귀 통과를 최초 원인 해결로 간주하지 않는다. 환경 복구 당시 찾지 못한 과거
미커밋 변경/SDK·산출물은 재발견·복구됐다고 주장하지 않으며 [앞선 복구 기록](VALIDATION_V666_RESOURCE_TEXT_PREFIX.md)을 따른다.
M11/M12/M4의 의도된 소유/계약 제한과 현재 완료를 새 잔여로 늘리지 않는다.

## 보관과 실제 공간

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/4c1a6216433c475dbaaba2e47c89dddb.json`
- 증거 ZIP SHA256: `91cdc960e117c78ca27a5f71d5b5638bc8bcf8ca32b5770d8b33f88e2348ed4d` (44,942,547B)
- index: `/workspace/artifacts/v536-verification-managed/packages/index.json`

| 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `a91bd900a22256647351810e8e6868a83e9540d2` | `9f62d0b9a127729f1817a63a80ad732a9b22360be6eee6dd431a5317814f28e5` | 53,822,037 | 2712/158 |
| rollback | `9588568e11a050e655b421aaee9832e781862414` | `8f310ebfcddc4ad78f1d505bcd11521ba452d63059eff600dea2c42adeb1efbf` | 53,819,209 | 2711/158 |

새 전체 복원과 증거 영속 보관 후 기존 두 세대 절차로 원자 승격했다. 직전 정상9588568e를
rollback으로 유지하고, 관리 index의 더 오래된6a82895b 검증 패키지 `19e7041d20d332e3f06f9c7317dbfa73774749a62b314e9e2c4b8fde8400a84f`만
기존2세대 보관 수명으로 퇴역했다. 선행 실패58a99f1c의 봉인 증거 내 사전 index와 이번 승격 후 별도 동반 증거를 구분해 보존했다.
두 실패 실행은 packagePublication 없이 중단됐고, 이번 rollback entry는 선행 latest와 전체 동일하다.
승격 후 index 동반 증거: `/workspace/artifacts/v536-verification-managed/runs/4c1a6216433c475dbaaba2e47c89dddb.closing-index.json`, SHA256 `205f26b29cd6deaecb60caffa69ca9290749bad2893a89e81def86c5aa5af8eb`.
사전 index는 선행 봉인 ZIP, 승격 후 index는 별도 동반 증거에서 확인한다. 이 밖의 과거 원본·로그/프로필·
SDK/Git·개인/사용자 자료나 다른 산출물은 삭제하지 않았다. 각 실행이 직접 만든 임시 checkout/
독립 cache/생성본만 자식 종료·소유권을 확인해 정리했다. 코드·문서·검사만 Git에 게시한다.
문서 마감 뒤 runtime/검사/패키지 source bytes와 동결 코드의 동일성도 확인한다.

추가 디스크 예산 264,241,152B(archive56MiB·증거128MiB·코드4MiB·
**별도 안전64MiB**), RAM 작업공간3GiB·추가 메모리7GiB+안전1GiB를 유지했다.
최종 실행 전/후 여유는 30,410,268,672/30,362,705,920B, 순증가는 47,562,752B다.
개발·두 실패 증거까지 보존한 이번 전체 단위의 파일시스템 측정 시작/종료는
30,516,322,304/30,362,705,920B이며 차이는 153,616,384B다. 이 수치는 해당 경로별 실제 점유량과
동일하지 않고 다른 동시 파일시스템 활동도 포함할 수 있다.
단계 표본 최저 디스크 30,410,203,136B·관측 cgroup peak
5,656,125,440B는 모든 압축/승격 순간의 절대 최저/최대나
후속 단위의 고정 순증가 보장이 아니다. 큰 무작위 테스트 입력/traffic 증거를 버려 수치를 줄이지 않는다.

큰 WebP/BMP/GIF/AVIF/SVG·문서,4MiB 초과/총 보관량 확대·내용편집/백업 확대는 기존 잔여다.
멤버/공유는 실제 신원·권한 source/별도 팩 선행이며 실제 계정/접근권한 변경은 하지 않았다.
고급 타입/핀 표시명 정책은 임의로 결정하지 않는다. 실제Windows/WebView2·모바일·DPI/IME·
전체UI·FHD/4K/GPU/장치·Library/Space 전달은 이번 자동화/교차 생성·복원과 구분해 미완료로 남긴다.
