# v821 직접 소유 슬롯의 기존 구현 교체

2026-11-20. 시작 게시본은 `b447994c9b2a5474fb82cfce3055de572119d06d`다. 이번은 화면에 이미 존재하는 직접 소유 객체 슬롯 하나의 기존 구현을 교체하는 첫 범위다. 복합 내부 순서 편집 결과는 이전 문서에 보존한다.

## 소유·계약 및 저장 경계

- primary 객체 카드에서 직접 붙인 로컬 모듈의 명시된 require와 객체 자신의 유효한 provide 연결에 ‘구현 변경’을 제공한다. 상속/기본 구현이나 다른 소유자에게 배정된 구현을 재사용하지 않는다. 같은 ProjectPack에 이미 등록된 미배정 구현 중 동일한 함수·primitive value/ref/out·return 계약을 가진 직접 common C# 본문만 선택한다. 새 소스·등록·복사·자동 변환·import나 런타임 의미를 추가하지 않는다.
- 후보와 owner의 현재 revision/hash, 이전 구현, 전체 읽기 원본의 경로·SHA를 불투명한 서버 관측 토큰과 fingerprint에 묶는다. source budget은 기존 bounded workspace 안에서 240개·16MiB로 제한한다. path escape/링크·읽기 전용 owner/target header·등록/계약 불일치·공유/다른 owner·변경된 원본·오래된 관측과 혼합 요청을 거절한다. 표시 없는 기존 API에는 새 권한을 부여하지 않는다.
- isolated SlotBatch에서 기존 `provide-function` 선언 편집을 실행하고 최종 effective 계약을 검사한다. checkpoint 원자 Save 직전까지 원본 읽기 closure와 기존 commit lease를 검사한다. 기존 `checkpointSourceChecks`는 내부 CAS에만 쓰고 export하지 않는다. 프로젝트/graph/checkpoint 버전과 receipt v1의 8필드·intent의 8필드는 유지한다.
- Review는 기존 receipt가 정확히 하나의 provide 차이와 원래 registration/read scope를 증명할 때만 배정으로 인증한다. readGuard는 파일 변경 권한이 아니다. 필요한 기존 헤더와 common 본문을 읽어 cold 상태를 다시 검증하며, dormant `draft:null`을 미저장 편집으로 오인하지 않는다. 실제 다른 source draft는 Confirm/discard 없이 섞지 않는다. Confirm은 기존 컴파일·최종 파일 CAS를 사용한다.
- 선택은 private 입력으로 Undo/Redo·cold 복원한다. 저장한 연결 변경은 기존 shared history의 `OWNERSHIP_CHANGED` 경계를 유지한다. Undo/Redo 전송 성공과 의미상 `accepted:false` 거절을 구별하며 연결이나 원본을 삭제해 되돌리지 않는다. 다른 객체의 private 입력도 보존한다.
- 일반/분기/복합 문서형 셀·조건 탭·기존 Blueprint/네이티브 보기는 그대로다. 슬롯 내부 구조 편집이나 새로운 종료 의미를 열지 않는다. `common`의 기존 target 선택 의미를 사용하며 모든 OS 실행을 새로 보증하지 않는다.

## 최종 검증 결과

고정 제품·검사 소스는 `58178272bcf88eb0cf08f852c0c7dc999a027a26`다. 최종 record `2e15017b360b4f578c1cf94a2691f4dc`는 `cleaned`, 오류 없음, 신규 **24단계 통과·실패 0·재사용 0**이다. .NET SDK 10.0.401과 수정 없는 독립 LF 체크아웃 하나에서 실제 Linux 엔진·Chromium으로 실행했다. 이 문서와 기준 문서의 후속 커밋은 검증한 제품·검사 소스를 바꾸지 않는다. 개발 overlay/진단과 최종 독립 실행을 합산하지 않는다.

| 신규 단계 | 실제 통과 범위 |
| --- | --- |
| 1–6 | LF 복제·고정 checkout, .NET 복원·Release·MCP·Linux 엔진 빌드 |
| 7–9 | 슬롯 교체 성공·계약 불일치·다른 편집자의 저장 거절 및 입력 보존 |
| 10–11 | 기존 표시 없는 정보 슬롯 API와 실제 작성·가져오기·본문 편집 UI |
| 12–18 | 자식/복합/분기, 조건 탭·접힘, 일반 셀, 실제 생성 미리보기·네이티브 회귀 |
| 19–21 | Windows x64 교차 패키지·구성/probe, managed 앱의 Linux 슬롯 성공 흐름 |
| 22–24 | 전체 복원 후 계약 거절·입력 보존, 네이티브 저장·실행, 패키지 실패 수명 |

- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/2e15017b360b4f578c1cf94a2691f4dc.zip`
- 증거 SHA-256: `5e7e466f17854b870ddbcbcbf25dd48227bf8b6b8b6b56fba3c40a1b32b85439`
- 패키지 source: `58178272bcf88eb0cf08f852c0c7dc999a027a26`, 54,245,177bytes
- 패키지 SHA-256: `8d60e313400812653379416835a80548df2bebed97227e9e3e0b3e4d061d2bf1`
- 전체 복원은 파일 2,761개와 디렉터리 158개, 합계 2,919개 항목의 바이트·종류·모드를 대조했다. `full-restore.json`의 `files`는 디렉터리를 포함하는 항목 수다.
- 인증된 2세대 저장소 latest는 위 소스이며 rollback은 이전 검증 소스 `e9ad9dcd2604d6b1e33a1dc1642c6a13d7624239`다. rollback 54,233,124bytes와 SHA-256 `a21ce82ef02dce39b9fedf649599db8140063f45426302e821a3b1cf92387598`도 실제 파일에서 재확인했다. 전체 검증·증거 보관 후 승격했고 이번 인증된 임시 공간만 정리했다. 기존 원본 체크아웃 `b5ea38c3d7eec3eb20f170e68f0f4215b86b2aee`와 알 수 없는 기존 임시 폴더는 보존했다.

대표 Linux 시나리오는 `amount=5`에서 실제 종료값 45와 stdout `45:55:True`를 확인한다. Confirm은 `Monster.celem`의 provide 연결만 바꾸고 모든 기존 본문/다른 target/manifest와 원본 모드를 보존한다. 개인 Undo/Redo·cold, 계약 불일치 후보 제외, 타 소유자/읽기 전용/위조 fingerprint·토큰/표시 없는 새 요청/혼합 편집 거절, 물리 원본·checkpoint 권한 실패, 다른 편집자의 저장과 최종 Confirm CAS를 검사한다.

실제 성공 Save 응답을 유실시킨 검사에서는 Save 한 번 뒤 receipt로 성공을 확인하고 cold에서도 배정과 입력을 유지한다. 최종 소스 앱과 패키지 양쪽 기록의 `pendingBeforeCold`는 빈 배열로 hot reconcile이 먼저 완료됐다. cold에서 처음 성공이 확인됐다고 표현하지 않는다. 공유 Undo/Redo는 기존 경계에서 `accepted:false`, `changed:false`다.

기존 정보 슬롯 API/UI 검사는 직접 작성·복사·기능 가져오기·정확한 64비트 기본값·본문 재편집·저장/cold·Review 취소/Confirm을 대상으로 한다. v821 기본 화면에서 숨겨진 그래프 노드를 기다리던 기존 검사는 ‘블루프린트 보기’를 명시적으로 열도록 맞췄다. 모든 구 실행 파일/reader 또는 모든 API 조합을 검사한 결과는 아니다. 미확정 새 배정 checkpoint의 구 reader 역호환은 보증하지 않으며, 보호 증거를 제거하거나 자동 downgrade하지 않는다.

개발에서는 primary `uiSurface`의 빈 문자열 처리, 배정 receipt 읽기를 native body group으로 오인한 경계, cold lazy `draft:null` 처리 누락을 수정했다. 격리 clone의 진단 출력은 제품에 넣지 않았다. 응답을 잡아둔 초기 테스트의 교착과 Review가 갱신한 checkpoint의 잘못된 비교 기준 등 검사 결함도 별도 보존한다. 개발 실패는 최종 결과와 구별하며 과거 초기 빈 화면 원인으로 해석하지 않는다.

소스 앱과 패키지 양쪽의 Confirm CAS 검사에서 Review가 열린 직후와 거절 직후의 checkpoint 바이트가 정확히 같았다. 각각 SHA-256은 `346cab94ca61a4092e19c0680ccb23e5c4d5f8c05653beefbe651b3215e4c2b8`, `01757fa24e9ff2fb0292859a18c20eeef17f4600ad57728c5ff8b39b3367d12c`다. 복원본 네이티브 회귀는 컴파일 실패·늦은 입력·원본 CAS·Review 취소를 보존하고, 새 Confirm 뒤 실제 실행값 15를 확인했다. 소스 앱 캡처에서 기존 슬롯 카드의 ‘구현 변경’과 `AssignedBody` 표시를 직접 확인했다. 원본 v821 목업과의 직접 시각 대조 결과는 아니다.

개발 증거 record `7b19f0a36cb04289a1153a7fd8986764`는 실패·격리 진단과 수정 후 별도 성공을 보존한다. ZIP SHA-256은 `0f5c12d4834818537c86e359a1d257c7d8edcba1b8f06dee40eba20ebf8695eb`다. 제품 진단 출력은 없으며 인증된 개발 임시 공간만 정리했다. 최종 신규 24단계와 합산하지 않는다.

## 남은 범위

비어 있는/신규 슬롯 배정, 정보/schema 카드, 상속·등록 팩·이미 공유/기본/contained/copy인 후보, Blueprint provider, 고급 타입·배열·async·공개 실행 분기, 여러 슬롯/다른 source draft와의 공동 편집, 슬롯 내부 구조·새 종료 의미와 private 네이티브 보기는 별도 범위다. 이번은 최대 16개 primitive 인수의 대표 ref/out 계약을 대상으로 하며 전체 ABI 조합이나 전체 엔진 검증이 아니다.

실제 Windows/WebView2·물리 기기·전체 UI·원본 v821 목업 직접 시각 대조·신규 CRLF 실행은 미실행이다. Windows x64 교차 패키지와 managed 앱을 Linux에서 검사한 결과를 실제 Windows 실행과 구별한다. 기존 reader Reference 제약은 해결했다고 표현하지 않으며 과거 초기 빈 화면 원인은 미확정이다. main과 Sites는 변경하지 않는다.
