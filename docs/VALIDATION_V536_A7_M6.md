# v536 모바일 ABI 이동·공유 출력 이름 수용

기준 `4102f2f` 이후 두 실제 화면 결함만 수정했다. CSS·레이아웃·권한·backend/CAS/Review 계약은 변경하지 않았다. 원본은 저장소 `196c605`의 v536이다. 실제 사용자 계정/프로젝트가 아닌 격리 fixture를 사용하며 로그인·모델 호출·실행은 하지 않는다.

## 재현과 수정

A7: 390×844 모바일 카드에서 `그래프 ↗ → 보기 → 미니맵 펼치기`를 누르면 원본 미니맵 영역은 나타났지만 SVG가 비었다. 실제 DOM에서 root 폭390, map 폭376, SVG 빈 문자열을 확인했다. 펼침 callback이 class만 바꾸고 다시 그리기를 예약하지 않았다. 미니맵/설명 펼침·접힘 후 기존 `schedule()`을 호출하여 지도와 연결선을 현재 크기로 갱신한다. fake node나 강제 클릭으로 검사하지 않는다. 기존 메뉴의 retired canvas 소유권 가드는 그대로다.

M6: 정의 탭에서 `reply → sharedValue`를 적용한 개인 초안에서는 두 배치의 원래 output ID가 `reply`로 남고 표시/정의는 remap된 이름을 쓴다. 한 배치 inspector의 공유 출력 검사가 원래 ID와 현재 이름을 비교하여 공유 여부를 놓쳤다. 같은 root remap을 사용해 비교한다. 정의 탭의 공통 rename은 유지하고 한 배치가 공유 정의를 조용히 바꾸는 경로를 차단하며 raw 입력은 보관한다. native rootParameters의 저장/CAS/수치/참조 검사는 바꾸지 않았다.

## 검증 범위

- `v536_general_copy_abi.py ... user-correction registered mobile-context`: 원본 모바일 Files→객체 슬롯→저장된 등록 callable copy→Graph/View/minimap→명시적 갱신. 취소, 미완성 값/핀 선택의 프로세스 재시작 보관, 잘못된 출력 대응 전체 미적용, 활성 창의 Undo 후 새 명시적 선택, 프로젝트 나가기/재진입 및 retired 창 callback 차단, 원자 authorBatch, Review 취소/명시 compiler Confirm. 외부 등록 팩/부모/원래 함수·본문은 보존한다. `mode`는 첫 추가 인자이며 `registered`/`mobile-context`는 별도 flags다.
- `v536_shared_output_name.py`: 직접 소유 함수의 한 out 정의를 공유하는 두 배치. 정의 rename·Undo/Redo·cold, inspector의 거절된 별도 rename 취소, 두 정확한 64비트 값/순서/경로 보존, 공유 그룹 Save·Review 취소·compiler Confirm. root 명시 변경만 허용하며 고정 native return 이름과 새 무명 출력 Save 제한은 유지한다.
- `v536_mobile_blueprint_touch.py`: 합성 touch의 기존 4건을 재검증한다. 이제 map 영역 가시성에 더해 실제 node glyph를 확인하므로 빈 지도가 통과하지 않는다. pan/pinch, touch cancel, finder 한글 조합/IME도 포함한다. 실제 기기 터치/native IME 검사가 아니다.

로그/실제 DOM·스크린샷 근거는 `/workspace/scratch/v536-a7-m6/`와 각 로그의 evidence 경로에 보관한다. 최초 mobile ABI session37900은 이전 묶음에서 이미 회수한 실패 결과였으며 중복 실행하지 않았다. 이후 blank-map 재현을 새 현재 코드에서 확인했다. M6 fixture의 누락 intent/signature, 일반 args의 mode 필드, 자동 생성 return export를 함께 세던 검사 오류를 수정했다. A7는 자동 카드 복귀 후 숨겨진 canvas를 직접 focus하지 않고 실제 Graph 버튼을 사용한다. Undo는 활성 편집 창에서 검증하며 퇴역한 창의 Undo 이력을 cold/Home까지 영구 보존한다고 주장하지 않는다. 프로젝트 재진입 후에는 보관한 대응·저장 시도 기록을 검증한다.

## 최종 판정 기준

[27개 조작 표](V536_RESIDUAL_UI_AUDIT.md)의 지원 경로만 마감한다. A4–A6 ABI, M4 async, M11 C#→중첩 변환, M12 root 실행 출력, I1–I6 정보/아이콘 정의 계약, B1 외부 runtime 소유권/B2 worker badge 및 M7/M8 보호는 별도 제한/미구현으로 남긴다. raw+saved-copy ABI/다중 target/Set 등의 차단도 유지한다. 정상 지원 경로 수용과 원본 전체 기능 구현을 혼동하지 않는다. 실제 Windows/WebView2·모바일 하드웨어·DPI와 Library 전달은 미검증이다.

최종 native 결과: A7 6건(`mobile-abi-acceptance.log`), M6 4건(`shared-name-final-2.log`), 실제 Linux 엔진의 합성 touch 회귀4건(`touch.log`) 모두 exit0. A7 evidence `/workspace/scratch/v536-info-definitions/tmp/confectory-saved-copy-abi-3gktdubx`, M6 evidence `/workspace/scratch/v536-info-definitions/tmp/confectory-wide-mixed-9de3wnzp`. driver는 실제 enabled idle·Graph 버튼·취소 후 원본 문서 탭을 사용하며 source/receipt/외부 팩 보존 assertion을 유지했다. 최종 지원 판정은 표의 11개 수용/16개 보호·미구현이다.

Linux 엔진 생성 exit0/blueprint warnings0, 73개 리소스 canonical 크기/hash, JS/Python 구문 및 diff 검사를 통과했다. 기존 Release solution 검증 이후 native C#는 변경하지 않았다. 새 Windows 교차 패키지는 `/workspace/artifacts/Confectory-v536-a7-m6/Windows-x64/Confectory.exe`와 동반 전체 폴더다. .NET Desktop Runtime10 x64/WebView2가 별도로 필요하다. package probe는 선언2321파일·73리소스·PE/의존성/변조 거절·다른 cwd/runtime-only managed 웹 기동·최소 로그인 renderer를 통과했다. 실제 Windows apphost/WebView2는 실행하지 않았다. 최종 checksum/checkout/게시 결과는 후속 기록한다.

실행 코드 커밋 `a1122d530bbbe27d155b33e40f170d6629481c3c`을 깨끗한 별도 checkout에 ff-only 적용했다. Linux 엔진 생성 exit0/warnings0, 실제 CRLF attribute pull·fresh-LF 73리소스·content/encoding/BOM/binary/budget 거절과 검사 전후 원본 바이트 불변을 통과했다. root/checkout의 추적 실행 소스·테스트3208파일은 줄끝 정규화 후 같으며 패키지의 추적 runtime 소스2101파일은 실행 코드와 바이트가 같다. 이번 후속 커밋은 검증 기록/표의 표현만 보완한다.

패키지는 marker 포함2322파일/131897026bytes, marker SHA-256 `e92e22d40e3fcd04a7abac042e1667d3dd39b80cea74a4f5ea9676c2b488d6d3`, 정렬 checksum 목록 SHA-256 `871e2d573f53ab0efb823fc0bd78624ffd7a61c884166579aed2ffc18b5449a3`. 사전 검토8파일(구현2/테스트3/문서3)에서 비밀 패턴 검출0이며 로그·사용자 자료·인증·산출물은 Git에 포함하지 않았다. 패턴 검사가 모든 비밀 부재의 증명은 아니며 실제 인증 파일은 읽지 않았다. checksum/파일 목록은 scratch review에 보관한다. 로컬 패키지 존재와 사용자 전달 성공은 별개다. 원격 SHA/깨끗한 상태는 최종 체크포인트로 확인한다.
