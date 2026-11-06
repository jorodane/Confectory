# V2 검토·확정 안내

기준은 보관한 v666 `dist/app.js:3484`의 변경 검토와 “적용할 변경을 선택하십시오.
Confirm만 공유 상태를 바꿉니다.” 문구, 그리고 [고정 V2 수용 목록](V666_ACCEPTANCE.md)이다.
native는 의미 변경 묶음·원본 전체 소스·실제 compiler와 최종 CAS를 사용하므로 원본의
로컬 demo 객체 저장 의미를 그대로 가져오지 않는다.

현재 native Review에 남은 영어 완료 안내·구어체를 19개 문구/24개 표시 지점으로 제한해
연결한다. [정확한 허용 목록](v666-review-guidance-copy.json)은 동일 문장 복제와 native
조건을 유지한 문체 적용을 구분한다. 검토 준비는 원본 미변경, Confirm 성공만 최종 반영,
컴파일/충돌 실패는 미반영임을 표시한다. 고급 검토의 실제 전후 소스 제목도 대응한다.

최초 실제 반복 검토에서 Blueprint가 Review를 덮는 기존 계층 결함도 재현했다. 고정된
플로팅 부모 z-index 80보다 canvas 내부 포커스 값이 커질 때 생기므로 canvas에만
`isolation:isolate`를 적용한다. 창 좌표/크기·canvas 내부 포커스 순서는 보존한다.

문구·한정된 canvas 쌓임 범위·canonical resource metadata 외 제품 코드는 바꾸지 않는다. 선택 묶음·재선택 시
고급 확인 초기화·빈 선택 거절·검토 token/target/source 재검증·stale 재시도·입력/초안·
권한·원본 C#·ID/계약/연결·부모/외부 원본·원자 저장·Review→Confirm·최종 CAS·공유
Undo·레이아웃과 나머지 CSS를 보존한다. backend 원문 진단이나 오류 코드를 전역 번역하지 않는다.

최종 독립 LF/CRLF·실제 엔진 Review/Confirm과 새 교차 패키지·전체 복원·실패 수명관리의
검증 결과를 별도 마감 기록에 남긴다. compiler CS0103 원문과 입력/초안 보존, 검토 취소·
반복·재선택·원본 충돌·명시 재시도·cold·실제 실행을 관련 회귀에서 구분한다.

V2 전체를 완료 처리하지 않는다. 다른 실제 노출 안내와 V1 미검증 문맥, V3–V7 별도 팩/
신원·권한·자산 backend, V8 실제 surface/audio, V9 실제 가시성과 종류 호환성/사용중 삭제
결정은 기존 고정 잔여다. Run의 제어 IPC·RenderInput Draw/Pump는 내장 렌더/오디오
전달 provider가 아니며 모의 화면·소리를 실제 연결로 표시하지 않는다. 실제 Windows/
WebView2·모바일·DPI/IME·전체 UI·Library/Space 전달은 별도다. main은 사용자가 병합한다.

[최종 35단계(신규 32·재사용 3) 검증](VALIDATION_V666_REVIEW_GUIDANCE.md)을 통과했다.
