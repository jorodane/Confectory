# V7 보관된 텍스트 사본 미리보기 최종 검증

[지원 범위](V7_RESOURCE_TEXT_PREVIEW.md) · [닫힌 제품 delta](v666-resource-preview-delta.json).
제품·검사·도구 동결 `2fca9f30a894cf7c1ea64d7d9f35bef25ad5675c` 이후 변경은 문서뿐이다.
**총 32단계: 신규 21·동등 근거 재사용 11**. LF 12·CRLF 12·
새 패키지/전체 복원/수명관리 8다. 개발 실패와 중단은 통과 수에 넣지 않는다.

## 구현과 실제 확인

- 검증된 v666 ZIP의 `app.js::openResourceEditor`·`renderResourceEditor`와
  `resource-preview.js::mountResourcePreview` 텍스트 분기가 근거다.
  ZIP SHA `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`.
  원본 760×520 창·패널/도구줄·설정 구조·CSS·텍스트 확장자와 BOM 판별을 재사용했다.
  실제 최종 화면에서 파일명 설정란까지 확인했다. 파일명은 현재 읽기 전용이며 native 보관 위치에
  맞는 설명을 사용한다. 숨은 저장/편집 기능이나 외부 프로그램 열기를 새로 만들지 않았다.
- 제품 delta7개는 UI6개와 WebInvoke bridge다. Core/targets·WebUI 수명/권한 primitive·
  ProjectResources 저장/receipt/기존 API·ProjectManager·소유 원본 C#·public/override 계약은
  바꾸지 않았다. asset 파일 형식의 migration이나 기존 자료 정리는 없다.
- `readProjectResource`는 observation에만 명시 등록하고 project/id/hash 3개만 받아
  기존 활성 ProjectContext의 Resources read를 호출한다. 기존 일반 호출 목록은 그대로다.
  실제 native 관측에서 현재 사본의 원래 bytes/전체 SHA와 정체성을 확인했다. 잘못된 hash·
  알 수 없는 ID·다른 project·추가 path/action을 거부했고 import endpoint를 observation으로
  호출할 수도 없었다. 기존 32개 등록/동시 관측 bound와 scope·취소 검사는 변경하지 않았다.
- 생성한 검사용 HTML/코드·UTF-16BE BOM·binary 사본만 사용했다. 실제 Enter/두 번 클릭으로
  원본 bytes를 읽어 UTF-8/CRLF·UTF-16 텍스트를 표시했다. `<script>`와 외부 이미지 문자열은
  텍스트 노드이며 실행/외부 요청이 없었다. 원본의 비엄격 TextDecoder 대체 문자는 표시뿐이고
  보관 bytes를 다시 인코딩하거나 쓰지 않는다. 별도 사용자 개인 파일/외부 자료는 읽지 않았다.
- 실제 native 파일 읽기 권한 거절에서 내용/저장본/다른 개인 입력을 보존하고 같은 ID/hash로
  명시 재시도했다. fixture 권한만 복원한 뒤 읽기를 회복했으며 import나 새 기준 배정은 없었다.
  실제 성공 reply를 보류한 뒤 같은 key의 창을 닫고 다시 열었다. 오래된 실패 응답은 새 창의
  정상 내용을 덮지 못했고 현재 창은 하나였다. 원본 일반 창 열기/포커스를 재사용했다.
- 실제 Home 이동·A 복원은 진행 관측을 폐기했고 늦은 오류가 새 화면을 바꾸지 않았다.
  cold engine은 owner/ID/hash 레이아웃만 복원해 다시 읽었다. 원문/base64와 관측 요청을
  presentation에 저장하지 않았다. 같은 namespace/source ID인 B 프로젝트에는 A 창/bytes가
  나타나지 않았고 A 왕복에서 자기 사본을 복원했다. no-project 읽기도 거부했다.
  이미 수행 중인 모든 파일 I/O가 즉시 중단된다고 주장하지 않는다.
- 기존 사본 보관·최대1MiB native 전송·누락/변경 identity 거절·실제 쓰기 실패·lost reply와
  exact replay·stale CAS·새 검색어/선택 입력·취소/늦은 File 읽기·실제 재시작/다른 프로젝트를
  회귀 검사했다. 새 observation의 모든 크기/인코딩 조합을 따로 실측했다는 뜻은 아니다.
  기존 정확한 C# target 찾기/원문 열기·미적용 입력·Undo/Redo·ABA/stale 거절도 유지됐다.
  원래 물리 C#/ID/계약/연결과 자료 저장 bytes가 변하지 않았고 source Save/Review/Confirm/
  실행·AI 호출을 미리보기로 대신하지 않았다. 창 geometry 저장과 자료 쓰기는 구분한다.
- 독립 Git 객체·NuGet/home·빈 엔진 cache/출력의 LF/CRLF를 생성했다. 새 Windows 교차 패키지의
  관리형 엔진에서 정상 미리보기, 전체 압축 복원본에서 미리보기 수명/기존 자료 보관을 확인했다.
  ZIP 전체 SHA/CRC·전체 파일/디렉터리 mode manifest·복원 구조와 실패/예외 증거 보존·
  소유 프로세스 종료/임시물 정리를 확인했다. 실제 Windows apphost/WebView2·모바일·전체 UI,
  모든 crash/물리 전원 장애 검증은 아니다.

## 실패·중단·재사용

첫 실행 `bd6ff1603e44489a959cef3831addafd`는 읽기 이름을 observation과 일반 호출에
중복 등록해 시작이 거부됐다. 증거 SHA
`a14491960a7a4eae0442157da1ba9fcfd9e0cdd0dc8495f76d58c2ffe801de24`.
실제 상한은32이며 quota 문제가 아니었다. observation에만 등록하도록 고쳤고 Core 한도나
권한 primitive는 바꾸지 않았다. 이미 통과한 독립 소유 IPC 수명관리1개는 도구/검사·SDK/
NuGet/config/RID·정규화 명령과 봉인 archive를 검증해 재사용했다.

두 번째 `093c339b2dbe452794add25373b50464`는 실제 읽기 실패 상태를 만든 뒤 재시도 버튼이
Browser 뒤에 가려졌다. 증거 SHA
`836269ac3678bdc29e2e11221cd245a58925d25ff58637aa6ac83d8d8eefbb52`.
사용자 열기에도 복원용 refresh 옵션을 쓴 것이 원인이었다. 실제 사용자 재열기를 원래 일반
openWindow 경로로 바꿔 focus/reveal을 유지했고 강제 click이나 z-index 우회는 하지 않았다.

세 번째 실행은 LF 미리보기·자료 보관·본문 찾기가 통과한 뒤 원본 화면 대조에서 발견한
파일명 설정 CSS2개 누락을 보완하려고 보존 중단했다. 해당 기록·SHA는 아래의 이전 기록 목록을
따른다. 아직 끝나지 않은 CRLF 검사/패키지는 완료 근거로 사용하지 않았다.

네 번째 `d4c01cb32ffd44769af164a21f3572b3`는 CRLF 미리보기/cold/프로젝트 격리까지 통과했다.
기존 자료 fixture가 지연 File 읽기 신호를 초기화하지 않아 기다리기 시작하자 ReferenceError가
발생했다. 증거 SHA
`f7ac2da9e31c503dac032d9fc26d05c3b3f1c7b2a2b60e089ec0c7fcebed4474`.
제품은 그대로 두고 lifecycle 분기의 변수 초기화 한 줄만 추가했다. 완료된 LF 정적2·경계·
미리보기·자료 정상·본문 찾기6개와 CRLF 정적2·경계·미리보기4개를 재사용했다.
제품과 선택 검사/정상 모드 본문이 같고 SDK/NuGet/config/RID·정규화 명령 및 전체 archive
무결성이 같다. 재사용 총11개는 각 `.reused.json`과 보존 driver에 구분했다.
실패한 lifecycle과 남은 CRLF 본문·모든 최종 빌드·새 패키지/전체 복원은 신규다.
소유 root가 각 실패 종료 시 이미 정리돼 필요한 checkout/빌드는 새로 생성했다.

## 보존·공간과 유한한 잔여

- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/8f41e30459c24383a7be9852099241ca.json`
- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/8f41e30459c24383a7be9852099241ca.zip` · 2,135,594 bytes
- 증거 SHA: `f99f9c0010e0083db61fcaa69d5994b4ca65b5978486b84f2054c9b11e7658fb`
- 최신 source: `2fca9f30a894cf7c1ea64d7d9f35bef25ad5675c`
- 최신 ZIP: `6be52fa22fd271dae2a6b1db35c001eedf3b3fcc13bbb7bcce87a622806f7cb2.zip` · 51,893,944 bytes · 파일2491 / 디렉터리153
- 최신 전체 manifest SHA: `661cfe284919748aa83cb6b320367b5a471bdbf0db87a18defbd5445b245316e`
- 정상 롤백 source: `69b27171e12c26014a2c647a85ab9357ce7b0481`
- 롤백 ZIP: `7ff3ed2f310f13327ee7554c1654f61798d06a1850407cc591b60b42786f2bde.zip`
- 롤백 전체 manifest SHA: `884a49c33cdd026be01ed5d396b315607ae269ef494a8e372b2c2729926cfcd4`

패키지는 `/workspace/artifacts/v536-verification-managed/packages/`의 기존 index를 따른다.
최신/롤백과 재사용·실패·중단 증거의 전체 무결성을 확인했다. 검증 뒤 기존 승인된 두 세대만
원자 승격했으며 다른 과거 자료는 삭제하지 않았다. 이번 모든 소유 RAM root는 자식 종료와
증거 보존 뒤 정리됐고 로그/프로필·생성한 입력·스크린샷은 지속 공간에 보존했다.

최종 실행 디스크 순증가 2.92MiB, 실패/중단 증거와 검토 화면을 포함한
이번 측정 구간 순증가 9.23MiB다. 측정 시 여유 1229.02MiB,
단계 표본 최소 여유 1231.90MiB, peak memory 4894.51MiB다.
지속 공간144MiB(안전64MiB 포함)·RAM3GiB+512MiB·추가 메모리7GiB+1GiB의 기존 사전 기준을
유지하고 순차 실행했다. 이 증가량을 다음 단위의 보장값으로 사용하지 않는다.

이전 기록:

- `bd6ff1603e44489a959cef3831addafd.json` · SHA `a14491960a7a4eae0442157da1ba9fcfd9e0cdd0dc8495f76d58c2ffe801de24` · 완료 10/실패 1 · 중단/실패는 최종 통과 수에서 제외
- `093c339b2dbe452794add25373b50464.json` · SHA `836269ac3678bdc29e2e11221cd245a58925d25ff58637aa6ac83d8d8eefbb52` · 완료 9/실패 1 · 중단/실패는 최종 통과 수에서 제외
- `d4c01cb32ffd44769af164a21f3572b3.json` · SHA `f7ac2da9e31c503dac032d9fc26d05c3b3f1c7b2a2b60e089ec0c7fcebed4474` · 완료 22/실패 1 · 중단/실패는 최종 통과 수에서 제외
- `265252c3faaa4bab99fdbaa54ef4c732.json` · SHA `8ec2ab898bad22bffb0650796762902cf3153123b954e07defef8f0198810d7c` · 완료 17/실패 0 · 중단/실패는 최종 통과 수에서 제외


이전 정상본도 동일한 자료 저장 형식을 읽을 수 있다. 새 미리보기 창 레이아웃은 이전 UI가
알아보지 못하거나 다시 연결해야 할 수 있으며, 이를 자료/소스 migration으로 숨기지 않는다.
현재 공급자의 파일1MiB·전체4MiB/64개 한계는 그대로다. 실제 OS 파일 선택/드롭 조작·기기와
전체 UI를 모두 실행했다고 주장하지 않는다.

원본의 폴더·이름/이동·삭제/복구와 큰/다중 파일·배치·프로젝트 전체 이동/내보내기,
다른 형식의 미리보기 및 내용/metadata 편집은 고정 잔여다. V4/V5 실제 신원/권한 backend·
다른 V2 안내·종류 C# 호환성 결정·고급 Run/GPU/장치 오디오도 남는다. 초기화 간헐 빈 화면은
원인 미확정이며 이번 성공을 원인 해결로 표시하지 않는다. M11/M12/M4나 선택적 조합의
새 필수 행을 추가하지 않았다. main은 사용자 검토/merge용으로 보존하고 Library/Space 전달은 미완료다.
