# 여러 forwarded 자식의 부모 계약 합성

[고정 5행 지원 경계](V536_I5_6_NESTED_SCOPE.md) 안에서 같은 함수를 호출하는 여러 forwarded 자식을 연결했다. 이전 `0b27449`는 frame마다 자식 하나인 계층만 지원했다. 현재는 공통 부모와 frame을 한 번만 구성하고, 각 자식의 출력·부모 바깥 입력/출력을 기존 대응창에서 명시 선택한다. 새 레이아웃·권한·자동 C# 재작성은 없다.

## 확인한 동작

- 깊이 2의 graph/call 분기에서 같은 부모를 공유하는 다섯 전달 호출, 일반 계산 code·live alias·정확한 64비트 값·공유 out 저장소와 실행 순서를 보존한다. 선택/units의 나열 순서를 뒤집어도 결과 graph가 같다.
- 각 자식과 부모는 원래 qualified ID·전체 graph 해시·현재 계약에 묶인다. 마지막 자식의 선택 누락·stale·잘못된 타입·추측 입력도 앞선 자식이나 선언을 저장하지 않는다. 수동 C# 본문과 세 후처리의 source/helpers·공개 SourceContext 계약을 함께 검사한다.
- 실제 API·기본/독립 창에서 Undo/Redo·불완전 입력 보관·취소·장치 오류·충돌·응답/receipt 유실·프로젝트 전환·재시작·Review 취소/재검토·명시 Confirm을 확인했다. 다른 창 입력·원문·부모/형제·다른 callee를 보존한다.
- 원래 정의가 유효한 다른 callee의 forwarded 형제는 해당 새 계약 후보 없이 변경하지 않는다. 독립 복사 fixture에서 이 경계와 물리 원본 미변경을 확인했다. 여러 함수 계약의 동시 합성은 8행으로 유지한다.

## 수정한 순서 문제

부모 A의 출력을 B의 입력으로 사용하는 후보에서, A의 명시 출력 대응을 적용한 뒤 B가 원래 인자를 다시 복사해 연결을 덮어쓰는 오류를 재현했다. 실제 결과는 `left`의 이전 반환을 유지했고 기대 결과는 명시한 `left.total`이었다. 물리 소스는 변경하지 않은 순수 후보 재현이다([관측](evidence/v536-information-multi-forward/linked-before-observation.json)).

모든 부모 인자를 먼저 구성하고 바깥 출력 대응을 마지막에 합성하도록 수정했다. frame 내부 값도 자식별 반복 변환 대신 한 번만 대응한다. 부모의 명시 출력 선택은 공개 함수의 출력 타입이 같다는 이유만으로 UI에서 막지 않고, 기존 서버의 타입·사용처·소유권·전체 후보/CAS 검증을 거친다. 호환되지 않는 연결을 삭제하거나 C#을 문자열 치환하지 않는다.

초기 추가 fixture는 다른 callee의 명시 import를 빠뜨려 `GRAPH_CALLEE_MISSING`으로 실패했다. 유효한 원래 정의임을 먼저 검사하도록 fixture를 보완한 뒤 실제 closure 거절을 확인했다. 순수 후보 결과의 별도 함수 선언 위치를 잘못 조회한 검사도 수정했다. 보호 조건은 완화하지 않았다.

## 검사 근거와 완료 경계

집중 결과는 **29 check**다(순수 후보 7·실제 API 3·렌더러 13·영향 회귀 6). 실패/재실행이나 이전 게시의 58건을 합산하지 않았다([선별 결과](evidence/v536-information-multi-forward/focused-checks.json)). [대응창](evidence/v536-information-multi-forward/multi-mapping.png)과 [독립 창 최종 상태](evidence/v536-information-multi-forward/independent-final.png), [원본 구조/CSS 근거](evidence/v536-information-multi-forward/layout-evidence.json)를 보관한다. CSS를 바꾸지 않았으며 전체 pixel 일치는 주장하지 않는다. Native Release는 경고·오류 0건, Linux 빌드 stderr는 0이다.

고정 5행의 직접 소유 함수 하나·기존 명시 대응 지원 경계를 마감한다. 7행 copy/등록·상속 receipt, 8행 여러 함수 공유 caller, 9행 고급 핀 타입/표시명은 별도 잔여다. I5-6 전체나 v536 전체 완료로 보고하지 않는다. 실제 계정·권한 설정·유료 AI·사용자 프로젝트 실행 없이 격리 fixture만 사용했다. 실제 Windows/WebView2·모바일 기기와 Library 전달은 미검증이다.

Windows 교차 패키지 manifest 2,340개(자기 manifest 포함 실제 2,341개)의 모든 해시와 변경 production 소스 4개·Native/Core DLL 2개의 바이트를 확인했다([기록](evidence/v536-information-multi-forward/package-bytes.json)). manifest SHA-256은 `d0d13decdc706a9452cb4de31b34d1acd6a34e6ea2b2639ef9158674d3869a1a`다. 로컬 산출물은 `/workspace/artifacts/v536-information-multi-forward/Windows-x64/Confectory.exe`이며 파일 전달이나 실제 Windows 실행을 의미하지 않는다.

## 깨끗한 checkout·패키지 마감

실행 소스 커밋은 `ab225ccdbf52eb769dbd58836d8ca31eabe00bfd`다. 깨끗한 checkout의 Native Release는 경고·오류 0건, Linux 빌드 stderr는 0이다. 연결된 부모/여러 자식/후처리 API 3건과 실제 독립 창 UI 3건의 저장·재시작·Review/Confirm을 재현했다([기록](evidence/v536-information-multi-forward/clean-checks.json)). 집중 29건과 별개인 재현 6건이며 기능 수에 합산하지 않는다.

Git retained CRLF/속성 pull과 fresh LF에서 74개 리소스·변조 거절 및 원래 working tree 바이트 보존을 확인했다([기록](evidence/v536-information-multi-forward/resource-checks.json)). 패키지는 SDK 없는 격리 runtime·별도 작업 디렉터리에서 managed 엔진·74 리소스·최소 로그인 화면을 기동했다. 누락/변조 의존성 거절과 fixture 프로필/명시 override 보존을 통과했다([기록](evidence/v536-information-multi-forward/package-probe.json)). 실제 Windows apphost/WebView2·모바일 기기·실제 로그인/추론·사용자 프로젝트 실행·Library 전달은 수행하지 않았다.

후속 마감 커밋은 검증 문서·증거만 추가하며 위 패키지와 실행 코드가 같다. 고정 5행의 기존 직접 소유 지원 경계를 마감하고 7~9행의 다음 구현을 별도로 유지한다.
