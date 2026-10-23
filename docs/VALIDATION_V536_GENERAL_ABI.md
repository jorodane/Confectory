# v536 호출 ABI의 명시적 핀 재매핑

2026-10-23, `7038f4a` 이후 연결이다. 같은 이름/순서/타입/out/반환을 유지하는 기존 값↔ref 지원과 **이번 명시적 입력/출력 대응**을 구별한다. 전체 ABI 문맥이나 전체 v536/Windows 실기기 완료 보고가 아니다.

## 원본 의미와 지원 범위

원본 v536 `blueprint.js`의 `bindWrapperNode`는 ‘원본 계약 갱신’에서 현재 source의 inputs/outputs를 다시 읽고 `pruneNodeLinks`를 호출한다. 실제 엔진은 연결을 조용히 제거할 수 없으므로 같은 진입점과 공용 modal 안에서 기존 핀→현재 핀을 명시적으로 선택하도록 연결했다. 원본 창/카드/핀 배치·CSS·HTML은 바꾸지 않았다. 새 설명/선택은 이번 기능에 필요한 일시적인 공용 modal 안에만 있으며 상시 패널이나 별도 권한 승낙을 추가하지 않는다.

- 같은 이름의 핀만 처음 표시한다. 다른 이름을 순서로 추측하지 않는다. 입력은 기존 input binding을 한 번 선택하거나 새 비-ref primitive 입력의 값을 직접 입력한다. 새 ref는 기존 storage만 사용한다. 원문 문자열·정확한 숫자를 보관하며 임의 C# 변환을 만들지 않는다.
- 출력은 기존 output/return을 현재 출력에 명시적으로 대응시킨다. graph의 소비자/alias/export binding도 같은 후보에서 갱신한다. 기존 연결된 입력을 버리거나 소비 중인 출력을 없애면 전체 거절한다. 중복/알 수 없는 핀·불완전 계획·incompatible type·잘못된 storage도 전체 미적용이다. 반환이 없어지는 경우는 기존 return에 소비자가 없어야 하며 void/data wrapper 매핑을 구별한다.
- 기존 typed import의 alias/scope, caller/owner/provenance, 불변 private seed와 현재 callee/직접 등록 receipt는 유지한다. 함수·import·wrapper·graph·모든 영향 record와 typed 소비자를 검증한다. 원본 callee/부모/등록 팩/다른 target을 자동 수정하지 않는다. 사용자 C# 본문/보조 코드는 그대로 두며 필요한 수정은 기존 코드 편집으로 한다.
- 현재 직접 소유 단일 Blueprint root/객체 슬롯, 직접 배치 저장 copy의 단일 Blueprint target, 새 private copy의 단일 context 없는 Blueprint target, 직접 등록 callable의 단일 caller target에 연결했다. owned ordinary root의 모든 Blueprint target도 기존 그룹 후보/CAS에 명시적인 target별 mapping을 결부했다. 실제 multi fixture는2target이며8target 전수 검증은 아니다.
- opaque C#/상속 implementation·nested/whole-body context, 같은 callee의 여러 사용, copy의 여러 target/공유 owner 및 등록 callable의 all-target receipt는 이번에 일반화하지 않았다. 이 문맥을 현재 한정된 성공으로 완료 처리하지 않는다. 정해진 source closure·소유권/receipt 계약 없이 자동 재작성하지 않는다.

새 schema 편집이나 별도 저장 경로의 결합은 이번 범위가 아니다. 원래 API의 별도 Save를 순서 호출해 부분 성공시키지 않는다. 세부 문맥과 실제 다음 완료 조건은 `V536_CALL_ABI_SCOPE.md`, `V536_REMAINING_ACCEPTANCE.md`다.

## 발견·수정한 실제 결함

처음 일반 단일 호출의 authorBatch는 callee의 node definition을 확인하고, 전체 source-ready 검사는 copy 경로에만 요구했다. 실제 registered fixture에서 잘못된 bool return→long 소비자 mapping이 임시 checkpoint에 접수됨을 재현했다. 이제 **모든 ABI authorBatch와 receipt 재확인**이 source-ready/source-assembled의 전체 typed graph/record 결과를 요구한다. checkpoint를 쓰기 전 staged 후보에서 거절하므로 import/graph/consumer가 부분 저장되지 않는다. 실제 negative와 올바른 입력의 cold 재시도·compiler Confirm으로 재검증했다.

Save는 전체 임시 draft의 접수다. C# 본문 구문·컴파일은 기존 명시적 Confirm에서 검증하며 자동 실행/Confirm을 하지 않는다. raw mapping form과 미저장 코드·기존 입력은 보관한다. 승인 전 form의 cold 복원/불완전 값 거절/취소, 승인 뒤 Undo·실패·CAS·응답 유실 복원도 구별했다. 등록 receipt 재확인에서 같은 계획인지를 비교할 때 새 mapping도 포함하여 이전 계획과 혼동하지 않는다.

화면 비교에서 승인한 새 값/연결이 Save 전 카드에 표시되지 않던 부분도 보완했다. 정확한 numeric token과 기존 input/output 대응만 투영하며 constant 객체의 내용은 핀 참조로 재해석하지 않는다. 공용 modal의 기존 `field` 스타일을 사용하여 각 선택 행을 구분했고 기존 CSS/화면 배치는 유지했다.

## 격리 검증 근거

모든 project/profile/등록 팩은 `/tmp` fixture다. 실제 사용자 자료/계정/로그인/인증파일·유료 추론·프로젝트 실행을 사용하지 않았다. 아래 수는 PASS 묶음으로 공통 준비가 포함되며 독립 시나리오 합계로 더하지 않는다. 로그는 `/workspace/scratch/v536-general-abi/`에 보존한다.

| 검사 | 실제 결과 |
| --- | --- |
| `v536_general_abi_metadata.py` | 6 PASS. 명시적 rename/order/ref-value/new input literal/multiple out/return 대응,11개 누락·중복·알 수 없는 핀/소비 중 출력/연결된 입력 제거/타입·storage·불완전 값 거절, raw64비트, void wrapper의 소비 없는 return 제거. source 쓰기 없음 |
| `v536_general_abi_adapter.mjs` | 3 PASS 묶음. exact long/한글·따옴표/불완전 literal·동일 이름만 표시, 승인한 mapping의 값/입력/소비자 화면 투영과 constant 객체 보존 |
| `v536_general_abi_ui.py` | 직접 등록 callable 실제 normal4; 최종 incompatible-map/정상 재시도5; 성공 응답 유실5; peer caller 충돌3; checkpoint 쓰기 거절5. 실제 원본 갱신/취소→승인 전 form cold 복원→부분 숫자 거절→name/order/long→double 입력/새 int 값/long return→out total와 bool return→한 후보/CAS→cold·Review 취소·명시 compiler Confirm. Lib 원본/owner/다른 구현/node 본문 보존 |
| `v536_general_multi_abi.py` | owned ordinary common/windows 실제 normal4, 마지막 windows 출력 mapping 오류5, 성공 응답 유실5, Undo/cold3. 공유 import·양쪽 graph·모든 record를 함께 검사하고 마지막 target 오류 시 첫 target도 미적용. 실제 compiler Confirm 및 source 보존 |
| `v536_general_copy_abi.py` | 저장된 직접 배치 copy 소유/직접 등록 callee 각각 실제4 PASS. owner/배치/provenance를 유지한 명시적 general mapping·form cold·Save/receipt·cold·Review 취소/compiler Confirm. donor는 별도로 현재 계약에 맞춘 fixture이고 제품이 donor를 수정하지 않음 |
| `v536_general_private_abi_metadata.py` | 4 PASS. 원래 seed/본문·정확한 숫자 보존, 명시 general mapping과 원래 body 편집의 한 후보, stale donor 자체의 실제 compiler 거절,10개 위조/소유/프로젝트/source 변경 거절 |
| `v536_general_private_abi_ui.py` | 소유 callee5, 직접 등록 callee5 PASS. 원래 seed·private 본문을 보존하며 donor/현재 callee가 독립 변경된 뒤 기존 새-copy Save/CAS·cold·Review 취소·명시 compiler Confirm. source/부모/다른 Windows target 불변 |
| 기존 회귀 | multi-target 순수4 묶음(14개 candidate·6개 group 거절), 기존 private 값/ref UI5, 기존 소유 슬롯 값/ref8 PASS. 강해진 전체 그래프 검사 뒤 기존 소유/출처/계약 경계를 확인 |

정상 registered 최종 증거는 `/tmp/confectory-general-abi-zdz4qzu_`, saved copy는 `/tmp/confectory-saved-copy-abi-ta82ppkn`이다. `mapping-dialog.png`/`explicit-general-map.png`를 열어 기존 modal/카드와 선택 값·연결을 확인했다. 최종 projection의 실제 DOM은 새 값3과 기존 amount 연결을 검사했다. 원본 전체 pixel equality나 모바일/native 전수 검사로 확대하지 않는다.

초기 병렬 실행 두 건은 fixture의 기본5초 owner-ready 기대에서 실패했다. 실제 owner/body 상태 hook을 기다리는 bounded60초로 바로잡아 통과했다. incompatible-map 실패는 위 실제 결함으로 구분해 수정했다. void 순수 검사는 처음 dummy wrapper hash를 사용해 실패했고 현재 함수에서 계산한 실제 hash를 사용했다. 보호 assertion을 제거하지 않았으며 초기 실패 로그를 유지한다. 최종 C#/UI 변경 영향이 없는 통과 검사는 불필요하게 반복하지 않았다.

## 패키지·게시 한계

Release 전체 솔루션 0 warning/0 error, Linux 생성 엔진과70개 canonical/exact UI 리소스의 원본 pin을 구성했다. 최종 Windows 교차 패키지·SDK 없는 managed 웹 시작·checkout·정상 게시 결과는 아래 최종 기록에 구분한다. 실제 Windows apphost/WebView2/더블클릭·DPI/IME/native snap·Android/touch는 미검증이다. 로컬 산출물은 Library 첨부 성공을 뜻하지 않으며 기존 discovery 네트워크 장애에 새 복구 근거가 없어 반복하지 않았다.

.NET Desktop Runtime10.0 x64·Edge WebView2 Runtime이 전제이며 자동 설치하지 않았다. 프로젝트 빌드에는 별도 .NET10 SDK가 필요하다. main/Android/원본 v536 ZIP/사용자 자료·기존 Agent 동의·권한을 보존한다. 일반화하지 않은 문맥·모바일/조작·기존 schema 및 별도 저장 결합은 여전히 미완료다. 이미지·협의·렌더 신규 backend는 추가하지 않는다.

최종 공용 field 행은 `/tmp/confectory-general-abi-sqqtbsqz/final-mapping-field-rows.png`에서 확인했다. 실제 renderer에서 세 선택 행이 겹치지 않고 선택·취소 뒤 source/입력이 그대로임을 검사했다(`form-evidence.log`). 이 마지막 변경은 기존 field class 적용뿐이며 통과한 C# 동작 검사를 다시 구현/반복하지 않았다.

## 게시 전 발견한 명시적 매핑 재시도 결함

실제 화면에서 잘못된 `long return → bool return` 선택은 전체 미적용으로 거절됐지만, 원래 Undo 뒤 `return → out total`을 명시적으로 다시 선택해도 저장 시도 기록이 달라졌다는 이유로 재시도가 막혔다. 초기 실패는 `user-correction.log`, `/tmp/confectory-general-abi-bhu98mxl`에 보존했다.

이제 먼저 기존 시도의 서버 결과를 조회한다. 성공 receipt이면 그 결과만 복구한다. 미적용이고 원래 checkpoint의 메모리·디스크 해시, 전체 source ID/해시, 현재 callee 해시/서명, copy 및 target 그룹 기준이 모두 그대로임을 확인한 경우에만 같은 wrapper의 명시적 mapping 변경을 새 시도로 접수한다. 본문·소유권·계약·대상·source 변경을 mapping 수정으로 취급하지 않으며 CAS와 staged 전체 타입 검사는 그대로다. 이전 실패 요청은 새 journal의 `previousAttempts`에 보관해 결과를 확인할 때까지 유지한다. 조회가 실패하거나 적용 여부가 불명확하면 새 요청을 보내지 않는다.

다음 검사는 격리 프로젝트와 실제 Linux 엔진/Chromium 화면을 사용했다. 각 수는 공통 준비를 포함한 해당 실행의 PASS 묶음이며 합산한 독립 테스트 수가 아니다.

| 추가 실행 | 결과 |
| --- | --- |
| 실제 잘못된 선택 → 거절 → 원래 Ctrl+Z → 새 선택 → Save/cold/Review 취소/명시 compiler Confirm | 등록 callable 5 PASS, `user-correction-fixed.log`, `/tmp/confectory-general-abi-dzzg1d18` |
| 마지막 windows target만 잘못 선택한 같은 흐름 | 두 owned target 5 PASS, `multi-user-correction.log`, `/tmp/confectory-multi-abi-bwj1p35_`; 첫 target/import도 실패 시 미적용 |
| 저장된 직접 배치 copy에서 같은 흐름 | 5 PASS, `copy-user-correction.log`, `/tmp/confectory-saved-copy-abi-iesyekix`; owner/donor/다른 구현 보존 |
| 실패 뒤 동료의 caller 저장 | 4 PASS, `user-correction-conflict-fixed.log`; 새 요청을 보내지 않고 기존 기록·새 입력·동료 checkpoint를 cold까지 보존 |
| checkpoint는 그대로인데 외부 callee 실제 서명만 변경 | 4 PASS, `source-change.log`; 기존 파일 해시만 보고 재시도하지 않으며 새 요청 없이 차단 |
| 수정 저장의 성공 응답과 후속 결과 조회 모두 유실 | 6 PASS, `user-correction-loss-fixed.log`, `/tmp/confectory-general-abi-slye5qgo`; 두 시도 기록과 입력 유지, 조회 불가 중 Save에도 추가 authorBatch 없음, cold 뒤 receipt 조회로 복구 후 Confirm |
| pure mapping 기준 비교 | adapter 3 PASS; 본문/source/receipt/owner/target/서명 변화는 mapping-only 재시도로 인정하지 않음 |

이 수정은 원래 Undo/갱신 동작을 연결하며 CSS/HTML/창 크기·레이아웃이나 권한을 바꾸지 않는다. 전 문맥 ABI·schema/별도 저장 결합·최종 모바일/조작 수용 및 실제 Windows 검증은 여전히 별도 잔여다.

## 최종 재현 및 Windows 교차 패키지

검증한 코드 기준은 `7d012d80fdea0d41f41ffb28c99272ec66d13014`다(`b56ea1f`의 일반 mapping + 게시 전 재시도 수정). 별도 깨끗한 checkout을 정상 fast-forward한 뒤 Release 전체 솔루션이 0 warning/0 error로 빌드됐고, 그 checkout에서 Linux EditorHome 엔진을 새로 생성했다. 실제 Git의 이전 CRLF checkout→현재 속성 pull과 새 LF checkout 모두에서 70개 canonical/exact 리소스를 로드했다. 잘못된 내용/encoding/BOM/binary/budget도 거절하며 원본 bytes를 보존했다. 근거는 `checkout-solution-final.log`, `checkout-engine-final.json`, `checkout-resources-final.log`다.

교차 패키지는 `/workspace/artifacts/Confectory-v536-general-abi-v3/Windows-x64/Confectory.exe`다. 실행 시 폴더 전체가 필요하다. 선언 파일 2,313개와 marker를 합쳐 2,314개, 총 131,687,710 bytes다.

- `confectory-desktop-package.json` SHA-256: `4a96511e4e30b1f04486031551916d92c8fafa58716ce30c59e2dfd27c3b896c`
- 정렬한 전체 파일 checksum 목록 SHA-256: `0a59af4eaf2fbb91359afdb669dc4b27ca87a4fd9323cc5ab445b6e1f72bb3ac`
- 파일별 목록/검토는 scratch의 `review-final/PACKAGE_SHA256SUMS`, `package-files.json`, `source-inventory.json`, `secret-review.json`에 보존했다. 추가 변경은 구현 4·테스트 4·문서 2개로 분류했고 secret-pattern 추가 발견은 없었다. 패턴 검토가 모든 가능한 비밀 부재를 보장한다는 뜻은 아니다. 기존 코드 묶음과 합친 게시 소스는 구현 8·테스트 7·문서 6개이며 로그/빌드/프로필/인증정보는 포함하지 않는다.

패키지 검사(`package-probe3-env.log`)는 .NET SDK가 없는 격리 runtime 복사본과 무관한 cwd/profile에서 실제 managed 패키지 엔진의 웹 시작·70개 리소스를 확인했다. 누락/변조 파일도 거절했다. 첫 probe는 `CONFECTORY_DOTNET` 환경 인자 누락으로 실행 도구를 못 찾았으며 올바른 도구 경로를 설정한 동일 검사로 통과했다. 패키지 source/pins는 root와 정확히 같고 CRLF checkout과는 LF 정규화 후 같다. helper DLL은 root와 패키지 사이 정확히 일치한다. 다른 경로/CRLF 재빌드 DLL 전체의 byte 재현성은 주장하지 않는다.

추가로 실제 fixture 검증에 사용한 Linux 엔진의 EditWorkspace·PackWorkspace·EditorHome·EditorHome.Model DLL과 Windows 패키지의 해당 DLL이 정확히 같음을 확인했다(`package-abi-runtime-match.json`). NativeUI의 Windows/Linux 차이는 의도된 플랫폼별 구현이며 같은 것으로 주장하지 않는다.

실제 Windows apphost/WebView2 실행, native/DPI/IME, Android/실기기 touch, 사용자 계정/유료 추론 및 전체 UI 수용은 미검증이다. 이 로컬 패키지의 Library 업로드·사용자 첨부 전달은 완료되지 않았다. 전체 UI 완료가 아니라 명시 mapping과 이번 안전한 재시도 범위의 검증 결과다. 다음 작업은 현황표에 고정한 기존 schema/별도 저장 경로 결합과 모바일·조작 잔여이며, 미지원 ABI 교차 문맥을 이번 단일/owned2target 성공으로 확장하지 않는다.
