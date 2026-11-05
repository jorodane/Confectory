# v666 기존 내보내기 출력 재배정 저장 복구 검증

게시본 `c2380222c3cf179e613c81e7a709036c5ba8a671`에서 생성한 프로젝트의 원래 실행을
확인하고, 기존 export의 출력 left→right를 고른 뒤 checkpoint 쓰기를 실패시켰다.
개인 입력이 사라지고 cold에서 원래 left만 복원되는 것을 재현했다. 원본·checkpoint·
C# bytes와 수정 전 입력·실패 화면·traffic·cold 증거는 개발 record에 보관한다.

[지원 범위](V2_EXPORT_BINDING_RECOVERY.md), [delta](v666-export-binding-recovery-delta.json)를 따른다.
현재 개발 검증 중이며 최종 LF/CRLF·새 패키지·전체 복원·게시 검증은 완료 전이다.
