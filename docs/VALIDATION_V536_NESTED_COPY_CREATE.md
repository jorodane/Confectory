# v536 고정 7행: private 일반 동작 생성·삽입

기준 게시 `62133c5a049b4825b4fbed0458b00e1cb56d9642`, 저장소 원본 v536 `196c605`의 `Confectory-v536/dist/blueprint.js`다. 원본 `addNode`, 검색의 ‘동작 만들기’, 모바일 시작/다음 줄의 삽입과 별도 노드 추가를 대조하고 원본 모바일 흐름 이미지 및 실제 렌더를 확인했다. 이번 단위는 기존 copy의 정확한 private frame에서 일반 `code next` 동작을 만들고 기존 시작/다음 실행선에 연결하며, 사용자가 직접 입력한 본문을 함께 저장하는 것이다. 공개 함수·override 계약과 부모/외부 원본, 다른 frame/target은 보존한다. 새 공개 계약 복제·새 계약 ID·AI 작성/실행 권한·레이아웃·메뉴는 추가하지 않는다.

미확정 copy는 기존 create/rename/source/value/entry/route 계획을 qualified 어댑터로 전달한다. 새 노드의 본문 경로는 소유 implementation과 전체 private 경로의 기존 digest 규칙을 사용한다. 서로 다른 깊이에 같은 local ID를 써도 기록/파일을 섞지 않으며 기존 기록과 immutable snapshot/seed를 변경하지 않는다. 생성할 노드와 명시 편집을 하나의 후보로 검증한다. 미완성 본문·위조/중복 ID·다른 frame 연결·branch 소유권 위조는 원본을 보존하며 전체 거절한다.

저장된 copy의 생성은 기존 `BlueprintNode`의 private 경로 처리를 사용한다. 기존 bound owner/project/view·copy provenance·정확한 source closure·원래 checkpoint를 요구한다. 생성은 격리 후보 안에서 먼저 처리하고 핀/값/명시 C#·표시 이름과 최종 실행선을 검사한 뒤 기존 단일 CAS로 쓴다. 새 본문도 후보의 실제 locator와 `missing` baseline을 검증하여 다른 파일을 덮지 않는다. receipt는 private frame에서 실제 생성한 node source ID/경로·해시를 확인한다. 일반 root의 기존 생성/receipt 규칙은 유지한다. 새 private graph·branch 정의나 다른 저장소/호출 의미를 이 어댑터로 추정하지 않는다.

실패 요청을 무조건 지우지 않는다. 미적용·동일 원래 기준이 확인됐을 때만 새 명시 입력으로 재시도하고 이전 시도를 보존한다. 응답 유실은 저장된 receipt를 먼저 조회한다. 원래 Undo/Redo·검색 취소·본문 편집 취소·cold 보관·Review 취소/명시 Confirm과 창별 입력을 사용한다. 문서/모바일 폭 전환에서는 기존 탭·워크스페이스 이동 조작을 사용한다. CSS/HTML과 다른 73개 UI resource 바이트는 기준 게시와 같고 authoring 동작과 해당 manifest hash만 바뀐다.

첫 순수 metadata 검사는 preview 응답에 저장 후보의 records를 기대한 검사 옵션 오류로 실패했다. 실제 후보 요청으로 바로잡았고 실패 로그를 보존하며 통과 합계에서 제외한다.

초기 화면 시도는 자동 흐름 전환 전에 숨겨진 버튼을 선택하거나 body portal의 inspector를 창 안에서 찾고, 문서 탭 상태에 창 caption을 요구한 검사 선택자 문제로 저장 전에 실패했다. 로그/fixture ZIP은 보존하고 통과 합계에 넣지 않는다. 실제 표시된 흐름·portal inspector·기존 ‘워크스페이스로 이동’ 메뉴와 850×600 창 복원을 사용하도록 검사를 정리했다. force click·DOM 표시 변경·레이아웃 재설계·검사 약화는 하지 않는다.

7행 전체 완료가 아니다. private callee의 명시 ABI 갱신과 내부 enum 편집 어댑터는 별도 후속이다. 일반 next 이외의 생성/저장소/제어 조합 전체를 새 필수 경우의 수로 늘리지 않는다. 공개 override의 타입·핀 수·역할·반환 구조 변경 거절은 정상 보호이고 독립 계약 복제는 필수 범위에서 제외한다. 고정 8행의 검증 단위 밖 공유 caller 문맥/기존 계약 결합, 9행의 정보·참조·외부 함수 핀 타입/표시명 및 I6/B2/A4~A6/M4/M11/M12는 별도다. 이미지 생성·협의/shared Confirm·렌더/FPS 새 backend와 Helper 도구 권한도 추가하지 않는다. 실제 Windows apphost/WebView2·모바일 기기·Library 전달·전체 UI는 미검증/미완료로 유지한다.

## 집중 검증

Native Release 0경고·오류, 순수 후보 15확인과 실제 엔진/렌더러·영향 회귀 10흐름 105확인을 통과했다. 기본/독립 창·키보드/실제 포인터·정상 저장·잘못된 후보 거절/명시 보완·Undo/Redo·취소·쓰기 실패·실제 peer 경합·저장/조회 응답 유실·프로젝트 전환·재시작·Review 취소·명시 compiler Confirm을 구분한다. 같은 제품 소스로 기존 핀 편집·일반 루트 다중 선택/원자 저장·view 권한·오버라이드 원계약 보호를 확인했다. 실패 시도는 합계에서 제외하고 증거를 보관했다. [명령·결과·해시](evidence/v536-nested-copy-create/focused-verification.json)에 기록하며 독립 checkout·새 교차 패키지는 별도로 추가한다.
