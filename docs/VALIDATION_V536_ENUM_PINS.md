# v536 wrapper enum 실행 핀 수용

이번 범위는 기존 소유 Blueprint의 `execution-enum` 호출 래퍼와 그 분기 소유 영역이다. 원본 v536 `blueprintParseCSharpRegions`·`resourceNodeMarkup`·`mountBlueprintMobileFlow`를 대조했다. 새 시각적 분기/반복, async, 복사본·다중 target·혼합 Save를 추가하지 않았다.

## 실제 수정

기존 parser는 `이름 일치 OR 숫자 일치`를 한 번의 find로 검사했다. `Ready=1, Done=2`를 `Done=1, Ready=2`로 바꾸면 앞에 있는 숫자 일치를 먼저 택해 Done에 ready ID, Ready에 done ID를 붙였다. 원본은 이름으로 먼저 찾고, 없을 때 숫자를 찾는다. 같은 순서를 재사용해 연결된 실행 핀의 ID를 보존했다. backend·CSS·카드/모달/버튼 배치는 바꾸지 않았다. 리소스 hash만 갱신했다.

수정 전 실제 모바일 C# 편집에서 잘못된 ID 대응을 재현했다(`/tmp/confectory-mobile-enum-pins-7ur9vg8y`, `before.log`). 실제 연결이 같은 ID를 유지해도 ID에 붙은 enum 의미가 바뀌는 결함이다. UI 성공 문구만 수정하거나 연결 삭제/이름 추측으로 통과시키지 않았다.

## 실제 엔진 검사

`tests/web/v536_mobile_enum_pins.py`의 자체 임시 ProjectPack/프로필을 사용했다. 최종 `actual3.log` exit0, 실제 엔진·Chromium390×844의8건. 근거 `/tmp/confectory-mobile-enum-pins-wfx5q221/evidence.json`, `mobile-enum-pin-flow.png`를 실제 열어 확인했다.

1. 연결된 enum 실행 핀 삭제 거절, C# 편집 취소와 원본/연결 보존.
2. enum 이름/숫자/순서 편집 후 ID 및 기존 case 연결을 유지한 Save.
3. 원본 모바일 특수 실행 줄의 검색 열기/취소.
4. 분기 소유 새 노드 생성 후 원본 구조 취소, 기존 successor/두 case 복원.
5. branchOwner·설명·본문·successor의 미적용 입력을 실제 프로세스 재시작 후 복원. 저장 전 live graph에 부분 적용 없음.
6. 기존 원자 batch로 정확한 case 영역에만 새 노드를 삽입. Ready 꼬리·Done·main continuation 보존.
7. 모바일 Review 취소 후 기존 문서 탭 재진입과 새 명시적 compiler Confirm. graph/새 source만 반영하며 callee·기존 source·객체·Main 보존.
8. 다른 편집자의 graph/checkpoint 변경 시 오래된 Save 거절. 새 peer 설명·기존 enum/연결·사용자 입력 보존.

중간 검사의 구조 취소는 모바일에서 기본 접힌 미니맵에 focus를 주려던 fixture였다. 실제 보이는 그래프 viewport에서 키보드 조작하도록 고쳤다. 취소 후 자동 카드 모드 복귀와 HTML open 속성의 빈 문자열도 원본 조작 경로에 맞춰 확인했다. 보호 조건을 지우거나 강제 클릭으로 통과시키지 않았다.

생성 Linux build1, JS/Python 구문·diff 검사 통과. Windows 교차 패키지는 `/workspace/artifacts/Confectory-v536-enum-pins/Windows-x64/Confectory.exe`다. 선언2305파일/66 UI 리소스. `desktop_package.py` exit0(`/tmp/confectory-desktop-package-fz158do0`): 구성·누락/변조 거절·SDK 없는 packaged 웹 기동·다른 cwd·프로필 재사용/명시 override·최소 로그인 화면 확인. .NET Desktop Runtime10.0 x64와 Edge WebView2 Runtime이 필요하며 자동 설치하지 않는다.

## 잔여와 다음 계약

- 일반 code enum은 별도다. 기존 `previewEnum`/`applyEnum`은 있지만 원본 C# 편집의 Result와 기존 본문/계약을 단일 저장으로 연결하는 어댑터는 미완료다. 현재 backend는 enum 적용 후 본문을 명시적으로 다시 적용하도록 한다. root 데이터 반환이나 readonly 핀을 임의로 실행 채널로 바꾸지 않는다.
- 원본 property는 실행 핀이 없는 값 연결이고, 현재 property/ref backend는 실행 노드 도달 시 읽기를 요구한다. 실행 핀을 몰래 추가하거나 평가 시점을 바꿀 수 없다. 이 차이와 최소 후속을 `V536_REMAINING_BACKEND_MAP.md`에 수정했다.
- 원본 set은 지역변수 중간저장이다. 객체 필드에 쓰는 property-set과 구별한다. 새 local+Set+연결의 원자 계획/target 재연결은 별도이며 순차 저장으로 대신하지 않는다.
- 복사본·다중 target ABI·속성/스키마+copy 혼합 Save 차단을 유지한다. 기존 EditBatch/checkpoint/SaveSlots 기반에 하나의 검토된 결합 intent와 전체 소유 source/CAS를 연결하는 것이 다음 최소 작업이다. 독립 API를 순서대로 호출하는 부분 성공은 허용하지 않는다.

이번 핀 범위의 완료이며 전체 UI 완료가 아니다. 사용자 자료·계정·토큰·유료 추론·프로젝트 Run을 사용하지 않았다. 실제 Windows apphost/WebView2·모바일 기기/가상 키보드는 미검증이다. Library 첨부로 전달하지 않았으며 로컬 산출물과 사용자 전달을 구별한다.
