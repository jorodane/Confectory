# 큰 XLSX 편집·복원·개인 초안 최종 검증

동결 `141f0b17ac58db3cbe70add8fb6acae43d7b0738`의 유효70단계(신규28·동일 입력 재사용42)를 통과했다. LF 신규9/유효30, CRLF 신규8/유효29이며
나머지 신규는 {"resource": 1, "windows": 2, "packaged": 3, "restored": 4, "package": 1}다. 개발 결과는 재사용하지 않았다.
[원본 근거·지원/보호·호환 경계](V7_RESOURCE_XLSX_PARTS.md)를 따른다. 제품8개 파일은879d5954와 동일하며141f0b17에는 관측 검사와 재사용 도구 보완만 추가됐다.

| 검사 | 실제 범위 |
|---|---|
| 독립 source | no-hardlinks LF/CRLF Git·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine. 고정 ZIP/hash·정확8개 제품 변경·canonical bundle·불변 core/공개/override 계약·DOM/CSS/원본·권한 경계 대조 |
| XLSX/ZIP/DOM | 명시4MiB source/output ZIP·기본1MiB/PPTX/ODT 거절. 숫자/boolean·앞자리0·literal 수식 모양 text·Unicode·시트 전환, 수식/병합/보호 거절, 기존 calcPr/다른 시트 수식 보존과 캐시 제거. 변경 외 압축 record/metadata·CRC/SHA 대조 |
| native | 정확4MiB 불투명 생성 PK bytes의 source/current/backup·조각/전체SHA·7MiB private 최악 escape·최종 source/private CAS·peer bytes·잘못된 generation/codec/format/target 거절. 이 fixture 자체는 유효 Office ZIP 증거가 아님 |
| 실제 UI | 현재 파서가 읽는 정상 ZIP/XML 약2MiB 생성 XLSX 셀 편집·Save/직전 복원/복원 취소·cancel/닫기·readonly 쓰기 실패·peer metadata 충돌·늦은 Worker/새 입력·다른 프로젝트·cold 재시작. 실제 Excel 앱/계산 실행은 아님 |
| 유실/손상 | private commit 유실 후 정확한 RO 영수증·손상/다른 소유/늦은 조각 거절. 문서 Save 유실은 같은 캡처 command로 명시 확인하며 backup을 두 번 바꾸지 않음. RO 관측은 source Save를 자동 호출하지 않음 |
| 회귀 | 큰 DOCX의 native/초안·유실 응답·손상·재시작과 작은 DOCX/XLSX·Office 미리보기·text 저장·provider·WebUI scope/cancel/dispose. 기존 동일 입력의 독립 checkout 관측과 새 생성/전체 복원본의 DOCX/XLSX 흐름을 구분 |
| 패키지/수명 | 새 Windows 교차 생성·구조/변조/의존성 검사와 Linux engine 실제 UI. 전체파일SHA/CRC/파일·디렉터리 mode 복원 후 lifecycle/transport·실패 수명/소유 임시 정리 |

## 실패와 호환 경계

개발 managed31시도 중30통과·1컴파일 실패를 전부 보존했다. 새 limits 대입에 object
initializer 쉼표를 잘못 사용한 구문을 수정했고, 같은 native 전체 경계·engine/UI가 통과했다.
수정 전 source·compiler 진단·입력/프로필/스크린샷·최종 source SHA를 남겼다.
검사 준비 중 잘못된 fixture 변수 assertion과 들여쓰기 없는 harness 추출도 실행 전에
잡아 교정했다. 잘못된 초안/AST 실패와 최종 정확3개 suite 분기를 보존했으며 잘못된
배치로 최종 suite를 실행하지 않았다. 최종 checkout/build/engine/boundary·변경/실패 XLSX UI·패키지/전체 복원은 신규다.

기본1MiB/v1 XLSX·기존 DOCX bytes/codec·import6,000,000B/RPC2MiB·공통 원자 snapshot16MiB와
전체 current64MiB/두 사본128MiB를 유지한다. 큰 XLSX는 content version2/format xlsx-v1,
private version2/xlsx-parts-v1을 명시한다. 이전98aa native bodies를 fixture에서 실제 실행해
새 형식 거절과 원본/두 사본 보존을 확인했다. 구 packaged engine의 실제 기기 실행은 하지 않았다.
rollback ZIP 복원 가능성과 새 데이터의 구 parser 호환은 구분하며 자동 변환/축소/비우기는 없다.

XLSX UI는 미참조 고엔트로피 media를 포함한 유효 약2MiB 생성 workbook이다. ZIP module4MiB,
native 불투명4MiB 경계를 복잡한 실제 Excel 문서 전체 호환·속도 증거로 확대하지 않는다.
수식 계산은 원본 프로그램에 재계산을 요청하는 기존 계약이며 새로운 계산 엔진이 아니다.
최종 cold 공개 읽기의 RO 재확인 로그는 3건이며 경로/문구는 closing-facts.json에 있다.
각 fixture는 그동안 source bytes와 문서 Save 호출0을 확인했다. 초기 빈 화면과 역사적
공개 cold/transient 실패의 원인·해결로 소급하지 않는다.

실제 Windows/WebView2·모바일·DPI/IME·Office 앱·GPU/물리 오디오·전체UI·Space/Library는 미실행/미완료다.
4MiB 초과/보관량·실제 신원/권한 backend·종류 C#표현/사용중삭제 대응·현재 예산 밖 custom
Run 출력은 기존 별도 잔여다. M11/M12/M4와 선택적 조합을 새 잔여로 다시 늘리지 않는다.

## 첫 최종 실패와 제한된 증거 재사용

첫 최종 record `/workspace/artifacts/v536-verification-managed/runs/d7b580439ee04a048a1979d52ddbd1d0.json`의66개 통과 뒤 복원본 프로젝트 왕복에서
Office part2가 실제 busy3회로 거절돼 기존 RO Retry가 보였으나 검사는 필드를 기다렸다.
개인 초안에 `immediate project exit input`이 그대로 보관된 것을 실제 파일/traffic으로 확인했다.
제품은 변경하지 않고 왕복에도 기존 RO 확인을 사용하고 Source Save 횟수의 이전 기준을
캡처하도록 검사만 보완했다. 같은 busy3회를 통제해 Retry/원본 불변/입력 복구를 검증했다.
이는 native busy의 스케줄 원인이나 역사적 초기 빈 화면을 해결했다는 주장이 아니다.
실패 원문/aria·관측·프로필·입력과 product/probe SHA를 보존했다.

그중 직접 통과한 동일 입력42개만 전체 manifest/CRC/SHA·SDK/NuGet/config/RID·LF/CRLF
독립 checkout·같은 command·제품/검사 입력 hash를 대조해 재사용했다. 이전 재사용은 없다.
허용한 차이는 정확한 XLSX 관측 검사와 재사용 도구/문서뿐이고 제품은 동일하다.
changed SDK/changed product 실제 거절과 각 reused.json/source-bound proof를 남겼다.
실패/변경 XLSX UI·모든 build/checkout/boundary·package/restore는 재사용하지 않았다.
재사용 flag 없는 전체 신규 경로도 유지한다.

## 지속 보관과 자원

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/9116ac6c208247e2a95265c5e7a07697.json`
- 최종 증거: `/workspace/artifacts/v536-verification-managed/runs/9116ac6c208247e2a95265c5e7a07697.zip` (517,725,957B), SHA256 `5729ca5ab489e24905e02ebdd23979b5c142e73be3fbf602faa05dbae269b2f4`
- 첫 최종 실패 증거: `/workspace/artifacts/v536-verification-managed/runs/d7b580439ee04a048a1979d52ddbd1d0.zip` (634,055,483B), SHA256 `bd06fea219ea383d51fbff3f91139148a8515acce9663315fed84644437ac26c`
- 개발 record: `/workspace/artifacts/v536-verification-managed/runs/5cedb57c9e824c43adb62fd6998dbc6a.json`, 증거 341,695,402B, SHA256 `4e27c261dab9af5efd8e7b5705b50d9f079b4e63c39c58e1005baba2c4e6f8f0`
- 승격 전 index는 최종 증거 package-index-before.json, 후 index는 `/workspace/artifacts/v536-verification-managed/runs/9116ac6c208247e2a95265c5e7a07697.closing-index.json`, SHA256 `e3f22694b30ffc05bca4061d723a8779bf0a06d314c0a204ffbf1939514992f9`

| 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | 141f0b17ac58db3cbe70add8fb6acae43d7b0738 | 922d2ba97a3f919742a99a4041441f332b1682b0b09a17ed40639584ea7a7aba | 53,841,591 | 2727/158 |
| rollback | 48242375886376cf5d583d58f6cf1689724d0faa | 1d7280076a4a4959a898925d842e7d5d1f2226e79534dc7dbc2665df0163a9ca | 53,841,952 | 2727/158 |

전체 복원·증거 봉인 뒤 원자 승격했다. 직전48242375를 rollback으로 유지하며 승인된 관리2세대
수명으로만 이전 rollback52082e6b `a9d008d7c74f0d881e7a234a6a3ce72aece8fa54373304df2e499b6d8720b8a7`를 퇴역했다. 다른 기존 자료/원본/로그/
프로필/SDK/Git를 삭제하지 않았다. 개발/첫 최종 실패/재검증의 세 임시 root는 자식 종료·소유·지속 증거 확인 뒤 정리됐다.

처음 단위 예산은 개발/최종 증거 각768MiB를 포함한1,740,636,160B였다. 공유 DOCX 회귀와
생성/복원 증거를 유지하기 위해 최종 증거를1GiB로 높여 전체 계획2,009,071,616B를 확인했다. 첫 최종 실패의634,055,483B 증거도 유지하며 재검증 전 두 번째 최종 예산을 포함한3,082,813,440B 계획과 실제 남은 여유를 재확인했다.
기존 자료를 삭제하거나 안전 여유를 줄이지 않았다. 최종 단계는 새 archive56MiB+증거1024MiB+
코드4MiB+별도 disk 안전64MiB=1,203,765,248B를 시작 전에 확인했다.
실제 개발/최종 증거는 325.87/493.74MiB다.
RAM 작업공간4GiB+별도512MiB, 추가 메모리9GiB+안전1GiB를 계획했다.

단위 시작/현재 disk 여유 28,226,400,256/26,726,600,704B, 관측 순증가 1,499,799,552B다.
최종 시작 27,246,866,432B·최종 단계 표본 최저 27,246,788,608B,
최종 신규 cgroup 표본 peak 13,213,425,664B·개발/첫 실패 최종 포함 managed 단계 표본 peak 13,213,425,664B,
limit 17,179,869,184B 대비 여유 3,966,443,520B다. tmpfs/컴파일러/cache 포함이며
제품 단독 peak·절대 극값·향후 단위별 순증가 보장은 아니다.
