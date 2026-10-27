# 7행 원래 조작과 남은 경계

최신 [wrapper와 다른 frame 결합 수용](VALIDATION_V536_COPY_WRAPPER_FRAME_SAVE.md)은 한 wrapper/callee 명시 갱신과 ordinary source/intent를 기존 Root/private Save·한 후보/CAS에 연결한다. 아래 과거의 wrapper 단독/다른 frame 입력 거절은 이 지원 범위만 해제한다. 실제 forwarded/opaque 영향 후보와 다른 계획은 해당 최신 표의 안전 경계·원래 요구 구분을 따른다.

Root 복귀 Save의 최신 지원/잔여 판정은 [Root 수용 기록](VALIDATION_V536_ROOT_COPY_SAVE.md)을 우선한다. 원래 빵부스러기·전체 graph Save에 근거한 ordinary private 입력 진입만 해제하며, forwarded/다른 frame 영향 후보와 opaque는 아래 같은 고정 항목으로 한 번만 관리한다.

새 copy 등록 복수 use의 최신 결과는 [새 등록 closure 검증](VALIDATION_V536_PENDING_REGISTERED_CLOSURE.md)을 우선한다. 아래 과거 단위의 같은 미완료 표현은 해당 지원 범위만 해제한다.

대조 기준은 게시 `7ea290211e472a50d661688774ed356c5e163a6e`, 원본 저장소
`196c605`의 v536 및 고정 9행이다. 과거 문서의 포괄적인 미완료 표현은
새 요구나 ref/out/값 변환 조합별 작업 목록으로 사용하지 않는다.

원본 `blueprint.js`의 wrapper 카드에는 기존 **원본 계약 갱신**이 있고,
내부 흐름에서도 같은 기능 카드를 사용한다. 현재 root의 일반 대응은
`V536_CALL_ABI_SCOPE.md`, 저장 copy의 private 첫 연결은
`VALIDATION_V536_SAVED_PRIVATE_ABI.md`에 실제 수용 범위가 있다.

이번 표는 직전 게시에서 **private callee ABI의 서명 경계 밖**이라고 남긴 조작을
재대조한 것이다. 다른 고정 수용 행을 새 7행 요구로 가져오지 않으며, 전체 7행이나
모든 copy 문맥의 전수 완료를 주장하지 않는다.

최신 저장 copy 복수 호출 단위는 [호출 closure 검증](VALIDATION_V536_COPY_CALL_CLOSURE.md)을 우선한다. 아래 대조 시점의 단일 호출 제한 중 그 지원 경계만 해제한다.

## 유한한 실제 잔여

| 원래 사용자 조작 | 대조 시점의 현재 결과 | 완료 조건 / 다음 단위 |
|---|---|---|
| 선택한 copy 내부 호출에서 원본 계약 갱신 후 기존 입력과 출력 소비자를 명시적으로 대응 | `BlueprintCallAbi`의 private 전용 guard가 ref→값 외 서명 변경을 일반 mapping 검사 전에 차단 | 기존 root의 입력/출력 mapping을 선택 frame에 재사용한다. 새 값은 직접 적고, 제거 입력의 남은 값·미대응 소비자·타입 오류는 전체 거절한다. 전체 tree/import/wrapper와 소유 증거를 한 후보/CAS로 검사한다. **이번 최소 단위** |
| 같은 copy에서 다른 호출/frame 계약·본문까지 영향을 받는 원본 계약 갱신 | 같은 callee의 다른 사용처/import 또는 별도 frame 입력이 있으면 현재 단일 호출 helper/저장이 전체 거절 | 실제 선택 호출과 영향받는 frame 계약·본문의 명시 대응, 모든 source/import를 하나의 후보로 결합해야 한다. 현재 미구현이며 자동 재작성으로 우회하지 않는다. 별도 target/copy closure와 공유 caller가 겹치면 기존 A4–A6/8행으로 한 번만 집계한다 |

두 행은 사용자 조작 단위다. 이름·타입·핀 수·역할·순서·반환의 가능한 순열을
독립 필수 항목으로 다시 늘리지 않는다. 일반 mapping의 명시 대응/타입 검증과
전체 후보 검증을 공유하고, 실제 검증한 문맥과 그 밖의 경계를 구별한다.

## 정상 보호 및 필수 요구에서 제외한 것

- 공개 override의 매개변수·출력 계약 변경은 사용자 확정 정상 금지다. 내부에서
  호출하는 다른 함수의 갱신과 구별한다. 새 독립 계약/ID 발급은 필수 제외다.
- donor/부모/외부 팩 쓰기, 다른 owner/target/nonce의 요청, stale source/CAS,
  미대응 값·소비자의 조용한 삭제와 임의 cast/C# 재작성은 정상 거절이다.
- 원본의 target 선택 복사는 유지한다. 모든 target 자동 복제와 alias/import만
  편집하는 새 전용 화면, legacy bool 시각 분기를 필수 잔여로 추가하지 않는다.
- 여러 target/shared-owner가 단일 copy receipt에서 거절된다는 사실만으로
  모든 조합을 새 의무로 만들지 않는다. 실제 원본 조작으로 필요한 source closure는
  위 두 번째 행 및 기존 A4–A6의 같은 항목으로 관리한다.

## 공간과 검증 경계

시작 시 `/workspace` 997.8MiB, 별도 `/tmp` tmpfs 약8.6GiB를 확인했다.
이전 동일 환경 build 증가 12.7MiB와 UI 최대 약4.8GiB cgroup 사용량을 근거로,
순차 검사 디스크 예산160MiB·RAM 임시 출력512MiB를 확보한 뒤 시작한다.
기존 독립 checkout을 FF하고 새 clone을 만들지 않는다. 현재 검사 소유 임시
fixture/package만 전체 증거를 보관한 뒤 승인된 수명관리로 정리한다.
기존 보관 빌드/원본/SDK/로그/스크린샷/사용자 자료는 삭제하지 않는다.

8행 나머지 공유 caller 결합과 9행 고급 타입/표시명, I6 로컬 아이콘·B2 실제 배지·
A4–A6·M4/M11/M12는 별도 목록이다. 신규 이미지/협의/렌더 backend와 Helper
권한은 추가하지 않는다. 실제 Windows apphost/WebView2·모바일 기기/터치·
Library 전달 및 전체 UI 완료는 이번 단위의 결과가 아니다.

## 이번 최소 단위의 결과

첫 행의 선택된 한 내부 호출은 기존 root 대응을 재사용하여 연결했다. 저장된 단독 배정 copy의 기본/독립 창과 새 복사 초안의 실제 UI/혼합 저장·compiler Confirm, 실패/충돌/응답 유실·Undo/cold를 검증했다([검증 기록](VALIDATION_V536_PRIVATE_ABI_REMAP.md)). 공개 override 계약은 유지한다.

남은 조작은 두 번째 행의 다른 호출/frame 계약·본문까지 영향을 받는 source closure 결합이다. 같은 callee의 여러 사용·opaque 문맥과 별도 frame 입력을 현재 단일 호출 경로에서 추측해 고치지 않는다. 이를 모드 조합별 작업으로 분해하거나 전체 7행/8·9행/UI 완료로 합산하지 않는다.

## 저장 copy의 기존 호출 closure

선택한 private 카드에서 같은 프로젝트 소유 callee의 여러 기존 ordinary wrapped call을 호출별 명시 대응과 한 후보/CAS로 연결했다. 두 private frame의 실제 기본/독립 UI와 Root/private 혼합 순수 후보를 검증했으며, 공유 import·전체 graph·본문 기록을 함께 검사한다. 공개 override·원본/본문/값/설명·소유권은 유지한다.

이 대조 시점의 잔여는 새 immutable copy의 복수 use 어댑터, Root 카드 직접 진입, 등록/all-target source receipt, 다른 frame 계약/본문 동시 편집과 opaque/whole-body closure였다. 새 copy 어댑터의 최신 결과는 아래 절과 해당 검증 문서를 우선한다. 현재 단일 저장/기존 wrapped-use 단위와 구별하고 기존 4/8행·A4–A6와 중복 집계하지 않는다. ref/out 변환 조합별 새 요구를 추가하지 않는다. 실제 지원/실패/검증은 위 최신 문서와 evidence를 따른다.

독립 checkout·교차 패키지 결과는 최신 closure 검증/evidence를 따른다. 실제 Windows/mobile/Library 전달은 별도 미완료다.

## 새 immutable copy의 복수 호출 어댑터

최신 [새 copy 검증](VALIDATION_V536_PENDING_CALL_CLOSURE.md)의 범위를 우선한다. 프로젝트 소유 callee의 기존 ordinary wrapped use들을 원래 snapshot/현재 계약의 별도 식별성과 호출별 명시 대응으로 결합한다. 저장 copy의 완료 단위와 구별하며 등록/all-target receipt·저장 Root 직접 진입·다른 frame 계약/본문/opaque closure는 실제 잔여로 유지한다.

독립 checkout·교차 패키지 결과는 최신 closure 검증/evidence를 따른다. 실제 Windows/mobile/Library 전달은 별도 미완료다.

## 저장 copy의 Root 카드 직접 진입

최신 [Root 진입 검증](VALIDATION_V536_ROOT_CALL_CLOSURE.md)을 우선한다. 원래의 전체 ordinary-use 후보·소유권/출처·명시 대응을 Root 카드에 연결한다. 새 copy 초안/private의 완료 범위와 구별하며 등록/all-target receipt·다른 frame 계약/본문/opaque closure는 실제 잔여로 유지한다.

독립 checkout·교차 패키지 결과는 최신 closure 검증/evidence를 따른다. 실제 Windows/mobile/Library 전달은 별도 미완료다.

## 저장 copy의 등록 callee 복수 use

최신 [등록 receipt closure 검증](VALIDATION_V536_REGISTERED_CALL_CLOSURE.md)을 우선한다. 기존 direct-dependency 읽기 전용 선언/receipt와 전체 ordinary-use 후보를 Root/private 진입·한 후보/CAS에 결합한다. 다중 target source/등록 receipt 그룹, 새 immutable 초안의 등록 복수 use 및 별도 frame 계약/본문/opaque closure는 실제 잔여로 구별한다.

독립 checkout·교차 패키지 결과는 최신 closure 검증/evidence를 따른다. 실제 Windows/mobile/Library 전달은 별도 미완료다.

## 일반 다중 target의 등록 receipt 결합

최신 [다중 target 등록 ABI 검증](VALIDATION_V536_REGISTERED_TARGET_ABI.md)은 직접 소유 ordinary all-Blueprint 구현의 target별 기존 명시 대응·공유 import와 읽기 전용 등록 snapshot을 한 후보/CAS·Review/Confirm에 연결한다. 이번 화면 표본은 common/windows 두 target, target당 한 등록 wrapped call이다. 저장 copy의 다중 target/provenance 그룹·새 copy의 등록 복수 use 및 별도 frame 계약/본문·opaque closure는 같은 기존 잔여이며 7/8행·A4–A6 밖으로 늘리지 않는다. 9행·I6/B2·M4/M11/M12와 실제 Windows/mobile/Library 전달은 별도 미완료다.

일반 다중 target 등록 receipt의 독립 checkout·새 교차 패키지 증거는 위 최신 검증/evidence를 따른다. copy 다중 target 및 다른 기존 잔여와 실제 Windows/mobile/Library 전달은 완료로 합산하지 않는다.

## 명시적으로 배정한 서로 다른 target copy의 한 후보

최신 [copy target 후보 검증](VALIDATION_V536_COPY_TARGET_CANDIDATE.md)은 서로 다른 owner가 기존 선택창에서 common/windows를 각각 명시 복사한 뒤 한 소유 callee와 두 copy 본문을 결합하는 실제 경로를 다룬다. 기존 backend를 재사용하고, 검토 뒤 배정 변경을 놓치던 read-only 원본 CAS만 보완한다. 한 copy의 모든 target 자동 복제와 공개 override 계약 변경은 추가하지 않는다. 새 copy 등록 복수 use·별도 frame 계약/본문·opaque closure와 8/9행·별도 UI·기기/Library는 위 범위의 실제 잔여로 유지한다. 전체 7행 완료로 합산하지 않는다.

## 새 immutable copy의 등록 복수 use

[새 등록 closure 검증](VALIDATION_V536_PENDING_REGISTERED_CLOSURE.md)은 단일 target의 기존 ordinary 호출들을 원래 snapshot/선택 receipt·qualified use 계획·한 후보/CAS에 결합한다. 생성된 copy의 저장 후보에 읽기 전용 receipt를 보관하고 cold·Review/Confirm에 재조회한다. 공개 override·부모/외부 원본·레이아웃/권한은 유지한다. 별도 frame 계약/본문 및 opaque closure, 기존8행 여러 함수 문맥·9행·I6/B2·M4/M11/M12·native/Library는 남긴다. target 자동 복제나 가능한 조합 전체를 새 요구로 추가하지 않으며 7행 전체/UI 완료로 합산하지 않는다.

## 저장 copy의 별도 frame ordinary 핀·본문 결합

[분리 frame 수용 검증](VALIDATION_V536_SAVED_COPY_FRAMES.md)은 동일 author surface/owner의 저장 single-target copy에서 현재 편집 중인 private frame의 Save를 통해 두 private frame의 기존 ordinary code leaf 핀·값·직접 작성 본문을 한 후보/CAS에 연결한다. Root로 돌아와 Save하는 진입은 원래 guard에 남아 있으며 완료로 세지 않는다. frame별 Undo/취소·실패 입력·원래 source closure와 Review/Confirm을 보존한다. 새 copy에서 이미 되던 owner 결합을 중복 구현하지 않는다. 원본 callee ABI 갱신에 따른 forwarded frame 계약·wrapper와 다른 frame 일반 편집의 결합, opaque/whole-body closure는 이 단위 밖의 기존 잔여로 구별한다. 공개 override 구조 변경은 정상 금지·독립 계약 복제는 필수 제외다. 8/9행·별도 UI·실제 Windows/mobile·Library 전달과 전체 UI 완료로 합산하지 않는다.

## Root 복귀 Save 마감

[Root 수용 기록](VALIDATION_V536_ROOT_COPY_SAVE.md)은 현재 frame뿐 아니라 기존 Root 버튼에서 단일/복수 ordinary private 핀·값·수동 본문을 같은 소유 후보/CAS로 저장한다. 직전 분리 frame 단위의 Root guard 잔여는 이 범위만 해제한다. wrapper 원본 계약 갱신 및 실제 forwarded 영향과 다른 frame 계획, opaque/whole-body source closure는 원래 내부 편집/전체 graph 저장에 필요한 기존 결합이며 독립 기능 설계나 가능한 조합 전체를 추가하는 뜻이 아니다. 공개 override 구조 변경/새 독립 계약 복제는 정상 금지·필수 제외를 유지한다. 8/9행·별도 UI·실제 Windows/mobile·Library 및 전체 UI 완료로 합산하지 않는다.
