# v536 same-contract copy의 native 별칭·외부 import 보존

원래 7행에서 **로컬 정보 함수에 직접 배정한 단일 target copy가 기존 native 매개변수 별칭과 등록 외부 함수 import를 가진 채 본문을 편집**하는 최소 단위다. 구현하는 함수 자체가 외부 namespace인 copy나 다중 target copy로 확장하지 않는다. 원본 v536의 같은 입력/출력 개수·타입·순서를 유지한 가져오기와 기존 C# 편집을 재사용한다.

C# 부모의 연결은 이미 존재했다. 최초 API 검사에서 기존 등록 계약 증거를 빼고 저장하여 정상 거절됐다. 화면은 원래부터 `functionDependencies`를 보관해 제출한다. API fixture를 같은 절차에 맞추고 외부 계약 증거 누락·잘못된 import 별칭·실제 외부 매개변수 타입 변경의 전체 미적용 검사를 추가했다. 이 분석 뒤 Blueprint 변환 부모에서 실제 결함을 찾았다. 고정 계약의 whole-csharp 본문도 import가 있다는 이유만으로 거절됐다. 정보 편집기가 이미 관측·검증한 functions map을 내부 typed 인자로 전달하며 공개/native 서명이 완전히 같고 원래 typed import 모두가 현재 선언과 일치할 때만 허용한다. 일반 root JSON의 임의 계약이나 서명 변경으로 우회할 수 없다. 기존 원계약·출처·CAS·Review/Confirm·레이아웃과 권한은 유지한다.

공개 amount/count와 nativeAmount/nativeTotal, External.Fields::Echo의 foreignInput/실제 구현 externalValue, import ForeignEcho의 타입을 분리한 격리 fixture다. 기존 alias·typed import·본문의 calls.ForeignEcho.Invoke(nativeAmount)와 출처·64비트 원문을 보존한다. 등록 함수/구현/body와 부모 원본 파일은 전부 바이트 비교한다. 확정된 변경 없는 header는 dirty 단위에 포함되지 않으므로 실제 등록 경로에서 읽어 검증한다. 이를 미확정 생성 header 누락과 혼동하지 않는다.

집중 11흐름과 기존 경로 영향 4흐름, 총 **63개 확인**을 통과했다([기록](evidence/v536-information-copy-imports/focused-verification.json)). 기본/독립 창·프로젝트 전환·불완전 입력 cold·Undo/Redo·팝업/전체 취소·저장 실패/재시도·응답/조회 유실 후 재시작/중복 방지·저장된 다른 창 경합·실제 부모/외부 계약 경합·Review 취소/재검토·명시 Confirm을 포함한다. C# 부모와 같은 문맥의 Blueprint 부모, 미확정/확정 copy의 재편집도 구분했다. 테스트 원문과 외부 원본은 보존하며 실제 사용자 프로젝트/유료 AI는 호출하지 않았다.

외부 함수를 *호출하는 로컬 copy*의 지원을 검증한 것이며, 외부 함수를 *구현하는 copy* 전체를 완료한 것은 아니다. 다중 target·native 별칭/import 자체 변경의 다른 명시적 대응·직렬 copy whitelist 밖 원본 graph는 [고정 7행](V536_I5_6_COPY_INHERITANCE_SCOPE.md)에 남긴다. 오버라이드 타입/핀 수/역할/반환 구조 변경 거절은 정상 보호이며 독립 계약 복제는 필수 제외다. 8행 복합 계약 closure·9행 고급 타입/표시명 및 I6/B2/A4~A6/M4/M11/M12는 별도다.

제품 코드 3파일의 좁은 검증 연결을 수정했다. C# 부모의 변경 없는 Retained 경로 4흐름은 초기 통과 근거를 재사용하고 현재 코드의 C# 화면을 영향 회귀로 재확인한다. 수정된 Blueprint 부모 경로는 새 API/독립 창과 실패/복원 경계로 확인한다. 일반 root 요청에 featureContracts/stableImports JSON을 넣어도 거절되는 순수 가드 2확인은 별도다. 이전 패키지 코드 동등성은 수정 전 진단에만 해당하므로 최종 검증 근거로 재사용하지 않으며, 새 Native/Linux 빌드·교차 패키지를 별도로 검사한다. 실제 Windows/WebView2·모바일 기기·Library 전달 및 전체 UI는 미완료다. 추가 기존 자료는 삭제하지 않고 이번 검사의 자체 fixture만 증거 보관 후 정리한다.

최종 독립 checkout 검증 및 게시 결과는 다음 기록에서 구분한다.
