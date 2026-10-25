# 정보 함수의 읽기 전용 등록 계약

고정 I5-6 7행의 첫 단위다. 프로젝트가 직접 등록한 팩의 함수와 프로젝트 소유 함수를 함께 호출하는 **소유 구현**에서, 사용자가 편집한 C# 본문과 소유 함수 계약을 한 후보/CAS로 검증한다. 등록 팩의 함수 선언이나 구현을 편집 대상으로 승격하지 않는다. 원본 v536의 기존 구현 선택·C# 편집·호출 매핑 화면을 사용하며 새 HTML/CSS·패널·권한은 추가하지 않았다.

## 계약과 저장 경계

- `InformationFunctionDependencies`는 현재 caller ID/원문 해시, 프로젝트 manifest, 직접 등록 팩 manifest와 선택된 함수 선언의 원래 receipt를 결부한다. 실제 파일 관측도 저장 후보에 넣는다. typed import가 이미 다르면 명시적 갱신 없이 진행하지 않는다.
- 등록 선언은 검증용 함수 집합에만 추가한다. 소유 선언의 순회·변경·소스 저장 집합과 분리하여 외부 등록 원본이나 provider 본문을 수정하지 않는다. provider 선택·본문 읽기·추론·실행은 수행하지 않는다.
- 기존 본문 편집/호출 선택 때 receipt를 보관하고 불완전 입력과 함께 복원한다. 이후 등록 계약이 바뀌면 새 receipt로 이전 입력의 기준을 덮지 않는다. 누락·위조·stale proof와 타입/컴파일 오류는 전체 미적용이다.
- 직접 등록 함수 선언만 제한적으로 읽는다. 파일/합계/수량 제한과 링크 경로 거절을 유지하고, 관측 중 바뀐 내용도 거절한다. 등록 변경 자체는 별도로 확정해야 한다.

## 실제 확인한 범위

격리 fixture에서 외부 `External.Fields::Echo`와 소유 함수의 호출을 갖는 소유 whole-body caller를 사용했다. 소유 callee 계약·native 본문·caller 수동 C#·typed import/context를 함께 저장한다. 임의 C# 자동 재작성은 없다. 실제 계정·유료 AI·사용자 프로젝트 실행은 사용하지 않았다.

순수 후보에서는 missing/forged receipt, caller hash, 다른 소유 ID, 오래된 typed import, 잘못된 C#, 실제 등록 manifest/선언 변경을 거절했다. 외부 provider 본문을 격리 fixture에서 잠시 없애도 순수 계약 후보를 구성할 수 있음을 확인했다. 이 검사는 provider 없이 실제 프로젝트를 컴파일/실행할 수 있다는 뜻이 아니다.

실제 엔진에서는 누락·위조·등록 변경에 대한 checkpoint 보존, 원자적 저장·재시작·컴파일 Review/Confirm과 외부 팩 불변을 확인했다. 기본 창과 독립 창의 기존 편집창에서 취소·불완전 입력·Undo/Redo·cold 복원, 저장 장치 오류, 응답/receipt 유실 뒤 조회로 중복 없이 복구, 변경된 등록 계약에 대한 보관 입력 보호를 확인했다. 선별 결과와 창별 추가 수용 결과는 마감 증거에 기록한다.

이전 다중 forwarded 호출의 후보/거절 회귀 6개와 속성 Read/Set/RefCell 계약 보호 회귀 3개를 보존했다. 속성 fixture는 실제 화면과 같은 명시적 등록 receipt를 제출하도록 갱신했다. 기존 property receiver/type/원본 관측 검사를 완화하지 않았다.

집중 결과는 **30 check**다(순수 후보 4·실제 API 3·렌더러 14·영향 회귀 9). 실패한 검사 문법/재실행과 이전 게시의 검사를 합산하지 않았다([기록](evidence/v536-information-registered-contracts/focused-checks.json)). 기본/독립 창의 충돌·취소·프로젝트 전환을 각 실제 경로로 마감했다.

Native Release 경고/오류 0건, Linux 빌드 stderr 0, 변경 JS 구문 및 고정 리소스 manifest 갱신을 확인했다. [C# 편집창](evidence/v536-information-registered-contracts/caller-csharp.png)과 [독립 창](evidence/v536-information-registered-contracts/independent-final.png)은 실제 렌더 결과이며 원본과 전체 pixel 일치를 주장하지 않는다. HTML/CSS 네 파일과 본문 편집창 배치를 변경하지 않았다([근거](evidence/v536-information-registered-contracts/layout-evidence.json)).

## 남은 고정 범위

7행 전체는 아직 완료가 아니다. 소유 saved copy의 owner/assignment/provenance receipt와 원래 copy snapshot을 이 정보 함수 계약 경로에 연결해야 한다. 공유 원본·부모·외부 팩은 변경하지 않는다. 등록 함수의 상속 선언과 상속 구현도 완전한 부모 계약 증거를 결합하기 전까지 기존 안전한 거절을 유지한다. 고급 핀 타입은 9행의 별도 범위다.

8행의 여러 함수 공유 caller, 9행의 고급 타입/표시명 및 기존 I6/B2·A4~A6/M4/M11/M12는 후속이다. 실제 Windows apphost/WebView2·모바일 기기·Library 전달은 미검증이다. 교차 패키징과 실제 Windows 실행을 구분한다.
