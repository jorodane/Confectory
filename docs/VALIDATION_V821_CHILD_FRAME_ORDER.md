# v821 소유 자식 frame의 기존 일반 셀 순서 편집

2026-11-20. 시작 게시본은 `671942e5ec751e9cff2e276d82b565dc13de40e0`다. 앞선 복합 전체 호출 이동은 별도 검증 문서에 보존한다. 이번은 정확히 선택한 소유 자식 안의 기존 일반 셀 순서만 바꾸는 첫 범위다.

## 소유·표현 및 저장 경계

- 기존 inline `kind:graph` 경로를 물리 root와 모든 부모 node ID로 식별한다. read 응답의 `documentFrameOrderBinding`은 root ID·전체 graph ID·전체 path·root/선택 frame의 canonical graph SHA를 묶은 표시용 관측이다. 권한 자체가 아니며 서버는 원래 소유 graph에서 이를 다시 만들고 정확한 계획과 비교한다. 같은 local ID가 형제/조상에 있어도 선택 대상을 추정하지 않는다.
- 직접 소유 `sync-acyclic-nested-v1` root와 모든 자식이 기존 exit로 끝나는 완전한 독립 직렬 code/graph 사슬일 때만 제공한다. 선택된 자식은 기존 일반 next C# 셀만 포함한다. root부터 깊이 8·전체 256개, 한 frame 63개 이하 노드·64개 이하 편집 제한을 넓히지 않는다. 분기/공유 진입, copy·slot·opaque/receiver·forwarded storage·async와 다른 소유 경계는 이 경로에서 거절한다.
- 같은 자식의 전체 entry/next 순서만 하나의 후보로 바꾼다. 노드 집합, signature/arguments, 입력/반환·exit, 부모 호출·후속 흐름, 형제와 기존 C# 파일은 재작성하지 않는다. 명시적 생산자 의존성은 화면과 엔진이 검사하고, 저장 전 root 전체를 다시 읽어 부모 경계도 검증한다. 추가·삭제·분해·frame 사이 이동은 허용하지 않는다. 다른 frame에 입력이 남아 있으면 이동을 비활성화하고 입력을 보존한다.
- 기존 공유 초안·권한·source proof·Review/Confirm·최종 파일 CAS를 유지한다. UI의 원자 저장 선택과 재시도 journal은 요청 전용 `documentFrame` 관측을 보존하며 plan hash에 전체 binding과 edits를 묶는다. 기존 표시 없는 batch와 직접 serialRoutes에는 새 권한을 주지 않는다. 기존 체크포인트 commit lease의 `checkpointSourceChecks`에 관측한 전체 소유 소스 ID를 내부적으로 넣어 형제 파일도 원자 저장 시 CAS로 확인한다. 이 임시 필드는 export하지 않으며 새 프로젝트/체크포인트 형식이나 런타임은 없다.
- 저장 전 개인 Undo/Redo는 전체 private 경로별 입력을 사용한다. 소유 멤버십이 바뀌지 않는 공유 순서 편집은 기존 batch-edit history다. Undo로 root가 원래 바이트가 된 상태도 저장·cold·Redo할 수 있도록 기존 ownedRoute receipt가 실제 bounded graph 자식 경로를 가리킬 때 root 관측을 유지한다. 경로를 실제 root graph에서 확인하며 파일 접근 권한을 부여하지 않는다. 이전 생성의 OWNERSHIP_CHANGED 경계는 바꾸지 않는다.
- v821 수직 셀·입력 왼쪽/출력 오른쪽·기존 조건 탭·접힘/보기 상태와 기존 Blueprint 탐색을 유지한다. 설명 행이나 새 native 보기·slot UI를 추가하지 않는다.

## 실제 검증

고정 제품·검사 소스는 `e9ad9dcd2604d6b1e33a1dc1642c6a13d7624239`다. 최종 record `24ccd1a95afd49fdbb0093e085fffe59`는 `cleaned`, 오류 없음, 신규 **27단계 통과·실패 0·재사용 0**이다. .NET SDK 10.0.401과 수정 없는 독립 LF 체크아웃 하나에서 실행했다. 이 문서와 기준 문서의 후속 커밋은 검증한 제품·검사 소스를 바꾸지 않는다. 개발 진단은 최종 결과에 합산하지 않는다.

| 신규 단계 | 실제 범위 |
| --- | --- |
| 1–6 | LF 복제·고정 checkout, .NET 복원·Release·MCP·Linux 엔진 빌드 |
| 7–9 | 전체 소유 경로로 선택한 일반 자식 순서의 성공, 값 의존성 거절, 공유 진입 조상의 거절과 원래 실행 |
| 10–12 | 이전 복합 전체 이동의 성공·의존성·공유 진입 회귀 |
| 13–18 | 이전 분기 추가·이동·실행, 의존성·공유·암묵 경로 거절, 기존 API와 조건 탭·접힘 |
| 19–21 | 일반 직렬 셀 추가·이동·실행, 실제 조립 미리보기와 네이티브 직접 편집 회귀 |
| 22–24 | Windows x64 교차 패키지 생성·구성/probe와 managed 앱의 Linux 자식 순서 전체 성공 시나리오 |
| 25–27 | 전체 복원 후 자식 의존성 거절·입력 보존, 네이티브 저장·실행, 주입된 실패의 임시 복사본 수명 |

- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/24ccd1a95afd49fdbb0093e085fffe59.zip`
- 증거 SHA-256: `e6d946116014e2391490af5fa29ce7b8f651701f3d45c3647477d678a649df7b`
- 패키지 source: `e9ad9dcd2604d6b1e33a1dc1642c6a13d7624239`, 54,233,124bytes
- 패키지 SHA-256: `a21ce82ef02dce39b9fedf649599db8140063f45426302e821a3b1cf92387598`
- 전체 복원은 파일 2,760개와 디렉터리 158개, 합계 2,918개 항목의 바이트·종류·모드를 대조했다. `full-restore.json`의 `files`는 디렉터리를 포함하는 항목 수다.
- 인증된 2세대 저장소 latest는 위 소스이며 rollback은 이전 검증 소스 `dfd80058d7e2f6ddd217e2adb5588e73546188e7`다. rollback 54,229,296bytes와 SHA-256 `f428bb9267dae345bfcd1e812bf3170f6efe5d1044791ba1c5525938e438e5f6`도 실제 파일에서 재확인했다. 모든 검사·증거 보관 후 승격했고 이번 인증된 임시 공간만 정리했다. 기존 원본 체크아웃 `b5ea38c3d7eec3eb20f170e68f0f4215b86b2aee`와 알 수 없는 기존 임시 폴더는 보존했다.

Linux .NET 엔진과 Chromium의 실제 소스 앱 및 패키지에서 다음을 확인했다.

- 대표 fixture의 `root/body/nest`와 `root/other/nest` 양쪽에 `inner`/`tail` local ID를 뒀다. 선택한 자식만 `tail → inner`로 이동하고 명시 입력·반환값 10, 부모와 형제 후속 실행을 보존했다. 실제 출력은 `inside → body → parent-tail → peer-inner → peer-tail → after → 10`, 종료값은 10이다. Confirm 후 선택된 자식의 entry/edges만 원래 값으로 되돌리면 전체 graph 객체가 원본과 정확히 같다. 다른 기존 소스 파일의 바이트와 모든 원본 파일 모드도 유지됐다.
- 개인 Undo/Redo, 형제의 같은 local ID 탐색과 다른 frame 입력에 의한 이동 거절, 기존 Blueprint 전환, 전체 경로별 개인 입력 cold 복원이 통과했다. 새 셀 추가는 비활성이다.
- binding 없는 요청, 다른 물리 root·전체 path·root/frame 해시·노드·exit·소유자, 불완전한 node 집합, 생성·삭제·다른 frame 연결·source 혼합, 오래된 proof/checkpoint와 중복 구조 의도를 거절했다. 직접 serialRoutes도 거절하며 live graph·체크포인트·원본·개인 입력을 유지했다.
- 형제의 실제 원본 JSON을 외부에서 변경하면 원자 Save를 거절했다. 체크포인트 쓰기 권한 실패와 cold 재시도는 입력을 보존하고 선택한 자식만 저장했다. 공유 Undo로 root를 원래 바이트로 되돌린 뒤 명시 Save·cold·Redo·Save·cold도 통과했다. Review 취소와 최종 원본 CAS는 원본/동시 변경을 보존했다.
- 생산자보다 앞서는 자식 이동은 UI와 서버가 거절하고 미저장 이름을 cold 복원했다. 공유 진입 조상은 편집을 제공하지 않으며 Positive/Negative 조건 탭과 기존 흐름의 실제 실행값 10을 유지했다. 복원본에서도 의존성 거절·입력 보존을 다시 확인했다.
- 이전 복합 전체 이동, 일반 셀 실행값 10·분기 실행값 7, 조건 탭·접힘, 실제 생성 C# 미리보기와 직접 네이티브 편집을 다시 검사했다. 네이티브의 늦은 입력·source proof·원본 충돌·컴파일 실패·Review 취소·최종 CAS 보존과 복원본 실행값 15가 통과했다. 실패 수명 검사도 원본 패키지/런타임을 보존했다.

고정 소스와 패키지의 실제 `frame-normal.png` 캡처를 모두 열어 `Pair › body › nest` 경로, tail/inner 순서, 왼쪽 입력/오른쪽 출력과 위/아래 이동, 추가 비활성 상태를 확인했다. 원본 v821 목업과 직접 시각 대조한 결과는 아니다. 검증·정리 후 여유 공간은 작업 디스크 22GB, `/tmp` 7.5GB다.

개발 중 UI의 기존 private 저장 선택이 새 순서 계획을 원자 batch로 보내지 않는 누락을 발견했다. 이때 개별 entry RPC는 서버가 거절했고 원자 요청이 없어 검사가 실패했다. UI의 정확한 frame-order 선택을 연결했다. 후속 저장 실패는 root·path·해시가 cold 전후 같았으나 서버의 기존 root 생성 분류기가 새 자식 순서 case를 인정하지 않은 원인이었다. 격리 체크아웃에만 진단 출력을 넣은 짧은 실제 API 재현으로 `Observed owned ordinary root creation batch required`를 확인했다. 전체 관측 binding·순서·소유 검사를 먼저 통과한 case만 명시적으로 연결하고 진단 없는 UI에서 재검증했다. 기존 소유 제한이나 generic API를 완화해 우회하지 않았다. 개발 실패와 보완 결과는 최종 신규 통과 수에 합산하지 않는다. 과거 초기 빈 화면 원인과도 별개다.


개발 증거 record `c83534a705b74932a583f6c15fb5bb04`는 위 실패·격리 진단과 수정 후 별도 성공을 보존한다. ZIP SHA-256은 `633b1028cb035ea74c5ba615fdde8988761fccbf82121587256bd585c5755395`이며 인증된 개발 임시 공간만 정리했다. 임시 진단 출력은 제품에 포함하지 않았다. 최종 신규 27단계와 합산하지 않는다.

## 남은 범위

복합 생성/분해와 내부 추가·삭제, 같은 root의 다른 frame을 함께 편집하는 계획, 슬롯, private 네이티브 보기, branch/opaque/async/receiver 문맥은 별도 범위다. 이번 대표 실행은 scalar 입력/반환을 사용하며 모든 C#·ref/out·고급 ABI 조합이나 전체 엔진 기능 검증을 뜻하지 않는다. 실제 Windows/WebView2·물리 기기·전체 UI·원본 v821 목업 직접 시각 대조·신규 CRLF 실행은 미실행이다. 기존 reader Reference 제약은 해결했다고 표현하지 않으며 과거 초기 빈 화면 원인은 미확정이다. main과 Sites는 변경하지 않는다.
