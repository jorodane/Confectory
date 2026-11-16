# Private C# 본문·공개 입력 이름 공동 저장 검증

게시본 `360e0aebd8bf9283bee42bb0abdf14d50b09e7ff`와 이전 증거를 보존하고 runtime `4c510278d3f04395ef471813e8645f724cff4bcc`의 [한정 흐름](V666_PRIVATE_PIN_RENAME.md)을 **최종 신규43·재사용0·실패0**으로 검증했다. LF22·CRLF13·새 패키지/전체 ZIP 복원8이다. Linux 실제 .NET 실행과 Chromium 자동화이며 실제 Windows/WebView2·물리 기기 및 전체 UI 검증과 구분한다.

- 직전 온전한 패키지에서 private 본문/helpers 계획과 다른 소유 함수의 공개 입력 `amount → receivedAmount` 계획은 각각 유효하고 원래 프로그램40을 실행하지만, 공동 제출만 쓰기 없이 거절되는 것을 새로 재현했다.
- 기존 함수 상세창의 C# 이름 편집과 private/native 본문·보조 함수 편집을 한 Save로 결합했다. 양방향 편집 순서에서 같은 후보이며 원래 pin의 caller 바인딩을 그대로 보존한다. private 함수/프레임/code ABI·nativeAmount/nativeCount·위치형 import 헤더·타입/역할/인자 수/순서·반환과 모든 독립 노드/연결/좌표·정확한64비트 local을 보존했다. private code/helpers와 직접 작성한 일반 본문으로 실제20을 실행했다. 남은 원래 C# 파일과 독립 record bytes/mtime를 유지했다.
- 잘못된/누락 pin 대응, 타입·역할·인자 수·순서 변경과 private ABI 변경·stale source/flow·helpers 경계 탈출·잘못된 마지막 C#은 모든 원본을 보존하며 거절했다. 캡처 계획/원래 function·source·flow hash·노드/locator·group·읽기 경로·함수 서명·caller 바인딩 변조도 검사했다. 변경된 caller 바인딩과 source proof hash를 함께 다시 써도 원래 계획의 재생 결과와 다르면 거절한다. physical read 버전은 기존 Review/최종 CAS가 검사하며 순수 shape guard와 구분한다.
- source Undo는 독립적인 공개 이름 변경을 남기고, 두 번째 Undo는 그 이름 변경만 취소하며, 두 Redo는 각 중간 계획과 최종 두 계획을 정확히 복원했다. 원래460px 카드/상세창·일반/독립 화면, 취소·미저장/저장 cold·쓰기 실패/재시도·저장/조회 응답 유실·중복 Save 방지·다른 창/프로젝트 경계·늦은 설명/후속 Save를 검증했다. UI/리소스/CSS를 변경하지 않았다.
- 정보/함수 설명과 private 본문·helpers의 후속 명시 저장, 이름을 바꾼 함수의 설명·두 번째 본문 저장 모두 통과했다. 현재 pin identity로 저장하면서 receipt에는 최초 `amount → receivedAmount` 대응과 원래 function/source/flow hash·읽기 기준을 유지했다. 캡처 계약·구조를 임의로 추가 변경하는 저장은 받지 않는다.
- Review 뒤 private graph·독립 원문·선택 node·공유 caller graph·변경 대상 함수 원본이 바뀌면 최종 Confirm 전체를 거절하고 peer text/checkpoint를 보존했다. 정확한 복원 뒤 새 Review/Confirm으로20을 실행했다. Review 취소는 원본을 바꾸지 않았다.
- 기존 계약 불변 private 단독/guard·retained 필수/독립 code 계획·whole/native API·nominal 혼합 import·등록 helper를 수정본에서 새로 회귀 검사했다. 새 패키지에서 정상 UI 저장/실행을 검사하고 전체 ZIP의 파일·해시·모드를 확인해 별도 추출한 엔진에서도 응답 유실·늦은 입력·표시와 실행을 검사했다. package 복사/UI/변조 실패 주입에서도 원래 패키지·런타임을 보존했다.

제품 변경은 `InformationFunctionWholeBodies` 한 파일이다. 기존 private/whole 행의 계약과 native 서명을 그대로 유지하면서, 일반 native 행에 한 개의 기존 값 pin 이름을 새 이름으로 대응하는 경우만 결합한다. 기존 단독 validator/assembled compiler·전체 읽기·한 후보·Review/Confirm·최종 CAS를 재사용한다. 캡처 재생에서는 검증된 하나의 공유 source 변경과 다른 scope의 원래 관측을 결합하고, 서로 다른 두 변경은 거절한다. 새 schema/receipt/profile·권한·경로·C# 생성/정규화·객체/참조 의미·자동 async 전환은 없다. 정보별 struct·종류 enum·모듈 interface와 기존 명시 async 전환 전 sync caller 오류를 유지한다.

개발 15단계와 최종 동결본43단계는 별도 증거다. 개발 중 실패·정정 근거는 {"dev-private-pin-rename-native": "Fixture incorrectly expected public argument names in a positional import declaration. The valid candidate preserves the exact original (long, long) import text; only the caller node signature and selected binding key change. Preserve the failed log/request/candidate; assert exact caller header bytes and rerun only this pure test, without rebuilding or changing the product.", "dev-private-pin-rename-ui": "Inherited source-only UI fixture expected one Undo to remove the second function. Preserved trace proves one Undo correctly removes only the explicit CSharp body while retaining the prior public rename. Product unchanged; require two independent Undo/Redo steps and assert each intermediate plan exactly, then resume UI and not-yet-run guards/late checks.", "dev-private-pin-rename-ui-history": "Original UI Save, cold, Review cancellation/Confirm and actual20 all passed, including the full renamed caller graph check. A later generic driver callback inherited the source-only expected amount binding key. Override that expected caller_arguments table to receivedAmount without changing the product, preserving the failed post-Confirm fixture/evidence and rerunning only UI plus not-yet-run guards/late checks."}로 보존했다. 보조 설정 정정은 1건이며 경로 확인용 준비 assertion으로, 제품/검증 실행을 바꾸지 않았다. 개발의 원래 요청·후보·Undo trace·실패 로그와 정정 후 실행을 모두 보존했다. 최종 43단계는 동결본에서 새로 실행했으며 이전 성공 결과를 재사용하지 않았다.

직전 `f2e72bacdcd800c6554c294981de4a98481f93c1` 패키지 archive와 추출된 모든 파일/디렉터리/hash/mode를 확인했다. 같은 추출본의 구 guard는 새 pending 계획을 `False`로 거절했고 현재 guard는 수용했다. 두 guard 실행 전후 원본 source hash·inode·mode·mtime가 같았다. 별도 source-only 복사본에서는 pending/checkpoint와 기존 output cache를 제외하고 같은 온전한 직전 CLI/providers로 새로 빌드해20을 실행했다. 원래 Confirm된 source bytes/mode/mtime도 보존됐다. 이 결과는 **직전 pending 검증기의 새 결합 수용 제약**이며 모든 기존 ABI 실행이나 일반 프로젝트 읽기가 불가능하다는 뜻은 아니다. 더 오래된 Reference parser 제약은 이전 기록으로 유지하며 이번 새 측정으로 세지 않았다. 이전 바이너리·원본·보관 패키지를 다시 쓰거나 자동 migration/downgrade하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 4c510278d3f04395ef471813e8645f724cff4bcc | 698a2c55c5fa39f92d95925b70a82fa13c15a05f6d152fd90024046d4a876a04 | 54148835 |
| rollback | f2e72bacdcd800c6554c294981de4a98481f93c1 | 6d85a7d00a96eacc8f8e617e0f9a548134f311a611a3e181ed2c7ad723abecd7 | 54145011 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/a1074d4ad09240ce8e10f393bfdd7b70.json` · evidence SHA256 `111f6aab626c3fdfb186a4347b3d967fb0f3902efc39d296e9c42eea0c284279`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/7ae709800cfe4c96a211d1df2da08b57.json` · evidence SHA256 `74239e7673ac5674faccbd22e465eecc3976c79b3a14dfc9ecd1842e5e161e59`.
두 패키지와 두 evidence hash를 재확인했다. 이번 인증된 임시물과 기존 두 세대 package 교대만 정리하며, 원본 checkout·360e0ae 게시본·이전 증거와 이전 미인증 IPC의 `/tmp/cv-5xgaibtx`를 보존했다. 디스크 여유 24255430656bytes(22.59GiB)다.

이 한 공개 pin 이름 대응·private 편집 흐름의 저장/복원/실행으로 이번 단위를 닫는다. 고급 타입·ref/out·반환/구조 변경과 opaque/private import 계약 결합·구 Reference reader/전체 UI 교환을 완료로 세지 않는다. 가능한 타입/문맥 조합을 새 필수 매트릭스로 늘리지 않는다. 실제 Windows/WebView2·기기·IME/GPU/audio·전체 UI는 미검증이고 초기 빈 화면 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
