# v536 독립 Browser Data·참조 연결 — 2026-10-23

기준은 게시된 `c08d08f29f16c35e896097f5a62042f50c5ae242`와 원본 v536 ZIP이다. 이번 변경은 소유 개념 Browser의 Data 행·셀·참조 상세 편집과 상속 hover에 한정한다. Blueprint나 신규 이미지/협의/실행 backend를 확장하지 않았다. 원본 HTML/CSS의 행 구조를 사용하며 새 패널을 추가하지 않았다.

## 변경과 보호 경계

- 독립 Browser의 Data 단계가 개발용 비교 대상/필드 표를 열던 경로를 원본의 이름·속성 행·상세 버튼으로 연결했다. 이전 즉석 Table 기능과 저장된 비교 설정/입력은 삭제하지 않는다. 즉석 Table 자체의 설계나 권한은 이번에 변경하지 않았다.
- 기존 embedded Data 셀의 private 입력·정확한 숫자 JSON·읽기/쓰기/CAS·오류·복구 동작을 `browser-data.js`로 공유한다. 데이터 쓰기는 기존 소유 객체/필드/타입 검증을 통과해야 하며 Save와 최종 Review/Confirm은 구별한다.
- 원본 Hover는 상속 부모, Shift+Hover는 상속 자손이다. 실제 선언 projection만 읽고 프로젝트/외부 공유 권한으로 확대하지 않는다. 참조형/배열/복합 값의 상세 버튼은 해당 필드를 펼친 독립 소유 편집 창을 연다.
- Enter로 이미 적용한 셀을 blur에서 중복 적용해 저장 클릭이 사라지던 경로를 막았다. 취소는 성공한 서버 취소 후 현재 창의 동일한 입력 스냅샷만 정리하며 늦게 바뀐 입력을 무조건 삭제하지 않는다.
- 레이아웃 복원이 metadata 객체를 교체했을 때 셀과 검토 가드가 서로 다른 private 입력을 읽던 경로를 수정했다. 화면·저장·검토는 같은 현재 metadata를 사용한다. 미적용/잘못된 값은 검토를 차단한다.

## 재시작 버전과 실제 충돌

이전 소스의 내용 hash는 같지만 Save/취소 후 revision 카운터가 재시작 때 달라져, revision을 포함하는 view hash도 바뀌었다. 이 때문에 보관된 입력을 명시적으로 재적용해도 stale로 거절됐다.

Browser 읽기에 내용 지문 `contentHash`를 추가했다. 객체 ID, 원본/등록부/overlay hash, effective typed schema/값/설명을 포함하고 일시적인 revision 카운터만 제외한다. 보관한 원본 hash와 내용 지문이 모두 정확히 같을 때만 사용자의 명시적 재시도에서 새 proof로 대응시킨다. 지문 없는 이전 입력은 자동 승격하지 않는다.

서버 쓰기는 계속 **최신 revision + textHash + viewHash** 세 필드를 원자적으로 검사한다. `contentHash`를 쓰기 CAS 대신 받거나 알 수 없는 version 필드를 허용하지 않는다. 소스·스키마가 실제로 달라지면 새 내용 지문이 달라져 기존 입력이 거절된다. 프로젝트/창 소유권·readonly·타입·최종 확정 경계도 유지한다. 재시작은 어떤 입력도 자동 전송/적용하지 않는다.

## 실제 실행 검증

| 검사 | 결과 |
| --- | --- |
| Linux EditorHome 생성/연결 | 현재 코드 build7 성공. 기존 CLI/엔진을 fixture provider로 대체하지 않았다 |
| `v536_standalone_browser_data.py` | **전체 9건, exit 0**. 원본 행/상속·역참조, int 오류/취소/실제 Save, 저장값 복원, 실제 프로세스 재시작과 명시적 한글 입력 재적용, 참조 선택/저장/취소/재시작, 미적용 입력 검토 차단, 명시 compiler Confirm, 실제 타 소스 변경 및 상속 스키마 변경 차단 |
| `v536_elements_data_write.py` | **전체 7건, exit 0**. embedded 경로의 정확한 64비트/한글·CAS/readonly/부모 및 다른 창 입력 보존·재시작·상세 창 저장 회귀. 초기 테스트의 개발용 ‘정의 열기’ 버튼 사용을 실제 Enter 경로로 바꾸고 검색 완료를 기다렸다 |
| `v536_browser_data_layout.py` | **11개 영역**의 크기·글꼴·padding·radius 일치. 원본 ZIP을 별도 임시 폴더에 풀고 동일한 1480×1050/한국어 환경의 원본 renderer와 현재 공유 renderer를 비교했다. 실제 backend 성공 증거는 위 엔진 검사에 별도로 있다 |
| 이번 소스의 Windows 교차 패키지 | win-x64 생성 성공. 2,305개 선언 파일과 marker, **66개 UI 리소스**. 별도 cwd/SDK 없는 런타임의 managed 웹 기동·최소 로그인 렌더·변조/필수 DLL 누락 거절 통과. 실제 Windows 실행은 미검증 |

실제 엔진 성공 fixture는 `/tmp/confectory-standalone-data-np5ceyky`, embedded는 `/tmp/confectory-element-data-write-x3qagf14`다. 같은 원본/현재 renderer 캡처와 치수 JSON은 `/tmp/confectory-browser-data-layout-ts2qmg4z`에 있다. 이 임시 파일과 로그/패키지를 Git에 넣지 않는다.

이번 교차 패키지는 `/workspace/artifacts/Confectory-v536-browser-data/Windows-x64`에 별도 보존했으며 package 검증 증거는 `/tmp/confectory-desktop-package-j21ha7gj`에 있다. 아래의 전달 대상 기존 c08d08f ZIP과 혼동하지 않는다. 최종 일반 Git checkout/원격 SHA 확인은 게시 시 별도 기록한다.

초기 실패도 보존했다. 잘못된 JSON 원문 비교를 수정한 것만으로 cold 문제가 해결되었다고 보고하지 않았다. 실제 cold proof 결함과 metadata 교체 결함을 수정한 뒤 소스/스키마 충돌 회귀까지 통과했다. 원본 비교 fixture의 데모 property migration 및 문서 언어 차이도 정정했으며 제품 CSS를 바꾸어 검사 숫자에 맞추지 않았다.

## 완료 범위와 남은 제한

검증한 범위는 root 소유 객체의 scalar Data와 기존 상세 편집/상속 참조 경로다. 등록 팩/다른 namespace는 readonly 권한을 유지한다. 모든 schema/function/module source의 Data 셀 편집을 제공한 것은 아니다. 일부 일반 context/reference 정의 탐색, 모든 이름 표면·사용자 아이콘/자식 수 배지·OS drag preview의 전체 정밀 수용, 삭제 receipt import/check-path의 별도 수용은 남아 있다. 기존 Table 비교 입력은 보존되지만 그 UI의 전면 이행을 이번 완료 범위로 주장하지 않는다.

화면 11개 영역 일치는 전체 Browser 또는 전체 v536의 pixel equality가 아니다. 실제 Windows apphost/WebView2/DPI/IME/snap, Android/터치는 미검증이다. 계정 로그인·인증파일/토큰 읽기·실제 권한 부여·유료 추론·사용자 프로젝트 실행은 하지 않았다.

## Windows 중간 ZIP 전달

요청한 기존 검증 패키지는 **c08d08f** 기준(제품 구현은 **0f91794**, 후속 커밋은 테스트/문서)이다. 이번 Browser 변경을 포함하지 않는다. 2,301개 패키지 파일 전체와 실행 안내/체크섬/포함 커밋을 ZIP으로 보존했다.

- 파일: `Confectory-v536-Windows-x64-c08d08f.zip`, 60,452,077 bytes.
- SHA-256: `573cc69aeae5bca5121c308e3f2989f0f51075647bc48db4a729ae9bec5dbb5f`.
- Library 읽기는 가능했지만, 지원되는 대용량 저장 경로가 `hosted apps tools/list ... network` 오류로 전송 전 실패했다. 같은 경로를 한 번 재확인했으나 동일했다. **첨부 전달 미완료이며 library_file_id는 없다.** 다른 업로드 경로로 우회하지 않았다.

Windows에서는 ZIP을 풀어 폴더 전체를 유지한 채 `Windows-x64/Confectory.exe`를 실행한다. .NET Desktop Runtime 10.0 x64와 Edge WebView2 Runtime이 별도로 필요하고 프로젝트 컴파일에는 .NET 10 SDK가 필요하다. 이 검증은 실제 Windows 실행이나 런타임 자동 설치를 뜻하지 않는다.
