# v536 공유 호출자의 일반 out 이름 결합

고정 8행의 다음 지원 단위는 같은 정보가 직접 소유한 함수 2~8개의 out 이름 변경이다. 같은 위치·타입·값/out 역할·핀 수와 반환을 유지한다. callee는 import 없는 code/export leaf이고 shared caller는 선택한 함수의 call/export만 사용한다. 값 입력 이름을 함께 편집해도 동일한 원래 핀 대응을 유지해야 한다. scalar 타입 변경과 out 계약을 한 그룹에서 섞거나 추가 caller 선택·C# 편집·중첩·copy를 섞지는 않는다. 7행 독립 복제 정책은 답변 대기이며 새 ID/함수/호출 대상은 만들지 않는다.

기존 원본 상세창의 안정된 핀 대응을 각 원래 스냅샷에서 먼저 검증한다. 각 closure를 내부 overlay에 순차 준비하고 공유 소스는 한 번의 원래 hash로 제출한다. 이전 closure가 바꾼 출력 이름이 다른 call의 값 인자나 최종 exit에 사용되면 같은 call ID/출력 핀의 새 이름으로 전파된다. 이는 명시된 원래 핀의 이름 변경이며 다른 출력으로 추측해 연결하는 동작이 아니다. 코드 매개변수·C# 본문·writer ID·제어 경로·값은 보존하고 기존 후보/CAS·receipt·Review/Confirm을 사용한다. 중간 결과는 live 상태나 파일에 쓰지 않는다.

## 검증 상태

격리 fixture는 같은 count 이름을 가진 두 out 함수를 직렬로 호출한다. A.count가 B.amount에 연결되고 B.count가 caller 반환으로 연결된다. A.leftCount/B.rightCount 편집 뒤 두 연결과 공개 출력 이름이 함께 바뀌되, 각 code의 count 매개변수·본문·설명 속 count 문자열과 정확한 64비트 값은 유지한다. 편집 역순도 같은 결과여야 한다. 구현 커밋은 `acbaaf312ab014530a3c6526b87c95b4be7bd522`다. [집중·회귀·checkout 근거](evidence/v536-information-shared-output-names/focused-verification.json)에 명령·결과·로그 해시를 남겼다.

| 검사 | 통과한 내용 |
|---|---|
| 순수 후보 3 check | 사용자 요청 불변·원래 hash 한 개씩, 두 writer/공개 이름/소비 연결, 편집 역순 동일 결과·C# 원문, 마지막 타입/역할/반환/삭제/잘못된 대응/중복/오래된 source 및 추가 C#/의존 계획 전체 거절 |
| 실제 API 3회 / 7 check | 한 후보 Save·cold·compiler Confirm, 마지막 함수 오류 전체 미적용, 물리 caller 파일 경합과 live 편집 경합의 원문 보존 |
| 실제 화면 7회 / 16 check | 기본/독립 상세창, 취소·Undo/Redo·미저장 cold, Save 실패·재시도, 응답 유실 뒤 receipt 조회만 수행, 전체 변경 취소, 프로젝트 전환·stale submit, 잘못된 타입 혼합 거절→Undo→원래 out 후보 저장, Review 취소/명시 Confirm |
| 영향 회귀 8 check | 기존 공유 caller 입력 이름/metadata 4, scalar 값 입력 타입·매핑 보호 4 |
| clean checkout 8 check | 기존 깨끗한 checkout을 구현 커밋으로 ff, Native Release, 후보 3·실제 API 3·독립 화면 2 재현 |

집중 합계 26은 반복 공통 준비를 포함한 check 문구 수다. 영향 회귀·checkout·패키지 재현과 합쳐 고유 새 기능 수로 세지 않는다. 이번 묶음의 검사 실패는 없었다. [기본](evidence/v536-information-shared-output-names/primary.png)·[독립](evidence/v536-information-shared-output-names/detached.png) 화면을 열어 살폈고 원본 460px 정보 카드·exact64 값과 최종 leftCount/rightCount 표시를 확인했다. UI 소스/WebBundle은 f4b9780에서 변경이 없으며 새 픽셀 단위의 전체 v536 비교를 주장하지 않는다.

커밋 후 Release solution/MCP와 clean Native 빌드에서 warning/error 0을 확인했다. 이번 변경은 Native authoring 조정자 한 파일이며 managed 엔진/pack/UI 소스는 그대로라 별도 Linux CLI build를 반복하지 않았다. 기존 격리 Linux 엔진으로 현재 Native와 실제 렌더러/API를 검사했고, 새 Windows 패키지의 managed 엔진도 SDK 없이 기동했다.

[교차 패키지 근거](evidence/v536-information-shared-output-names/package-verification.json): manifest 2,343개+marker 총 2,344파일, 132,728,805 bytes, symlink 없음. manifest SHA-256은 `153dae8b2022a2121c8daaa3e16d9d2a6a09c7b1bca51c643fa4bbebe2094df1`이다. 모든 manifest 해시·파일 집합, 제품 소스/Native DLL·현재 Core 7개 사본 일치를 검사했고 packaged Native 후보 3 check도 통과했다. SDK 없는 기존 runtime은 전체 파일/해시를 확인 후 읽기 전용으로 재사용했다. 새 legacy profile tree는 현재 RAM 패키지의 읽기 전용 hard link로 검사한다. 다른 cwd·74리소스·최소 로그인 화면·변조/누락 거절·프로필 재사용/override를 모두 통과했다. 실제 로그인·유료 추론·사용자 프로젝트 실행은 하지 않았다.

실행 코드 기준은 acbaaf3이며 이후에는 검증 문서/evidence만 추가한다. 커밋 후 다시 빌드하여 다른 커밋 버전의 DLL 혼합을 피하고 실제 해시로 확인했다. 작업 볼륨은 시작 약43MiB에서 검사 후 약29MiB이며 추가 기존 파일 삭제는 없었다. RAM에서만 새 패키지를 검증했고 exec 종료 뒤 보관본/전달 파일로 사용할 수 없다. 기존 e827a52 코드의 보관 패키지는 변경하지 않았다. 이는 교차 빌드와 Linux/Chromium 검사이며 실제 Windows apphost/WebView2·모바일 기기 실행과 Library 전달은 미검증이다.

## 남은 경계

출력 타입·추가/삭제·역할·반환과 입력 수/순서/ref 변경, C#·혼합 target·중첩/private/whole/postCall, copy/상속/등록 및 owner 속성이 섞인 여러 함수 후보는 별도 미완료다. 기존 source/body를 자동 재작성하지 않는다. 원본 v536 UI/레이아웃·권한과 단일 함수 지원은 유지한다. 9행 named 타입·표시명, I6/B2 및 A4~A6/M4/M11/M12도 별도 후속이다.

검사는 Linux managed 엔진과 Chromium 및 Windows 교차 패키징으로 진행한다. 공간 피크는 사전에 확인하고 새 기존 파일을 삭제하지 않는다. RAM fixture/패키지는 같은 exec 안에서만 사용하고 로그·선택한 화면·해시를 보존한다. RAM의 새 패키지를 영구 보관본이나 Library 전달로 표시하지 않는다. 실제 Windows apphost/WebView2·모바일 기기 실행은 미검증이다.


## 다음의 고정 구현 경계

1. 여러 출력 타입/반환 변경: 기존 `outputs` writer 계획과 `callers.outputs`의 명시 대응을 결합한다. 먼저 생산자의 명시 출력 대응이 다른 선택된 call 인자에 미치는 변환을 원래 증거로 확인해야 한다. 현재 이름 단위의 단순 guard를 풀거나 hash만 최신으로 바꾸지 않는다.
2. 공유 C#/혼합 target: 같은 caller의 사용자가 편집한 최종 본문 한 개를 두 최종 계약과 함께 컴파일해야 한다. 함수 하나씩 최종 C#을 검증하면 다른 계약이 옛 상태라 실패할 수 있으므로 원래 증거와 최종 계약 집합을 구분하는 후보 검증이 필요하다. C# 자동 치환은 하지 않는다.
3. 중첩/private 결합: 기존 qualified frame/부모 계약의 명시 매핑을 여러 함수에 결합하되 그래프 경계나 C# 의미를 추측하지 않는다. 이들은 기존 8행의 미구현이며 새 사용자 설계 결정으로 돌리지 않는다. 7행 독립 복제의 새 계약 정책만 별도로 답변 대기다.
