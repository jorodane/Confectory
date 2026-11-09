# 공통 아이콘 창 IME Escape 보호 검증

동결 `fe3d35dd441a1dccc5ca7d9b3bb6e14eb25b0e3d`의 신규29단계·재사용0을 통과했다. 분포 `{"glyph": 1, "lf": 11, "crlf": 11, "windows": 2, "packaged": 1, "restored": 2, "package": 1}`.
[원본 근거·지원/호환 경계](V2_GLYPH_IME.md)를 따른다.

| 범위 | 확인 결과 |
|---|---|
| 원본·변경 | 고정 v666 editIconValue와 게시 4ef098e4를 대조했다. 공통 glyph-popover.js의 Escape listener 한 곳과 bundle의 해당 크기·해시만 제품 변경이다. 기존 함수 상세 IME guard·call site·native backend/계약/권한·CSS/HTML·저장 형식은 동일하다 |
| 재현·수정 | 실제 소유 분류 헤더에서 기호/생성 이미지 각각의 isComposing·legacy229 Escape 입력 유실 네 경우를 게시본으로 재현했다. 수정 후 복사본·미리보기·포커스/aria·적용 가능 상태를 유지하고 조합 기본 동작을 막지 않음을 확인했다 |
| 취소·수명 | 일반 Escape는 창을 닫고 anchor로 돌아가며 적용하지 않는다. 반복 명시 닫기·cold에서 미적용 복사본만 버리고 checkpoint/원본을 보존한다. 원래 이미지 decode sequence/수명·pointer/scroll/resize·owner callback은 소스가 같다 |
| 저장·최종 적용 | 명시 한글 기호 Apply·private Undo/Redo·Save/cold·Review 취소/Confirm 후 생성 이미지도 별도 Apply·Save/cold·Review 취소/Confirm했다. 원래 Exact64·부모·주석 CRLF와 해당 metadata 파일 외 모든 원본 C#·선언 바이트를 보존했다 |
| 독립·패키지 | LF/CRLF no-hardlinks 독립 checkout·HOME/NuGet·Release/MCP·빈 Linux engine cache와 boundary/normal/cancel UI를 새로 실행했다. 새 Windows 교차 생성/구조·SHA와 포함 Linux engine 정상 UI, 전체 ZIP CRC/SHA/파일·디렉터리 mode 복원 뒤 cancel/cold, 실패 수명 관리를 확인했다 |

실제 UI 표본은 직접 소유 GlyphCategory이며 공통 helper의 다른 진입점 전체를 개별
실행한 것은 아니다. 기존 call site와 계약/원본/권한·저장·Review/최종 CAS 구현 불변은 정확한
소스 대조로 확인한다. 전체 ABI/권한 거절·충돌/응답 유실 행렬을 이번에 새로 실행했다고
주장하지 않는다. 이 단위는 실제 compiler Review/Confirm까지 검사했으며 별도 프로그램
실행이나 새 C# 의미·생성 계약을 구현한 단위가 아니다.

개발은 완료11단계 중10통과·1실패다. 첫 정상 UI는 제품 확인 일곱 개를 통과한 뒤 마지막
스크린샷 경로의 Path/문자열 연산 우선순위 오류로 exit1이었다. 실패 단계 전체를 통과로
세지 않는다. 해당 입력·로그·before SHA를 보존하고 경로 괄호만 수정한 뒤 정상 UI와 남은
취소 UI를 통과했다. 제품 코드는 바뀌지 않았다. 최종29단계는 수정된 검사와 동결 제품으로
모두 새로 실행했으며 개발 증거를 재사용/합산하지 않았다.

이미지는 테스트 canvas에서 생성한 PNG만 사용했고 외부/사용자 개인 파일을 업로드하지 않았다.
CompositionEvent/KeyboardEvent는 생성한 DOM 이벤트다. 일반 Escape는 브라우저 키보드로
검사했다. 실제 OS IME·물리 키보드·Windows/WebView2·모바일/터치·GPU/오디오·전체 UI·
Space/Library 전달은 미검증/미완료다. 초기 빈 화면과 과거 Agent 준비 지연 원인은 미확정이다.

저장 형식/마이그레이션은 없다. 이전 runtime도 확정된 기호/이미지 metadata를 읽지만 이번
IME guard는 없다. 핀 표시명/native 식별자·고급 ABI·기존 혼합 계약·신원/그룹 권한 backend·
정보 종류 C# 표현/사용중 항목 삭제 정책은 별도 잔여다. M11/M12/M4를 재개하거나 가능한
조합마다 새 필수 범위를 추가하지 않는다.

## 증거와 보관

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | fe3d35dd441a1dccc5ca7d9b3bb6e14eb25b0e3d | 1a883216f5399c36b45cf146f04fcb123f81ca466b9d0ac5320c04d94d35ba0a | 53,856,046 |
| rollback | ecb47f0acd220c617281374d6db42594e5e74d33 | 39a59e2b7698dd18c35870db6f279391a7542d396c2c55593e6b7c4b08e06a4b | 53,856,143 |

record `/workspace/artifacts/v536-verification-managed/runs/d85ad534ebe24602a88d10288b518b62.json`, evidence SHA `3312960b69ce028a05161a49900ea0714b9b77713dcc209acf25bf7cdef82021` (1,908,792B).
개발 evidence SHA `8cf322e14aae6b08f655162870c0cae12e673ea978413462cefc8b2ce88a8ec9` (934,916B).
두 보관본 전체 manifest/SHA를 대조했고 이번 완료 owned RAM root만 정리했다.
승인된 두 세대 정책의 관리 rollback047a71fa만 교체하고 다른 과거 자료/증거를 보존했다.
시작 index는 최종 archive에 포함하며 SHA `69f1df4a5644b81bdfef11edd7303cf94b817052b9f153de881e4d5018bdca9b`,
closing index SHA `94a5fabd83c2f439e2cb5f091db0fe7dcbc1cafa3c72c07cbe4fd45bf790a652`다.

첫 개발 preflight는 memoryCurrent 6,446,178,304B로 기존9GiB 추가 예산/1GiB 안전을
만족하지 못해 workspace 생성 전에 거절됐다. 거절 로그를 보존했다. 한도를 바꾸지 않고
이번 소유 Python bytecode cache를 준비한 뒤 통과했고 검사/제품 실패로 합산하지 않는다.
개발/최종 실제 시작 preflight는 각각 별도 이름으로 보존하며 덮어쓰지 않았다.
추가9GiB·RAM4GiB·안전1GiB·최종 증거512MiB 예산을 유지했다.
표본 cgroup peak 9,171,517,440B는 limit 17,179,869,184B에서 안전 1,073,741,824B를
남긴 범위다. 직전 완료 latest ZIP의 read-only FD/FADV_DONTNEED는 SHA·metadata 불변을
확인했고 전역 cache/allocator/cgroup 변경은 없다. 이번 소유 bytecode만 최종 마감 뒤 제거한다.
단위 첫 df 25,884,594,176B, 마감 25,877,639,168B (24.1004GiB),
순증가 6,955,008B (6.6328MiB).
게시 후 실제 df·원격SHA/clean·main/원본 보존은 scratch publication.json에 별도 기록한다.
