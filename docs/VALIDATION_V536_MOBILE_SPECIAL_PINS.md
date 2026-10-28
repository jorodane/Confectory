# v536 모바일 특수 핀 첫 수용 묶음

선행 소유 슬롯 ABI는 `50f505876a837710030a49a82470120f57c9e1eb`로 게시했다. 이 후속 묶음은 기존 연결이 실제로 동작하는 범위를 확인한 테스트·기록이며 runtime/UI 코드를 새로 바꾸지 않았다. 전체 특수 핀이나 모바일 UI 완료를 뜻하지 않는다.

## 원본 및 지원 경계

기준 ZIP의 `dist/blueprint.js`에서 `mountBlueprintMobileFlow`, `blueprintCSharpContract`와 C# 매개변수 영역을 대조했다. 원본 카드의 C# 코드 편집 버튼에서 같은 편집기로 들어가며, 새 pass-mode 선택창이나 핀/영역을 만들지 않는다. 원본은 실행 채널/async 등 더 넓은 UI 모델도 포함하지만 이를 새 실행 언어로 구현하지 않는다.

| 문맥 | 이번 확인 / 남은 범위 |
| --- | --- |
| 소유·단일 본문으로 변환된 whole-body root | 기존 C# 영역에서 값↔ref 편집, out 유지 및 공개 함수 이름과 다른 native 이름의 위치 대응을 확인했다. 입력/출력 탭의 보호는 유지한다. |
| out 및 반환 | 모바일 탭에서 각각 보이며 C# 변경과 함께 기존4개 소스 그룹으로 저장/확정한다. ref를 별도의 새 출력으로 발명하지 않는다. Core의 `FeatureOutputs`는 out와 반환을 별도 출력으로 다룬다. |
| 소유 슬롯 ABI | 선행 문서의 단일 root/본문/호출 값↔ref만 지원한다. 그 묶음의 실제 화면 검증은 desktop/common이며 모든 모바일 호출 조합의 증거로 합치지 않는다. |
| 복사본·등록 callable·여러 target 본문 | ABI 증거/범위를 함께 갱신하는 경로가 미지원이다. `V536_CALL_ABI_SCOPE.md`의 차단을 유지한다. |
| wrapper enum/특수 실행 핀·속성/ref 노드 | 기존 backend의 개별 C#/graph 계약과 모바일 카드 연결을 따로 검증해야 한다. backend가 전부 없다고 단정하지 않으며 이6건으로 완료 표시하지 않는다. |
| 영역/다중 선택·내부 흐름/async·공유/고정 출력 이름·잠정 빈 출력 | 기존 고정 잔여다. 현재 비활성/안전한 차단을 성공처럼 바꾸거나 새로운 시각적 분기/반복 체계를 추가하지 않았다. |

## 실제 검사

`tests/web/v536_mobile_special_pins.py`는 자체 임시 ProjectPack/프로필에서 변환한 root를 사용한다. `actual3.log` exit0, 6건, 근거 `/tmp/confectory-mobile-special-pins-sllpir3v/evidence.json` 및 `mobile-special-pin-editor.png`.

1. 390×844의 원본 입력/출력 탭, 보호된 whole-body 입력과 out/반환 분리.
2. 원본 C# 버튼으로 진입, 비호환 타입의 오류·입력 유지·취소.
3. 명시적 value/ref와 out/native 이름 유지, desktop↔mobile 폭 전환 시 미적용 입력 유지.
4. 실제 프로세스 재시작 후 미적용 매개변수·본문 복원, 원본 보존.
5. 함수·구현·graph·body의 기존4개 소스 원자 Save. Confirm 전 원본 파일 불변.
6. 모바일 Review 취소 후 기존 문서 탭으로 재진입, 새 Review와 명시적 compiler Confirm. 선택한4개만 변경되며 원본 C#·Main은 그대로다.

준비 검사에서 converter가 만든 `.confectory` 디렉터리를 파일로 읽으려던 fixture를 수정했다. 첫 실행의5건 이후 Review 취소가 document tab을 비활성화한 상태에서 숨겨진 버튼을 다시 누른 기대도 수정했다. 기존 탭을 실제 사용자 클릭으로 선택하며 강제 클릭/레이아웃 변경/자동 확정을 사용하지 않았다.

runtime이 선행 ABI와 같으므로 그 Linux 생성 빌드·Windows 교차 패키지·66리소스 checkout 결과를 재사용했다. 새 Windows 실행 검증은 하지 않았다. 실제 모바일 기기/터치 키보드·Windows apphost/WebView2·사용자 계정·유료 추론·프로젝트 Run은 미검증/미실행이다. 로컬 실행 파일은 `/workspace/artifacts/Confectory-v536-slot-call-abi/Windows-x64/Confectory.exe`이며 엔진 코드는 `50f5058`에 해당한다. Library 첨부로 전달했다고 주장하지 않는다.
