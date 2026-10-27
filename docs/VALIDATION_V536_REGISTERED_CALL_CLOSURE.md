# v536 등록 callee receipt와 저장 copy의 복수 호출

기준 게시 `0cf19d0`, 원본 저장소 `196c605`와 고정 7행의 기존 원본 계약 갱신을 따른다. 다음 최소 단위는 **단독 직접 배정·단일 target same-contract 저장 copy 안에서 하나의 등록 direct-dependency callee를 쓰는 기존 ordinary wrapped use들의 명시 갱신**이다. 완료한 Root/private/새 초안의 owned-callee 연결을 재구현하거나 다중 target·모드 조합을 새 요구로 늘리지 않는다.

## 기존 기반과 연결

기존 `blueprintCallableContracts`는 선언된 project dependency/registry의 manifest와 선택된 함수 선언만 읽는 receipt를 제공한다. 이번에는 그 읽기 전용 조회를 callee별로 한 번 관측하고, 현재 함수 원문의 hash·bodyReads=0·기존 2MiB 예산을 검사한다. Root/private 카드의 복수 use 후보에만 관측한 외부 선언 값을 전달한다. owned draft/소유 unit 목록에 외부 선언을 등록하지 않고 외부 구현이나 provider 선택을 읽지 않는다. compiler Review의 기존 dependency 검증은 별도 단계다.

전체 graph/import/wrapper/기존 records의 `BlueprintCallAbiUses` 후보와 선택 카드 계획이 같아야 한다. 기존 copy owner/직접 배정/출처/target 증거와 callee receipt를 저장 전·메모리 후보 적용 전 lock에서 다시 확인한다. read 종료 시에도 관측한 등록 receipt 전체를 재조회한다. Root와 private의 qualified ID, 원래 본문·값·설명·공개 override 계약을 유지하며 한 authorBatch/checkpoint CAS·copy review group으로 저장한다. 어떤 사용처라도 부적합하면 전체 미적용이다.

실패한 요청의 미적용 조회는 기존 source/CP/hash뿐 아니라 원래 등록 receipt도 같아야 기준 불변으로 반환한다. manifest 원문이 바뀌었는데 함수 원문만 같다고 실패를 자동 재기준화하지 않는다. 응답 유실은 기존 receipt 조회를 먼저 하고, 미적용·원래 기준 불변일 때 사용자의 새 명시 대응으로만 재시도한다. 기록이나 입력을 무조건 지우지 않는다.

새 레이아웃/메뉴/권한·독립 계약 ID·공개 override 구조 변경·자동 C# 재작성은 없다. 74개 canonical UI 리소스와 descriptor/HTML/CSS는 기준 게시와 byte 동일하다.

## 유한한 격리 수용

`Owned.Context`의 copy가 등록 팩 `Lib::Native`를 Root `native`, `frame/native`, `other/native`에서 호출하는 표본을 사용한다. 원래 `ref long amount -> long`을 현재 `int step, double renamed, out long total -> bool`에 명시 대응하고, 값3/5·정확한 int64 local·기존 연결·수동 C# 원문을 보존한다. 이것은 기존 조작의 표본이며 가능한 서명 변경 조합의 전수 지원 주장이 아니다.

기본/독립 창과 private 진입에서 취소·불완전 값·Undo·저장·재시작·Review 취소/compiler Confirm을 확인한다. receipt 누락/위조·다른 callee/owner/nonce·누락 use/경로/binding/마지막 비호환 대응, 실제 쓰기 실패·물리 source/CP 경합·응답 유실·Undo 재시도도 검사한다. 선택 함수 원문이 동일한 상태에서 등록 manifest에 줄바꿈만 추가해 receipt hash가 달라지는 표본도 전체 거절과 실패 기준 승격 차단을 확인한다. 외부 팩 변경은 fixture의 명시적 준비뿐이며 제품이 외부 파일을 바꾸지 않는다.

기존 owned-callee 복수 갱신과 등록 단일 호출은 영향 회귀로 검사한다. 확정 통과 수·실제 명령·해시는 후속 evidence에 기록한다.

## 공간과 남은 경계

시작 여유834.2MiB, 디스크200MiB·RAM 임시 출력768MiB의 순차 검사 예산을 확인했다. 기존 독립 checkout을 FF하고 새 clone을 만들지 않는다. 이번 검사 소유 임시 fixture/package만 전체 증거 보관 후 승인된 수명관리로 정리한다. 기존 원본/SDK/보관 빌드/로그/프로필/사용자 자료는 삭제하지 않는다.

- 다중 target 및 여러 target의 등록 receipt/source 그룹 결합은 이번 최소 단위와 구별한다. copy의 모든 target을 자동 선택·복제하는 새 의미는 추가하지 않는다.
- 새 immutable copy 초안의 등록 복수 use 어댑터와 별도 frame 계약/본문·opaque/whole-body 수동 C# closure는 기존 7/8행·A4–A6의 같은 항목으로 관리한다. 조합별 새 필수 요구로 분해하지 않는다.
- 9행 고급 타입/표시명, I6 아이콘/B2 실제 배지, M4/M11/M12와 신규 이미지·협의·렌더 backend는 별도 미완료다.
- 전체7행/I5/UI 완료, 실제 Windows apphost/WebView2·모바일 기기/터치 수용·Library 전달은 미검증이다. 새 RAM 교차 패키지는 전달용 보관 빌드가 아니다.

## 확정 집중 검사

최종 제품의 실제 엔진/렌더러 12흐름 92확인과 순수 closure4확인이 통과했다. 기본/독립 창의 취소·cold·C# compiler Confirm, 누락/위조/마지막 비호환 대응의 전체 미적용, 쓰기 실패·물리 source/CP 충돌·응답 유실·Undo 후 새 대응 재시도 및 동일 local ID의 Root/private 문맥과 기존 입력 보존을 확인했다. owned-callee 복수 use와 등록 단일 호출은 영향 회귀로 지켰다. 독립 checkout/새 패키지는 별도 후속 evidence다.
