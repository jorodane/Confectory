# v536 새 copy 초안의 복수 호출 갱신

기준은 게시 `425b2cc`의 고정 7행 경계와 원본 저장소 `196c605`의 기존 복사·원본 계약 갱신이다. 이번 단위는 **확정 전 단일 target same-contract copy의 immutable snapshot 안에서 같은 프로젝트 소유 callee를 쓰는 여러 기존 ordinary execution-enum 호출의 명시 갱신**이다. 이미 끝난 저장 copy의 기능을 새로 구현하거나 공개 override 계약을 바꾸지 않는다.

## 연결과 보존

`PrivateImplementationCopy`의 현재 계약 조회가 기존 단일 호출 검사로 처리할 수 없는 복수 use를 `BlueprintCallAbiUses`로 검사한다. 원래 seed/snapshot·소유자·출처·target guard에 전체 graph/본문 기록/import/현재 계약과 qualified 사용처를 묶는다. 새 독립 계약 ID나 함수는 발급하지 않는다.

기존 대응창에 각 frame의 계획을 전달한다. 모든 호출의 입력·출력 대응을 명시해야 하며 선택 카드의 계획도 전체 계획과 같아야 한다. 누락·추가·경로 변조·오래된 binding·중복/중첩 계획과 마지막 비호환 출력을 전체 거절한다. 중간 결과나 앞선 copy/선언만 반환하지 않는다. 원래 snapshot은 갱신하거나 재기준화하지 않는다.

한 메모리 후보에서 공유 typed import·모든 wrapper/graph·기존 본문을 먼저 검사하고, 원래 UI가 보관한 본문 입력을 함께 적용한 최종 source-ready 후보를 검사한다. 기존 copy 생성/owner 혼합 Save의 단일 후보·checkpoint CAS·receipt·Review/Confirm을 그대로 사용한다. 실패/충돌/불명 응답은 기존 기록과 입력을 보존하고 기존 결과 조회를 따른다. 자동 C# 재작성·추정 cast·외부/부모/원본 쓰기나 권한 확대는 없다. 74개 canonical UI 리소스·HTML/CSS·배치는 기준 게시와 동일하다.

## 유한한 검사 표본

격리 fixture의 `frame/native`, `other/native`는 동일한 local ID를 사용한다. 원래 `ref long -> long` 호출을 현재 `int step, double renamed, out long total -> bool`에 명시 대응한다. 서로 다른 직접 값3/5, 기존 연결, 정확한 int64 local `9223372036854775806`, owner 값 `9007199254740993`, 별도 본문 입력과 현재 donor·부모·Windows target을 보존한다. 이는 기존 사용자 조작의 검사 표본이며 가능한 타입/모드 조합을 새 필수 요구로 늘리지 않는다.

실제 기본/독립 정보 창에서 생성·cold 복원·대응·불완전 입력·Undo/Redo·혼합 저장·Review 취소·compiler Confirm을 검사한다. 마지막 호출 거절, 쓰기 실패/재시도, 실제 callee/owner 경합, 응답 유실 및 취소도 격리 fixture로 확인한다. 확정 통과 수는 후속 evidence에 기록하며 초기 실패를 합산하지 않는다.

첫 fixture의 두 frame 실행선 연결 누락은 정상 source-ready 거절이었고 fixture만 수정했다. 다음 read 검사의 `valueJson`은 상수 숫자 자체가 아닌 기존 `{"constant":5}` 형태이므로 실제 저장 graph와 조회 계약을 확인하여 검사 기대값을 수정했다. 두 실패 로그/fixture는 scratch에 보존한다. 마지막 호출 거절 뒤 Undo 재시도 검사는 창을 닫아 이력을 재구성한 순서 오류를 확인하고 기존 창을 접어 보존한 상태에서 실제 Undo로 재검증한다. 최초 build는 기본 CLI HOME의 읽기 전용 경로 때문에 시작 전에 실패했으며 기존 승인된 SDK/CLI 환경으로 재실행했다. 제품의 검증 조건은 완화하지 않았다.

## 공간과 남은 경계

시작 여유912.2MiB, 디스크 최대200MiB·RAM 임시 출력768MiB 예산을 확인하고 기존 독립 checkout을 FF하여 순차 검사한다. 이번 검사 소유 임시 fixture/package만 전체 증거 보관 후 정리하며 기존 원본/SDK/보관 빌드/로그/프로필/사용자 자료를 삭제하지 않는다.

- 등록 callee/all-target receipt 결합과 저장 copy의 Root 카드 직접 진입은 별도 실제 잔여다. 등록 callee의 단일 호출 기존 지원은 유지한다.
- 다른 frame 계약/본문의 동시 변경과 opaque/whole-body 수동 C# closure는 이번에 결합하지 않는다. 기존 4/8행·A4–A6의 같은 항목으로 중복 집계하지 않는다.
- 9행 고급 타입/표시명, I6/B2 및 M4/M11/M12와 신규 이미지·협의·렌더 backend는 별도 미완료다.
- 전체7행/I5/UI 완료, 실제 Windows apphost/WebView2·물리 모바일/터치 수용, Library 전달을 주장하지 않는다. 새 RAM 교차 패키지는 검사 산출물이며 다운로드 가능한 전달본이 아니다.

## 확정 집중 검사

최종 제품의 실제 엔진/렌더러 10흐름 72확인과 순수 closure7확인이 통과했다. 기본/독립 창의 취소·cold·C# compiler Confirm, 누락/위조/마지막 비호환 대응의 전체 미적용, 쓰기 실패·물리 source/CP 충돌·응답 유실·Undo 후 새 대응 재시도 및 원래 snapshot·별도 본문·owner 정확한 값과 늦은 입력 보존을 확인했다. 새-copy 단일 호출과 저장 copy의 기존 지원도 회귀로 지켰다. 독립 checkout/새 패키지는 별도 후속 evidence다.
