# v536 copy 내부 실행 enum 편집

기준은 저장소 `196c605`의 v536 `blueprintCSharpContract`/`blueprintCSharpSections`와 기존 enum/body/helpers 편집창이다. 실행 enum은 내부 C# 동작의 실행 결과이며 공개 함수의 매개변수·out·반환 계약과 구별한다. 원래 문서/모바일 카드/Script 창을 그대로 사용한다.

이번 단위는 미확정 및 저장된 same-contract copy의 **기존 private ordinary code switch 노드**다. 기존 분기의 이름·순서·int32 값과 사용자가 편집한 본문·helpers를 한 후보에 묶는다. 루트 copy의 enum 계약 변경, next→switch 변환, 새 제어 흐름 생성 또는 모든 그래프/저장소 조합을 완료로 세지 않는다. 공개 오버라이드 원계약 변경과 독립 계약 복제/새 공개 ID 생성은 제외한다.

- 미확정 copy: qualified 경로의 선택된 frame에서 기존 enum validator와 전체 정의/본문 검증을 사용한다. 원래 snapshot·소유 ID·출처를 유지한다. 본문을 추측해서 바꾸지 않는다.
- 저장된 copy: 기존 소유 정보 창/독립 창의 exclusive binding·원래 checkpoint·전체 source closure·private leaf binding을 요구한다. enum 적용과 수동 본문/helpers 재적용은 격리 후보 안에서만 수행하고 한 번의 checkpoint CAS로 저장한다. 응답 유실은 원래 receipt를 조회한다.
- primary 포트 ID 변경과 소비 중인 case 포트 제거는 거절한다. 다른 frame·동명 leaf·local/정확한64비트 값·공개 계약·부모/외부 원본을 보존한다. enum 변경이 외부 함수/실행 권한을 바꾸지 않는다.
- 이전 실패를 바꾸려면 원래 checkpoint/source가 그대로이고 이전 요청이 미적용이라는 조회 증거가 있어야 한다. Undo 후 사용자가 명시한 새 enum 입력만 재시도하며 이전 실패 기록을 유지한다. 실제 경합/불명 응답은 자동 재적용하지 않는다.

다른 창의 미적용 입력이 있으면 기존 전역 Review가 차단한다. 검사도 그 입력이 Save/cold/재진입에서 보존됨을 확인하고 Review 차단과 원본 불변을 검증한 뒤, 격리 fixture의 해당 창에서 사용자가 명시 취소하는 기존 버튼을 누른 후 Confirm한다. 다른 창 입력을 자동 채택/폐기하거나 검토 보호를 완화하지 않는다.

검증은 `v536_nested_copy_metadata.py enum` 및 `v536_information_external_copy_ui.py ... nested-source nested-enum`의 격리 fixture를 사용한다. 등록 원본·다른 target·공개 계약 보존, 기본/독립 창, 저장/취소/Undo·Redo/cold·실패/충돌/응답 유실/프로젝트 전환/Review 취소·명시 Confirm을 확인한다. 결과와 패키지/checkout 증거는 이 단위의 evidence JSON에 확정 결과만 기록한다.

초기 화면 검사 도중 검사자가 리소스를 갱신한 뒤 재시작하여 manifest 크기 검증이 실패했다. 실패 로그는 scratch에 보존하고 최종 product hash를 고정해 재빌드·전체 해당 흐름 재검증한다. 실패를 통과에 포함하지 않는다. 확정된 copy가 checkpoint 변경 목록에 없을 때는 실제 owned 그래프를 읽도록 fixture를 고쳤으며, 독립 peer 입력이 있을 때 기존 전역 Review 차단·해당 창 명시 취소 절차를 건너뛰던 검사도 정정했다. 제품 보호를 완화하지 않았다.

## 원본 모바일 Script 배치

원본 저장소 v536의 C# 창을 실제로 렌더해 대조한 결과, 현재 스타일에 마지막 모바일 Script 7규칙(전체 높이·고정 머리/버튼·가변 본문·키보드 시 안내 숨김)이 빠져 있었다. 해당 규칙만 `196c605` ZIP의 `Confectory-v536/dist/style.css`에서 그대로 복원한다. 기존 CSS 바이트 접두부와 다른 영역을 유지하고 해당 리소스의 canonical 크기/해시만 갱신한다. 기존 검사가 종료된 뒤 적용해 재시작 리소스 세대가 섞이지 않게 한다.

390×844에서 원본 C# 창은 x/y=6, 폭378, 높이832다. 최종 모바일 검사도 같은 외곽과 버튼의 화면 내 위치·실제 편집/취소/폭 전환·저장·cold·Confirm을 확인한다. 원본 데모의 시각 렌더는 `prototypeOnly`이며 실제 엔진 검사의 통과 수에 넣지 않는다. 물리 모바일 키보드/터치 검증은 아니다. 이 공통 C# 창 범위의 복원이며 전체 UI 시각 대조 완료로 세지 않는다.

## 고정 후속

7행의 private callee ABI 명시 갱신은 이번 단위에서 구현하지 않는다. 내부 enum의 새 case 실행선/새 동작·다른 control 결합도 기존 수용 기준과 실제 연결 상태를 대조한 후 필요한 범위만 판단한다. 이를 가능한 조합 전체의 새 필수 목록으로 늘리지 않는다. 공개 오버라이드 계약 위반 거절은 정상 보호다.

8행의 미검증 공유 caller 문맥/계약 결합과 9행의 정보·참조·외부 함수 핀 타입 및 표시명/native 식별자 연결, I6/B2 및 A4~A6/M4/M11/M12는 별도 후속이다. 전체 UI·실제 Windows apphost/WebView2·모바일 기기/터치·Library 전달은 미완료/미검증이다. 이미지 생성·협의/shared Confirm·렌더/FPS 새 backend와 Helper 작업 권한은 추가하지 않는다.

## 확정 집중 검사

Native Release 0 warning/error, 순수 후보 9확인 및 실제 엔진/렌더러 12흐름 89확인을 통과했다. 취소·연결된 포트 제거 거절·이름/순서/값·잘못된 이름 거절→Undo→cold→명시 재시도·쓰기 실패·응답 유실·경합·기본/독립 창·프로젝트 전환·Review 취소/Confirm과 새 동작/기존 non-copy enum/권한·override 회귀를 포함한다. 74리소스의 canonical 크기/해시를 확인했고 어댑터 JS와 원본 모바일 Script 7규칙 복원 CSS 외 72항목·HTML은 동일하다. 현재 실행의 fixture는 로그/스크린샷/프로필·원본 증거를 ZIP/manifest로 보존한 뒤 그 검사 복사본만 정리했다.

## 독립 checkout·새 교차 패키지

소스/집중 검사 체크포인트 `6381512bb8523b5f3175bb6da26a5ec2e8f31245`를 기존 독립 checkout에 정상 FF하고 원래 `core.autocrlf=true`와 clean 상태·변경 Git blob을 확인했다. Native Release·새 Linux 엔진·실제 독립 copy UI/명시 재시도와 기존 non-copy private enum 회귀 2흐름 12확인, 별도 순수 후보 9확인이 통과했다. 집중 12흐름 89확인은 별도다.

restore·솔루션 Release·MCP Release·새 Windows x64 교차 패키지·package probe·실제 패키지 runtime의 모바일/독립 창 UI/컴파일러 8확인까지 6단계가 통과했다. manifest 2346개/전체 2347개의 파일 목록·SHA, 링크 부재와 Core/Native DLL·변경 소스 바이트가 일치한다. manifest SHA `8a1382f61d73a427d8b3a2fe27dc3b374b1af90190cc9cabed270063492f2bf8`, Native DLL `4b007e041f00b4088f58d97dd25163e5e3abb4e3b2f71434c0530c02a3a16da3`. 실제 Windows apphost/WebView2나 모바일 기기를 실행한 검사가 아니다.

전체 manifest와 fixture ZIP/무결성 증거를 보존한 뒤 이번 RAM 검증 패키지만 정리했다. 보관 패키지·원본·사용자 자료와 기존 캐시는 삭제하지 않았다. 새 전달용 산출물 보관/Library 업로드가 아니다. 이 기록 이후 게시 커밋은 문서/결과 JSON만 추가하고 실행 소스는 위 체크포인트와 같다. 여유 1090.8 MiB. [명령·결과·해시](evidence/v536-nested-copy-enum/package-clean-verification.json).
