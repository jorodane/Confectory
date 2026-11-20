# v821 복합 호출 셀의 같은 frame 내 순서 편집

2026-11-20. 시작 게시본은 `f283bf90d4bade272ba28c0450dac5a438411b85`다. 기존 분기/네이티브/일반 셀 검증은 별도 문서에 보존한다. 이번은 복합과 슬롯 전체 완료가 아니라 기존 복합 호출을 한 단위로 이동하는 첫 흐름이다.

## 표현과 구현 경계

기존 `kind:graph`는 부모에 소유된 inline graph와 명시적 signature/arguments를 가진 private 함수 호출이다. 별도 전역 호출이나 슬롯 배정으로 바꾸지 않는다. 내부 C# leaf는 물리 root 아래의 전체 경로로 소유하며 같은 local ID를 가진 다른 자식과 공유하지 않는다. 자식 반환 후 원래 부모 next로 복귀하고 부모 값/receiver를 암묵적으로 캡처하지 않는 기존 compiler 규칙을 유지한다. 슬롯은 객체/정보의 모듈 요구 및 소유 구현 배정과 별도 owner/revision/hash 계약을 갖는다.

이번 문서형 이동은 직접 소유한 물리 root의 `sync-acyclic-nested-v1`에서만 제공한다. 부모와 모든 자식은 명시적 next와 기존 exit로 끝나는 완전한 독립 직렬 code/graph 사슬이어야 한다. 분기·공유 진입·호출·export·opaque/retained/receiver·forwarded storage·copy·slot·async 및 다른 private frame은 이 경로에서 거절한다. 기존 예산을 넓히지 않으며 깊이 8·전체 노드 256, 한 frame의 63개 이하 노드와 64개 이하 편집으로 제한한다.

복합 셀 전체와 주변 일반 셀을 같은 상위 순서에서 위/아래로 이동한다. 내부 graph·노드 집합·서명·값 연결·종료점·기존 leaf 파일은 재작성하지 않는다. 값 생산자의 순서 위반은 화면과 기존 엔진의 최종 후보 검사로 거절한다. 새 셀 추가, 내부 이동/분해, 슬롯 편집은 활성화하지 않는다. 기존 내부 탐색과 보기 전환은 유지한다. 조건 탭이나 설명 행은 바꾸지 않는다.

읽기 응답의 지원 여부는 관측한 원본에서 계산한 표시 정보이며 권한이 아니다. authorBatch는 요청의 명시적 `documentCompound` 의도를 확인용 plan hash와 개인 저장 시도에 묶고, 격리 후보의 전체 graph에서 정확한 순서 계획을 다시 검사한다. 기존 표시 없는 API에 복합 이동 권한을 추가하지 않는다. 직접 serialRoutes는 여전히 거절한다. 새 저장 형식·런타임·공개 계약은 없다. 원문·권한·source proof·Review/Confirm·최종 CAS와 백업을 유지한다.

순서 이동은 소유 파일이 늘거나 줄지 않으므로 기존 batch-edit history의 개인/공유 Undo/Redo를 사용한다. 저장 전 개인 입력, 공유 체크포인트 Save, 물리 원본 Confirm을 구분한다. 이 단위가 이전 새 셀 생성의 OWNERSHIP_CHANGED 경계를 없애지는 않는다.

## 검증

고정 제품·검사 소스는 `dfd80058d7e2f6ddd217e2adb5588e73546188e7`다. 최종 record `f40edd1904b24c839ef87a9e21c73686`는 `cleaned`, 오류 없음, 신규 **24단계 통과·실패 0·재사용 0**이다. 수정 없는 독립 LF 체크아웃 하나에서 실행했다. 이 문서와 기준 문서의 후속 커밋은 검증한 제품·검사 소스를 바꾸지 않는다. 개발 진단은 최종 결과에 합산하지 않는다.

| 신규 단계 | 실제 범위 |
| --- | --- |
| 1–6 | LF 복제·고정 checkout, .NET 복원·Release·MCP·Linux 엔진 빌드 |
| 7–9 | 복합 전체 호출 이동의 성공, 값 의존성 거절, 기존 switch 조건 탭의 공유 진입 거절 |
| 10–15 | 기존 분기 추가·이동/실행, 의존성·공유·암묵 경로 거절, 표시 없는 typed 생성 API, 조건 탭·접힘 |
| 16–18 | 일반 직렬 셀 추가·이동/실행, 실제 조립 미리보기, 네이티브 직접 편집 회귀 |
| 19–21 | Windows x64 교차 패키지 생성·구성/probe, Linux 패키지의 전체 복합 이동/실행 |
| 22–24 | 전체 복원 후 복합 의존성 거절, 네이티브 저장/실행, 주입된 실패의 임시 복사본 정리 |

- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/f40edd1904b24c839ef87a9e21c73686.zip`
- 증거 SHA-256: `1c0f162fccbe793285389507aead063afc839cc11b1a7babca3c26870526ec20`
- 패키지 source: `dfd80058d7e2f6ddd217e2adb5588e73546188e7`, 54,229,296bytes
- 패키지 SHA-256: `f428bb9267dae345bfcd1e812bf3170f6efe5d1044791ba1c5525938e438e5f6`
- 전체 복원은 파일 2,760개와 디렉터리 158개, 합계 2,918개 항목의 바이트·종류·모드를 대조했다. `full-restore.json`의 `files`는 디렉터리를 포함하는 항목 수다.
- 인증된 2세대 저장소 latest는 위 소스, rollback은 `c556cf783022120d297bfcdb36dfd27e1a30563e`다. rollback 54,219,250bytes와 SHA-256 `4d88d4d7b083fde46275d7ac2e467193e51aa65062b80993b07901cbf27d33b6`도 재확인했다. 전체 검사·증거 보관 뒤 승격하고 이번 인증된 임시 공간만 정리했다.

Linux .NET 엔진과 Chromium의 실제 소스 앱 및 패키지에서 다음을 확인했다.

- 복합 셀을 `other → body → after`로 이동한 뒤 자식 내부의 `inner → tail` 호출과 같은 local ID를 가진 다른 자식의 소유권, 입력/반환과 기존 출구를 보존했다. 실제 실행 출력은 `other → body → inside → after → 10`, 반환값 10이다. Confirm은 상위 graph의 entry/edges만 바꾸고 모든 node 객체·자식 graph·본문/선언 파일을 그대로 유지했다.
- 같은 부모에서 개인 Undo/Redo, 내부 탐색·상위 복귀, 기존 Blueprint 보기, 개인 입력 cold 복원을 확인했다. 내부 frame의 이동/추가는 비활성으로 유지했다. 저장 실패·재시도, 공유 Undo/Redo와 명시 Save 후 cold 복원도 통과했다.
- 명시 의도 없는 새 batch, 다른 frame·소유자·종료점, 불완전한 node 집합, source 편집 혼합, 오래된 proof/checkpoint, 중복 구조 의도와 직접 serialRoutes 요청을 거절하고 live graph·체크포인트·원본·개인 입력을 보존했다. Review 취소와 최종 물리 파일 CAS에서도 원본/동시 수정을 유지했다.
- 생산자보다 앞서는 복합 이동은 UI와 서버가 거절했고 미저장 이름 입력은 cold 복원 후에도 정확히 남았다. 공유 진입은 기존 Positive/Negative 조건 탭을 유지하고 편집은 비활성이다. 그 원래 공유 흐름의 실제 실행값 10도 확인해 실행 불가능한 fixture를 거절 통과로 세지 않았다.
- 일반 셀 실행값 10과 분기 실행값 7, 조건 탭/접힘, 네이티브 미리보기/직접 편집을 다시 검사했다. 네이티브 늦은 입력·source proof·원본 충돌·컴파일 실패·Review 취소/최종 CAS 보존과 복원본 실행값 15가 통과했다.

고정 소스 앱과 패키지의 실제 문서형 화면 캡처를 열어 복합 셀 순서, 왼쪽 입력/오른쪽 출력, 이동·내부 탐색과 추가 비활성 상태를 확인했다. 원본 v821 목업의 직접 시각 대조는 아니다. 검증 종료 후 여유 공간은 작업 디스크 22GB, `/tmp` 7.5GB였다.

첫 개발 검사의 중첩 leaf fixture는 전역 feature 기준으로 정의 해시를 계산해 실제 소유 구현의 정의와 달랐다. 제품은 needs-implementation으로 표시하고 이동을 비활성화했다. 기존 blueprintDescribeOwned로 정확한 구현/body target에 묶인 fixture를 만들도록 고쳤다. 제품의 소유/준비 검사는 완화하지 않았다. 실패 로그와 fixture를 보존한다. 공유 거절 검사의 초기 bool graph fixture는 기존 화면의 표시 범위 밖이라 문서 화면 진입에 실패했다. 이를 통과로 바꾸지 않고 기존 switch 조건 탭에서 같은 복합 셀로 진입하는 경로로 수정해 별도 검사했다. 기존 표시 범위를 넓히지 않았다.

개발 증거 record `220c2451bec14bdbbb07d3bd827d0297`는 위 두 fixture 실패와 수정 후 별도 성공을 포함한 개발 진단이다. ZIP SHA-256 `2a3f1ad08d00384b51c38a4c8e8dd782ce4934f8a225dea85e8d338b4560d1af`로 보관했고 인증된 임시 작업공간만 정리했다. 최종 24단계의 소스·실행과 합산하지 않는다.

## 남은 범위

복합 내부의 구조 추가·이동, 복합 생성/분해, 슬롯 배정 및 슬롯 내부 구조는 별도 frame·소유권·호출/계약 관측 계획이 필요하며 이번에 구현했다고 표현하지 않는다. 개별 private 네이티브 보기와 실제 Windows는 이번에 섞지 않는다. 실제 Windows/WebView2·물리 기기·전체 UI·원본 v821 목업과 직접 시각 대조·신규 CRLF 실행은 미실행이다. 기존 reader Reference 제약과 과거 초기 빈 화면의 원인은 이번 단위로 해소됐다고 단정하지 않는다. main과 Sites는 대상이 아니다.
