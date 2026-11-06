# V666 선언 재조회 입력 보호 검증

제품·검사·도구 동결 `ed0575776752d51bef6b8a7f3bcda0e06e6ca59b` 이후 마감 commit은 문서만 바꾼다.
[지원/취소 의미](V2_DECLARATION_RELOAD.md)·[정확한 delta](v666-declaration-reload-delta.json)를 따른다.

## 실제 결함과 수정

이전 게시 엔진에서 고급 선언 폼의 이름을 입력한 뒤 현재 초안 다시 읽기를 누르면
readonly 조회 성공만으로 미적용 입력이 확인 없이 사라졌다. 이 native 어댑터 버튼은
기존 취소/독립 창 해제 경로로도 쓰여 입력 버리기 의미는 보존하고 명시 확인을 추가했다.
입력 없는 읽기는 그대로다. 취소는 읽기/삭제를 하지 않고, 승인한 정확한 record·값·편집
epoch가 유지되며 같은 project/창/owner/view의 읽기가 성공했을 때만 지운다. 같은 값으로
돌아온 새 입력(ABA)·조회 실패/응답 유실·대상/프로젝트 변경에서는 입력을 보존한다.
이 확인은 private 폼 입력 버리기이며 최종 소스 Review/Confirm이나 권한 부여가 아니다.

제품 변경은 declarations.js와 그 canonical resource metadata 두 파일이다. 기존 공통
modal/소유 cleanup을 재사용했다. Apply의 exact revision/hash CAS·공유 초안/원자 Save·
모든 .celem/공개 실행/override 계약·Core/targets/packs·원본 C#/ID/연결·부모/외부 원본·
권한·공유 Undo·기존 CSS/레이아웃·Run은 변경하지 않았다. 새 native endpoint·외부 접근·
자동 재기준화/자동 적용은 없다. private epoch는 저장하거나 공개 ID로 만들지 않는다.

## 최종 검증

독립 LF 15·CRLF 14·새 패키지/전체 복원/IPC·실패 수명관리 10, **총 39단계(신규 39·재사용 0)** 통과했다.
Git 객체·EOL·NuGet/home·엔진 cache를 독립시키고 최종 동결 코드에서 새로 실행했다.
개발/실패/과거 완료 기록은 최종 통과 합계에 넣지 않는다.

- 실제 Linux .NET/Chromium의 primary 선언과 독립 모듈 view에서 입력 없는 재조회,
  이름/미적용 모듈 계약의 명시 버리기·취소·반복·기존 독립 창 해제를 확인했다.
- 확인 전과 readonly 결과 응답 대기 중의 같은 텍스트 ABA 편집을 제어된 DOM 이벤트로
  주입했다. 확인 전에는 읽지 않고 응답 중에는 새 입력을 보존했다. 해당 입력과 원래
  CAS 기준은 cold에서도 복원되고 미완료 확인을 재생하지 않았다.
- readonly 결과 유실 fixture에서 입력을 보존하고 명시 재시도로 같은 현재 초안을
  읽었다. 테스트는 실제 네트워크 장애가 아닌 로컬 transport 주입으로 구분한다.
- 다른 공유 초안 변경 뒤 예전 private revision/hash의 Apply가 기존 native CAS에서
  거절됨을 확인했다. 입력은 유지되고 명시 버리기 뒤 실제 현재 초안을 표시했다.
  원문 bytes와 정밀 정수·원래 계약/ID를 보존했다.
- 확인 창을 연 상태에서 프로젝트를 나가도 오래된 확인이 읽기/삭제/창 재개를 하지
  않았다. 동일 namespace/ID의 B에는 A 입력이 없고 A로 돌아오면 정확히 복원됐다.
- 기존 헤더의 혼합 입력 보존·모듈 독립 창 normal 저장/Review/Confirm·늦은 취소 입력과
  Run 최대화/실제 소유 제어 회귀를 새 코드에서 확인했다. 새 재조회 UI가 Save/Review/
  Confirm/실행/AI를 요청하지 않는 것도 확인했다. 기존 헤더 회귀의 명시 저장/Confirm은
  별도 생성 fixture의 승인 동작이며 실제 사용자 소스를 사용하지 않았다.
- 새 Windows 교차 패키지의 구조/무결성과 패키지 엔진의 primary 버리기·독립 view 실패/
  재시도·헤더 보존을 확인했다. 전체 SHA/CRC/모드로 완전히 복원한 엔진에서 독립 ABA/
  cold와 프로젝트 왕복을 확인했다. 성공·실패·예외의 증거 보존·자식 종료·소유 임시물
  정리도 확인했다. 실제 Windows apphost/WebView2 실행을 뜻하지 않는다.

개발 fixture의 대화/레이아웃 admission과 관측 전 단언을 정리했다. cold 탐색은 이미
복원한 기존 노드/탭을 재사용하며 새 선언 생성으로 오인하지 않도록 수정했다. 충돌 후
비워진 진단 metadata는 현재 소스 자체가 아니므로 readonly inspect로 실제 공유 초안을
확인했다. 이러한 fixture 실패와 수정 근거를 보존하고 제품 실패/최종 통과로 섞지 않는다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/16209a49e4e1471ebb8e067dd847ae0b.json`
개발 증거 SHA `850ea6e7a29fa4c9736ff01765f816ff6d57b935ee2d21afc24f97d4d0a054a0`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/24e7b44a7bbb4a71b4663cd748dd97a6.json`
최종 증거 `/workspace/artifacts/v536-verification-managed/runs/24e7b44a7bbb4a71b4663cd748dd97a6.zip`
SHA `789bd29f13de346231544222be3e3943c11adc8cd2e0a356511ed1aca6f38728` (4.39MiB).

## 보관·공간·잔여

Index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: `ed0575776752d51bef6b8a7f3bcda0e06e6ca59b`, `9855adba833598d15ddfaec8674e6080fa6546b5ffa56c0cb833d9f301493b0e.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `3a20d65be2adcb009b96e606d8ce1376692e6a74acb7a591ab29d3218c2c11eb`.
- rollback: `ab66bc2761dc7582c370dcbc791e308cd879d3c1`, `c2a3383e1277f45b6cb6600f7fa643ea15dc86cde105e4f4dbc487d002baedf4.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `d7ee71d421bbdf7642988d7ae8649fdd20bade6249aa8c737aaeb0f4e24ac320`.

전체 archive SHA/manifest·복원 확인 뒤 최신/이전 정상 롤백과 증거를 지속 보관했다.
승인된 저장소의 원자 승격·2세대 수명만 적용하며 이전 index가 지정한 교체 대상만 정리했다.
이와 별개로 해당 실행이 만든 임시물만 소유/자식 종료 확인 뒤 정리했다. 다른 과거 자료·원본·로그·
프로필·SDK/캐시의 추가 삭제나 보관정책 변경은 없다.

표본 최소 디스크 여유 1437.44MiB, 최대 cgroup 메모리 4893.96MiB.
최종 실행 순증가 5.38MiB, 개발 시작부터 보관 확인까지 8.82MiB,
문서 마감 전 여유 1432.11MiB. 다음 단위의 증가량은 보장하지 않는다.

선언 폼 재조회는 이번 지원 경계에서 마감했다. V3–V7 팩/backend·V8 실제 내장 화면/오디오,
V9 실제 신원/가시성과 구체적 근거가 있는 추가 읽기, 종류 C# 표현/사용중 삭제 대응·V1/V2
후속은 기존 고정 잔여다. Run의 실제 process/프레임 제어 IPC와 RenderInput의 native
Draw/Pump는 내장 화면/오디오 전달 계약이 아니다. 현재 DISPLAY/Wayland/Xvfb·오디오
장치와 해당 provider가 없어 모의 장면/소리를 실제 성공으로 쓰지 않았다.
실제 Windows/WebView2·모바일·DPI/IME·전체 UI·Library/Space 전달은 미완료다. main을
보존하고 live AI·계정/키·유료 호출·새 외부 접근은 수행하지 않았다. M11/M12/M4는 구체적
회귀 없이 재개하지 않으며 3D/권한 별도 팩·이동 연출/실행 분리·명시 async caller를 유지했다.
