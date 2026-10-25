# v536 여러 out 타입과 공유 소비자 결합

고정 8행의 다음 단위다. 같은 정보의 직접 소유 함수 2~8개, import 없는 code/export callee와 선택 함수 call/export만 있는 caller라는 경계를 유지한다. 이름·위치·수·값/out 역할, 모든 값 입력의 타입과 반환을 그대로 두고 scalar out 타입을 바꾼다. 기존 scalar는 bool/int/long/float/double/string이다. 새 메뉴·레이아웃·함수/계약 ID·권한은 만들지 않는다. 7행 독립 복제 정책은 여전히 답변 대기다.

출력 writer와 caller의 기존 호환 출력 대응을 원래 스냅샷에서 먼저 검증한다. 같은 caller에 A와 B가 있고 A의 원래 출력이 B의 인자로 쓰이면, A에 대해 사용자가 명시한 출력 대응을 원래 graph의 복제본에 적용한다. 이 예상 graph와 현재 내부 후보의 선택된 B call·연결·제어 경로·기타 필드를 대조하고 검증된 다른 call의 서명/인자 변화만 구분한다. 그때만 내부 mapping 복제본에 현재 내부 graph hash를 설정한다. 원래 요청·선택·최종 update hash·물리 source 기준·checkpoint CAS는 바꾸지 않는다. 이미 처리한 생산자의 검증된 대응만 사용하며 미래 선택이나 임의 값으로 연결하지 않는다.

caller의 값 인자는 원래 바인딩을 유지하며 새 값/교환/해제 선택을 이 단위에 섞지 않는다. 소비 중인 출력을 null로 버리거나 호환되지 않는 타입으로 대응하면 전체 거절한다. callee의 C# 형식 매개변수·본문은 원래 상태를 유지하고, public writer 값과 consumer 출력이 달라지는 부분은 사용자가 명시한 선택만 반영한다. 기존 후보/CAS·receipt·Review/Confirm으로 선언·import·writer·호출자 전부를 저장한다.

## 검증 상태

격리 fixture에서 A.count→B.amount, B.count→caller 반환이라는 연결을 두고 두 count를 long에서 double로 바꾼다. writer는 각 함수의 기존 real 값을 선택한다. 소비 중인 기존 long count는 각 함수의 호환 long return으로 명시 대응한다. 그 결과 B.amount는 A.return을, caller 반환은 B.return을 사용해야 한다. C#의 원래 long count 계산·설명 문자열·선택 외 입력과 exact64 값, writer/call ID 및 제어 경로는 보존한다. 기존 count 계산값을 임의로 double 변환했다고 주장하지 않는다. 추가 순수 후보는 명시 bool/한글 string 리터럴도 검사한다.

집중·회귀·checkout·교차 패키지 결과와 로그/화면/해시는 이 단위 마감 시 기록한다. 사용자 프로젝트·계정·유료 추론을 사용하지 않는다. 실제 Windows/WebView2·모바일 기기 실행 및 Library 전달은 별도 미검증이다.

## 남은 경계와 공간

입력/출력 타입 동시 변경, 핀 수·순서·역할·추가/삭제·반환 변경, C#/혼합 target·중첩/private/whole/postCall, copy/상속/등록/owner 속성 혼합은 별도 미완료다. 9행 named 타입·표시명 및 I6/B2/A4~A6/M4/M11/M12도 유지한다. 기존 명세의 엔지니어링 미구현이며 7행 외 새 사용자 설계 결정으로 돌리지 않는다.

작업 볼륨 시작 약28MiB와 이전 패키지의 실제 증가량 약13MiB를 대조해 순차 RAM 경로를 사용한다. 실행 직전 공간/메모리를 재확인하고 기존 파일은 삭제하지 않는다. RAM 패키지/fixture는 해당 exec 동안만 이용하며 로그·선택한 화면·해시를 작업 볼륨에 보존한다. RAM 파일을 보관본이나 사용자 전달로 표시하지 않는다.
