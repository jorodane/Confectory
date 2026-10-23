# v536 호출 ABI 갱신 범위

공개 출력은 호출 뒤 SourceContext로 읽는 값이다. 외부 공유나 프로젝트 접근 권한을 뜻하지 않는다. ABI 갱신은 원본의 계약 갱신 버튼으로만 시작하며, 호출자 typed import와 호출 노드 서명을 같은 저장 단위에서 변경한다. callee 원본 계약을 자동 변경하지 않는다.

| 문맥 | 현재 연결 범위 / 제한 |
| --- | --- |
| 소유 일반 Blueprint root | 단일 본문·단일 동일 callee 호출의 값↔ref. 기존 이름·순서·타입·out·반환·명시적 storage binding을 보존한다. 기존 통합 검증 범위다. |
| 객체 소유 슬롯 | 실제 엔진/화면 검증 완료. 같은 일반 root 제한에 더해 객체 원본 hash·revision·provide 대상을 read/batch/재시도에서 재검사한다. 슬롯 자신의 공용 구현을 편집하며 복사본을 자동 만들지 않는다. |
| 저장된 직접 배치 복사본 | 소유 공용 슬롯 함수와 단일 Blueprint 본문의 값↔ref를 별도 `rebindCopyAbi` 후보로 결부한다. 직접 owner·요구 계약·출처·전체 node record와 최종 provider를 재검사한다. 소유/직접 등록 callee의 common 실제 범위와 한계는 `VALIDATION_V536_SAVED_COPY_ABI.md`를 따른다. donor/등록 팩은 바꾸지 않는다. |
| 비공개 새 복사 초안 | wrapped call/ABI의 source receipt·copy intent 결합은 아직 미지원이다. 기존 copy edits 제한과 차단을 유지한다. |
| 등록 callable | 직접 등록 의존성의 함수/manifest receipt를 기존 명시적 ABI 갱신·적용·checkpoint에 결부했다. 소유 Caller의 typed import/graph만 바꾸며 등록 팩을 쓰지 않는다. 단일 root/본문/호출 값↔ref에 한정하고 `VALIDATION_V536_REGISTERED_CALL_ABI.md`의 common/long 실제6건과 제한을 따른다. 전이 의존성이나 provider 자동 선택은 지원하지 않는다. |
| 실행 대상 | 정확히 선택된 단일 Blueprint 본문만 가능하다. target별 본문이 여러 개인 구현은 import를 공유하므로 다른 본문 영향 검증 없이 변경하지 않는다. 현재 UI 통합 검증은 common 대상이다. |
| 상속/다른 소유자·중첩 그래프·같은 callee 다중 호출 | 미지원. 출처·다른 사용처를 조용히 바꾸거나 연결을 삭제하지 않는다. |
| 이름/타입/순서/추가삭제/out/반환 변경 | 이 갱신 경로에서는 미지원. 임의 대응·storage 생성·자동 변환을 하지 않는다. |

소유 슬롯의 계약 오류 중 현재 root를 안전하게 읽고 `callAbiAvailable`이 확인된 경우에만 기존 편집 버튼으로 들어간다. 배지는 `계약 확인 필요`이며 유효한 연결로 표시하지 않는다. 다른 오류는 성공으로 승격하지 않는다. 저장은 기존 checkpoint/CAS 및 Review/명시적 compiler Confirm 경계를 유지한다. 전체 v536 복원 완료를 뜻하지 않는다.
