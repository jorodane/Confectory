# v536 선택한 copy 내부 호출의 명시 계약 대응

원래 조작과 유한한 잔여는 [7행 재대조](V536_ROW7_REMAINING_BOUNDARY.md)를 따른다.
이번 단위는 단독 직접 배정·단일 target same-contract copy에서 **선택한 내부 호출
하나**의 기존 원본 계약 갱신이다. 공개 override 계약·새 ID·원본 본문은 바꾸지 않는다.

`BlueprintCallAbi`의 private ref→값 전용 선행 제한만 제거한다. root와 같은
명시 input/output 대응을 선택 frame에 적용하고, typed import와 전체 graph를
기존 workspace 후보/CAS·receipt·Review/Confirm으로 검증한다. UI/HTML/CSS와
canonical 리소스는 변경하지 않는다. 자동 cast·입력 기본값·C# 재작성은 없다.

대표 fixture는 원래 `ref long amount -> long` 호출의 현재 callee를
`int step, double renamed, out long total -> bool`로 준비한다. 사용자가 step의
정수3, renamed의 원래 amount 연결, 기존 long return 소비자의 total 대응을
선택한다. 이것은 같은 조작의 검증 표본이며 모드 조합별 필수 요구 추가가 아니다.
미대응/비호환 출력·누락 입력은 전체 거절한다. 공개 root 계약·frame 경계·정확한
int64 local·wrapper 수동 C#·donor/다른 target/외부 원본을 보존한다.

저장 copy의 기본/독립 정보 창과 기존 미확정 copy 순수 후보에서 명시 대응을
검증한다. 여러 frame의 같은 callee/import와 opaque 문맥은 전체 거절을 유지한다.
쓰기 실패·물리 source/CAS 충돌·응답 유실·취소/Undo·재시작·명시 compiler Confirm은
집중 fixture로 확인하며, 결과는 후속 evidence에 통과한 것만 기록한다.

실패했던 ref→값 전용 DLL의 재현 로그와 첫 cold 검사에서 presentation flush 전에
브라우저를 종료한 검사 오류는 scratch에 보존한다. 독립 창의 후속 모달 종료도
호출 추적으로 cold restore가 완료되기 전 조작한 검사 순서로 확인했다. 기존
flush/복원 완료를 기다린 뒤 오류 표시와 수정 입력이 유지된다. 제품의 저장·검증
조건과 레이아웃은 완화하지 않는다.

새 교차 패키지는 RAM 검사 산출물이며 실제 Windows apphost/WebView2 실행이나
Library 전달이 아니다. 전체7행/I5/UI 완료가 아니며 여러 호출 source closure·
8/9행·I6/B2/A4–A6/M4/M11/M12와 실제 기기 수용은 별도다.

## 확정 집중 검사

최종 제품의 집중 12흐름 77확인과 미확정 copy 순수 후보6확인을 통과했다.
기본/독립 창의 source/owner/nonce/미대응/비호환 거절, 쓰기 실패·실제 source/CP 충돌·응답 유실·다른 frame 입력·Undo 취소·cold·Review 취소/compiler Confirm 및 기존 root/private/미확정 UI 회귀다.
74개 canonical 리소스와 HTML/CSS가 기준 게시와 byte 동일하다. 독립 checkout/새 교차 패키지는 별도 후속 evidence로 구분한다.

## 독립 checkout·새 교차 패키지

소스 커밋 `89c9b6669dbdc2e9c64d3a15789513fbc907666a`의 변경9개 Git blob과 기존 autocrlf/clean을 확인했다. Native/CLI Release·Linux 엔진 및 독립 UI2흐름21확인·순수6확인이 통과했다. 새 RAM Windows x64 교차 패키지의 restore·Release·MCP·생성·probe·패키지 자체 독립 창 UI12확인까지 6단계가 통과했다. 전체 2347개/manifest 2346개 목록·SHA·Core/Native DLL 및 소스 바이트를 확인했다.

manifest SHA `72ae633de27a329ce769df95f1b22c9329b4a7262aab8bdd720ab85660bd88d1`, Native DLL `6b8fbdfc9004d652e3acf805f105160301d390e60133f9975c3fc1ced9bd0666`다. 전체 manifest·fixture/로그/프로필 증거를 보관한 후 이번 임시 패키지만 정리했다. 보관 패키지/SDK/원본/기존 자료는 그대로다. 다운로드 가능한 새 보관 패키지나 Library 전달이 아니며 실제 Windows apphost/WebView2·모바일 기기는 미검증이다. 후속 최종 커밋은 문서/evidence만 바뀌므로 실행 소스는 이 소스 커밋과 같다.

초기 순수 검사에서 새 nested fixture의 remap을 잘못 제거한 실패도 `pure-remap.log`에 보존했다. 이를 수정한 순수6 및 실제 새-copy UI가 통과했다. 첫 시도나 진단 실패를 통과 수에 합산하지 않는다.
