# v536 고정 7행: 기존 private 동작의 핀 편집 연결

기준 게시 bd26d52f08a0515518aebd6cf4ea3734ed570de8, 저장소 v536 레퍼런스 196c605. 원본 blueprint.js의 bindActionPins/chooseActionPinType/pinRemoveButton/openInternal은 내부 동작에도 기존 이름·추가·삭제·타입 조작을 제공한다. 이번 단위는 이 기존 UI와 ordinary code next의 명시 parameters 계획을 qualified private 프레임의 기존 검증기로 연결한다. 새 메뉴·레이아웃·핀 ID 체계·공개 계약 복제를 만들지 않는다.

공개 오버라이드 계약과 private 동작의 내부 매개변수는 다르다. 부모/외부 함수의 타입·개수·역할·반환 구조 변경은 정상 보호로 거절한다. 별도 전역 함수 ID나 독립 계약 복제는 필수 범위에서 제외한다. 내부 그래프도 자신의 부모 signature를 몰래 바꾸지 않는다. 기존 code leaf의 계약만 선택된 프레임 안에서 편집한다.

ImplementationCopyEdits는 선택된 frame을 BlueprintTree.Select로 확인하고, 그 프레임의 직접 code leaf/record만 기존 Parameters/argument/source 규칙에 넘긴다. full qualified 경로를 보존하고 다른 깊이의 동명 body와 파일 위치를 바꾸지 않는다. 명시 null 해제는 이전 핀 계약에서 확인한 뒤 parameters를 적용하고 새 선언의 값과 사용자 본문을 검증한다. exact type/value/ref/out remap, 사용 중인 입력·출력·반환 삭제 거절, 현재 frame의 consumer/locals/exit 대응은 기존 검증을 재사용한다. caller storage/whole-body/native context와 다른 종류의 노드는 이 어댑터로 바꾸지 않는다.

본문은 opaque 사용자 C#이다. 계약이 바뀌면 이전 record는 stale이며 사용자가 본문을 다시 명시해야 한다. 이름을 문자열 치환하거나 새 매개변수의 값을 추측하지 않는다. signature·각 값·본문·import/record/provenance 전체가 유효해야 기존 단일 후보/CAS가 적용된다. 다른 소유/부모/외부/다른 target은 쓰지 않는다.

기본/독립 창의 authorBatch는 서버 bound owner/project/view와 원래 checkpoint·전체 source closure를 유지한다. parameters/null disconnect/새 값/source를 의미 순서로 후보에 준비하여 입력 Map의 삽입 순서에 따라 부분 적용되지 않게 한다. 실패한 요청은 미적용과 원래 checkpoint/물리 source가 동일함을 조회로 확인한 경우에만 새 명시 핀·값·본문 후보로 바꿀 수 있으며 이전 실패 기록은 보관한다. 불명 응답은 먼저 receipt를 조회하고 중복 적용하지 않는다.

기존 창 850×600, 동작 카드 폭 360의 실제 렌더와 입력 화면을 확인했다. WebBundle의 74개 항목 중 feature-authoring.js만 바뀌고 나머지 73개 UI 리소스와 CSS/HTML 바이트는 기준 게시와 같다. 기존 frame별 structuralEdit을 핀 편집에 연결한다. 불완전 핀 이름은 기존 contract-draft로 보관하고 Escape는 그 입력만 취소한다. 새 값은 기존 값 선택기로 명시한다. CSS/HTML/배치·Review/Confirm·Agent 권한은 유지한다.

순수 후보는 기존 6확인과 pin 계획 3확인을 분리한다. 이름/새 입력과 수동 본문·기존 binding 보존, 명시 해제 후 새 핀/값 대응, stale 본문·호환불가 매핑·소비 중 삭제·마지막 형제 오류의 전체 거절을 검사한다. 실제 UI에서는 복사 전 핀 이름/추가와 별도 frame 본문, 저장된 copy의 삭제/추가·미완성 거절·cold·새 명시 값 재시도, 기본/독립 창·프로젝트 문맥·실제 쓰기 실패·경합·응답 유실·Review/Confirm을 확인한다. 최종 결과는 통과 후 기록한다.

첫 순수 검사의 private preview 요청은 편집을 적용하지 않는 기존 경로였으므로 실제 편집 요청으로 바로잡았다. 초기 렌더 검사에서 작업 완료 전에 내부 열기를 눌러 이동이 실행되지 않은 시도는 통과로 세지 않고, 기존 busy 표시가 해제된 뒤 조작하도록 동기화를 바로잡아 재검증한다. 기능/데이터 검사는 유지한다.

7행 전체 완료가 아니다. 다른 code/ref 저장소/출력·반환의 모든 조합을 새 필수로 추가하지 않는다. 새 private 동작/실행선·callee ABI·내부 enum 어댑터와 8/9행·I6/B2/A4~A6/M4/M11/M12는 별도 고정 잔여다. 새 alias/import 전용 UI·legacy bool 시각 분기·전체 target 자동 복제를 추가하지 않는다. 이미지 생성/협의/shared Confirm/렌더·FPS 신규 backend는 범위 밖이다. 실제 Windows/WebView2·모바일 기기·Library 전달·전체 UI 완료는 미검증/미완료로 유지한다.

확정된 copy를 private 화면에서 cold 복원하면 선택된 하위 graph에는 copySource가 없어 출처 표시와 원자 저장 분류가 빠지던 실제 결함을 재현했다. 읽기는 기존 transient unit metadata가 없을 때 검증된 물리 rootGraph의 copySource를 사용하도록 수정했다. copy private 문맥이 불완전하거나 미지원 입력이 섞이면 개별 필드 저장으로 내려가지 않고 모든 입력을 보존해 거절한다. 기존 readonly 출처/단독 owner/공개 계약 검증을 유지한다. 해당 실패는 focused/storage 증거로 보관하고 최종 엔진으로 재검증한다.

쓰기 실패 후 재시도 journal은 새 명시 후보로 교체되며 이전 미적용 요청은 previousAttempts에 보존된다. 입력 원문과 checkpoint가 그대로이고 이전 실패도 정확히 남았지만 검사에서 journal 전체 동일성을 요구하던 비교를 바로잡았다. 실제 입력 셀 원문 전체·이전 실패 포함·checkpoint hash 불변과 live 핀/본문의 원래 상태를 각각 검증하며 실패를 통과로 집계하지 않는다.

cold 복원은 원래 basis가 없는 journal에도 프로세스 로컬 basis를 붙인다. 이전 실패의 비교에서는 이 최상위 basis만 제외하고 attempt·scope·graph·checkpoint/sourceProof·edits·셀의 원문 전체를 정확히 비교한다. 이전 실패가 새 previousAttempts에 보관된 것과 입력/소스가 보존된 사실을 내부 read token의 변경과 구분한다. 복원 시 생기는 basis를 사용자 데이터 손실로 오판한 두 번째 검사 실패도 보관한다.

응답 유실 뒤의 편집창은 기존 private 화면으로 복원된다. 이 화면에서 먼저 receipt를 조회하고 자기 저장 결과를 확인한다. 검사에서 결과 조회 전에 복원 창을 닫고 정보 카드의 재편집 버튼을 누르던 시도는 별도 실패로 보관했다. 코드 대조에서 일반 private copy의 known-request 조회가 원문 proof 검사 뒤에 있어 자기 저장으로 바뀐 source를 먼저 차단할 수 있는 경계를 확인했다. 기존 서버 bound checkpointPlain/copySource 문맥의 journal만 원문 검사 전에 readonly settlement 조회로 연결한다. exact receipt/plan/source closure 확인과 불명 결과·peer 변경 차단은 유지하며 새 authorBatch 없이 복구되는지 실제 엔진으로 검사한다.

## 집중 검증 완료

Native Release 0경고/오류와 순수 후보 9확인, 실제 엔진/렌더러 및 영향 회귀 10흐름 95확인을 통과했다. 정상·독립 창 값 Undo/Redo·cold·취소·저장 실패·다른 창 경합·응답 유실 조회·원래 source의 실제 물리 변경 거절·거절 후 명시 값 수정 재시도·프로젝트/창 문맥·Review/Confirm을 구분했다. 첫 기본·독립 창의 미확정 경로는 확정 copy 복원 출처 보완 전 결과를 재사용한다. 해당 미확정 경로는 출처 보완 분기를 사용하지 않는다. 확정/private의 쓰기 실패·실제 경합은 출처 보완 뒤 통과했고 마지막 readonly receipt 선조회 추가 전 결과를 재사용한다. 응답 유실과 나머지 영향 회귀·독립 checkout·패키지는 최종 엔진으로 확인한다. 이후 추가한 원본 치수/스크린샷과 저장된 핀 Undo/본문 취소 단언은 나머지 집중 흐름·독립 checkout·패키지에서 실행한다. 이전 실패 시도는 합계에서 제외했다. [명령·결과·제품 해시](evidence/v536-nested-copy-pins/focused-verification.json)에 기록했다. 다음 checkout/새 교차 패키지 결과는 별도 추가한다.

독립 checkout의 첫 충돌 검사는 peer 저장 뒤 화면 갱신이 끝나기 전에 클릭하여, 거절 메시지 대기에서 타임아웃됐다. 보관된 traffic에는 해당 클릭 뒤 authorBatch/settledAuthorBatch 요청이 전혀 없고 입력·peer 저장은 남아 있다. 제품/CAS의 거절 검사를 완화하지 않고 기존 idle 표시를 기다려 조작하도록 동기화한다. 실제 settledAuthorBatch가 미적용이고 원래 기준이 달라졌음을 응답으로 확인하는 단언을 추가했다. 이 실패는 clean/evidence/conflict.zip과 로그로 보존하며 해당 충돌 및 미실행 권한 회귀만 재검증한다. 제품 5개 파일은 실행 소스 70457ac와 같으며 통과한 독립 화면 12확인과 빌드 결과는 재사용한다.

## 독립 checkout·새 교차 패키지 검증

최종 소스/검사 체크포인트 `c3b9ecb6468aa0ded8a8197619d850c0383ddf17`로 기존 독립 checkout을 정상 FF하고 원래 `core.autocrlf=true`를 유지했다. 실행 제품은 `70457ac45ecec320ef7ecdf553b69e96c13d28c8`과 같으며 이후 차이는 검사 동기화·실제 거절 조회 단언과 이 검증 문서뿐이다. 변경 파일의 Git blob과 clean 상태를 확인하고 Native Release·새 Linux 엔진·실제 기본/독립 창·nested copy 경합·권한/오버라이드 회귀 4흐름 25확인을 통과했다. 이미 통과한 같은 제품의 독립 view 12확인은 재사용하고, 실패한 충돌의 증거는 보존한 채 동기화 수정 후 실제 충돌·미실행 권한/오버라이드 3흐름을 실행했다. 루트의 10흐름 95확인과 별도로 구분한다.

restore·솔루션 Release·명시 MCP Release·새 Windows x64 교차 패키징·패키지 probe·실제 패키지 `content/runtime/Confectory.App.dll`의 등록 함수 nested copy 독립 창 UI/컴파일러 11확인까지 6단계가 통과했다. manifest 2346개, 전체 2347개 파일/해시와 링크 부재, 실제 Core/Native DLL 및 변경 제품 소스의 바이트 일치를 확인했다. manifest SHA-256 `3ceba4fd86eee5bf03794db5f486f222433f46cd36c7a9b8a285e02cae3e17a0`, Native DLL `2c74d972de7cb673a6362b75150b582eb1b4f492474ae90863f72a3c6088f5ba`. SDK 없는 Linux runtime에서 패키지 웹 기동·74 resource·변조/필수 의존 누락 거절·기존 프로필/명시 override 보존은 probe로 구분한다. Windows apphost/WebView2를 실제 Windows에서 실행한 검사가 아니다.

전체 manifest와 fixture ZIP을 보관·무결성 확인한 뒤 이번 RAM 검증 패키지만 정리했다. 이전 보관 패키지/원본/사용자 자료는 삭제하지 않았다. 새 전달용 산출물을 보관하거나 Library에 업로드한 것은 아니다. 기록 시 workspace 여유 1239.3 MiB. [상세 결과](evidence/v536-nested-copy-pins/package-clean-verification.json)에 실제 명령·로그·SHA를 남겼다. 이 이후 커밋은 이 검증 문서와 결과 JSON만 추가하며 실행 코드는 위 소스 커밋과 같다.
