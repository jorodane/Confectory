# v666 기존 root 반환 출력 핀 값 저장 복구 검증

게시본 `f37c06237eed76bcc674a05a92bc0df3a609553a`에서 생성한 프로젝트의 원래 실행을
확인한 뒤 기존 root 반환 핀에서 정수 37을 선택하고 checkpoint 쓰기를 실패시켰다.
개인 입력이 사라지고 cold에서 원래 호출 출력 연결만 복원되는 것을 재현했다.
원본·checkpoint·C# bytes와 입력·실패 화면·traffic·cold·실행 증거를 보관한다.

[지원 범위](V2_ROOT_RETURN_RECOVERY.md), [delta](v666-root-return-recovery-delta.json)를 따른다.
현재 개발 검증 중이며 최종 LF/CRLF·새 패키지·전체 복원·게시 검증은 완료 전이다.
