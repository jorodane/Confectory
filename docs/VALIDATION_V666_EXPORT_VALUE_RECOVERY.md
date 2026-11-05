# v666 기존 내보내기 값 저장 복구 검증

게시본 `6b70043833a739e875d542c53066b8ac136a90a3`에서 기존 직접 소유 직렬 export의
값 37을 선택하고 checkpoint 쓰기를 실패시킨 뒤 cold에서 원래 연결만 남는 것을
재현했다. 개인 입력·실패 화면·요청·원본을 개발 record에 보관한다.
첫 분기 fixture는 기존 영역 검증에서 먼저 거절돼 입력이 보존됐으므로 유실 재현이 아니다.

[지원 범위](V2_EXPORT_VALUE_RECOVERY.md), [delta](v666-export-value-recovery-delta.json)를 따른다.
현재 개발 검증 중이며 최종 동결 LF/CRLF·패키지/전체 복원·게시 검증은 아직 완료 전이다.
