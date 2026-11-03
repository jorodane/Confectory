# M12: 소유 private frame의 공개 함수 호출 결합

## 원래 사용자 흐름과 지원 경계

저장소 v666 `dist/blueprint.js:135`의 call 포트는 참조한 함수 정의에서 나온다. `:969–976`의 공개 분기/반환 편집과 `:248`의 결과 분기 뒤 다음 동작 규칙을 기존 소유 private graph에도 연결한다. 물리 Blueprint Root 안의 일반 switch-profile frame에서 공개 함수를 호출할 때도 전체 호출 경로를 명시 대응하고 한 후보로 저장한다.

호출 위치는 물리 graph ID와 `frame/invoke` 같은 qualified node key로 식별한다. 실행선/반환 대상은 그 호출이 실제로 속한 local frame에서만 찾고 갱신한다. private 반환은 그 frame을 끝내며 부모 함수의 기존 다음 동작이나 반환값을 묵시적으로 바꾸지 않는다. 같은 local ID의 형제 코드도 다른 source ID로 수집한다. `/node:frame/node:after`는 실제 leaf 관측 ID이고 `/graph:frame` author view와 구별한다. 기존 implementation+body target의 sourceOwner를 전달해 private 함수 ID·definitionHash를 재발급하지 않는다.

공개 계약·물리 graph·소유 구현·재귀적으로 읽은 모든 C# leaf·기존 import 관측은 같은 원자 그룹과 Review/Confirm·최종 read-CAS에 포함한다. 형제의 readonly 원문도 단순히 같은 local ID라는 이유로 누락하지 않는다. 원래 C# record의 bytes/mode·인수/출력·노드/핀·부모/형제 연결·권한을 유지한다. 임의 깊이 제한·자동 별도 함수/계약 복제나 새 권한을 추가하지 않는다. 기존 BlueprintTree의 전체/깊이 안전 예산을 재사용한다.

이번 실행 fixture는 직접 소유 동기 void+int out 공개 함수와 기존 ordinary switch-profile private caller다. caller 자체의 공개 분기/전달 중인 private 분기 계약, native whole-body/this, postCall wrapper, copy provenance와 등록 외부 import는 기존 복합 closure의 다른 경계다. 구형 private profile을 자동 승격하거나 전달 중인 실행 계약을 새 공개 enum으로 치환하지 않는다. 이런 보호를 새 필수 migration이나 무한 타입/소유 조합으로 확대하지 않는다. override 원계약·부모/참조 원본 보호는 그대로다.

## 검사 상태

집중 API에서 잘못된 frame·unqualified ID·낡은 증거·암묵적 profile 변경 거절, cold/receipt, 형제 C# 원문 변경의 최종 CAS와 실제 frame 반환→부모 continuation을 확인했다. 화면 검사에서는 Main 전환 대기 전에 private frame을 찾던 fixture 순서를 고쳤고, 작은 배율의 창 밖 반환 카드는 기존 전체 맞춤으로 조작한다. 실패 로그/DOM/픽셀을 보존하며 강제 클릭·제품 UI/레이아웃 변경은 하지 않는다. 기본 view/독립 창/프로젝트 왕복의 전체 검증을 완료로 표시하지 않는다.

최종 코드의 신규 LF/CRLF·패키지/전체 복원·수명관리 결과는 완료 후 아래에 기록한다. C# 생성기와 M11의 기존 소유/원문 보호를 재작성하는 단위가 아니다. 실제 Windows/WebView2·모바일·전체 UI·Space/Library 전달은 별개 미검증이다. 남은 M12는 실제 복합 caller/provider·native/whole-body·기존 copy provenance 및 등록 외부 import의 계약 결합이며 M4의 확정된 async 호환 정책은 유지한다.


## 최종 동결 검증과 보관

최종 제품/테스트/harness source는 `29e22100810cabe094777c389fa9d23b10ee8dda`다. 제품 코드는 b01ef16574fa1a8c9d90088d6bbc3361e1cc42ad와 같고 테스트의 conflict 대상 파일 표현식 한 곳만 바로잡았다. 이후 결과 문서 두 개만 갱신한다. no-hardlinks 독립 checkout·별도 home/NuGet·빈 엔진 캐시에서 **총 LF21·CRLF18·패키지/전체 복원/실패 수명관리6, 45단계(신규39·동등 재사용6)**가 통과했다. 각 EOL의 반환 계약/runtime16·소유 경계2씩 총36개는 위 stage에 포함되며 CRLF18개는 신규, LF18개는 동일 소스 근거의 재사용이다. 양쪽 checkout/빌드와 package/복원은 모두 신규다.

CRLF의 private caller API는 신규 실행이고 LF API는 동등 통과 근거를 재사용했다. qualified 호출·leaf ID, 다른 frame/낡은 증거 거절, branch capability가 없는 profile의 묵시적 변경 거절, 전체 그룹·cold/receipt·부분 Review 거절, 같은 local ID 형제의 raw 원문 최종 CAS와 실제 실행을 확인했다. private 분기 반환 뒤 부모의 기존 다음 줄과 반환값이 유지됐으며 C# record bytes·readonly mode·형제 graph를 보존했다. 여기서 profile 거절은 이번 연결의 지원 경계이며, 기존 methods profile을 영구 금지하거나 새 필수 자동 migration으로 확정하지 않는다.

LF normal/cancel/storage는 동등 재사용, LF conflict·CRLF loss/late 화면은 신규이며 명시한 private 호출, Root 입력/Undo/Redo·쓰기 실패·경합·cold receipt·늦은 분기명의 별도 Save, private 진입·readonly 공개 포트·local 반환 카드 연결·저장·Review 취소/Confirm·실행·최종 재시작을 확인했다. 두 EOL의 신규 회귀인 호출자 없는 기존 단일 provider·비void Root API·비void saved-copy(LF API/CRLF cancel 화면)와 최종 read-CAS, LF의 여러 provider API도 새 회귀다. 이 단위의 실제 데이터 fixture는 기존 void+int out이며 타입/깊이/소유 조합별 새 필수 행렬을 만들지 않는다.

제품 UI 트리·Core/생성기·M11 및 workspace Blueprint 소스는 직전 게시 2df737f와 같다는 source-equivalence.json을 별도 보존했다. 더 넓은 M11 문맥은 이전 근거와 구분하며 이번 신규39나 실기기 검증으로 표시하지 않는다. 집중 `/workspace/artifacts/v536-verification-managed/runs/d2e13bd63f7247b7aa85a4024bd73634.zip`(SHA256 `cc69cee2d2f677f76117ba98a28e208adbf563f4c0610b7522d2a960e3a3b3a6`)는 API/수정 후 화면의 선행 근거와 두 fixture 진단 실패를 보존하며 최종45에 중복 합산하지 않는다. 실패1은 Main 전환 전에 frame을 검사하던 대기 순서, 실패2는 작은 배율에서 창 밖 반환 카드의 클릭이었다. DOM/로그/픽셀과 실제 최종 스크립트·수정 역순으로 재구성한 진단 스크립트의 provenance를 구분해 보관했다. 정상 전체 맞춤 조작으로 통과했으며 강제 클릭·제품 레이아웃/생성기 변경·검증 완화는 없다. 추가로 첫 최종 시도의 conflict fixture가 관측하지 않는 옛 After.node.json을 바꿔 잘못 거절을 기대했다. `/workspace/artifacts/v536-verification-managed/runs/d89b0ba7943347f9a9d0185f0fcaf3c4.zip`(SHA256 `622d832656bbcb7d85bdb279ff76d9da9fe5e95fda4226f8d6bac383a094082b`)의 15개 통과/그 fixture 실패와 그 시도의 입력/로그·보존된 화면 픽셀을 보관했다. 관측된 NestedAfter.node.json으로 수정한 conflict는 신규 통과했다. 다른 6단계의 재사용은 같은 제품/Core/팩/UI/빌드/테스트 소스·SDK/NuGet과 변경한 if conflict 분기가 그 모드에서 실행되지 않는다는 근거를 fixture-correction-equivalence.json 및 실제 controller에 기록했다. 이는 소스 동등성이지 informational-version을 포함한 binary bytes의 동일성 주장이 아니다.

새 Windows 교차 패키지의 normal 화면과 전체 SHA/CRC·파일/디렉터리 mode 복원 뒤 late 화면, 실패/예외 임시 복사본 수명관리도 신규다. 실제 Windows apphost/WebView2·모바일·전체 UI·Space/Library 전달은 미검증이다. 기본 화면 배율의 모든 문맥·독립 창·프로젝트 왕복을 새 검증했다고 표시하지 않는다. 구 authoring에서 이 중첩 공개 계약의 미확정 checkpoint를 검증/편집하는 호환성도 보장하지 않는다. 원문·입력/checkpoint와 정상 롤백을 보존하고 자동 승격하지 않는다.

| 구분 | source commit | archive SHA256 | manifest SHA256 | bytes / 파일 / 디렉터리 |
|---|---|---|---|---|
| 최신 | `29e22100810cabe094777c389fa9d23b10ee8dda` | `74fbb8f6b4f5a91b1895b544dba79726b77dc7aa685d4744c88342358e786128` | `dd7967666126abdfb8516cc900c2058cace08c8e8615aed74b5dc384be5067cd` | 51346616 / 2370 / 147 |
| 정상 롤백 | `4e087d55098c4882f1cb670a173f048af89d7711` | `26dadada9e9d0d374e8fec48a903017e84367b90978eb6b595c4bae8bf1d18f1` | `7b489a2e4a225611f623fdf6686fd2cdb02ace90e0f228b3866c79aebb815bb2` | 51346011 / 2370 / 147 |

보관 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신 실행/복원은 신규이며 롤백 실행은 이전 정상 근거를 재사용하고 archive SHA를 재확인했다. 최종 `/workspace/artifacts/v536-verification-managed/runs/4364b7153c664211aef68ca04c7bde8f.zip`(SHA256 `d16155c7f821fdbda837f7558b7c0d4dd909425f1b79298474432e45bbe2bd90`)와 집중 증거·원본 입력·프로필·스크린샷·전체 manifest를 지속 보존했다. 자식 종료·소유권·보존 무결성 확인 후 이번 세 RAM root만 정리했다. 승인된 관리 latest/rollback 승격 외 기존 자료 삭제는 없다.

집중 여유 1884.01→1883.05MiB(사용 순증가 0.95MiB), fixture 실패 최종 시도 1882.92→1881.00MiB(사용 순증가 1.91MiB), 수정 후 최종 1880.96→1876.81MiB(사용 순증가 4.14MiB)다. 세 실행의 기록상 순증가 합계 7.01MiB, 단위 사전 점검부터 수집까지 파일시스템 관측 순증가 7.21MiB(코드/문서/진단 증거 포함)다. 수집 시 여유 1876.81MiB, stage 표본 최소 여유 1880.90MiB, 관측 cgroup memory peak 4114.07MiB다. persistent144MiB(안전64MiB 포함)·RAM3GiB+512MiB·memory7GiB+1GiB 예산을 낮추지 않았고 향후 증가량을 보장하지 않는다.
