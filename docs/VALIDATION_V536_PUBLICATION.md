# v536 중간 소스 게시 검증 — 2026-10-23

대상은 `https://github.com/jorodane/Confectory.git`의 `work/current`이다. 저장소와 브랜치를 명시한 사용자 승인 후 누적 구현·테스트·문서와 사용자가 제공한 v536 레퍼런스를 검토했다. 전체 UI 복원 완료나 실제 Windows 실행 통과를 뜻하지 않는다. 이전 로컬 전용 검사 기록은 `VALIDATION_V536_LOCAL_INTERMEDIATE.md`에 그대로 남겼다.

## 게시 자료 검토

- 구현 138개, 테스트 187개, 문서 28개, 원본 레퍼런스 1개를 `0f91794c7bc88ddad0ced8504a4b183d2eaa74af`로 보존했다. 이 기록과 확정 완료 대기 테스트 정정이 후속 변경이다.
- 빌드·로그·사용자 프로필·프로젝트·인증정보는 게시 대상에 포함하지 않았다. 비밀 패턴 검사 0건은 가능한 모든 비밀의 부재를 증명하지 않으며, 제외한 사용자 프로필 내용을 읽지 않았다.
- 원본 v536 ZIP은 사용자 지정 main `196c605fd60bb6afe73d5765d994a8989639c31d`의 파일과 SHA-256이 일치한다: `b53156e73fdbbe1f6b8b36a0829cdbfdaec002352304da0060fa53026314bd22`.
- 97개 테스트 파일은 이전 단계의 격리 fixture 또는 보관 상태를 전제로 한다. 테스트 파일 전체를 독립 실행 가능한 전체 회귀로 보고하지 않는다.

## 새 Git 체크아웃 검사

원래 작업 폴더의 빌드/설정을 복사하지 않고 `--no-hardlinks` clone으로 소스 커밋을 가져왔다. `core.autocrlf=true`를 동일하게 적용하고 .NET SDK 10.0.401을 사용했다. 출력/fixture는 무시되는 빌드 경로 및 별도 임시 저장소에만 생성했다.

- 전체 솔루션 Release: 경고 0, 오류 0.
- 실제 EditorHome Linux 생성/링크: 성공.
- schema/상속 소유권/독립 선언/typed import/컴파일 중 소스 변경 영향 회귀: 8 passed, 0 failed, 0 skipped.
- `v536_run_windows_followup.py`: 전체 8건 통과. 조회 중 입력, 종료 취소/거절, 시작 응답 유실 시 중복 실행 방지, 컴파일 실패/재시도/중지, 실제 내보내기 결과, 미선언 target 거절을 검사했다.
- `web_resource_checkout.py`: 실제 legacy checkout → fast-forward pull의 유지 CRLF 및 새 LF checkout에서 65개 리소스 검증. 내용/인코딩/BOM/binary/크기 변조는 거절하고 원본 바이트를 유지했다.
- `desktop_package.py`: 패키지 변조/필수 DLL 누락 거절, 다른 cwd와 SDK 없는 .NET 런타임에서 packaged managed engine 웹 기동, 65개 리소스와 최소 Codex 화면 렌더 통과. 기존 checkout profile 재사용 및 명시적 저장소 override도 격리 fixture로 확인했다.

Blueprint 최초 실행은 저장·cold 재시작·명시적 compiler Confirm까지 12개 항목을 통과한 뒤 마지막 충돌 검사 준비에서 중단됐다. 테스트가 review 창 소멸을 확정 작업 완료로 간주하여 다음 요청을 너무 일찍 보냈다. 실제 `confirmGroup` 성공 응답과 UI 활성화를 기다리도록 정정했다. 서버 CAS/계약/타입 검사를 완화하거나 초안을 지우지 않았다. 최종 재실행 결과는 아래에 구분한다.

정정한 `v508_feature_serial_engine.py` 전체 재실행은 **13건/exit 0**이다. 원본 핀 선택·숫자 정의 적응 취소·정확한 64비트/한글/배열 값·잘못된 값 입력 유지·노드 생성/Undo·cold 개인 초안 복원/저장·명시적 그룹 Review/compiler Confirm·실제 타 편집 이후 stale Save 차단을 검증했다. 페이지 오류 및 외부 요청은 0건이며 실제 프로젝트 실행이나 모델 호출은 하지 않았다. 제품 구현/리소스는 바꾸지 않았으므로 앞서 만든 패키지의 소스 구현과 리소스 해시는 동일하다.

## Windows 산출물과 한계

교차 패키지 경로는 `/workspace/artifacts/Confectory-v536-reviewed-0f91794/Windows-x64`이며 2,300개 선언 파일과 검증 marker를 포함한다. 파일 목록과 SHA-256은 상위 폴더의 `package-files.json`, `PACKAGE_SHA256SUMS`에 있다. 이 산출물은 Git에 포함하지 않는다.

Windows에서는 폴더 전체를 유지하고 `Confectory.exe`를 실행한다. .NET Desktop Runtime 10.0 x64와 Microsoft Edge WebView2 Runtime이 별도로 필요하다. 프로젝트 컴파일에는 .NET 10 SDK가 필요하다. 사용자 PC에 자동 설치하지 않았다.

실제 Windows apphost/WebView2/더블클릭/타이틀바/DPI/IME/snap 및 Android 기기는 미검증이다. 실제 사용자 로그인·토큰 읽기·유료 모델 호출·권한 부여를 하지 않았다. Browser standalone Data/일부 참조·시각 대조, Blueprint 다중 구현·변환/특수 핀/추가 ABI 문맥/혼합 Save/검색·키보드 수용은 남아 있다. Helper 이미지 제공자·협의/승자/공유 Confirm·내장 renderer/FPS는 별도 backend 부재다. 정확한 전체 목록은 `V536_UI_CONNECTION_STATUS.md`, `V536_UI_RESTORATION_SCOPE.md`를 따른다.
