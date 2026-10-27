# v536 고정 7행: 기존 private 직렬 실행선 편집

기준 게시 `0e321531387eb82230763ab8015c583ae360aa3d`, 저장소 v536 레퍼런스 `196c605`의 ZIP `Confectory-v536/dist/blueprint.js`다. 원본 connect와 실행선 Delete, openInternal, 모바일 실행선 선택 메뉴가 내부 흐름에도 기존 시작/다음 연결·해제를 제공한다. 원본 모바일 flow 이미지와 실제 기존 850×600 편집창/동작 카드 렌더를 확인했다. 이번 최소 단위는 **이미 있는 ordinary code next 노드 사이와 선언된 exit에 대한 private 시작/다음 실행선**이다. 새 노드·새 공개 계약·별도 편집 UI·레이아웃은 만들지 않는다.

공개 오버라이드의 매개변수·출력·반환 계약은 유지한다. private frame의 실행 순서는 구현 내용이며 공개 계약 변경과 다르다. 원본·부모·외부 등록팩과 다른 frame/target의 소유권·본문·값·설명을 보존한다. C# 자동 재작성, 새로운 전역/계약 ID 또는 독립 계약 복제는 없다.

Native copy 후보는 qualified frame의 기존 entry/route 편집을 재사용한다. 시작 sentinel은 정확한 `$entry`, 출발 노드는 기존 일반 code next, 목적지는 같은 frame의 일반 code next나 선언된 exit만 허용한다. graph/call/branch/forward caller storage의 별도 경계를 추정하지 않는다. 여러 선을 최종 그래프에 함께 적용한 뒤 기존 전체 그래프·반환·acyclic 검증을 수행하여 중간 연결 순서가 거절/부분 적용을 만들지 않는다. 모든 C#/helpers record와 노드·핀·값 식별성을 보존한다.

저장된 복사본의 authorBatch도 기존 owner/project/view/source closure·checkpoint의 증거를 유지한다. 내부 serialRoutes는 서버가 생성한 격리 author 후보의 private copied frame에서만 실행된다. 외부 직접 호출·일반 루트·잘못된 포트·다른 frame·분기 영역은 허용하지 않는다. 후보 내부에서 선 전부를 한 번에 바꾸고 기존 metadata 검증·EditBatch를 거친다. 다른 편집과 원래 전체 후보/단일 CAS를 검증한 뒤에만 checkpoint를 쓴다. 실패·충돌·불명 결과는 입력과 이전 요청을 보존하고, 이전 요청의 미적용·동일 원래 기준이 증명될 때만 새 명시 후보를 허용한다. 응답 유실은 exact receipt를 먼저 조회한다. Review 취소/명시 Confirm과 기존 bound view nonce·Agent 권한은 유지한다.

기존 포트 버튼과 실행선 Delete, 지도/방향키, 핀 선택기와 원래 창을 사용한다. private 실행선 staging을 기존 frame별 structuralEdit에 연결하여 Undo/Redo·취소·부모/자손 재진입·cold 보관을 유지한다. CSS/HTML과 다른 73개 UI 리소스 바이트는 기준 게시와 같으며 authoring 동작과 해당 manifest hash만 변경한다.

첫 중앙 포트 클릭 시도는 값 컨트롤 또는 clipping에 가려 저장 전에 실패했고 로그·fixture 증거를 보존했다. 키보드 활성화는 기존 HTML button Enter와 SVG Delete를 사용한다. 실제 포인터 검사는 DOM을 변경하거나 force click하지 않고 elementFromPoint로 원래 클릭 가능한 지점을 읽는다. 원본 Home은 가로만 초기화하므로 포트가 viewport 밖이면 기존 지도 방향키로 팬한 뒤 일반 click으로 검증한다. viewport 안에서도 실제 hit가 없으면 PNG/좌표를 남기고 실패한다. 원래 레이아웃을 통과용으로 수정하지 않는다.

첫 저장 거절 검사는 entry가 비어 있으면 무조건 잘못됐다고 가정했으나 기존 implicit 계열은 `end:$entry`와 `csharp-type-default` 반환을 명시 지원한다. 이 정상 종료를 미구현/오류로 바꾸지 않는다. 실제 미생산 값을 내보내는 `entry -> exit:return` 후보로 거절 검사를 바로잡았고, 거절 뒤 원문·checkpoint·모든 입력/실패 기록과 명시 재연결을 확인한다. 이 실패도 통과 합계에서 제외한다.

7행 전체 완료가 아니다. 기존 새 내부 동작/삽입·callee ABI·내부 enum 어댑터는 원본 UI와 대조할 후속으로 남긴다. 이 일반 실행선 단위 밖의 모든 type/ref/출력·반환/제어 조합을 새 필수 경우의 수로 늘리지 않는다. 공개 override 계약 구조 변경 거절은 정상 보호이며 독립 계약 복제는 필수 범위에서 제외한다. 고정 8행의 공유 caller 다른 문맥/계약 결합과 9행의 정보·참조·외부 함수 핀 타입/표시명, I6/B2/A4~A6/M4/M11/M12는 별도다. 새 이미지 생성·협의/shared Confirm·렌더/FPS backend와 Helper 도구 권한을 추가하지 않는다. 실제 Windows apphost/WebView2·모바일 기기·Library 전달·전체 UI 완료는 미검증/미완료로 유지한다.

## 집중 검증

Native Release 0경고·오류, 순수 후보 12확인과 실제 엔진/렌더러·영향 회귀 11흐름 94확인을 통과했다. 기본/독립 창·키보드/실제 포인터·정상 저장·잘못된 후보 거절/명시 보완·Undo/Redo·취소·쓰기 실패·실제 peer 경합·저장/조회 응답 유실·프로젝트 전환·재시작·Review 취소·명시 compiler Confirm을 구분한다. 같은 제품 소스로 기존 핀 편집·일반 루트 다중 선택/원자 저장·view 권한·오버라이드 원계약 보호를 확인했다. 실패 시도는 합계에서 제외하고 증거를 보관했다. [명령·결과·해시](evidence/v536-nested-copy-routes/focused-verification.json)에 기록하며 독립 checkout·새 교차 패키지는 별도로 추가한다.
