# v536 여러 out 타입과 공유 소비자 결합

고정 8행의 다음 단위다. 같은 정보의 직접 소유 함수 2~8개, import 없는 code/export callee와 선택 함수 call/export만 있는 caller라는 경계를 유지한다. 이름·위치·수·값/out 역할, 모든 값 입력의 타입과 반환을 그대로 두고 scalar out 타입을 바꾼다. 기존 scalar는 bool/int/long/float/double/string이다. 새 메뉴·레이아웃·함수/계약 ID·권한은 만들지 않는다. 7행 독립 복제 정책은 여전히 답변 대기다.

출력 writer와 caller의 기존 호환 출력 대응을 원래 스냅샷에서 먼저 검증한다. 같은 caller에 A와 B가 있고 A의 원래 출력이 B의 인자로 쓰이면, A에 대해 사용자가 명시한 출력 대응을 원래 graph의 복제본에 적용한다. 이 예상 graph와 현재 내부 후보의 선택된 B call·연결·제어 경로·기타 필드를 대조하고 검증된 다른 call의 서명/인자 변화만 구분한다. 그때만 내부 mapping 복제본에 현재 내부 graph hash를 설정한다. 원래 요청·선택·최종 update hash·물리 source 기준·checkpoint CAS는 바꾸지 않는다. 이미 처리한 생산자의 검증된 대응만 사용하며 미래 선택이나 임의 값으로 연결하지 않는다.

caller의 값 인자는 원래 바인딩을 유지하며 새 값/교환/해제 선택을 이 단위에 섞지 않는다. 소비 중인 출력을 null로 버리거나 호환되지 않는 타입으로 대응하면 전체 거절한다. callee의 C# 형식 매개변수·본문은 원래 상태를 유지하고, public writer 값과 consumer 출력이 달라지는 부분은 사용자가 명시한 선택만 반영한다. 기존 후보/CAS·receipt·Review/Confirm으로 선언·import·writer·호출자 전부를 저장한다.

## 검증 상태

격리 fixture에서 A.count→B.amount, B.count→caller 반환이라는 연결을 두고 두 count를 long에서 double로 바꾼다. writer는 각 함수의 기존 real 값을 선택한다. 소비 중인 기존 long count는 각 함수의 호환 long return으로 명시 대응한다. 그 결과 B.amount는 A.return을, caller 반환은 B.return을 사용해야 한다. C#의 원래 long count 계산·설명 문자열·선택 외 입력과 exact64 값, writer/call ID 및 제어 경로는 보존한다. 기존 count 계산값을 임의로 double 변환했다고 주장하지 않는다. 추가 순수 후보는 명시 bool/한글 string 리터럴도 검사한다.

구현 커밋은 `3f724997f97f09296dab8d6d8cdcf4b4329ab3ba`다. [집중/회귀/checkout 근거](evidence/v536-information-shared-output-types/focused-verification.json)에 명령·결과·로그 해시를 남겼다.

| 검사 | 통과 내용 |
|---|---|
| 순수 후보 4 check | 요청 불변·중복 없는 원래 hash·역순 동일 결과, 두 writer/import/호환 소비 대응·제어 경로·C# 보존, bool/한글 string 명시 리터럴, 중간 hash 재사용·누락/잘못된 writer/입력/소비 대응·역할/반환/본문/문맥 변경 전체 거절 |
| 실제 API 3회 / 7 check | 마지막 함수 오류의 전체 미적용, 한 후보 Save·cold·compiler Confirm, 물리 caller 파일 경합과 live 수정의 원문 보존 |
| 실제 화면 7회 / 16 check | 기본/독립 창, 상세창 취소·Undo/Redo·미저장 cold, Save 실패·재시도, 응답 유실 뒤 receipt 조회만 수행, 전체 변경 취소, 프로젝트 전환·stale submit, 잘못된 입력/출력 혼합 거절→Undo→원래 출력 후보 재시도, Review 취소/Confirm |
| 영향 회귀 11 check | 기존 값 입력 이름/metadata 4, 값 입력 타입 4, 일반 out 이름/연결 보존 3 |
| clean checkout 9 check | 기존 깨끗한 checkout을 구현 커밋으로 ff하고 Native Release 빌드, 순수 후보 4·실제 API 3·독립 화면 2 재현 |

집중 27은 반복 공통 준비를 포함하는 check 문구 수다. 회귀·checkout·package 재현과 합쳐 고유 새 기능 수로 세지 않는다. 이번 실행 실패는 없었다. [기본](evidence/v536-information-shared-output-types/primary.png)·[독립](evidence/v536-information-shared-output-types/detached.png) 화면을 열어 살폈으며 원본 460px 카드·exact64와 최종 count 실수 표시를 확인했다. UI/WebBundle은 2a33c95에서 바이트 변경이 없고 새 전체 v536 픽셀 비교를 주장하지 않는다.

Native/clean Native 및 커밋 후 Release solution·MCP Release에서 warning/error 0을 확인했다. 이번 변경은 Native 조정자 한 파일이고 managed 엔진/pack/UI 소스는 그대로라 별도 Linux CLI build를 반복하지 않았다. 기존 격리 Linux managed 엔진에 현재 Native와 실제 API/렌더러를 연결해 검사했고, 새 교차 패키지의 managed 엔진도 SDK 없이 기동했다.

[교차 패키지 근거](evidence/v536-information-shared-output-types/package-verification.json): manifest 2,343개+marker 총 2,344파일, 132,736,101 bytes, symlink 없음. manifest SHA-256은 `58f0fc15879f2527416dd02491f2453aaa7f8d224ab8c55104e1af68e25dd3dc`이다. 전체 manifest/파일 집합, 제품 소스/Native DLL과 현재 Core 7개 사본 일치를 검사했다. packaged Native로 후보 4 check도 통과했다. 기존 SDK-less runtime은 전체 파일/해시 검증 후 읽기 전용으로 재사용하고 새 legacy profile은 현재 RAM package의 읽기 전용 hard link로 검사했다. 다른 cwd·74리소스·최소 로그인 화면·변조/누락 거절·프로필 재사용/override 모두 통과했다. 사용자 프로젝트·로그인·유료 추론은 사용하지 않았다.

실행 코드 기준은 3f72499이며 이후 문서/evidence만 추가한다. 커밋 후 다시 빌드해 DLL 버전 혼합을 피하고 해시로 검증했다. Windows 교차 빌드와 Linux/Chromium 검증이며 실제 Windows apphost/WebView2·모바일 기기 실행 및 Library 전달은 미검증이다.

## 남은 경계와 공간

입력/출력 타입 동시 변경, 핀 수·순서·역할·추가/삭제·반환 변경, C#/혼합 target·중첩/private/whole/postCall, copy/상속/등록/owner 속성 혼합은 별도 미완료다. 9행 named 타입·표시명 및 I6/B2/A4~A6/M4/M11/M12도 유지한다. 기존 명세의 엔지니어링 미구현이며 7행 외 새 사용자 설계 결정으로 돌리지 않는다.

작업 볼륨 시작 약28MiB와 이전 패키지의 실제 증가량 약13MiB를 대조해 순차 RAM 경로를 사용한다. 실행 직전 공간/메모리를 재확인하고 기존 파일은 삭제하지 않는다. RAM 패키지/fixture는 해당 exec 동안만 이용하며 로그·선택한 화면·해시를 작업 볼륨에 보존한다. RAM 파일을 보관본이나 사용자 전달로 표시하지 않는다.


이전 순증량 13,332,480 bytes에 8MiB 여유를 더한 21,721,088 bytes를 실행 기준으로 정했다. 현재 검사에서는 200ms 간격으로 기록한 최저 workspace 여유가 14,573,568 bytes, 최고 cgroup memory.current가 17,107,537,920 bytes(한도 17,179,869,184 bytes)였다. OOM/oom_kill은 0이다. 샘플링 수치이며 모든 순간의 절대 peak라고 주장하지 않는다. 검사 후 RAM 패키지는 소실되며 전체 manifest·로그/화면/해시는 보존했다. 기존 e827a52 보관 패키지는 변경하지 않았다. 다음 같은 대형 검사에는 현재 여유를 다시 확인해야 하며 기존 파일 정리를 자동 승인받은 것으로 처리하지 않는다.

다음 고정 단위는 출력 추가/삭제·반환이다. 기존 outputGraphs의 전체 writer 삭제·생성 위치/값·publicOutputs와 callers.outputs를 같은 원래 증거/후보에 결합해야 한다. caller 입력은 유지하고 소비 중인 제거 출력은 명시한 호환 출력으로만 대응한다. 공유 C#/혼합 target·중첩/private에서는 사용자가 편집한 최종 본문과 모든 최종 계약을 함께 검증하는 경계가 별도로 남는다. 이들을 완료한 것으로 표시하지 않는다.
