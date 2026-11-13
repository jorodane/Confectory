# 속성 타입 Undo/Redo 포커스 검증

제품 동결 `fba4192b7ede61bea4c913d4e6bb81af2b045134`의 [지원 범위](V666_PROPERTY_TYPE_FOCUS.md)를 최종 **신규 37단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout·격리 HOME/NuGet의 새 복원·Release/MCP·빈 cache의 실제 Linux 엔진,
새 Windows 교차 package·구조/무결성과 ZIP 전체 복원을 검사했다. 개발 단계와 최종 단계를 합산하지 않는다.

- 게시1a021f63의 기존 속성과 새 초안에서 타입 Undo 뒤 BODY 포커스·연속 Redo 미전달을 실제 UI로 재현했다.
  재현은 Save/Confirm 없이 원문·checkpoint와 Undo가 남긴 입력을 보존했다.
- 수정 뒤 기존 property path와 새 definition key를 같은 소유 창에서 유지한다.
  첫 포커스 지정 뒤 다시 클릭하거나 focus하지 않는 Ctrl+Z/Ctrl+Y/Ctrl+Shift+Z 세 주기를 검사했다.
  정확한 pending 입력·초안 ID/이름/기본값·다른 함수/C#·설명/아이콘과64비트 값을 보존했다.
- 기본/독립 정보 창에서 속성 타입·native 계약/본문을 한 Save·cold·Review 취소/Confirm으로 확정하고 Linux 실행40을 확인했다.
  이전 scalar/native 단위에서 별도 재검증하지 않았던 독립 정보 창의 해당 공동 저장도 이번 새 실행에 포함한다.
- 새 속성 초안의 연속 Undo/Redo·명시 취소·cold 재진입과 기존 아이콘의 연속 키/포커스 동작을 검사했다.
  input-target/isComposing 경계는 합성 DOM 이벤트로 확인했으며 실제 OS IME를 주장하지 않는다.
- capture 단계의 닫기가 history handler보다 먼저 실행된 경합은 오래된 키를 거절하고 입력을 보존했다.
  닫힌 창에 포커스를 넘기지 않고 재진입·명시 취소가 원문/checkpoint를 유지했다.
  owner 경합·프로젝트 A/B/A·저장 실패/재시도·응답 유실·반복/취소·늦은 설명의 후속 Save와 직전 peer 경합을 검사했다.
- 새 package의 일반 UI/새 초안과 전체 추출본의 응답 유실·늦은 입력·독립 정보 창 UI/실행 및 실패 정리 수명을 검사했다.
  actual Windows가 아닌 Linux 엔진·Chromium과 Windows 교차 package를 구별한다.

개발 기록은 20단계다. 초기 boundary 검사1건은 capture listener의 microtask 닫기보다
Undo가 먼저 실행될 것으로 잘못 기대해 실패했다. 실제로는 소유 창이 먼저 분리돼 입력이 유지됐으며,
그 순서와 정확한 pending/checkpoint/source 보존을 확인하도록 검사만 수정했다. 당시 실행 입력·hash/로그와 수정 뒤 통과를 보관했다.
후속 late 설명 기대값을 기존 schema/header fixture에 전달하는 검사 보완도 원래 로드된 입력과 새 hash로 기록했다.
실행 중이던 storage 프로세스나 완료 검사를 다시 시작하지 않았다. 이 보완 때문에 제품 패치를 추가하지 않았다.
최종 단계는 동결 코드와 최종 검사에서 모두 새로 실행했다.

제품 변경은 elements.js와 해당 canonical size/SHA256 pin뿐이다. 다른 resource pin·CSS/레이아웃,
리소스 pin 이외 C# 동작 본문·계약/권한·Review/Confirm·CAS를 유지한다. serialization/receipt 버전·migration은 없다.
과거 구 Reference reader 증거는 해시 확인한 재사용 자료이며 신규 단계에 포함하지 않는다.
초기 간헐 빈 화면의 원인이나 실제 Windows/WebView2·물리 기기·OS IME·GPU/audio·전체 UI 전수 완료는 주장하지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | fba4192b7ede61bea4c913d4e6bb81af2b045134 | 7c9c3c1ecf7c8da3e5d659e7352156d70d75b934f6c53290e6ef8b482762da69 | 54101699 |
| rollback | 54c342d880ec909336691315ea1dcf5ecb5c9972 | c70e509b3603ddd18a118efb0c82eb16673fec22abe898aef031f817f7ba6e46 | 54104531 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/cd9bb93ea714458d8a4fe6f284f216f2.json` · evidence SHA256 `48b8bb84dcd6ba342cbe9259493376f79caaad39f5521b88758680e7dabe910e`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/26512df927d44b91816f4f0b7ad07bd0.json` · evidence SHA256 `54d0c39ae1fe5d3e672eba160acefc3c2fe08538f3b97a6baad77a713b03680f`.
package2개와 증거 SHA를 확인했다. 기존 latest/직전 정상 rollback 교대와 이번 소유 임시물 정리만 적용했다.
원래 checkout/main·비관리 자료·과거 증거를 보존하며 퇴역한 세 번째 관리 ZIP의 전체 보존을 주장하지 않는다.
여유 24766443520bytes(23.07GiB)다.

남은 다른 복합 계약·속성 구조 편집, opaque/private 명시 C# 계획,
선택 native callee 의존성과 기존 import/등록 외부 원본 결합은 같은 고정7/8행의 원래 조작으로 유지한다.
다른 에디터의 일반 포커스나 가능한 모든 타입/문맥 조합으로 확대하지 않는다. 정보별 struct·종류 enum·모듈 interface를 유지한다.
초기 빈 화면 원인은 미확정이며 새 credential/grant·과금·main 변경은 없다.
