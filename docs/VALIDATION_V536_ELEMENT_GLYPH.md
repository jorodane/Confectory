# v536 객체·정보의 기호·이모지 아이콘

기준은 게시 `01a5644`와 저장소 `196c605`의 v536 ZIP이다. 이번 단위는 고정 I6의
**객체·정보 properties 카드 → 아이콘 편집 → 기호/이모지 적용 → 임시 저장 →
Review/Confirm**만 연결한다. 기본 창과 기존 독립 properties 창을 재사용한다.
창 간 키보드 진입에서도 원본처럼 아이콘 팝오버 하나만 유지한다. 원본 팝오버의 선택 목록·문자 입력·적용·닫기·Escape·초점 복귀·화면 배치를 유지한다.
CSS와 공개 함수 계약, 계정·실행 권한은 변경하지 않는다.

## 원래 잔여와 구현 안전 경계 대조

| 조작 또는 조건 | 확인한 현재 상태 | 이번 판정 |
|---|---|---|
| copy의 ordinary wrapper 갱신과 다른 frame 수동 본문을 함께 저장 | `01a5644`의 단일 후보/CAS·Root/private·기본/독립 수용이 존재 | 이미 완료한 단위를 반복 구현하지 않음 |
| 직접 소유 private graph의 실제 forwarded 부모 계약 대응 | 기존 `InformationFunctionPrivateCalls`의 명시 부모/자식 매핑·본문 검증이 존재 | 엔진 기반 전체 부재 또는 새 독립 메뉴로 분류하지 않음 |
| copy의 실제 내부 변경이 forwarded 부모 또는 opaque/whole-body/import에 영향을 줌 | `BlueprintCallAbi`/`BlueprintCallAbiUses`는 미대응 source/storage를 거절한다. 수동 C#·typed import 검증 기반과 해당 copy closure의 결합은 구별해야 함 | 실제 관련 원래 내부 편집의 조건부 안전 경계로 A6/7행에 유지. 이번에 완료로 바꾸지 않음. 별도 영향을 주지 않는 조합을 새 필수 작업으로 추가하지 않음 |
| 공개 override의 입출력 구조 변경·부모/외부 원본 쓰기 | 원계약·소유권 보호로 거절 | 정상 금지. 독립 계약 복제·새 ID 발급은 필수 제외 |
| 객체·정보 카드의 아이콘 편집 | 원본 `editObjectIcon`→`editIconValue` 조작이 있으나 현재 버튼은 unsupported. 기존 `editorIcon` 문자열 저장 기반이 있음 | 원래 요구와 실제 미연결이 명확한 다음 최소 단위로 선정 |

`forwarded`/`opaque`라는 엔진 표현만으로 새로운 부모 계약 편집 기능이나 가능한
C# 조합 전체를 의무화하지 않는다. 실제 영향받는 원래 흐름의 source closure는
계속 검증해야 하며, 이 대조는 7행·8행·A6 전체 완료 선언이 아니다.

## 실제 저장과 보존 경계

팝오버의 적용 전 선택·불완전 입력은 기존 원본 의미대로 취소할 수 있다.
적용한 glyph는 해당 프로젝트·문서·properties 창의 입력에만 보관한다. 기존
설명·값 입력과 같은 source revision/hash를 유지하고, 임시 저장 때 한 owner 후보에
전달한다. 객체와 정보 모두 `editorIcon` 메타데이터만 변경하며 필드·참조·부모·
정확한 64비트 값·주석·함수/핀/본문은 기존 병합·검증으로 보존한다.

새 후보의 아이콘 작업은 한 grapheme 기호/이모지, 제한된 길이와 제어문자/마크업
검증을 사용한다. 부적합한 마지막 작업·중복 아이콘·잘못된 대상/동시 변경은 후보
전체를 거절한다. 여러 endpoint를 순서 저장하거나 live의 일부를 먼저 변경하지 않는다.
기존 checkpoint 거래와 최종 CAS, source 관측·명시적 Review/Confirm을 그대로 사용한다.

성공 여부가 불명확하면 기존 receipt 조회를 먼저 수행한다. 응답 대기 중 새 glyph는
확인된 저장본 hash와 실제 수락 glyph를 receipt에 구별해 보관하며, 재시작은 실제
source 변경을 자동으로 재기준화하지 않는다. 다른 창의 입력을 채택하거나 지우지 않는다. 다른 창에 미적용 입력이 남은 최종 Review는 기존 보호로 거절하며, 사용자가 그 창에서 명시적으로 처리한 뒤 진행한다.

## 수용 증거

명령·종료코드·확인 수·source SHA·공간/메모리·원본 ZIP 함수 위치 및 해시는
`evidence/v536-element-glyph/focused-verification.json`에 기록한다. 로그·화면·fixture·
프로필은 해당 실행 scratch 증거로 보관하고 Git에는 게시하지 않는다.

검사는 격리 fixture에서만 수행한다. 사용자 프로젝트 실행, 유료 AI/이미지 호출,
사용자 자료 삭제 또는 권한 확대는 하지 않는다. 기존 자료를 추가 정리하지 않으며
이번 검사 소유 임시 복사본의 승인된 종료 수명관리만 사용한다.

## 정확한 미완료

- I6 전체는 부분 완료다. 이번 대상은 객체·정보 카드의 문자 glyph다. 사용자가 고른
  로컬 PNG/JPG/WebP의 자산 저장·복원, 속성/함수 핀 아이콘, 이 properties factory 밖
  요소의 원본 아이콘 팝오버는 별도 미연결/미검증이다. 이미지 업로드 버튼은 원본
  자리에 비활성으로 남기고 미연결 이유를 표시한다. AI 이미지 제공자는 추가하지 않는다.
- copy의 실제 forwarded 부모/opaque/import source closure와 8행의 여러 함수 복합
  문맥은 기존 조건부 경계를 유지한다. 9행의 고급 핀 타입·표시명/생성 식별자도 남는다.
- B2는 기존 실제 작업 상태의 배지 어댑터 잔여다. 데이터 전체 부재로 단정하거나
  가짜 작업자를 생성하지 않는다. M4 async, M11 개별 C#→graph, M12 Root 실행 분기는
  기존 실행/저장 계약 연결 잔여이며 이번 glyph 단위에 섞지 않는다.
- 실제 Windows/WebView2·DPI/IME·모바일 기기/터치, Library 전달, 전체 UI 수용은
  미완료다. RAM의 새 Windows 교차 패키지 검사는 실제 기기 실행이나 전달이 아니다.

집중 9흐름 49확인, 객체/정보 순수 후보 2확인 및 영향 회귀 8확인이 통과했다. 성공·실패·경합·응답 유실·취소·문자 입력 Undo·cold·Review/Confirm, 성공 응답 대기 중 새 glyph의 receipt 보존과 다른 기본 창 exact64 입력 보존을 확인했다. 원본 팝오버 10영역 비교와 74개 WebBundle 리소스의 바이트/해시가 일치한다.

## 독립 checkout·새 교차 패키지 결과

제품 소스 커밋 `ca03d9ca3311fd2fb573ccbc2d719a3e622d1cc3`와 검사 ZIP 경로만 수정한 `e5e583f3d26fd82702079846f55075fee697d5c3`를 기존 독립 checkout에 정상 fast-forward하여 변경 Git blob·기존 autocrlf·clean을 확인했다. Native/CLI Release와 새 Linux 엔진, 독립 정보 창의 늦은 glyph/기본 창 입력/Review 보호 9확인 및 생산 final CAS 4확인이 통과했다. 새 RAM Windows x64 패키지는 restore·Release·MCP·생성·probe·패키지 자체 glyph 화면 9확인까지 6단계를 통과했다. 전체 2349개/manifest 2348개 목록·SHA·Core/Native DLL 및 변경 제품 소스 바이트를 대조했다.

manifest SHA `52e9560d16d090116f3c3036e6abb0820c29dce8fe20d84332cdc6f4697762ac`. 출시물에 원본 ZIP이 없는 것은 의도된 구성이다. 검사 원본을 검사 저장소에서 읽도록 경로를 고친 뒤, 제품 소스/패키지 해시 불변을 확인하고 기존 새 패키지에서 화면 검사를 재개했다. 통과한 생성/probe 단계를 중복 실행하지 않았다. 전체 manifest와 fixture/로그/프로필 증거를 보관한 뒤 이번 실행의 임시 패키지만 정리했다. 기존 보관 빌드·SDK·원본·사용자 자료는 삭제하지 않았다. 최종 후속 커밋은 문서/evidence만 달라 실행 코드는 위 소스 커밋과 같다. 실제 Windows apphost/WebView2·모바일 기기·Library 전달 및 전체 UI는 계속 미완료다.
