# v666 그래프 동작 카드 아이콘

기준은 저장소 `Confectory-Editor-Prototype-v666.zip`(SHA-256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)의 `blueprint.js` → `bindResourceNode`다. 원본의 내부 동작 생성은 별도 `node.definition` 객체를 만들고, 아이콘 핸들러는 `node.definition.icon`을 바꾼다. wrapper와 call은 이 핸들러 전에 돌아가므로 **직접 소유한 동작 정의의 표시 변경**이며, 호출된 함수 정의나 같은 함수를 호출하는 모든 카드의 일괄 변경이 아니다. 이미 완료한 정보 함수 카드의 `editorIcon` 편집과 구별한다.

## 유한한 지원 범위

- 실제 소유 `.graph.json`의 code/graph 동작 카드에서 기존 아이콘 버튼·공통 팝오버를 사용한다. 기호·이모지와 사용자가 선택한 PNG/JPG/WebP를 지원하며, 이미지는 기존 128×128 canvas WebP로 정규화한다. 선택한 개인 원본 파일이나 외부 URL을 업로드·저장하지 않는다. 이미지 검사는 생성한 테스트 자산만 사용한다.
- 기존 원본과 같이 선택하지 않은 기본 아이콘은 원래 SVG gear다. 명시한 아이콘은 해당 node의 선택적 `icon` 메타데이터로 저장한다. node ID·함수/핀 계약·본문·값·실행 연결·public override 계약을 바꾸지 않는다.
- 명시적으로 선택한 same-contract copy의 소유 graph와 private 동작에도 같은 메타데이터를 사용한다. 등록된 함수·donor·부모·외부 원본과 copy 출처는 유지한다. 새 독립 계약/함수 ID나 자동 target 선택을 추가하지 않는다.
- call·wrapper·property/set 카드의 다른 종류 편집이나 원본에 없는 핀을 이 기능에 포함시키지 않는다. 원래 readonly인 참조 카드에는 편집 버튼을 만들지 않는다. C#에서 아직 변환하지 않은 가상 Blueprint 미리보기도 기존 보호를 유지한다.

## 저장과 보호

아이콘은 기존 private 입력 map·Undo 스냅샷에 기록한다. 기호/이미지 표시만 갱신하여 저장 중인 창의 generation과 receipt 문맥을 끊지 않는다. 팝오버 취소/Escape는 새 선택을 적용하지 않으며 기존 미저장 입력을 보존한다. Save는 기존 source proof·후보·checkpoint CAS와 `authorBatch`/copy 거래를 사용한다. 수락 응답 유실은 같은 receipt를 조회하고, 저장 중 새 아이콘은 수락된 source로 재기준한 뒤 별도의 명시 Save로 저장한다.

일반 graph의 임시 Save와 원본 파일 확정은 별도다. 다른 편집이 graph/checkpoint를 저장한 경합은 임시 후보 CAS에서 거절한다. Review 뒤 실제 원본 파일이 바뀐 경합은 최종 Confirm CAS에서 거절하며 저장된 이미지 초안과 바뀐 원문을 보존한다. 원본 파일이 바뀌었다는 이유만으로 임시 초안 저장도 항상 차단된다고 주장하지 않는다. 자동 merge나 원문 덮어쓰기를 추가하지 않는다.

graph 변경은 기존 고급 Review의 전체 소스 확인이 필요하다. 검토 상태 `ready`만으로 Confirm을 활성화하거나 자동 확인하지 않는다. 실제 검사도 고급 검토를 열어 전체 내용을 확인한 다음 명시적으로 compiler Confirm을 실행한다.

Core는 기호의 grapheme·길이·금지 문자와 기존 128×128 WebP container 계약을 검증한다. 기존 `RasterIcon` 검증 본문을 공통 Core에 옮기고 기존 선언 편집 호출은 얇은 wrapper로 재사용한다. 새로운 이미지 codec·원격 fetch·파일 경로 해석을 추가하지 않는다. 아이콘은 `displayName`처럼 선언된 node 위치에서만 실행 의미 해시에서 제외하며, argument/local/constant 안의 같은 이름 데이터는 제거하지 않는다. 이 때문에 표시만 바꿔 기존 C#를 stale로 만들거나 본문을 재작성하지 않는다.

## 실제 결함과 검증 구분

- 배율이 복원된 창의 초기 배치에서 아직 transform하지 않은 DOM 좌표를 저장 배율로 나누던 문제가 드러났다. 초기 측정은 실제 미변환 배율을 사용하여 재표시·Undo·cold 후 카드 위치가 늘어나지 않도록 수정했다. 스타일/레이아웃을 새로 만들지 않았다.
- 아이콘을 바꿀 때 전체 창을 다시 만들어 수락 응답의 generation을 끊던 어댑터를 수정했다. 기존 Undo 스냅샷과 renderer의 아이콘 markup을 재사용하면서 표시만 갱신한다.
- 저장된 copy의 표시 입력을 기존 본문/소유 frame 거래에 전달하도록 빠진 `icon` 허용 항목을 연결했다. 공개 계약 편집이나 외부 source 쓰기를 허용한 것이 아니다.
- 새 copy를 아직 Confirm하지 않은 상태에서 재편집하면 생성 등록부가 atomic Review 묶음에서 빠지던 문제를 수정했다. 기존 CreationGroup과 필수 등록부를 보존하며 불완전한 Confirm 거절·명시적 전체 검토는 유지한다.

원본 handler/ZIP 동일성, glyph·위험 이미지 거절, root/private 부모 계약 해시 불변을 native 검사로 확인한다. 집중 실제 UI는 정상·Undo/Redo·취소/Escape·cold·로컬 이미지·쓰기 실패·호출/wrapper로 변조한 요청·응답 유실·늦은 입력·peer checkpoint 경합·최종 원본 CAS를 구분한다. copy의 첫 저장과 저장된 private frame 재편집은 별도 증거로 기록한다.

집중 native 4개 확인과 실제 UI의 정상·쓰기 실패·변조 요청 거절·응답 유실·늦은 입력·취소·peer checkpoint/최종 파일 CAS, 직접 소유 private graph, 기본/독립 정보 창 copy가 통과했다. copy는 최초 root/private 아이콘 동시 저장, 저장된 private 재편집, 형제 동명 leaf 불변·출처/본문 record·필수 등록부 보존, cold·Review/Confirm을 확인했다. 집중 실행은 `runs/29e7e89c433c45f9b223317629b0e589.{json,zip}`로 마감한다. 초기 빌드/검사 실패도 보존하며 통과로 계산하지 않는다. 화면 밖 카드·현재 배율 메뉴의 selector·입력 map 이름·cold 메뉴 위치·Review 진입/확인·copy 문맥 상태 문구를 잘못 가정한 검사와 위 제품 결함을 구별했다. 실제 UI 조작·원문/CAS 확인을 강제 클릭이나 약한 성공 조건으로 대체하지 않는다.

## 최종 독립 검증·보관

실행 코드 commit `450ce7620282105bb63ece5e3be6ebd6f87c7f01`에서 `tools/verify_desktop.py --suite action-icons`의 **49단계가 모두 exit 0**으로 통과했다. LF/CRLF는 `--no-hardlinks` 독립 Git checkout·별도 HOME/NuGet/cache·빈 엔진 cache에서 Release/MCP/엔진을 새로 빌드했다. 일반/private 아이콘, 기본/독립 정보 창 copy, 저장 중 늦은 입력과 기존 소유 중첩 정의·전환·배율·카드 이미지 회귀를 실행했다. 새 Windows 교차 패키지와 그 ZIP 복원본에서 엔진/실제 UI 저장·Review/Confirm을 실행했고 Core/ElementAuthoring DLL의 원본 빌드 일치도 확인했다. package 수명 검사는 성공 반복·복사 중 예외·UI 실패·변조 거절의 5경로에서 해당 실행의 복사본 정리와 증거/원본 보존을 확인했다.

최초 최종 실행 `runs/c6cf72b5e98f4e28bb4ee97184714366.{json,zip}`는 19단계 통과 뒤 기존 배율 검사의 cold 후 메뉴 재진입에서 실패했다. 앞선 배율·휠·터치·미저장 입력/cold 복원의 7개 확인은 통과했다. 같은 제품 코드로 원래 검사 1회와 이벤트/리스너 추적만 추가한 검사 3회는 마지막 창 종료를 포함한 8개 확인이 모두 통과했다(`runs/299532a382834281a8caba91e173cb4d.{json,zip}`). 후속 최종 LF/CRLF에서도 원래 검사 8개씩 통과했다. **이 일시 실패의 원인은 미확정**이며 제품 결함 수정이나 selector 문제 확정으로 표현하지 않는다. 검사 조건·제품 코드 변경 없이 최종 49단계를 재실행했고 최초 실패·진단 증거를 함께 보존했다.

최종 기록은 `/workspace/artifacts/v536-verification-managed/runs/83e498ee7f7642c9bf3915ebb054ce33.{json,zip,manifest.json}`이다. 증거 ZIP은 5,106,220 bytes, SHA-256 `da55ece688752a0cbedbb03a056d40a80b97fa3e19652bae93df134d7d418b4b`다. 승인된 관리 절차로 다음 두 실행 패키지를 지속 보관하고, 보관 후 ZIP SHA/CRC·전체 항목 SHA/모드를 다시 확인했다.

| 보관 역할 | 실행 코드 commit | ZIP bytes / manifest 항목 | ZIP SHA-256 |
|---|---|---|---|
| 최신 | `450ce7620282105bb63ece5e3be6ebd6f87c7f01` | 51,196,450 / 2,502 | `c2752a8078dbc897e72b9113269968fb25259688ef1eb684aaa3be1b78f45de9` |
| 정상 롤백 | `9c83c78c61b195f0436fcadb76913f3db6fa91ec` | 51,187,197 / 2,502 | `c02d624027378f35bcca9883dff9a22d5fca425980e668c4de0a066da122a94d` |

위 ZIP과 전체 manifest/index는 `/workspace/artifacts/v536-verification-managed/packages/`에 있다. 새 패키지의 manifest SHA-256은 `184137e0b345359cb8bedd6aac181c1e934d6522a42095cde6aab3e3e2f93ca8`다. 최종 결과 문서 커밋은 실행 입력을 바꾸지 않으며 패키지 출처는 위 실행 코드 commit으로 유지한다.

최종 실행의 지속 디스크 여유는 2,333,323,264 → 2,327,027,712 bytes로 순증가 6,295,552 bytes(약 6.00 MiB)다. 집중·실패·진단을 포함한 이번 관측 구간은 약 15.30 MiB 증가했다. 단계 샘플 메모리 피크는 약 4.00 GiB였다. 최종 기록은 `cleaned`이며 RAM root는 존재하지 않는다. 이번 실행의 소유 임시물과 기존 승인된 최신/롤백 수명관리만 정리했고, 다른 과거 자료는 삭제하지 않았다. 3–6 MiB를 고정 보장값으로 삼지 않는다.

신규 실행은 위 집중 native/UI와 최종 49단계다. 기존 검사 스크립트·공통 이미지 검증/팝오버·저장/receipt/CAS 기반을 재사용했으며, 이전 패키지는 롤백으로 보관했다. 새 기능 검증을 이전 패키지 결과로 대체하지 않았다. 아래 기기·전체 UI 경계는 미실행으로 유지한다.

## 남은 경계

최신 UI/runtime을 함께 사용한다. 새 `icon` private 입력/저널을 모르는 구버전과 혼용한 재개·저장은 보장하지 않으며 별도 마이그레이션을 수행하지 않는다. 모든 graph/profile/target의 조합을 새 필수 목록으로 늘리지 않는다.

최초 단위의 분류·개념·모듈 헤더 후속은 별도 헤더 단위에서 마감했고, 모듈 핀·Set 출력·종류 항목은 고정 후속이다. 원본에서 readonly인 call/wrapper를 편집하지 않는 것은 정상 보호다. ABI closure·고급 타입/표시명·B2/M4/M11/M12·V2–V9 및 확대의 독립 창/프로젝트 전환 검증도 이번 완료로 묶지 않는다. 최초 단위에서 미실행이던 일반 graph 동작 카드 아이콘의 실제 프로젝트 왕복은 후속 헤더 단위에서 같은 namespace/ID의 다른 프로젝트를 거쳐 이미지·private 입력·원문 보존을 확인했다. 모든 graph/profile/창 조합의 프로젝트 검증 완료로 확대하지 않는다. [후속 검증](VALIDATION_V666_DECLARATION_ICONS.md). 3D/권한 별도 팩과 이동/실행 분리 합의는 유지한다. 실제 Windows/WebView2·물리 모바일·DPI/IME·Space/Library 전달은 별도 미검증이다.
