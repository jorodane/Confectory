# 기존 실행 분기 호출자와 본문 공동 저장 검증

최종 runtime `8820e99c46cb5d28f2d1248c278c0bf29f1c72fd`의 **신규41단계·재사용0**을 통과했다.
LF16·CRLF17·프로세스 수명1·새 패키지/전체 복원/실패 수명7이며 개발16단계와 구별한다.
[원본 수용 근거·지원 경계](V666_RETAINED_BRANCHES.md)를 따른다.

| 범위 | 실제 결과 |
|---|---|
| 게시본 재현 | bool 분기와 Result 선택기 모두 원래 프로그램41·각 본문 후보는 유효. 공동 후보/원래 UI Save만 거절. checkpoint·원본·두 입력 보존 |
| 후보/실행 | 순서를 바꿔도 같은 후보이며 명시한 두 native 본문만 변경. 선택기의 ID·이름·값17/−3·primary·분기 포트·종료점·연결·지역값9223372036854775806와 C# 원문은 보존. 원래 alternate 경로로 실제22 실행 |
| 기존 보호 | copy/private/forward/wrapper·알 수 없는 control을 거절. 기존 전체 graph/source 검증이 잘못된 선택기 서명/분기 ID와 stale C# definition hash도 거절. 추정 변환·호출자 source 쓰기 없음 |
| CAS/원문 | Save 전 호출자 변경 거절. Review 후 header·selector C#·graph 변경 각각 최종 Confirm 거절. 두 본문과 checkpoint/peer 보존. 정확 복구·cold 후 새 명시 Review/Confirm 및 실행22. 읽기 의존 source의 bytes/inode/mode/mtime 보존 |
| cold/증거 | 분기 상태가 제거된 유효 peer graph도 saved readGuards를 빈 legacy scope로 재해석하지 않고 거절. 정확 복구 후 Review 허용. hash/path/owner/version·guard 누락/변조7개 거절 |
| 실제 UI 수명 | 기존460px 상세창/본문 editor의 취소·Undo/Redo·미저장/저장 cold·Review 취소/Confirm. 저장 실패 재시도·응답/조회 유실 복구·프로젝트 왕복·취소와 독립 창 확인 |
| 늦은 입력/활성화 | 지연된 본문 Save 뒤 새 설명을 cold/후속 명시 Save/Review/Confirm까지 유지. owner peer 변경은 rebase 없이 거절. pointerdown/peer refresh/release에서 기존 Save 노드·현재 handler 유지 및 stale 입력 거절 |
| 기존 호환 | 일반 next caller 후보와 원래 leaf/빈 guard의 cold/Review/Confirm·실행20을 최종 코드에서 새로 검사. native/public/override 계약·권한·UI 배치와 이미 완료된 M11/M12/M4는 변경하지 않음 |
| 패키지/복원 | 독립 LF/CRLF no-hardlinks·HOME/NuGet·Release/MCP·빈 engine cache. 새 Windows 교차 패키지 구조/무결성·포함 Linux 엔진 UI, ZIP CRC/SHA·파일/디렉터리 mode 전체 복원, 복원 API/CAS·bool 분기 응답 유실 및 실패 수명관리 통과 |

제품 변경은 `InformationFunctionBodyBatch.cs` 한 파일의 기존 ordinary caller
허용 검사다. code next/branch/switch는 원래 전체 그래프/typed signature·정의 hash·
source-ready·assemble 검사 뒤 읽기 의존성으로 남는다. call/export는 기존 next만
허용한다. source snapshot/240개 예산·version3 receipt·cold header/graph 관측·원자
checkpoint/CAS·Review→Confirm 최종 source lease와 원래 거절 경계를 유지한다.
새 metadata/ABI/permission·자동 C# 재작성이나 분기 선택 편집을 추가하지 않는다.

개발16단계는 모두 통과했고 최종 검사에 재사용하지 않았다. 개발 시작 전 메모리
사전검사3회 차단은 작업공간·build 시작 전이었다. 실패 로그·기존 preflight와 최종
preflight를 이름별로 구분했다. 봉인된 관리 package/evidence ZIP에서 SHA·크기·
inode/mode/mtime을 검증한 read-only FD별 cache 조언만 사용했다. 내용·전체 cache·
예산이나 기존 데이터를 삭제/변경하지 않았다. 최종 preflight 원본 SHA는
`0da8c0df6f27276a53071f6d449cc3f59de4769d501f381dba73b84453ea6226`이며 수집 과정에서 덮어쓰지 않았다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 8820e99c46cb5d28f2d1248c278c0bf29f1c72fd | 86d3d9d373e0c498ce371c15c25da7c797c49cc16e37279ce17699f1b4ac98df | 53,866,852 |
| rollback | 7938a4f01e6331cd980e4397fbba66fc3ffc0ea8 | 94d6d4670a8d25a38c1c09b73bc5a44a47ab9de526d1bcbdece5a4af4b25c5a9 | 53,867,355 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/0fff6088a1ae497281780b405da0673d.json`, evidence `f708a33518f483e04cd581c39f854b5d273aa8904875e918c6ac9321609d7f89` (8,227,284B).
개발 evidence `eb1f4e32825bea134e28e5d8ee867cda3693c718a4ce63ca3afd6e9427223b98` (2,278,700B).
양쪽 manifest와 보관 ZIP2개를 재검증했다. 시작 index `c937f87a241f8dc1f4768a4f11dc1854084e51e3b1d0f3be7a6b78811264d7bd`,
종료 sidecar `068abf67d5b9a10936fbbb0bab22fa7328b900b0d5bec2175889ab1e5372595b`. 승인된 두 세대 보관 절차에서 이전 rollback
`dcf4cf7b82a3d6f84515a4b921dfb17dcce62c94`의 관리 ZIP만 교체했으며 과거 evidence·사용자 원본·이전
checkout을 보존했다. 이번 개발/최종 RAM 작업공간만 identity·봉인 검증 뒤 정리했다.
재생성 build 출력의 hash 목록을 남기고 fixture 원문·checkpoint·실패/실행 로그·화면을
archive에 유지했다. 그 밖의 과거 자료나 임시 경로는 삭제하지 않았다.

시작 여유 25,769,578,496B, 마감 25,754,234,880B(23.9855GiB), 순증가 15,343,616B.
최대 cgroup 전체 memory 9,505,779,712B, 최종 stage 최소 디스크 25,765,298,176B.
추가 cgroup 메모리9GiB+안전1GiB·RAM 임시파일4GiB+파일시스템 여유512MiB·
디스크 안전64MiB·개발 evidence256MiB/최종512MiB의 기존 사전검사 예산을 유지했다.

고정7/8행의 다른 실제 ABI/source closure와9행 일반 입력/out 표시명·고급 타입
실행 통합은 기존 잔여다. 고급 정보·참조 핀의 공통 값/참조 타입 대 정보별 C# 타입
생성은 사용자 답변 대기이며 임의 확정하지 않았다. 기존 신원/그룹 backend·종류
CLR/사용 중 삭제 정책·실기기 잔여와 구분하며 경우의 수별 새 필수 요구를 추가하지 않는다.

실행 검증은 Linux native 엔진·Chromium·격리 fixture다. Windows 교차 패키지는
실제 Windows/WebView2 실행이 아니다. 실제 모바일·물리 IME/GPU/audio·사용자 프로젝트·
전체 UI·Space/Library 전달 및 모든 구 reader 교환은 미검증이다. 초기 빈 화면 원인과
과거 Save 클릭 요청 미발행의 모든 간헐 원인은 이번 통과로 해결됐다고 판단하지 않는다.
