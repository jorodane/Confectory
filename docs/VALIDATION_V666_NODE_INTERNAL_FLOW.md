# M11 개별 C# 내부 흐름: 첫 지원 단위 검증

기준 ZIP과 의미·제한은 [지원 경계](BLUEPRINT_NODE_INTERNAL_FLOW.md)를 따른다. 공개 계약을 바꾸는 독립 복제나 자동 C# 역변환은 추가하지 않았다. 원본 카드의 기존 ‘직접 작성’과 모바일의 기존 내부 편집 진입을 사용한다. 새 헤더 버튼/레이아웃은 추가하지 않았다.

## 집중 검사

관리 실행: `/workspace/artifacts/v536-verification-managed/runs/248cf6d218f0411f9282bb6dfd07b21e.json`. 이 실행의 실패 로그도 보존한다. 임시 checkout/캐시/프로필/합성 프로젝트만 사용하며 기존 사용자 자료나 과거 산출물은 삭제하지 않는다.

- 실제 API: 읽기 전용 미리보기, CRLF 원문·helper 보존, 바깥 ID/핀/실행선 유지, 새 leaf 별도 소유, 누락/변조 증거·경로 충돌·구형 profile·whole-body/forwarded/ref/out/분기 문맥 거절.
- 하나의 author 후보·최종 checkpoint CAS, 원본 물리 경합 거절, 그룹 일부 Review 거절, cold 복원, 실제 C# 컴파일 오류와 수정 입력 보존, Review 뒤 원문 경합의 전체 미반영, 정상 컴파일 Confirm 및 전후 CLR 호출 결과.
- 실제 브라우저/엔진: 원본 진입·단일 코드 미리보기, 전환 및 C# 대화상자 취소, Undo/Redo, 편집 후 cold 취소/재실행, Root 왕복 Save, Review 취소와 명시 Confirm, 최종 cold.
- 쓰기 실패·충돌·응답 유실·늦은 입력·동일 namespace/ID의 다른 프로젝트 왕복을 별도 합성 fixture에서 검사했다. 미확정 응답은 receipt로 조회하고 중복 authorBatch를 적용하지 않는다.
- 최종 원본 버튼 연결은 `flow-ui-final-original-buttons`; 컴파일 오류·최종 CAS 수정은 `flow-api-final-cas`로 다시 검사한다. 앞선 집중 흐름 중 공통 저장 체계 검사는 재사용하며 최종 독립 checkout/패키지 검사는 아래 별도 기록한다.

수정한 실제 결함은 cold 창 메타데이터에서 전환 의도가 누락되던 문제와, 변경되지 않는 보존 원문이 최종 파일 CAS에서 빠지던 문제다. 후자는 Review/Confirm 검증 및 CommitPlan의 읽기 전용 checks로 닫았다. 도중의 fixture·고정 선언 영역 입력 방식 문제는 제품 결함과 구분하고 검사 기대를 유지했다.

<!-- final-verification -->
최종 독립 LF/CRLF checkout·새 Windows 교차 패키지·압축 전체 manifest/복원 검증과 게시 SHA는 검사가 완료되면 갱신한다. 이 문서의 이 상태는 최종 검증 완료나 게시를 뜻하지 않는다.

## 미완료 경계

M11 전체 완료가 아니다. 현재 직접 소유 Root 일반 next 지원을 넘어서는 whole-body 문맥, ref/out/실행 분기, copy/상속/참조 전환 및 별도 편집된 C#/graph 사이의 재활성화 정책은 원문을 보존한다. 구형 profile 자동 승격은 하지 않는다. 저장 전 전환 Undo와 저장 후 ownership barrier를 구별한다. 독립 슬롯 창의 새 전환은 지원을 주장하지 않는다.

B2 다른 사용자/그룹 권한 backend, 종류 C# 표현/사용 중 삭제 대응, M4/M12, 3D/권한 별도 팩 및 나머지 고정 수용 항목은 별도 잔여다. 실제 Windows apphost/WebView2·실제 모바일 기기·전체 UI·Library/Space 전달은 미실행이다. 이번 검사의 CLR 실행과 브라우저 자동화는 Linux에서 수행한다.
