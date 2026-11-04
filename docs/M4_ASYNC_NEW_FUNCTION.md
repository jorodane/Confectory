# M4: 새 전역 함수의 첫 Confirm 전 비동기 전환

저장소 v666의 새 기능 생성과 `blueprint.js`의 Root/동작 async 메뉴가 기준이다.
이번 흐름은 활성 ProjectPack에서 직접 소유한 새 전역 함수다. 기존 생성 대화상자와
`createDeclaration` → `readFeature/createFeature`를 거친 함수·구현·graph·코드는
첫 물리 Confirm 전에 async 전환·C# 편집·Save·전체 Review→Confirm할 수 있다.
원래 진입 함수와 사용자 C#·ID/연결·권한·레이아웃은 유지한다.

새 전역 scaffold만 현재 method/switch 프로필을 선택한다. 일반 값과 out의 기존
입출력 및 export 연결은 유지하며, ref의 forwarding과 async 거절은 그대로다.
기존 legacy graph나 이미 작성된 본문을 자동 migration하지 않는다. 소유 정보의
별도 구현 scaffold와 참조 scaffold도 이 변경으로 자동 변환하지 않는다.

## 생성 소유권과 원자성

`missing`은 임의의 기존 파일 부재가 아니다. 기존 프로젝트 manifest의 실제 원본
hash와 namespace를 확인하고, 새 함수/구현의 ID·경로가 원본 등록에 없고 현재 등록과
정확히 일치하는지 검사한다. 새 제공 구현·body locator와 graph·code record도 같은
소유 관계로 연결한다. 다른 원본 헤더나 body locator의 경로를 재사용하지 않는다.
정규화한 소유 경로로 비교하며 경로 탈출·별도 ID의 alias는 계속 거절한다.

첫 명시 async 전환 시 새 함수의 계약 원문을 primary receipt의 `creationFunction`에
보관한다. 아직 물리 원본이 없는 함수도 IO 이름/타입/순서와 기존 공개 분기의 보존을
cold·Review·Confirm에서 검증한다. 함수/구현/graph/코드의 원래 `missing`과 기존
manifest/관측 원본 hash는 동일한 최종 CAS에 남는다. 새 파일이나 기존 등록이 바뀌면
전체 Confirm을 거절한다. 미완성 int C#은 실제 compiler에서 거절하며 placeholder를
실행 가능한 코드로 자동 작성하지 않는다.

부모/참조/외부 source나 공개 override 계약을 새 전역 함수로 취급하지 않는다.
미전환 동기 호출자는 계속 오류이며 자동 대기/변환하지 않는다. 새 함수의 값/out
계약도 선언한 그대로며, Task 실행 계약은 기존 companion 인터페이스를 사용한다.

## 유한한 잔여

- 정보 소유 함수의 생성은 기존 `creationOwner`·소유 배정/slot 그룹 경계를 별도로
  연결해야 한다. 전역 함수 증명을 그 경계에 묵시적으로 확대하지 않는다.
- 직접 소유 private/internal graph의 명시 Task 경계와 호출자 연결은 남아 있다.
- 첫 생성 draft Save 전의 생성/계약/async 입력 결합은 후속이다. 이 단위의 순차 Save를
  원래 UX의 영구 정책으로 정하지 않는다.

M11/M12를 다시 열거나 모든 타입/문맥의 순열을 새 필수 항목으로 늘리지 않는다.
고정 V1 검증 잔여/V2–V9·별도 팩/backend·종류 호환성 결정과 실제 기기·전체 UI·Space
전달은 별도 미완료다. 이전 rollback은 새 생성 전환 receipt를 거절할 수 있어 코드
rollback과 해당 생성 초안의 복구를 구분한다. 기존 자료의 추가 삭제는 하지 않는다.
