# 작업 사본 필터 복원 후 지도 외부 변경 갱신

기준: `cc496e2bf84cceba245812ce16c0849264d3f0f5`. 이전 [대규모 Browser 검증](VALIDATION_V821_LARGE_BROWSER_PREFETCH.md)의 복합 경로에서, 저장 작업 사본 필터가 선택한 객체 ID는 그대로 두면서 전송 상태의 schema projection을 생략하여 기본 속성 창의 표시가 남았고, 이후 명시적 지도 재조회가 그 창에 새 스키마를 읽지 않았다.

수정은 명시적 관계도 재조회 시 실제 현재 프로젝트・활성화・선택 ID와 동일한 보이는 기본 속성 창의 바인딩을 확인한다. 이 창의 schema projection이 없어졌다면 기존 `schema` 읽기 경로로만 다시 읽는다. 프로젝트 전환이나 창 교체, 선택 변경은 기존 최신성 확인과 함께 거절한다. source/CAS·검토·소유권·프로젝트 DLL 관련 계약은 변경하지 않았다.

실제 Linux EditorHome과 Chromium에서 40개 및 400개 객체, 8창을 저장 작업 사본 필터와 함께 재진입·재시작한 뒤 지도 재조회로 외부 스키마 필드가 나타남을 확인했다. 원래 값 대신 입력한 미저장 기본 속성 문자열은 그대로 유지되었다. 임시 프로젝트 외부 스키마 수정은 테스트 종료 전 복구하고 전체 원본 바이트를 검사했다.

검증 실행은 모두 `tests/run_isolated_browser_test.py`를 경유했다. Worker Review(`v821_worker_review_binding_ui.py`), 400개 삭제·복구(`v821_paged_object_retirement_ui.py 400`), 미저장 입력/외부 변경/닫힌 창(`v821_workspace_restore_status_ui.py primary-external-during`, `primary-close-persist`) 통과. 문자열/정수 저장 400개 추적(`project_string_property_save_ui.py 400 --trace-files --guards`)에서 컴파일러 및 프로젝트 DLL 열기 각각 0. `v821_reference_data_run_ui.py 400 --detached`에서 명시 Run 전 각각 0, Run 후 컴파일 7 및 DLL 열기 84와 종료 코드 0 확인.

Windows 실제 기기 실행은 확인하지 않았다.

확장 회귀에서는 기본 창과 독립 창에 서로 다른 미저장 문자열을 입력한 뒤 외부 필드를 추가했다. 두 규모(40 및 400) 모두 두 미저장 입력을 유지하고 두 창에서 새 필드를 표시했다. 수행한 모든 격리 검증의 잔류 자손은 0이었다.
