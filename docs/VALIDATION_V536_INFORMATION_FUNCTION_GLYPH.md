# v536 정보의 직접 소유 함수 카드 아이콘

기준은 게시 `acf4cd5`와 저장소 `196c605`의 v536 ZIP이다. 원본의
`data-function-icon`은 `editIconValue({...method, name:..., icon:method.icon||'⚙'},...)`를
호출한다. 이번 최소 단위는 **정보 화면의 저장된 직접 소유 함수 카드 → 기호/이모지
선택 → 기존 Save → 재시작·Review/Confirm**이다. 함수 핀·동작 카드 아이콘·중첩
정의·로컬 이미지를 함께 완료로 보지 않는다. 원본 함수 팝오버에는 해제 버튼이 없으므로
새로 만들지 않았다. 기존 팝오버·카드·CSS·키보드 Undo/초점과 창 배치를 재사용한다.

## 연결과 보존

기존 function-add/function-edit 후보의 선택적 `icon`만 `editorIcon`으로 저장한다.
정확한 함수 ID·직접 소유 contain 관계·함수 source hash·등록 경로와 기존 후보/CAS를
유지한다. glyph만 바뀐 경우 typed 계약·핀·caller import·제공 구현·C# 본문을 재작성하지
않는다. 부모/외부/재정의 함수는 기존 writable 경계를 유지한다. 기본·독립 창에서
함수 이름을 편집했다 되돌려도 선택한 아이콘 입력을 지우지 않는다.

실제 화면 검사에서 함수 icon 입력은 보존되지만, 함수 카드의 표시 모델에서 icon을
빠뜨려 재그리기 후 gear로 보이던 연결 누락을 재현했다. ownNode에 같은 glyph를 전달해
수정했다. 소유 함수 projection은 원래 source의 icon을 반환하고, 기존 단일 팝오버가
정보·객체·함수 카드 사이에서도 이전 팝오버 하나만 닫는다. 새 UI는 없다.

저장 응답 대기 중의 새 glyph는 수락한 glyph·함수의 정확한 새 hash와 원래 owner
receipt를 확인한 뒤 별도 입력으로 보존한다. cold 뒤 새 명시 저장만 이를 적용한다.
기존 함수 receipt 형식은 유지하며, 함수 source가 바뀌면 자동 재기준화하지 않는다.
부적합 glyph나 source/소유 충돌은 전체 미적용이고 원문/입력·Undo·취소를 유지한다.
기본값·새 실행 권한·paid model/AI/image 호출·개인 파일 업로드는 없다.

## 승인된 공간 정리

구현 전에 사용자 승인 네 복사 디렉터리만 정리했다. 두 완료 fixture
`v536-information-binding/tmp/confectory-desktop-package-15eugafk`와
`confectory-desktop-package-qm6suimo`의 `owned checkout/Builds/Windows-x64/`
`content/targets/dotnet`, `content/targets/browser-wasm`만 대상이었다.
136개 파일의 목록/SHA·소유권·단일 링크·링크 경계를 보관 원본과 재확인했다.
기존 검사/컴파일러는 zombie 상태였고 활성 앱/검사·실행 컨테이너는 없었다.
FD/maps 제한을 우회하지 않았다. 대상 밖 4,547개 파일의 hash/권한과 보관 원본을
전후 확인했다. 실제 회수 127,619,072 bytes, 정리 후 여유 397,815,808 bytes였다.
상세 승인지역·파일 증거는 scratch의 `v536-approved-target-copies-cleanup/result.json`에
보관한다. 이후 기존 자료는 추가 삭제하지 않는다. 다음 구현의 예산 200MiB와 안전
여유 64MiB를 충족한 뒤 순차 검사한다. 새 테스트 자체 임시 복사본만 기존 수명관리로
정리하며 원본·보관 빌드·고유 버전 파일·로그·프로필·Git·사용자 자료는 보존한다.

## 검증과 정확한 잔여

명령/종료·확인 수·source SHA·원본 handler·공간/메모리·리소스는
`evidence/v536-information-function-glyph/focused-verification.json`을 따른다.
실제 UI 표본은 typed import와 별도 C# 제공 구현이 있는 저장된 소유 함수다.
새 함수의 glyph는 순수 생성 후보에서 확인하며, 신규 함수의 모든 UI 조합을 완료로
넓히지 않는다. 최초 실패/수정 로그·fixture·화면은 scratch에 보관하고 Git에 게시하지 않는다.

I6의 자체 중첩 정의·함수/서명 핀·다른 요소/동작 카드 팝오버·로컬 PNG/JPG/WebP
선택/저장/복원은 별도 잔여다. forwarded 부모·opaque/import 영향 결합, 8행 여러 함수
문맥, 9행 고급 타입/표시명, B2 실제 배지, M4 async/M11 C#→graph/M12 Root 실행
분기도 유지한다. 전체 UI·실제 Windows/WebView2·모바일 기기·Library 전달은 미완료다.

집중 7흐름 51확인, 순수 후보 10확인, 기존 객체/정보 속성·새 정보 속성·함수 생성/편집·연결 계약·생산 final CAS 영향 회귀 38확인이 통과했다. 원본 팝오버 10영역의 치수/위치/스타일과 74개 리소스의 바이트/해시와 이전/새 생성 receipt 보호 6확인을 확인했다. 스키마 실제 경합·쓰기 실패·취소·Undo·응답 유실 조회·늦은 입력·다른 창 보존·compiler Confirm을 분리 검증했다.

## 독립 checkout·새 교차 패키지 확정 결과

실행 소스 커밋 `a23f1d596dcd2ddbae5dea8514a6a1cc0e871534`의 변경 Git blob·기존 autocrlf·clean을 확인했다. 함수의 기존 ID·타입·값과 부모/외부 원본을 보존했다. 기존 독립 checkout에서 Native/CLI Release·새 Linux 엔진, 정보 직접 소유 함수 카드 아이콘·늦은 입력/다른 창 보호의 독립 창 11확인 및 생산 final CAS 4확인이 통과했다. 새 RAM Windows x64 교차 패키지는 restore·Release·MCP·생성·probe·패키지 자체 함수 카드 아이콘 UI 11확인까지 6단계를 통과했다. 전체 2349개/manifest 2348개 목록·SHA·Core/Native DLL과 변경 제품 소스 바이트를 확인했다.

manifest SHA `87253fc9599578df8ae37b8ac8f8b25caab5b3c1a9c232f574ebafd180d44cd8`. 전체 manifest와 fixture/로그/프로필 증거 보관 뒤 이번 실행의 임시 패키지만 정리했고 기존 보관 패키지/SDK/원본/사용자 자료는 삭제하지 않았다. 최종 후속 커밋은 문서/evidence만 달라 실행 코드는 위 소스 커밋과 같다. 실제 Windows apphost/WebView2·모바일 기기/터치·Library 전달 및 전체 UI는 계속 미완료다.
