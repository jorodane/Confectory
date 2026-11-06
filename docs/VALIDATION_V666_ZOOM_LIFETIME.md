# V666 Workspace 확대 팝오버 수명 검증

제품·검사·도구 동결 `5304b65237cb020780781ea7c32ae25b9ddd5592` 이후 마감 commit은 문서만 바꾼다.
[지원 경계](V1_ZOOM_LIFETIME.md)·[정확한 delta](v666-zoom-lifetime-delta.json)를 따른다.

## 재현·변경

고정 v666 ZIP의 `dist/app.js:371–385`가 정의한 기존 확대 팝오버를 유지한다.
현재 게시 `d11b3f6`와 제품 소스가 같은 보관 패키지 `ba629cd`를 전체 SHA/manifest로
복원했다. 실제 Linux managed engine/Chromium에서 닫힌 팝오버의 slider/preset/
blur/Enter 함수를 보관하고 재개방 뒤 호출하니 현재 150%가 400%로 바뀌었다.
지연은 생성 fixture의 직접 callback 전달이며 실제 OS 이벤트 지연을 재현했다고
표시하지 않는다. 사용자 파일/외부 자료·실계정·AI 호출은 사용하지 않았다.

`workspace.js`의 확대 setup에서 현재 프로젝트 객체·설치 토큰·버튼 연결과 정확한
팝오버 인스턴스를 확인한다. blur/Enter는 그 입력의 commit만 사용하고 닫을 때 blur를
해제한다. 기존 markup·geometry·배율 규칙·새 디자인·원본/C#·IO/핀/연결·권한·
Review→Confirm·CAS·Undo·부모/외부 원본은 바꾸지 않았다. 다른 제품 변경은 해당
리소스의 canonical 크기/SHA 갱신뿐이며 delta 감사로 최종 LF/CRLF에서 확인했다.

## 최종 검증

독립 LF 12·CRLF 12·새 패키지/전체 복원/실패 수명관리
7, **총 31단계(신규 31·재사용 0)**
exit 0이다. Git 객체·NuGet/home·engine cache를 각각 독립시켰다. 초기 재현과 과거
검증은 최종 합계에 넣지 않는다.

- 실제 엔진에서 재개방/반복 취소·늦은 slider/preset/blur/Enter가 현재 배율과 새 미적용
  입력을 덮지 않았다. 정상 Enter/슬라이더·바깥 클릭·500% 제한과 cold의 400%/개인
  입력 복원도 통과했다. 원래 직접 입력/프리셋/휠 정책은 pinned 원본 함수와 대조했다.
- 같은 namespace/창 ID의 생성 프로젝트 A→홈→B→A에서 이전 버튼 열기/입력 callback이
  홈이나 다른 프로젝트에 팝오버를 만들거나 배율을 적용하지 않았다. A의 300%, B의
  125%와 각 개인 입력이 분리되고 B의 cold에서 버린 숫자 입력/팝오버는 복원되지 않았다.
- 기존 실제 Blueprint 회귀는 LF/CRLF 및 전체 복원본에서 각각 8개 확인을 통과했다.
  400/500%·수치 제한·Escape·휠/plane transform·미저장 설명·모바일 폭 두 접점·
  엔진 재시작·창 종료를 확인했다. 모바일 폭은 Linux Chromium의 입력 검사다.
- 생성 fixture의 물리 원본은 byte 단위로 미변경이다. 확대 조작은 source edit/Save/
  Review/Confirm·작업 실행을 호출하지 않는다. 새 source 거래가 없으므로 source 충돌을
  별도 생성하지 않았고 기존 최종 CAS/계약 검사를 통과한 것으로 새로 계상하지 않는다.
- 새 Windows 교차 패키지의 구조·무결성을 확인하고 packaged managed engine에서
  반복/취소/cold를 실행했다. 전체 SHA/CRC/모드로 복원한 엔진에서 프로젝트 수명과
  Blueprint 회귀를 재실행했다. 실제 Windows apphost/WebView2 실행은 아니다.
- 기존 소유 임시물 수명관리의 성공/실패/예외·증거 보존·자식 종료/정리가 통과했다.
  실행별 RAM 임시물만 승인된 수명으로 정리했고 다른 과거 자료를 삭제하지 않았다.

재현 record `/workspace/artifacts/v536-verification-managed/runs/88986b195e20410cb687a7d8028e29f7.json`, 증거 SHA `70285b19161b43a4c870b2dc58e69694847f43ad295ae435c7bb618bf6f83ac1`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/0fe29ac066264158939157f8702e5f7b.json`

증거 `/workspace/artifacts/v536-verification-managed/runs/0fe29ac066264158939157f8702e5f7b.zip`

SHA `2025ea4a46d6b2a090abd0ba1089d6a4ddba029fd20144195c9384ee489096a4` (1.64MiB).

## 보관·공간·잔여

Index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: `5304b65237cb020780781ea7c32ae25b9ddd5592`, `ca2446a0e5c3415305506f25ede63516883ddb052ff2b5162cc9d7e304a2eb7e.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `ab6c1868ef9786b93afb58f7e4f90dd73ad819c2cbba6133feabf4a1f9667fbb`.

- rollback: `ba629cd66c8e319c1ddf332679753f94be60c277`, `4d08bbf6ef0f06181022506e03100ba8567a70b5846ebcd68a721a28fec26eba.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `255ff7deb220ab605bcb45b91fc3b4fa78827ca642b86f017fa0d3ce74cbc9f8`.


최신/롤백과 재현/최종 증거의 전체 SHA/manifest를 재확인했다. 승인된 두 세대의
원자 승격과 소유 임시물 정리만 유지했다. 이번 실행의 RAM root는 제거됐다.
표본 최소 디스크 여유 1418.36MiB, 최대 cgroup 메모리 4869.95MiB.
최종 실행 순증가 2.47MiB, 단위 시작부터 확인까지
2.85MiB, 현재 여유 1415.96MiB다. 이후 사용량의
보장값이 아니며 기존 144MiB 추가 예산/64MiB 안전 여유를 낮추지 않았다.

이번 마감은 Workspace 팝오버의 반복/프로젝트 수명 경계다. 독립 정보 편집 창의
모든 확대 문맥과 DPI/IME는 별도 미검증으로 유지한다. M11/M12/M4는 구체적 회귀
없이 다시 열지 않는다. V2의 다른 노출 안내, V3–V7 실제 backend/packs, V8의 실제
Run renderer/audio provider, V9의 신원/가시성 adapter와 종류 C# 표현/사용 중 삭제
대응의 기존 정책 경계는 남는다. 실제 Windows·모바일·전체 UI·Library/Space 전달은
미실행이며 교차 패키지 검사와 구분한다. 새 권한/접근/과금/원문 변환 정책은 없다.
