# 소유 copy와 읽기 전용 등록 부모 계약

[고정 7행의 경계](V536_I5_6_COPY_INHERITANCE_SCOPE.md)를 따라 저장된 소유 copy와 등록 함수의 부모 계약을 정보 함수 편집 후보에 연결했다. 소유 copy의 현재 ID/배정과 원래 donor/부모 출처를 구분하고, 외부 원본을 쓰기 대상으로 승격하지 않는다.

## 구현과 발견한 결함

- `InformationFunctionCopies`는 `BlueprintCopyAbi`의 단독 배정/함수/module/provider/provenance 증거와 현재 graph·구현·선언 문맥을 결합한다. 검증된 내부 view만 기존 편집기에 전달하고, 원래 provenance를 복원한 뒤 새 provider 계약을 재검증한다. 저장·취소·응답 유실 처리와 CAS는 기존 원자적 거래를 사용한다.
- 기존 C# 선택창이 copy 메타데이터를 받아도 일반 ‘이 기능’으로 표시하던 결함을 실제 화면에서 확인했다. 같은 markup의 항목·제목에 소유 copy 표시를 연결했다. C# 형식 인자명은 입력 이름만 바꾸고 위치/타입/mode가 그대로이며 기존 핀 재정렬이 없을 때 원래 native 이름을 유지한다. C# 원문을 자동 치환하지 않는다.
- 등록 callable의 부모는 선언된 상속 edge와 팩의 명시 dependency에 한정하여 읽는다. 전체 부모 receipt·선언/manifest 관측·타입/순환/상한 검사를 같은 후보에 결부한다. provider 본문은 읽거나 수정하지 않고, 부모 조회를 root caller의 직접 import 권한으로 사용하지 않는다.

초기 copy fixture는 노드의 graph 상대 경로를 project 상대 경로로 읽었고, pure helper는 CRLF 파일의 원문/해시를 LF로 바꾸어 실제 CAS가 거절했다. fixture를 실제 경로와 raw 파일 해시/원문에 맞췄다. UI 검사에서 다른 제목의 매핑창을 건너뛰어 불완전 출력 대응을 제출하던 선택자도 수정했다. 실제 매핑창의 native 출력 identity를 확인하고 수락한다. 제품의 소유권·타입·CAS·필수 대응 검사는 완화하지 않았다.

## 실제 검증

실제 copy 준비 API로 native donor에서 만든 저장 복사본을 사용했다. 정보의 직접 copy와 다른 객체의 module/provider에 배정한 caller copy를 구분한다. 입력 이름 변경·수동 C#·typed import/context·명시적 출력 대응을 하나의 후보로 저장하고 donor 선언/CRLF 본문·배정·출처를 보존한다. 누락/위조 proof·공유 배정·바뀐 owner/graph/구현/출처·저장 기준·잘못된 C#은 전체 미적용이다.

등록 상속 fixture는 부모가 별도 팩에 있지만 현재 프로젝트에는 그 부모에 대한 직접 dependency가 없는 경우를 포함한다. 선택한 함수의 부모 관계로만 읽을 수 있으며 같은 부모를 직접 import하려는 요청은 거절한다. 부모 receipt 누락/위조, 실제 부모 변경, 타입 불일치와 순환을 거절한다. 실제 API의 저장 실패/재시도·cold·compiler Review/Confirm에서도 외부 팩을 보존한다.

기본/독립 창의 기존 선택창·C# 편집기·호출 계약 매핑창에서 취소·불완전 입력·Undo/Redo·저장 오류·peer 충돌·응답/receipt 유실과 결과 조회·재시작·두 프로젝트 전환·닫힌 저장 동작·Review 취소/재검토·명시 Confirm을 확인했다. 집중 결과는 **38 check**다(순수 후보 10·실제 API 9·렌더러 13·영향 회귀 6, [기록](evidence/v536-information-copy-inheritance/focused-checks.json)). 이전 게시 검사와 실패/재실행을 새 기능 수에 합산하지 않는다.

[소유 copy C# 편집창](evidence/v536-information-copy-inheritance/copy-csharp.png)과 [저장 후 화면](evidence/v536-information-copy-inheritance/copy-final.png)을 실제 렌더로 확인했다. 원본 HTML/CSS 네 파일은 이전 게시와 바이트가 같다([근거](evidence/v536-information-copy-inheritance/layout-evidence.json)). 전체 pixel 일치는 주장하지 않는다. Native Release 경고/오류 0건·Linux 빌드 stderr 0, 변경 JS 구문과 canonical 리소스 manifest를 확인했다.

## 최종 checkout·패키지 검증

기능 소스 기준은 `5c1d6d795f28b1731fc3a6b55dd6092a571173a8`이다. 이 소스를 별도 깨끗한 checkout에서 Native Release 경고/오류 0건·Linux 빌드로 재현했다. 실제 callee copy API 3건·다른 소유자의 caller copy API 3건·다른 등록 팩의 부모 계약 API 3건·독립 창 copy 화면 2건도 통과했다. 저장 오류/재시도·위조 거절·원문/출처 보존·cold·명시적 compiler Review/Confirm을 포함하며 checkout의 소스는 그대로다. 이 **재현 11건**을 위 집중 38건의 새 기능 수로 더하지 않는다([최종 기록](evidence/v536-information-copy-inheritance/final-checks.json)).

실제 과거 CRLF checkout을 현재 attributes로 pull한 뒤 보관 바이트를 확인하고, 새 LF checkout의 실제 엔진 기동과 74개 canonical/exact 리소스를 확인했다. 내용·잘못된 UTF-8·BOM·UTF-16·bare CR·크기 초과·PNG 변조를 거절하고 원래 파일 바이트를 복원한다. 검사 조건은 바꾸지 않았다. 최초 fresh checkout의 Git 종료 128은 stderr를 보존한 재현에서 `No space left on device`로 확정했다. 사용자가 승인한 동일 패키지/SDK 복제폴더 8개만 전수 해시·소유권·사용 여부 확인 후 정리했고, 원본·검사 증거·fixture는 보존했다. 이후 전체 검사는 종료 코드 0이다. 중간 로그 수집기의 종료 처리 오류 120은 수집기만 고친 재실행으로 구분하여 마감했다.

Windows x64 교차 패키지의 manifest 2,342개 파일과 manifest 자체를 합한 실제 2,343개 파일의 목록·SHA-256을 확인했다. 변경한 제품 소스 12개와 편집 호스트/현재 Core DLL도 패키지와 일치한다([바이트 근거](evidence/v536-information-copy-inheritance/package-bytes.json)). 별도 cwd·SDK 없는 런타임에서 packaged engine과 74개 리소스·최소 Agent 화면을 실행했고, 누락/변조 거절과 기존 fixture profile 보존도 통과했다. 로컬 실행 파일은 `/workspace/artifacts/v536-information-copy-inheritance/Windows-x64/Confectory.exe`다. 패키지는 위 기능 소스를 포함하며, 뒤에 추가한 문서/검증 기록만으로 실행 코드가 바뀌었다고 주장하지 않는다. DLL의 이전 assembly revision 표시는 소스 포함 증거 대신 사용하지 않는다. 실제 Windows apphost/WebView2 실행이나 사용자에게 파일 전달 성공을 뜻하지 않는다.

원본 HTML/CSS/레이아웃과 권한은 바꾸지 않는다. 실제 Windows apphost/WebView2·모바일 기기·실제 로그인/추론·사용자 프로젝트 실행·Library 전달은 미검증이다. **7행 전체 및 I5-6 전체 완료는 아니다.** 직접 상속 implementation 참조의 부모 header/body 증거와 기존 명시적 copy/local 편집 진입, 새 미확정/외부 함수/다중 target copy 제한은 [범위 표](V536_I5_6_COPY_INHERITANCE_SCOPE.md)에 그대로 남는다. 8행의 여러 함수 공유 caller와 9행의 고급 타입/표시명은 별도 후속이다.
