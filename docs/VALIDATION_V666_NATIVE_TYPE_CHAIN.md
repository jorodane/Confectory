# 선택 C# import 함수의 고급 입력 공동 저장 검증

동결 runtime `7e76b90039c32a51811fcd5c7e58891c3e75bbb6`의 [Main→선택 A→선택 B 흐름](V666_NATIVE_TYPE_CHAIN.md)을 **신규45·재사용0·실패0**으로 검증했다. LF24·CRLF13·새 패키지/전체 ZIP 복원8이며 개발 진단과 구분한다.

- 원래 scalar 입력의 C# import 프로그램을70으로 실행하고, 이전 planner의 거절을 재현했다. A/B를 정보별 구조체로 명시 전환하고 두 구현과 Main의 세 본문을 직접 작성했다. 함수별 네 명시 계획을 원래 경로/hash/before/after 선언으로 인증했고, 역순에서도 같은 원래 해시/후보를 확인했다. A는 자기 계약과 B의 caller 계획에서 같은 source여야 하며 한 번만 반영됐다. 새 프로그램의 실제 실행값은73이다.
- 두 함수의 원래 scope/type proof, 누락한 Main 또는 A caller 계획, 잘못된 선택 consumer 선언, stale hash, 잘못된 C#, 상충 A text를 전체 거절했다. 캡처된 proof/read 누락·교차, 재서명한 원래 alias/native 이름·선택 import/native ABI, 본문/함수 hash와 외부 경로 변조도 원문/checkpoint 쓰기 없이 거절했다.
- 한 Save·cold 복원·후속 owner/function 설명 Save에서 두 nominal scope와 세 본문을 유지했다. Review 뒤 Main.csbody, A 본문 또는 Payload.celem이 바뀌면 Confirm이 차단되고 peer text·checkpoint가 보존됐다. 정확히 복원하고 cold·새 Review/Confirm을 거쳐73을 실행했다.
- 기존 타입 선택기·C# 선택기와 카드/상세창의 취소·Undo/Redo·미저장/저장 cold, 기본/독립 창·프로젝트 왕복/stale form 거절, 쓰기 실패/재시도·응답 유실·후속 입력/두 번째 Save를 확인했다. B를 편집할 때 이미 명시한 A 자기 본문의 선언을 현재 원래 hash/path/서명·선택한 A 계약과 대조하여 표시한다. 본문은 각 계획에서 직접 선택·작성한다. 기존 카드 크기·DOM/CSS 배치를 유지했다.
- 이전 공유 caller UI/native/guard, incremental 타입 scope 경계, 단일 nominal API와 scalar 역할 import native/guard를 별도 회귀로 검사했다. 기존 소유/등록 외부 타입 공유 호출자의 readonly 경계도 회귀로 확인했다. 새 패키지 생성/구조/probe/UI, 전체 ZIP file hash/추출/probe·응답 유실·후속 입력·독립 창과 반복 성공/실패 수명을 새로 검증했다.

제품 변경은 InformationFunctionNativeJoint/InformationFunctionNativeTypes, 기존 element-functions/feature-authoring JS와 해당 두 리소스의 WebBundle size/hash 등록이다. 검증된 모든 미래 계약/타입을 내부 compiler view에 제공하고, 각 원래 계획을 별도로 인증하며, 기존 buffer에서 같은 최종 header/body만 합친다. 기존 native 이름·순서·값 역할·scalar 반환·원래 import alias와 미선택 Main ABI를 보존한다. C# text를 추측하거나 변환하지 않는다. version2 workspace/version3 receipt·native-type-source-guards-v1·read240/member64·type64·등록/권한·Review/Confirm·최종 CAS를 유지한다. 정보별 struct·종류 enum·모듈 interface 및 명시 async 전환 전 sync caller 오류도 유지한다.

초기 개발20단계의 실패3건(두 JS resource pin 누락과 서명 JSON 속성 순서 비교의 UI 실패/진단)을 원래 로그·관측·pending 계획과 함께 보존했다. 각각 pin 갱신과 기존 methodSignature 정규화로 수정했다. 초기 harness 초안의 들여쓰기 오류1건도 증거에 남겼다.

첫 동결 e4e464bf의 최종 실행은 15단계 완료 후, 별도 역순 UI 재현에서 보관된 B 계획의 오래된 선언이 A의 새 명시 선언보다 우선하는 표시 결함을 확인해 게시 전에 중단했다. 그 결과를 새 완료 검증으로 계산하지 않는다. B→A로 편집한 뒤 B를 다시 열 때 A가 이미 작성한 현재 선언을 표시하도록 수정했다. 재개방 취소는 이전 B 계획을 그대로 보존하고, 사용자가 코드 저장을 눌러야 B 계획의 선언이 갱신된다. 이 후속 수정은 새 개발9단계·실패0건으로 실제 재개방·취소/명시 저장·cold·Review/Confirm·실행73 및 guard 회귀를 통과했다. 선행 역순 재현과 이전 패키지 호환성 증거는 해시를 확인해 개발 증거로 재사용하고 최종 통과 수에 더하지 않았다. 위 최종45단계는 수정된 새 source에서 전부 새로 실행했다.

중단한 실행의 모든 worker/child 종료는 인증됐다. 정리 guard가 미인증 Chromium SingletonSocket을 발견해 `/tmp/cv-5xgaibtx`의 삭제를 차단했다. 해당 폴더와 원래 record, 부분 증거 `/workspace/artifacts/v536-verification-managed/runs/ae341c4d6dfb44f68bbcf2929afebd12.partial-5870bc8583b241ffa4bef37bedf015ca.zip`(SHA256 `ccad011c37add8331c2cc33cbe382ae7f125882a881ac77b86f679c1ae0c496d`)를 보존했으며 강제 정리하지 않았다. 그 실행은 미완료이며 패키지 승격/게시가 없었다. 수정 후 새 개발/최종 임시물의 인증된 정리와 이 보관 상태를 구분한다.

초기 단위에서 검증해 보관한 온전한 이전 패키지 `47b621640df65f75166a9941eb85a9638024e3f1`의 모든 file/hash/mode를 별도 추출했다. 원래70 실행·새 선택 import 계획 거절과 이전 UI Save 거절·입력/checkpoint/원문 보존을 확인했다. 선행 단위의 실제 저장 capture를 전달한 이전 pending guard 수용은 `False`였다. 같은 세대 authoring/runtime을 사용하며, 이전 전체 UI cold/Review/Confirm 교환·자동 migration/downgrade·구 Reference parser 변경은 별도 잔여다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 7e76b90039c32a51811fcd5c7e58891c3e75bbb6 | a3381d2098edab289586cf328676affa071070b767db4660a8719fefff85e97f | 54145710 |
| rollback | 47b621640df65f75166a9941eb85a9638024e3f1 | 505b90e66964536b5ce98531684d8267ca2024550a530ef7ea684b89da6f1138 | 54146308 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/a1830001b4d0428881c8037089f930cd.json` · evidence SHA256 `cfc6a8473ebc16ed3b2421afee0f9fc548f5ee26b13c5462c7ba8e17dd5c7b3e`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/d3404e09595048c29865252fed07b070.json` · evidence SHA256 `490c9a43a3304f0bc72f532ced120bf4beec727f53725991aef9d39e26fe6ed8`.
두 패키지·새 개발/최종 및 선행 archive hash를 재확인했다. 인증된 이번 검증 임시물과 기존 latest/직전 정상 rollback 교대만 정리하고 7ee203d 게시본·원본 checkout·과거 증거를 보존했다. 디스크 여유 24333426688bytes(22.66GiB)다.

이번 유한 단위는 기존 직접 소유 동기 함수의 nominal 값 입력 전환과 명시 C# import 계획이다. 고급 반환·reference/array·out/ref·async·private/whole 결합은 별도 범위다. 오버라이드의 공개 계약 구조 변경은 기존 정책상 금지이며 필수 잔여로 추가하지 않는다. 외부 원본 수정 권한도 확장하지 않는다. Linux 실제 .NET/portable 실행·Chromium 자동화이며 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. 초기 빈 화면 원인은 미확정이며 main은 사용자 검토/merge에 남긴다.
