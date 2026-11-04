# M4 비동기 함수의 속성 편집

기준은 저장소 v666 ZIP의 `dist/blueprint.js`에 있는 속성 대상/값 연결과 `blueprintSetAsync`의 명시 async 상태다. 기존 속성 카드·노드 검색·핀 값 선택·Set 출력 UI를 재사용하며 새 레이아웃이나 권한 정책을 추가하지 않는다.

직접 소유한 기존 async Blueprint root에서 속성을 검색하고 대상 객체와 소비 작업을 명시적으로 연결한다. 읽기는 해당 소비 작업 직전에 실행한다. 기존 읽기→출력 보관→필드 쓰기→다른 읽기 순서를 유지하고, 같은 객체를 이후 수정해도 앞서 보관한 출력은 바꾸지 않는다. 이미 지원하는 속성 쓰기의 동일한 typed 계약을 async profile에도 허용한다. field-ref는 async에 허용하지 않으며 receiver·형식·원본 선언·등록된 ObjectModel 계약 검증을 유지한다.

새 읽기·필요한 typed import·receiver·실행 연결·Set binding은 기존 propertyPlan의 한 후보/CAS에 묶는다. 개인 입력의 Undo/Redo·취소·cold 복원, Save 응답 유실의 영수증 재조회와 늦은 새 입력 보존을 기존 체계로 처리한다. 프로젝트 manifest도 async 읽기의 관측에 포함해 저장·복원·Review와 최종 CAS가 같은 원본을 검사한다. 서버가 만든 propertyObservations에 본문·선언·manifest·객체/스키마·C#의 경로와 물리적 원본 baseline을 보관한다. 저장 응답 확인용 authorSaveReceipt는 후보 해시를 계속 사용한다. 두 의미를 분리하여 이후 명시적인 C# 본문 편집이나 Undo/Redo가 물리적 읽기 보호를 재기준화하거나 정상 저장을 막지 않는다. 새로 생성한 소유 소스는 expected-missing CAS를 유지한다. 관측된 속성 본문의 후속 C# 편집은 기존 authorBatch의 후보·저장 응답/실패 수명관리를 사용하여 checkpoint 성공 전에 개인 입력을 지우지 않는다. 기존 slot/copy 저장 경로는 그대로 둔다. 알려진 소스 ID만 cold에서 복원하고 전체 Review를 요구하며, checkpoint와 최종 원본 쓰기의 같은 파일 CAS에 읽기 전용 검사를 전달한다. 이 목록은 새 소스 경로나 외부 접근을 부여하지 않는다. 사용자의 명시적 본문 편집 없이 C#·입출력·비동기 metadata·ID·권한·부모/외부 원본은 변경하지 않는다. 전체 관측 대상이 Confirm으로 실제 반영되면 이전 원본 관측을 종료하여 같은 세션의 후속 저장도 허용한다.

전환 후보를 만들 수 없는 문맥에서도 검증된 현재 async profile의 시계를 표시한다. 표시가 전환 권한을 부여하지 않는다. 호환되지 않는 동기 호출자는 명시적으로 전환하기 전까지 계속 오류이며 자동 대기·호출자 변환을 하지 않는다.

## 경계와 검증

이번 사용자 흐름은 기존 직접 소유 ordinary root의 속성 편집이다. copy/slot/private 문맥의 기존 편집 보호를 완화하지 않는다. 이 단위가 opaque/native 호출 원문이나 공개 override 계약을 자동 변환하지 않는다. Result 없는 본문의 완료 어댑터와 새/내부 소유 본문의 명시 전환은 기존 M4 잔여이며 별도다. M11/M12는 관련 회귀 외 닫힌 상태를 유지한다.

`tools/verify_desktop.py --suite async-property`는 독립 LF/CRLF·캐시에서 실제 Task/await fixture의 속성 UI·저장 실패·경합·응답 유실·늦은 입력·Review 취소/Confirm·실제 CLR 실행을 확인한다. 기존 동기 속성·공개 완료/async 전환도 영향 회귀로 확인한다. 새 교차 패키지와 전체 SHA/manifest 압축 복원본에서 UI/실행·실패 수명관리를 검사한 뒤 최신/롤백·증거를 보관하고 해당 실행 소유 임시물만 정리한다. 최종 단계 수·출처·신규/재사용·보관 SHA는 검증 종료 기록에서 확정한다. 실제 Windows/모바일 기기·전체 UI·Space 전달 완료를 뜻하지 않는다.

이전 M4 compiler는 async profile의 property-set을 거절한다. 코드 rollback만으로 새 async 속성 프로젝트의 실행/편집 복구를 보장하지 않으며 최신 패키지와 프로젝트 원본/초안을 함께 보존한다. 이전 저장 응답 영수증을 새 물리적 관측으로 묵시적으로 해석하지 않는다. 새 propertyPlan 저장에서만 현재의 명시적 전체 읽기 관측을 확정하며 기존 초안·입력을 자동 변환하지 않는다. 선택적 legacy 자동 변환을 새 필수 요구로 만들지 않는다.
