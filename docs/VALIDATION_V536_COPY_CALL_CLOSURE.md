# v536 저장 copy의 여러 기존 호출 갱신

기준은 `0c7f1b7`의 [고정 7행 경계표](V536_ROW7_REMAINING_BOUNDARY.md)와 저장소
`196c605` v536의 기존 원본 계약 갱신이다. 가능한 변환 조합을 새 필수 항목으로
늘리지 않는다. 이번 단위는 **직접 단독 배정한 단일 target 저장 copy의 private
카드에서, 같은 프로젝트 소유 callee를 쓰는 여러 기존 execution-enum 호출을
함께 갱신**하는 조작이다. 공개 override 계약과 copy ID/출처는 유지한다.

## 한 후보와 명시 대응

`BlueprintCallAbiUses`는 실제 전체 tree에서 해당 callee의 모든 qualified 경로를
수집한다. caller/graph/공개 함수/참조 계약/본문 기록의 hash와 호출 목록을 고정한다.
누락·추가·잘못된 경로·오래된 binding은 거절하며, 기존 단일 API에 boolean을
넣어 이 범위를 얻을 수 없다. 2–32개 호출과 전체 요청/계획 크기 예산은 검증
경계이며, 모든 개수/조합을 실기기로 검증했다는 뜻이 아니다.

원래 대응창을 재사용해 호출·frame별로 기존 입력 또는 직접 값, 출력 소비자의
대응을 확인한다. 공유 import와 모든 wrapper/graph는 메모리 후보에서 함께 검증하고
기존 한 authorBatch·checkpoint CAS·복사본 review group으로 저장한다. callee·공개
함수·donor·부모·외부 팩은 쓰지 않는다. 본문 기록까지 포함한 전체 `source-ready`
검사를 통과해야 후보를 반환한다. 마지막 호출만 부적합해도 앞선 호출/import를
따로 적용하지 않는다. C# 본문을 추측해 재작성하지 않는다.

같은 로컬 노드 ID가 Root/private 또는 여러 frame에 있어도 소비자 재연결은 해당
frame에만 적용한다. private graph 내부를 부모 노드 ID로 탐색해 바꾸지 않는다.
기존 소유권·source/물리 파일·project/view nonce·receipt·응답 유실 조회와 명시적
Review/Confirm은 유지한다. 실패 시 기록을 무조건 지우거나 기준을 자동 갱신하지 않는다.

## 검증 대상과 초기 실패

격리 fixture의 두 private frame은 같은 `native` ID를 쓰고 각각 직접 값3/5를
선택한다. 원래 정확한 int64 local·실행선·CPP source·public 계약을 보존한다.
Root와 private에 같은 ID를 둔 3호출 후보도 순수 검사로 구별한다. 기본/독립
정보 창의 취소·불완전 값·Undo·쓰기 실패·충돌·응답 유실·cold·Review/Confirm과
마지막 비호환 대응·누락 use·경로/binding 위조의 전체 미적용을 실제 경로로 검사한다.

초기 순수 검사에서는 마지막 frame의 출력 타입 오류가 노드 정의 검사만으로
거절되지 않았다. 전체 본문 기록의 `source-ready` 검사를 추가해 수정했다.
Root 혼합 표본의 `switch` 프로파일 지정 누락은 정상 `GRAPH_CONTROL` 거절로
확인하고 fixture만 바로잡았다. 첫 화면 진입은 정규화된 `calledFeature` 대신
`feature`를 조회하던 연결 오류를 수정했다. 초기 실패 로그/fixture는 scratch에
보존하며 최종 통과 수에 포함하지 않는다.

74개 canonical 리소스 중 기존 어댑터2개와 descriptor만 바꾸며 HTML/CSS/배치는
유지한다. 시작 여유958.7MiB에 디스크200MiB·RAM 임시 출력768MiB 예산을 확인했다.
기존 독립 checkout을 FF하고 순차 검사한다. 이번 검사 소유 임시 복사본만 증거
보관 후 정리하며 기존 보관 빌드/원본/SDK/로그/사용자 자료는 삭제하지 않는다.

## 남은 원래 범위

- 새 immutable copy 초안의 복수 use 갱신 어댑터, Root 카드에서 직접 시작하는
  복수 use 갱신, 등록 callee/all-target의 별도 source receipt 결합은 이번 수용과
  구별한다. 자동 전체 target 복제와 독립 계약 복제는 필수 요구가 아니다.
- 다른 frame 계약/본문의 동시 편집과 opaque/whole-body의 수동 C# source closure는
  아직 결합하지 않는다. 현재 별도 입력은 지우지 않고 차단한다. 기존 4/8행 및
  A4–A6와 같은 항목으로 한 번만 관리한다.
- 9행 타입/표시명, I6/B2와 M4/M11/M12, 신규 이미지/협의/렌더 backend 및 실제
  Windows apphost/WebView2·모바일 기기/터치·Library 전달은 별도 미완료다.

확정된 검사/checkout/패키지 결과는 후속 evidence에 기록한다. 전체 7행/I5/UI
완료나 실제 기기 실행으로 합산하지 않는다.

## 확정 집중 검사

최종 제품의 실제 엔진/렌더러 12흐름 83확인과 순수 closure4확인이 통과했다. 기본/독립 창의 취소·cold·CPP compiler Confirm, 누락/위조/마지막 비호환 대응의 전체 미적용, 쓰기 실패·물리 source/CP 충돌·응답 유실·Undo 후 새 대응 재시도 및 다른 frame 입력 보존을 확인했다. 단일/root/새-copy 기존 지원도 회귀로 지켰다. 독립 checkout/새 패키지는 별도 후속 evidence다.

## 독립 checkout·새 교차 패키지

소스 커밋 `ebfc040ecbb3b736727915e9a99ffc26f80a9b8c`의 변경12개 Git blob과 기존 autocrlf/clean을 확인했다. Native/CLI Release·Linux 엔진 및 독립 UI2흐름22확인·closure 순수4/기존 순수6확인이 통과했다. 새 RAM Windows x64 교차 패키지의 restore·Release·MCP·생성·probe·패키지 자체 독립 창 UI12확인까지 6단계가 통과했다. 전체 2348개/manifest 2347개 목록·SHA·Core/Native DLL 및 소스 바이트를 확인했다.

manifest SHA `a81965bfff3b3007bfae2083c85b632d5a5d21bf5ec71f7ab9e27bf4735acc77`, Native DLL `0aebc2c25d3027433fc8cb9371d893b92049debc4d03844a621d5d6ebfbe040d`다. 전체 manifest·fixture/로그/프로필 증거를 보관한 후 이번 임시 패키지만 정리했다. 보관 패키지/SDK/원본/기존 자료는 그대로다. 다운로드 가능한 새 보관 패키지나 Library 전달이 아니며 실제 Windows apphost/WebView2·모바일 기기는 미검증이다. 후속 최종 커밋은 문서/evidence만 바뀌므로 실행 소스는 이 소스 커밋과 같다.

초기 마지막 출력 검증 누락·Root fixture 프로파일 오류·모듈 진입 조회 실패도 각각 scratch 로그에 보존했다. 전체 source-ready 검사와 정확한 정규화 필드/fixture 수정 후 재검증했다. 첫 시도나 진단 실패를 통과 수에 합산하지 않는다.
