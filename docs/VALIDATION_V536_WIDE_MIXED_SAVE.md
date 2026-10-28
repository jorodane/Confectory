# v536 여러 새 복사본·구조/typed 값의 혼합 Save

2026-10-23, `c03349b` 이후의 current-widget 연결이다. 원본 v536(`196c605`)의 HTML/CSS·창 크기·컨트롤 배치는 바꾸지 않았다. 전체 UI 복원이나 실제 Windows 수용이 아니다.

## 문제와 결과

기존 엔진의 다중 슬롯 batch는 존재했지만 owner 선언이 함께 있으면 새 copy 하나와 설명/단일 primitive만 허용했다. 복합/배열/참조·override/unset·부모/modules·새 속성 입력 뒤 copy를 선택하거나 여러 copy와 Save하면 차단됐다.

이제 같은 owner의 명시적 new private copy 1~8개와 **현재 원본 UI가 실제 제공하는** 설명·기존 scalar/typed 값·순서/참조·부모 값 override/local reset·owned parent/Root·로컬 modules·새 primitive 속성 정의/기본값을 하나의 후보/CAS로 처리한다. 순수 helper가 현재 schema/typed path/상속·참조를 검사하고, 필요한 새 소유 schema/uses/manifest를 후보에 포함한다. 모든 copy의 immutable snapshot/source/import/wrapper/graph/record를 검사한 뒤 최종 metadata closure에서 각 copy가 유효한 direct owner provider이면서 최종 요구 슬롯에 남아 있는지 확인한다. 원래 dependency proof와 live context를 다시 검사하고 전체 checkpoint를 한 번만 수용한다. 마지막 copy/구조/typed 값이 부적합하면 앞 copy·새 schema·선언·등록도 미적용이다.

정확한 JSON 숫자는 JsonDocument/typed JSON 원문으로 보존한다. 배열·modules·새 필드 순서는 요청의 순서를 따른다. 중첩 typed path 검사는 다른 참조 owner를 따라 쓰지 못하고 겹치는 root/child 계획을 거절한다. 새 필드는 기존 schema를 수정하지 않고 owner에만 새 schema를 만든다. 기존 필드 이름/타입/아이콘/삭제·새 compound schema 정의·외부 소유 수정은 이번 UI 범위에 없다.

Save는 **전체 임시 초안의 접수**다. Review는 그룹과 최종 source baseline을 고정하며, C# 컴파일은 기존 명시적 Confirm에서 수행한다. metadata/import/계약/저장/CAS 오류는 Save 전체 미적용이다. C# 컴파일 오류는 완전한 임시 그룹과 편집 입력을 보존하고 최종 source 반영 전체를 막는다. 자동 Confirm이나 프로젝트 실행을 하지 않는다.

receipt는 모든 intent 수/고유 function과 선언 계획·전체 source proof에 결부한다. 일부 copy 목록을 전체 저장으로 인정하지 않고 proof 예산은 쓰기 전에 검사한다. 성공 응답 유실 뒤에는 같은 receipt를 재검사하여 중복 copy를 만들지 않는다. 현재 schema가 같다는 증거가 있는 늦은 값/설명만 접수한 hash로 연결하며 parent/modules/새 정의 또는 다른 schema를 조용히 새 기준에 재적용하지 않는다. 기존 raw 입력과 다른 객체 입력을 보존한다. 이전 단일 scalar proof/journal 형식도 유지한다.

## 격리 검증

실제 사용자 profile/프로젝트/계정·인증·유료 추론·프로젝트 실행을 사용하지 않았다. 실제 fixture는 `/tmp`의 owned ProjectPack과 저장소, 엔진과 Chromium이다. 두 copy 중 하나는 Blueprint+실행 enum wrapper, 다른 하나는 C# 본문이다. 슬롯 원본/부모/다른 Windows target 파일 bytes를 비교했다. 수치는 스크립트의 PASS 묶음이며 공통 준비가 포함되어 독립 시나리오 합계로 더하지 않는다.

| 검사 | 실제 결과 |
| --- | --- |
| `v536_wide_mixed_metadata.py` | 2 PASS 묶음. 정확한 long·한글/따옴표·복합/배열/참조/순서·parent/modules/local reset·새 정의. 중복/겹침/스키마/ref/외부·자기 부모/새 이름·타입/알 수 없는 연산/raw owner/다른 ref owner/unset 등12개 거절, source 쓰기 없음 |
| `v536_mixed_declaration.mjs` | raw64비트/compound 원문이 요청과 정확히 결부됨, 불완전 입력 거절, 정확한 receipt/current schema의 값만 복원, 구조/다른 source 변경을 자동 재기준화하지 않음 |
| `v536_wide_mixed.py backend` | 실제 API4 PASS. 마지막 copy 잘못된 node로 전체 미적용, 두 copy+구조/typed 값/새 schema 한 후보 접수, receipt 일부 목록 거절, cold·실제 compiler Confirm에서 owner/manifest/새 파일만 반영 |
| normal UI | 실제4 PASS. 원래 속성 widget·부모/modules/새 필드 행과 copy 선택/본문/wrapper 편집을 통해 한 번 Save, cold·Review 취소·명시 compiler Confirm. 정확한 long9223372036854775806/9007199254740995/9007199254740993, 한글·배열 순서·참조 보존 |
| last-copy | 실제6 PASS. 전송된 마지막 copy만 잘못되게 만들어 Save 전체 거절, checkpoint/등록/첫 copy 불변과 cold 입력 보존. unmodified 명시 재시도·cold·Review 취소·compiler Confirm |
| storage | 실제4 PASS. 격리 checkpoint 쓰기 거절 시 전체 미적용, 원래 두 seed/구조/정확한 입력 cold 보존·다음 명시 재시도. 다른 Target1 객체 입력 보존 |
| response-loss | 실제3 PASS. 실제 접수 결과를 transport 오류로 바꾼 후 receipt 한 번 확인. 대기 중 새 설명/MP9007199254740997/compound9223372036854775807 보존·cold 후속 Save·두 copy 중복 없음, 다른 객체 입력 보존 |
| conflict | 실제3 PASS. peer의 실제 owner Save 뒤 오래된 혼합 요청 거절, peer checkpoint와 모든 private 입력/cold 보존, 자동 재기준화/부분 적용 없음 |
| cancel | 실제3 PASS. 원본 취소는 현재 owner 구조/typed 값/두 copy 선택만 정리. 다른 객체 입력·부모/source 보존 및 cold 원상태 |
| scope-change | 실제3 PASS. 부모를 요구 슬롯 없는 Unit으로 바꾸면 두 copy 준비 뒤 최종 검증에서 모두 미적용. cold 후 사용자가 호환 parent를 명시적으로 선택하면 기존 두 copy/입력을 함께 접수 |
| compiler | 실제6 PASS. 마지막 본문의 실제 C# 오류는 명시 Confirm에서 `sourceConfirmed=false`/invalid, Confirm 직전 checkpoint 및 모든 최종 source 불변. 해당 본문을 실제 UI로 고쳐 같은 그룹 재검토·cold/Review 취소·명시 Confirm 통과 |
| 기존 최소 혼합 API / private-copy ABI UI | 각각 실제5 PASS. 기존 단일 scalar·위조10개·receipt/cold/Confirm 및 immutable seed·명시 ABI/원래 source·다른 target 보존 경로 회귀 |

로그는 `/workspace/scratch/v536-wide-mixed/`에 보존했다. normal/last-copy의 `wide-mixed-pending.png`와 실패 화면을 별도 fixture 경로에 남겼다. HTML/CSS·원본 리소스 그림은 수정하지 않았고 이번은 기능 연결 검사로 전체 pixel equality/모바일 전수 수용을 주장하지 않는다.

초기 UI 테스트의 Counts 선택자는 원본 `.property-content-box` 계층을 빠뜨려 실패했다. 실제 현재 위젯 계층으로 고쳐 실행했다. compiler 테스트는 처음 Review가 컴파일하는 것으로 잘못 예상했다. 기존 Confirm 실제 경로로 고쳤고 cold 전 저장본의 runtime revision과 비교하던 기대도 **Confirm 직전의 전체 checkpoint bytes**로 바로잡았다. 검사/보호를 완화하거나 오류를 성공으로 바꾸지 않았으며 초기 실패 로그를 보존했다.

## 빌드와 남은 경계

Release 전체 솔루션과 helper 0 warning/0 error, 새 Linux 실제 생성 엔진/69개 리소스 연결이 통과했다. Windows x64 교차 패키지는 `/workspace/artifacts/Confectory-v536-wide-mixed/Windows-x64/Confectory.exe`이며 전체 폴더가 필요하다. .NET Desktop Runtime10.0 x64·Edge WebView2 Runtime이 전제이고 자동 설치하지 않았다. 프로젝트 빌드는 별도 .NET10 SDK가 필요하다. 패키지 구성/SDK 없는 managed 시작·checkout 검증과 게시 결과는 아래 최종 기록에 추가한다.

실제 Windows apphost/WebView2/더블클릭·DPI/IME/native snap, Android/실기기 touch는 미검증이다. 로컬 폴더가 있다는 것은 Library 전달 성공이 아니다. 기존 Library discovery 네트워크 실패에 새 복구 근거가 없어 반복하지 않았다.

실제 fixture는2copy이며8copy/모든 타입·구조/플랫폼 조합의 전수 수용은 아니다. saved-copy ABI·multi-target ABI·Set/property·다른 provider·dirty raw source 결합 및 기존 schema 편집은 미지원 차단을 유지한다. 일반 ABI와 원본 모바일/조작의 구체적 완료 조건은 `V536_REMAINING_ACCEPTANCE.md`, 고정 조합은 `V536_ATOMIC_REMAINING_COMBINATIONS.md`다. 이미지/협의/렌더 신규 backend는 이번 범위가 아니다. main/Android/원본ZIP·사용자 자료·동의·권한 경계를 보존한다.

## 최종 재현 기록

코드 커밋은 `ffcd5e1c44ec3377cc68f2faea3d124bd96c3145`다. 별도의 clean checkout이 이 커밋으로 정상 fast-forward한 뒤 Release 솔루션0 warning/0 error와 새 Linux 엔진 빌드를 통과했다(`checkout-solution.log`, `checkout-engine.json`). 패키지의 변경 구현9개와 helper DLL은 이 코드 커밋/검증 Release와 byte 동일하다. 후속 변경은 이 검증 기록과 안전 예산의 설명뿐이며 C#/UI/리소스를 바꾸지 않는다.

`desktop_package.py`의 package 구성/변조·누락 거절, 별도 cwd·SDK 없는 managed 웹 시작, 기존 profile 재사용·override, 69 UI리소스 검사 PASS. 증거는 `/tmp/confectory-desktop-package-xkznqfbv`다. Windows apphost/WebView2/더블클릭 실기기 검사는 아니다.

패키지는 선언 파일2,312개+marker로 총2,313개, 131,664,721 bytes다. marker SHA-256은 `6f357e9dd2cca569ee2aad5100bc3ea766d3c590d4cae3f97366c30309a2caaf`, 파일 목록 checksum은 `9f390860ff1022cb825c1ccec4a17b2a90538257d01d246a0551369cb08227ff`이다. 전체 경로/크기/checksum 목록은 scratch의 `review/package-files.json`/`review/PACKAGE_SHA256SUMS`에 보존한다.

검토한19개는 구현9/테스트3/문서7이고 비밀 패턴 추가 검토 항목0, 외부 임시 fixture를 필수로 요구하는 테스트0이다. 생성 빌드/로그/profile/인증정보는 커밋하지 않았다. 패턴 검사는 모든 비밀 부재의 절대 증명이 아니다. 원격 게시 SHA와 두 checkout clean/리소스 pull 재현 결과는 완료 checkpoint에 직접 확인한다.

실제 Git 속성 pull 뒤 retained CRLF와 fresh LF 양쪽의69개 canonical/exact 리소스 및 내용/encoding/BOM/binary/budget 변조 거절도 통과했다(`checkout-resources.log`). 원래 byte는 그대로 유지됐다. 최종 문서 변경은 이 결과만 기록하며 이미 통과한 코드 검사를 반복하거나 전체 UI 수용으로 확대하지 않았다.
