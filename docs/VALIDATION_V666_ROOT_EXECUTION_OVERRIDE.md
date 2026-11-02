# v666 M12 자식 소유 공개 분기 반환

## 원본과 지원 범위

저장소의 v666 ZIP(SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)만 기준으로 삼았다. `dist/blueprint.js` 969–976의 공개 분기/반환, 718–739의 종료점 선택과 `dist/app.js` 2469–2476의 원계약 유지가 근거다. 기존 원본 팝오버·카드·레이아웃을 재사용하며 CSS/HTML은 변경하지 않았다.

직접 소유 함수의 동기 void·값 입력·선택적인 int out 하나에서 자식이 직접 선언한 ordinary switch Blueprint target(code/export, native context·call·중첩 없는 Root)의 기존 공개 분기/None 반환을 편집·저장·실행한다. 등록 외부 부모는 기존 dependency registry 및 readonly 관측만 사용한다. 상속된 Blueprint 실행도 선언 원본의 source identity를 보존하며, 부모 본문을 자식 locator로 편집하는 것은 거절한다.

공개 입출력/분기 ID·계약, C# 원문, 부모/참조 원본·권한을 변경하지 않는다. 반환 entry/edges/exits만 바꾸고 전체 관측 소스를 원자 Review 그룹과 checkpoint/final CAS에 보존한다. 최신 입력과 Save journal은 최초 외부 부모 관측 해시를 유지한다. 저장 직전 부모 변경을 새 관측으로 대체하던 결함은 이 해시 결합으로 수정했다.

## 검증 상태

집중 검사 및 최종 동결 소스의 독립 LF/CRLF·새 Windows 교차 패키지·전체 압축 복원 검증 결과는 완료 후 이 절에 확정 기록한다. 초기 nullable 컴파일 진단, 최초 외부 부모 변경 재현과 검사 runner의 실행 전 들여쓰기 진단도 증거에 보존한다. 실패를 통과로 세지 않는다.

## 잔여와 한계

등록 외부 함수 계약 자체의 반환 편집, 나머지 원래 데이터/호출 문맥과 M4는 별도 잔여다. 공개 override 계약 변경·부모 원본 쓰기는 정상 보호이며 독립 계약 복제/구형 profile 자동 migration은 필수 요구가 아니다. M11은 회귀 검증 대상으로만 유지한다. ABI/고급 타입/표시명·종류 실행 표현/사용중 삭제 대응·B2 권한 backend·V2–V9 등 고정 ledger는 확장하지 않는다.

실제 Windows/WebView2·모바일 기기·전체 UI 및 Space/Library 전달은 이번 Linux hosted UI/CLR와 교차 패키징으로 완료 처리하지 않는다. main과 과거 보관 자료는 보존하며, 이 실행이 소유한 임시물의 승인된 수명 관리와 최신/정상 롤백 두 패키지 보관만 사용한다.
