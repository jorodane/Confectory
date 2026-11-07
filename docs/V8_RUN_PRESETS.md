# V8 프로젝트별 개인 해상도 등록

저장소 v666 ZIP `Confectory-v666/dist/app.js`의 `savedRunResolutions`,
`runResolutionOptions`, `setupRunDeveloperMenu`에 있는 이름 등록·목록 선택·등록 삭제를
기존 팝오버/CSS와 실제 소프트웨어 크기 요청에 연결한다. 원본의 이름40자·최소240px를
유지하고, 현재 opt-in provider의 실제 전송 한도512px 안에서 지원한다.
창에 맞춤/고정 대형 해상도·8192px·GPU/FPS와 진행 중 I/O는 별도 고정 잔여다.

## 소유와 저장

기존 Helper/UserProfile 표시 metadata와 같이 이 등록은 현재 사용자의 프로젝트별
개인 설정이다. 다른 사용자와 공유하는 실행 계약·프로젝트 원본·권한을 만들지 않는다.
`EditorHome.Model.RunPresets`는 실제 활성 ProjectContext/manifest/Identity와 session 수명을
검사하고, host profile의 `run-resolution-presets/{SHA256(projectId)}.json`만 사용한다.
브라우저가 project/path/storage를 제공할 수 없다. 일반 배치 autosave와 별도 파일이어서
새 입력·레이아웃 저장이 등록 목록을 덮어쓰지 않는다. 기존 권한 팩/3D 분리를 유지한다.

기존 FileStream Snapshot/Commit을 사용해 전체 파일 revision의 최종 CAS와 원자 저장을
검사한다. 한 프로젝트에 최대32개, 전체16KiB, 이름1–40 UTF-16 코드 단위와 240–512 정수
크기다. 안정적32자리 ID와 이름을 보존하고, 이름은 서버 OrdinalIgnoreCase로 비교한다.
같은 이름·크기는 기존 ID를 선택하며 새 파일을 쓰지 않는다. 같은 이름의 다른 크기는
원본과 같이 거절한다. 등록을 자동 이름 변경/덮어쓰기하는 기능은 추가하지 않는다.

마지막 명령의 고유 ID·입력 digest·기준 revision을 함께 원자 저장한다. 정확한 응답 유실
재시도만 receipt를 회수하며 같은 명령의 다른 입력은 거절한다. 재확인할 대상이 실제 저장된
ID/이름/크기와 달라졌거나 삭제 대상이 다시 나타나면 과거 성공을 재생하지 않는다.
다른 변경 뒤의 stale revision은 자동 병합/재전송하지 않고 명시적인 목록 재확인을 요구한다.
손상·다른 프로젝트 자료·symlink·읽기/쓰기 실패는 기존 파일을 보존하고 빈 목록으로
가장해 덮어쓰지 않는다. 이 receipt는 실행 권한이나 source Review/Confirm token이 아니다.

## 실제 사용자 흐름

원본의 직접 입력·이름·등록·삭제 컨트롤을 사용한다. 등록 저장을 확인한 뒤에만 현재 창에
기존 publisher/size sequence/command의 크기 요청을 보낸다. 실제 크기 완료는 기존
[Present 픽셀과 ACK](V8_RUN_RESOLUTION.md)로 확인한다. 일시정지 중 요청은 대기하며
자동 Resume/Step은 없다. 등록 성공과 실행 출력 반영은 별개의 사실로 안내한다.
기존 cooperative lease 만료에 따른 안전 pause 정책도 바꾸지 않는다.

명령 접수 후 응답이 유실돼도 같은 명령·기준 revision으로만 재확인한다. 저장 중 새로 쓴
이름/치수나 선택이 있으면 등록만 확인하고 옛 크기를 묵시적으로 적용하지 않는다. 목록
다시 확인은 출력 크기를 변경하지 않는다. 쓰기 오류/충돌 동안 입력을 남기며 저장 결과를
확인하기 전에는 새 등록·선택 적용을 진행하지 않는다. 원본 이름은 HTML로 해석하지 않는다.

같은 프로젝트의 다른 Run 창은 같은 등록 목록을 선택할 수 있으나 각 실행의 lease와
runtime은 독립적이다. 등록 삭제는 이미 적용되거나 요청 중인 출력 크기를 취소하지 않는다.
삭제된 항목을 선택한 창은 보존된 직접 입력 크기로 돌아가고 자동 실행/크기 요청을 하지 않는다.
닫기·프로젝트 변경 후 늦은 callback은 옛 창의 크기를 바꾸거나 다른 창에 적용하지 않는다.

확정된 등록은 cold에서 복원되지만 마지막 선택/runtime 명령/프로세스는 복원하지 않는다.
미적용 이름/치수는 기존 직접 입력과 같은 창의 휘발성 초안이며 저장 실패 중 현재 창에서
보존한다. cold에서 미저장 폼까지 복원한다고 주장하지 않는다. 기존 source/설명/값·권한·
부모/외부 원본·override 입출력 계약·Review→Confirm·source CAS/Undo는 변경하지 않는다.

이전 binary는 새 개인 등록 파일/API를 사용하지 않지만 프로젝트 C#이나 기존 profile 형식을
변환하지 않는다. 새 UI와 server는 짝맞춘 버전을 사용한다. 실제 Windows WebView2·모바일·
DPI/IME·전체 UI·Space/Library 전달은 교차 패키지와 구별한다.

[검증·보관·공간 기록](VALIDATION_V666_RUN_PRESETS.md)을 따른다.

후속: 현재240–512px 창 영역의 명시적 자동 맞춤은 [실제 창 크기/출력 ACK](V8_RUN_AUTO.md)에 연결했다. 당시 검증과 원래 provider 한도는 보존한다.

후속: 원본640×360 선택과 축640/총262144픽셀 capability는 [출력 범위 후속](V8_RUN_WIDE.md)에 연결했다. 기존 검증 기록/소유자·실제 ACK 보호와512 provider 지원은 보존한다.
