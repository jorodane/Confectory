# V666 root 반환 핀 표시 위치 저장 복구 검증

현재 개발 검증 단계다. 최종 동결 코드의 독립 LF/CRLF·새 교차 패키지/전체 복원·
실패 수명관리 결과와 출처/공간 수치를 완료 후 이 문서에 기록한다.
[닫힌 지원 범위](V2_ROOT_RETURN_POSITION_RECOVERY.md)와
[정확한 delta](v666-root-return-position-recovery-delta.json)를 따른다.

baseline은 `ddd2c7b1a058f4627a182dc323ce854d0b02a3b7`의 실제 출력 이동 UI다.
값 입력 하나·out 셋·int 반환을 유지하고 반환 핀만 옮긴 뒤 쓰기 실패에서 개인 입력
하나가 사라지는 것을 확인했다. checkpoint·signature·C#와 caller bytes는 같았고 cold에서
이전 순서가 복원됐다. baseline JSON SHA는
`0ed90cebac0054845849d99615d2de30273f664417ae21ff55f78420fe0893ff`다.

제품 변경은 JS/native의 같은 반환 표시 이동 admission과 canonical 자산 SHA뿐이다.
writer·receipt 형식·이력·권한·Review→Confirm/CAS와 원본 레이아웃을 보존한다.
실제 Windows apphost/WebView2·모바일·전체 UI·Space 전달은 이번 자동 검사와 구분한다.
