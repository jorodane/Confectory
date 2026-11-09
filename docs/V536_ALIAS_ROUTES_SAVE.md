# 기존 값 이름과 일반 실행선의 결합 저장

고정 v666 `blueprint.js`는 `variable.name=name`/`graph.localVariables.push(...)`와
`graph.links`의 `port:'next'` 연결을 같은 함수 Blueprint 초안에 보관한다. 기존 고정 혼합
저장의 실제 조작이며, 가능한 타입/문맥 조합을 새 요구로 늘리는 목록이 아니다.

게시 `dc230cb5`에서 기존 출력 이름과 소비자·세 next 실행선의 다섯 입력을 실제 원본 UI로
만든 뒤 Save하면 UI와 native authorBatch가 모두 결합을 거절한다. 원문은 보존되지만 사용자는
같은 함수의 편집을 한 번에 보관할 수 없다. 직전 값 이름+C# 본문 저장은 별도 완료 범위다.

첫 지원은 직접 소유 동기 ordinary root의 기존 code next1–63개 연결(기존 전체64행 예산에서 aliasPlan 한 행 포함)과 기존 aliasPlan이다.
선택한 각 원본 노드의 next를 명시하고 마지막에 별칭 이름/입력·종료 소비자 계획을 둔다.
한 격리 후보에서 모든 실행선·저장소 가용성·타입·순환과 전체 source proof를 검증한 뒤
checkpoint CAS 한 번으로 저장한다. 실행선과 이름을 별도 endpoint로 순차 Save하지 않는다.
별칭 ID/타입/원래 source·함수/노드/핀 ID·C# 바이트·공개/override 계약은 유지한다.

잘못된 마지막 목적지/별칭/소비자는 전체 미적용이다. 실제 쓰기 실패·동료 checkpoint 충돌·
응답 유실·늦은 입력·cold·공유 Undo/Redo를 기존 receipt에 연결한다. 실패 후 명시 수정은
같은 원래 source/checkpoint/물리 baseline과 저장소 ID/타입/source·소비자가 일치할 때 이름과
명시 next 목적지만 허용한다. 적용된 결과와 그 뒤 입력은 구별하며 암묵적으로 재실행하지 않는다.
초안 Save와 실제 파일 반영은 구별하고 Review 취소·명시 Confirm 및 최종 물리 CAS를 유지한다.

기존 별칭 단독·순수 next 묶음·이름+C# 편집을 보존한다. entry/분기·완료 포트·C# 본문/계약·
새 동작 생성·Set/속성·async·private/copy/slot/부모·외부 원본과의 새 결합은 이 단위 밖이다.
정상 비소유 거절을 미구현으로 바꾸거나 M11/M12/M4를 다시 열지 않는다. 같은 루트의 한 일반
실행선 묶음과 값 이름의 수용이며 모든 graph 편집의 범용 결합 완료가 아니다.

새 graph/profile/receipt 버전은 없으며 확정 graph는 기존 문법을 유지한다. 이전 runtime의 새 결합
미확정 author-attempt 복구는 미지원이고 구판 실행 전수 검사는 미실행이다. 입력을 자동 분해·폐기·이행하지 않고 현재판에서
저장 결과를 먼저 확인한다. 현재 실행/권한 경계·원래 팝오버/키보드 연결·레이아웃은 보존한다.

최종 LF/CRLF 독립 checkout·새 교차 패키지/전체 복원과 최신/롤백·증거 보관에서 마감한다.
실제 Windows/WebView2·모바일/기기 IME·GPU/물리 오디오·전체 UI·Space/Library 전달은 별도다.
초기 빈 화면과 과거 Agent 준비 지연의 근본 원인은 미확정으로 유지한다.

[최종 신규40단계·재사용0 및 보관 기록](VALIDATION_V666_ALIAS_ROUTES.md)을 따른다.
