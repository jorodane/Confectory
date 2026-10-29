# v666 직접 소유 중첩 속성 정의

이번 단위는 새 `복합` 속성 안에서 직접 소유하는 하위 속성을 추가하고 이름·타입·기호/이모지/로컬 이미지·기본값을 편집하며 삭제하는 기존 화면을 연결한다. 정보와 객체의 직접 소유 속성을 다룬다. 원본 기준은 저장소 `Confectory-Editor-Prototype-v666.zip`의 `renderObjectSchema`, `property-add-child`, 타입/아이콘 팝오버다. 새 레이아웃·별도 JSON 편집 화면·외부 업로드를 추가하지 않는다.

## 저장과 보호

native의 기존 qualified schema 선언 및 객체의 로컬 속성 schema를 사용한다. 익명 타입 문법을 새로 만들지 않는다. 소유자 ID와 **변하지 않는 native 속성 키 경로**에서 자식 schema ID를 계산하고 양쪽에 `owned-nested-v1` 프로필을 기록한다. 표시명 변경이 저장 키나 참조 ID를 바꾸지 않는다. 부모·외부·기존 named 정보는 이 프로필만으로 복사하거나 소유권을 취득하지 않는다.

정의 트리와 정확한 typed JSON 값은 하나의 private 입력으로 캡처한다. 정보/객체·등록·모든 소유 자식의 변경은 기존 candidate 및 SlotBatch/최종 CAS로 저장한다. 모든 source hash·경로·소유 증거와 기존 기본값/객체를 검증하고 하나라도 불일치하면 전체 미적용한다. `9223372036854775806` 같은 값은 JS Number로 변환하지 않는다. 다른 선언이 내부 자식을 직접 재사용하면 구조 변경을 거절한다. named 정보 자식은 값 편집과 정의 편집을 구분하고 정의 버튼을 노출하지 않는다.

자식 삭제는 해당 키의 값과 정의를 제거하되 기존 자식 선언을 영구 삭제하지 않는다. 기존 자식의 숨겨진 기본값 metadata도 관련 없는 편집에서 유지한다. 타입 변경은 값을 추측해 변환하지 않으며 호환되지 않으면 Save를 거절한다. 기존 소유 복합을 일반 타입으로 바꿀 때도 사용자가 새 기본값을 명시해야 한다. 이미 저장한 일반/named 속성을 새 소유 복합으로 전환하는 UI는 아직 미지원이다. 원래 타입 전환의 잔여로 구분하며 공개 override 계약 위반의 정상 금지나 새 독립 계약 복제 제안과 혼동하지 않는다. 명명된 정보와 부모 원본은 유지된다.

## 실제 발견·수정

- renderer 모듈 초기화에서 live API getter를 spread하여 `view` 초기화 전에 읽던 오류를 prototype facade로 수정했다.
- nested UI를 저장한 뒤 cold 복원이 object 소유 새 schema만 허용하던 누락을 수정했다. 생성 그룹/복원/Confirm은 정확한 프로필·ID·owner·locator를 native에서 검증한 schema 소유 자식만 허용한다. 일반 권한 검사를 완화하지 않는다.
- 저장 응답과 metadata의 객체 속성 순서 차이를 의미 비교로 처리하고, 늦은 입력을 새 source 증거와 canonical private key로 재기준한다. 표시명 앞뒤 공백은 기존 native 정규화와 대응한다.
- 같은 이모지의 문자/Unicode escape 표기를 다르게 비교하여 늦은 입력의 receipt 재기준이 누락되던 오류를 수정했다. 문자열은 값으로 비교하고 숫자 원문 토큰은 유지하며, cold 뒤 전체 typed 값의 의미도 대조한다. 검사 자체의 보류 응답/idle 대기 교착은 별도 수정했고 실패 로그를 보존했다.
- 기본 화면 회귀의 버튼 가림은 cold 후 검사 viewport가 바뀐 경우였다. 검사 창 크기를 일관되게 유지했고 제품 CSS/레이아웃이나 클릭 검증을 약화하지 않았다.

## 검증·제한

집중 실행 증거: managed run `d9395f794dba4d9a8f5d4799197e080f`. 실패 로그·원인·수정 전후 입력 snapshot도 함께 보존한다. 최종 코드의 독립 LF/CRLF checkout·새 Windows 교차 패키지·전체 SHA/mode manifest와 압축 복원본 실행 결과는 아래 마감 기록에 명시했다. 각각의 실제 실행/재사용/미실행 범위를 구분한다.

기본/독립 창·객체, private Undo/Redo·취소·쓰기 실패·source 충돌·응답 유실·저장 중 새 입력·재시작·Review 취소/명시 Confirm을 각각 실제 엔진 fixture로 확인한다. 프로젝트 문맥 검사는 같은 namespace/ID를 가진 별도 실제 프로젝트를 열고 cold로 왕복하는 방식이다. 실행 중 UI 프로젝트 선택기 조작과 동일하다고 표시하지 않는다. 로컬 이미지 검사는 생성한 PNG만 사용한다.

새 프로필을 포함하는 **미확정 생성 초안**은 이전 패키지에서 열지 않는다. 이전 버전의 cold 복원은 schema 소유 새 자식을 모른다. 원본은 Confirm 전 유지되고 새 패키지로 재개할 수 있다. 최신/롤백 패키지 보관이 구버전의 새 초안 호환성을 보장하는 것은 아니다. 확정 선언은 기존 문법이지만 구버전에는 새 정의 편집 UI가 없다.

깊이 8·전체 필드 128·요청/값 예산 및 기존 CAS/권한 보호를 유지한다. 모든 타입/참조/배열 조합의 화면 검증 완료를 의미하지 않는다. 확대의 독립 창/프로젝트 전환, 다른 I6 아이콘, ABI closure·고급 타입/표시명·B2/M4/M11/M12 및 V2–V9는 별도 고정 잔여다. 3D/권한 별도 팩과 이동/실행 분리 합의는 그대로다. 실제 Windows/WebView2·물리 모바일·DPI/IME·Space/Library 전달은 미검증이다.

## 최종 마감 기록 — 2026-10-29

실행 소스 commit은 `a8b59d5d428cbc55ef9f5746296b69cf1be6527f`다. 이후 수용 표/검증 문서만 갱신한다. 패키지의 출처 commit을 문서 commit으로 바꾸지 않으며 `examples/`, `packs/`, `targets/`, `src/`, `tools/`, `tests/` 실행 입력이 같은지 Git diff로 확인한다.

- 집중 native 검증 9개: 신규/저장 소유 정의, 정확한 수치와 주석, cold 생성 소유 증거 위조 거절, cardinality, 숨겨진 기본값 보존, 일반 metadata와의 구분, stale/중복/비호환 전체 거절, raw 직접 재사용 보호, 객체 로컬 schema/기존 데이터 보존.
- 집중 UI 9흐름: 기본 정보·독립 정보·객체, private 취소, checkpoint 쓰기 실패, 실제 source 충돌, 적용/조회 응답 유실, 저장 중 이름 입력, 동일 namespace/ID 별도 프로젝트 cold 왕복. 마지막 두 흐름은 최종 receipt 수정 후 재실행했다. 이전 통과 오류 경계는 해당 원자 저장/거절 경로가 바뀌지 않아 증거를 재사용하고, 버튼 배치 및 문자열 receipt 수정은 새 checkout/패키지의 영향 검사로 확인했다.
- 최종 managed run `3d514d1763ba4a62b7463f734629f911`: **36단계 전부 통과**. 새 독립 LF/CRLF Git checkout·독립 cache에서 Release/MCP/엔진을 각각 새 빌드했다. native 9개와 기존 named 정보/Schema+값 보호, mixed receipt/image guard, 실제 기본/독립/객체 화면, CRLF 독립 창 늦은 입력, 기존 확대/속성 카드 이미지 회귀를 실행했다.
- 새 Windows 교차 패키지의 실제 managed 엔진에서 생성 이미지·중첩 정의·삭제·타입 변경·cold·Review/Confirm을 확인했다. 전체 SHA/모드 manifest로 ZIP을 복원한 뒤 독립 창의 늦은 입력·cold/재저장/Confirm을 다시 실행했다. 패키지 실패 수명 5개 사례도 통과했다. 실제 Windows/WebView2 실행은 하지 않았다.

증거는 `/workspace/artifacts/v536-verification-managed/runs/`의 위 두 run ZIP 및 manifest에 지속 보관한다. 집중 실행의 수정 전 실패/교착 로그와 진단 snapshot도 삭제하지 않았다. 최종 run의 실패 단계는 0개다.

최신 보관 ZIP은 `packages/71ba721824b561f8056c5cfe700634551cc7f59e372af55319302404b116079d.zip`, 51,183,946 bytes, manifest 2,502항목이다. 전체 SHA256은 파일명과 같다. 정상 롤백본은 `b22e7e7f3dba0b24db1b5ffd434eb4f036bc64a1`, ZIP `923bd25e0ef9b784588a433437d6cc248be4d81cb732d5ee0a9169d8d89335b4.zip`이다. 두 보관본과 source/evidence 연결은 managed index에 있다. 앞서 명시한 구버전의 새 미확정 생성 초안 호환 제한은 남는다.

최종 검증 전 디스크 여유 2,358,190,080 bytes → 보관/정리 후 2,354,966,528 bytes. 해당 실행 순증가는 **3.074219MiB**이며 RAM 작업공간은 제거됐다. 표본 최대 메모리는 약 3,971.59MiB였다. 이 수치는 이번 실행의 관측치이며 모든 후속 실행의 증가량을 보장하지 않는다. 승인된 실행 소유 임시물/최신·롤백 수명 외의 과거 자료는 정리하지 않았다.

남은 경계는 기존 일반/named 속성의 소유 복합 전환 UI와 아직 실행하지 않은 참조/배열 조합, live 프로젝트 선택기·기본 viewport/DPI/IME, 확대의 독립 창/프로젝트 전환이다. 다른 실제 노출 아이콘·ABI closure·고급 함수 타입/표시명·B2/M4/M11/M12·V2–V9 및 실제 기기/Space/Library 전달은 원래 고정 목록의 별도 후속으로 남긴다. 이번 지원 단위를 전체 UI 완료로 표시하지 않는다.
