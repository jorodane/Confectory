# v821 직접 소유 자식 경로의 네이티브 미리보기

2026-11-20. 시작 게시본은 `d23fcc3e9462f733d7236e0d12c91649048d1e70`이며 구현 고정 소스는 `42d28235fa2508ae3f1c48c2b7eba4a0f14bdfad`다. v821 첨부 기준, 기존 네이티브 보기와 직접 소유 자식 편집의 기록을 유지한다. main과 Sites는 대상이 아니다.

## 구현과 권한 경계

기존 root 조립 한 번에서 실제 `FeatureBlueprint.Process`가 생성하는 정확한 자식의 `body`·`members`·해시를, 부모가 자식 요약에서 본문을 제거하기 직전에 선택한다. 다른 emitter, 문자열 절단/부분 재생성, 근사 C#을 쓰지 않는다. 정상 root 조립의 결과와 생성 소스 자체는 그대로다. 선택 필드는 요청/응답에만 있고 프로젝트·graph·노드·체크포인트에 저장하지 않는다.

같은 소유 함수의 physical root, 전체 `/graph:` 경로, root/frame 해시, 전체 source id/revision/hash 및 checkpoint 관측을 서버에서 대조한다. 실제 조립 후에도 원본 source와 checkpoint를 다시 검사한다. 기존 `frame-order` 가드가 증명하는 직접 소유 nested-profile 독립 직렬 tree와 일반 code leaf만 지원하며, 모든 조상·형제의 소유/구조 경계를 유지한다. 기존 깊이·노드·소스 한계를 완화하지 않는다. 기본 편집 화면만 대상이며 copied/inherited/slot/독립 properties-view 문맥은 열지 않는다.

자식 미리보기 API는 선택 경로의 body/members/해시·상태와 확인용 관측만 돌려준다. root 전체 C#, 형제 private 본문, 노드 원문/편집 후보를 응답에 넣지 않는다. 논리 코드·블루프린트 전환과 기존 편집 권한은 유지한다. 미리보기 영역은 읽기 전용 `pre`이며 직접 C# 입력이나 Save 경로를 추가하지 않는다. 소스·입력·경로·checkpoint가 바뀌면 결과를 무효화하고, 실패 시 본문과 멤버의 DOM 텍스트를 모두 비운다. 읽기만 가능한 원본/체크포인트에서도 표시할 수 있지만 읽기 권한이 없으면 거절한다.

공유 진입·분기·opaque·receiver/forwarded·async·슬롯·자식 아래에 다시 graph가 있는 선택 문맥 등은 이 첫 범위에 포함하지 않는다. 상위 root 미리보기로 대체하거나 소유권을 완화하지 않는다. 캐시·보기 presentation을 포함한 모든 파일 쓰기 금지라는 뜻이 아니라, preview가 원본/공유 초안 checkpoint/history를 편집하지 않는다는 뜻이다.

## 검증

고정 소스의 독립 LF checkout에서 신규 **23단계·실패 0·재사용 0**을 완료했다. 개발 시도와 다음 별도 core 가드 확인은 이 23단계에 합산하지 않는다. 실제 Linux 앱/엔진 검사이며 전체 UI 검증은 아니다.

| 단계 | 실제 통과 범위 |
| --- | --- |
| 1–6 | 독립 복제·고정 checkout, .NET 복원·Release·MCP·Linux 엔진 빌드 |
| 7–8 | 자식 C# 정확성·경로/권한/관측 거절·무변경·늦은 응답·cold, 공유 진입 미지원·원래 실행 |
| 9–10 | 기존 함수 전체 미리보기와 순수 네이티브 직접 편집·Save/history·컴파일 실패·CAS·실행 |
| 11–14 | 최근 자식 추가·자식 순서·복합 전체 이동·분기 내부 추가/이동의 Save/cold·Undo/Redo·Confirm/CAS·실제 실행 |
| 15–17 | 조건 탭·접힘의 무변경, 일반 셀 추가/이동·실행, 슬롯 교체·권한/동시 수정/응답 유실 복구·실행 |
| 18–20 | Windows x64 교차 패키지·구성 검사, 패키지 managed 앱의 Linux 자식 미리보기 전체 정상 흐름 |
| 21–23 | 전체 복원 뒤 공유 진입 미지원·원래 실행, 네이티브 편집·실행 및 패키지 실패 수명 |

- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/97ff0628f7a446118494e2b91381d7a7.zip`
- 증거 SHA-256: `caae8227357f678e7c2a89230808672b88f0658f932328db8f00019a8d037f99`
- 패키지 source: `42d28235fa2508ae3f1c48c2b7eba4a0f14bdfad`, 54,253,202bytes
- 패키지 SHA-256: `67ec94edf78087f2d073e2299410a9eee78a2336308face59947ad19758e8e7a`
- 전체 복원은 파일 2,761개와 디렉터리 158개, 합계 2,919개 항목의 바이트·종류·모드를 검증했다. `full-restore.json`의 `files`는 디렉터리를 포함한다.
- latest는 위 소스이고 rollback은 이전 검증 소스 `e6b0973d341e736b5e58a0e772408502cb1bff34`다. rollback 54,250,610bytes, SHA-256 `e6eb133881a1580627a72b3f9746ca7fa632e5bb504fe89cc99f14dbb61aa6a8`도 실제 파일에서 재확인했다. 증거 보관 뒤 승격했고 이 실행이 만든 소유 인증 임시 공간만 정리했다.

23단계와 별도로 같은 고정 소스의 실제 `blueprintDescribeOwned`에 유효한 소유 root·`body/nest` 경로·`assemblePreview:true`를 직접 전달했다. HTTP 관측 해시/UI 바인딩 검사를 거치지 않아도 공유 조상 문맥은 `Direct synchronous compound chain required`로 거절됐고 원래 root 파일 해시는 모두 같았다. 이 확인의 요청·응답과 metadata/Core binary 해시는 `/workspace/artifacts/v536-verification-managed/runs/97ff0628f7a446118494e2b91381d7a7-shared-core-guard.json`에 보존했으며 SHA-256은 `b2e281237deab30637f57a9e0760537862066e75029b1180c927763f0928a0b4`다. 공유 fixture API의 바인딩 거절만을 core 경계 증거로 사용하지 않는다.


대표 fixture는 `body/nest`와 `other/nest` 양쪽에 같은 `inner`/`tail` local ID를 둔다. 각 결과의 body/members가 실제 상위 root 조립 결과에 그대로 포함되며 body+members의 SHA-256이 emitter 해시와 같음을 확인한다. 자식 API payload에는 반대 형제/부모의 private 본문이 없다. 이 좁은 nested-profile leaf fixture의 members는 빈 문자열이며 다른 문맥의 비어 있지 않은 private helper 멤버 지원을 증명한 것은 아니다.

잘못된 owner/root/path/frame/hash, sibling id에 다른 binding, 추가 surface, 누락·오래된 source proof/checkpoint, code 노드를 graph로 지정한 요청을 거절한다. 실제 UI에서 형제를 바꿔 정확한 결과를 표시하고, 선택·형제 원본 변경 또는 읽기 권한 실패 시 두 코드 컨테이너를 비운다. 읽기 전용 graph/checkpoint는 변경 없이 읽는다. 실제 생성 응답을 붙잡은 동안 가능한 개인 입력을 변경한 뒤 응답을 돌려줘도 오래된 C#을 표시하거나 입력을 잃지 않는다. 글로벌 작업 잠금이 걸린 동안 경로 이동을 강제로 실행한 검사는 아니다. 이후 미저장 입력을 cold 복원하며, 원래 root 실행은 `body → inside → parent-tail → peer-inner → peer-tail → after → 10`, 종료값 10을 유지한다.

미리보기 자체는 공유 history를 만들지 않는다. 기존 구조 편집·추가의 개인/공유 Undo/Redo와 Save/Review/Confirm/CAS는 회귀 검사로 별도 확인한다. 구조 Undo가 임의의 이름 텍스트를 제거한다고 새로 보장하지 않는다.

## 개발 검사와 남은 범위

개발 record `c5d19cbeb64042ab8f152005d989a53c`에는 초기 세 검사 시도의 로그와 마지막 정상/공유 진입 검사를 보존했다. v1은 실제 API update 응답을 붙잡아 글로벌 busy 잠금이 유지된 상태에서 경로 이동 완료를 기다려 시간 초과됐다. v2는 응답 반환 전에 `pending()`의 presentation flush를 기다리는 검사 교착으로, 기록한 worker identity만 종료하고 모든 자식 프로세스 종료 인증을 받았다. v3은 늦은 응답의 입력 보존을 통과한 뒤 구조 Undo가 이름 입력을 지울 것이라는 잘못된 assertion에서 멈췄다. 제품을 잠금 우회나 입력 삭제로 바꾸지 않고, v4에서 실제 가능한 형제 이동·대기 중 입력·응답 반환·cold 복원으로 정상/미지원 범위를 통과했다. 제품에 진단 추적을 추가하지 않았다. 개발 증거 ZIP SHA-256은 `c307ab05e0a6122878052d4331be6688710ebc9225a9c139b07baec510cba876`이며 고정 소스의 최종 신규 실행과 합산하지 않는다.

실제 Linux 화면에서 전체 breadcrumb와 읽기 전용 생성 C#을 확인했다. 원본 v821 목업과의 직접 시각 대조, 실제 Windows/WebView2·물리 기기·전체 UI·신규 CRLF 실행은 미실행이다. Windows x64 교차 패키지 생성과 managed 앱의 Linux 실행은 실제 Windows 실행과 구별한다. 구 Reference reader 제약과 과거 초기 빈 화면의 원인은 이번 결과로 해소됐다고 단정하지 않는다.

다음 범위는 상위 복합/다른 private·opaque/async 문맥에서 emitter 결과의 포함 범위·권한을 별도로 증명하는 것이다. 현재 가드를 우회해 일괄 지원하지 않는다. 기존 원본 체크아웃과 알 수 없는 이전 임시 폴더는 보존한다.
