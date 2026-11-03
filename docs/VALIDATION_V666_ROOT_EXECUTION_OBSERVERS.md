# M12 공개 분기 갱신과 기존 ordinary 소비자 관측

기준은 저장소 v666 `dist/blueprint.js:135`의 참조 정의 기반 call 포트와 `:248`의 출력→분기→다음 실행이다. 공개 분기 계약을 갱신할 때 기존 native import나 legacy wrapper가 같은 함수를 ordinary `IInvoke`로 소비하고 있어도 그 소비 의미를 바꾸지 않아야 한다. `:1504–1512`의 명시 wrapper 계약 갱신과 `:1514–1519`의 OriginalResult 연결은 기존 NoBranch adapter의 자동 재해석과 구별한다.

실제 직접 call은 계속 명시 대응한다. 같은 소유 프로젝트에서 실제 함수 의존성이 있는 native 코드·ordinary wrapper는 전체 원본 문맥을 먼저 검증하고 관측 그룹에 포함한다. 사용하지 않는 import 선언만으로 새 공개 분기 caller를 만들지 않는다. 선언된 Blueprint target이 누락됐거나 원문·서명·문맥·receipt가 이미 낡았다면 거절한다. ordinary observer의 기존 profile은 바꾸지 않고 Core의 전체 원본 검증을 적용한다. 공개 분기를 직접 dispatch하는 target/caller의 기존 profile 보호는 유지한다. 부모·참조·외부 소유자·copy의 별도 경계나 override 계약을 열지 않는다.

native 코드 정의는 imported 함수의 전체 계약 hash를 포함한다. 기존 원문이 준비된 상태인지 확인하고, 후보 전후의 정의에서 해당 callee의 hash만 달라졌음을 증명한 뒤 생성 record의 `definitionHash`만 갱신한다. C# source/helpers, source identity, implementation context, 입력/출력·node ID·graph·연결은 보존한다. 다른 정의 변화나 stale record는 자동 수리하지 않는다. scope object와 선언의 읽기 전용 raw receipt도 checkpoint/Review→Confirm/최종 CAS에 결합한다.

집중 fixture는 원래 implicit-profile로 단일 래핑한 native consumer와 기존 NoBranch wrapper를 직접 caller 옆에 둔다. native C#의 CRLF·원래 파일명/CallerMemberName·scoped import와 출력20을 검증한다. legacy wrapper는 기존 NoBranch0을 받고 자신의 분기17·출력30을 계속 실행한다. 새 공개 결과를 받는 소비자로 조용히 바꾸지 않는다. 실제 public caller만 선택한 성공 포트로 반환하고 원래 out10은 먼저 발행돼야 한다. 생성 record 이외의 원문·graph·readonly0400 선언은 바이트와 mode를 대조한다.

검증은 누락/변조 observer·native record·source receipt, 잘못된 소유 문맥·legacy public 위장, Save 전/Review 뒤 원문·scope 경합, 원자 저장·반복·부분 Review 거절·cold·완료 후 그룹 퇴역과 후속 원문 입력을 포함한다. UI normal/cancel/Undo·저장 실패·충돌·응답 유실·늦은 입력, 독립 LF/CRLF·새 교차 패키지/전체 압축 복원 결과는 최종 동결 뒤 기록한다. 초기 집중 fixture가 이미 provider가 있는 함수에 새 provider 준비 API를 잘못 사용한 실패는 제품 실패와 구분해 보존한다.

CSS/HTML·원본 레이아웃·공개 IO·권한·원래 C#을 보존한다. 승인된 실행별 임시물 정리와 최신/롤백 보관만 사용한다. 실제 Windows apphost/WebView2·모바일·전체 UI·Space 전달은 별도 미검증이다. 원래 wrapper의 명시적 실제 공개 결과 연결, 같은 계약 copy·자식 전체 갱신과 등록 import 관측의 잔여는 [유한한 마감표](M12_CLOSURE.md)를 따른다.
