# V666 기존 일반 동작 표시명 묶음 저장 복구 검증

현재 개발 검증 단계다. 최종 동결 코드의 LF/CRLF·새 교차 패키지/전체 복원·실패
수명관리 결과, 출처와 보관/공간 수치를 완료 후 기록한다.
[닫힌 지원 경계](V2_NODE_NAMES_RECOVERY.md)와
[정확한 delta](v666-node-names-recovery-delta.json)를 따른다.

게시본 `1055fd0a0c083a00a52cabc71a9df145081d49f7`의 원래 제목 inspector에서 두 기존
일반 동작의 표시명을 입력했다. 쓰기 실패 뒤 개인 입력 두 개가 사라지고 live만
바뀌었으며 cold에서는 이전 이름으로 돌아왔다. checkpoint·signature·C#/caller와
모든 물리 원본은 같았다. baseline JSON SHA는
`c29138d431b0daf75c18396b1f89c223717a88afdc9ec70d091d7611b655682b`다.

JS의 닫힌 표시명 묶음과 native의 기존 ownedRename batch 판별만 연결한다. writer·
receipt 형식·권한·원본 레이아웃·Review→Confirm·최종 CAS는 그대로다. 실제
Windows/WebView2·모바일·전체 UI·Space 전달은 자동 검사와 구분한다.
