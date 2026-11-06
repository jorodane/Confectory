# V8 Run 프로젝트 PCM 오디오

v666 ZIP의 `Confectory-v666/dist/app.js`에는 기존 개발 메뉴의 `data-run-sound` 스위치와
`data-run-sound-test` 버튼이 노출돼 있다. 그 배치와 소프트웨어 영상/해상도·실행 제어를 유지하고,
명시적으로 오디오를 제공하는 실행에 실제 PCM 관측과 로컬 미리듣기를 연결한다.

## 실제 지원 경계

독립 `Confectory.RunAudio` 팩은 기존 FrameControl owner에 오디오 reader 하나를 명시적으로
붙인다. `Open(frameOwner)`, `Append(owner, pcm)`, `Close(owner)`를 호출하는 새
`examples/audio-output` 예제만 generated440Hz PCM을 제공한다. 기존 사용자 C#과 기존
software-output/resizable-output의 바이트는 바꾸지 않는다. 오디오를 제공하지 않는 실행은
계속 미지원으로 표시한다. 기존 provider와 새 팩을 섞은 상태에서 자동 채택하지 않는다.

포맷은 모노16bit little-endian PCM,16kHz다. Append는 canonical base64의 완전한1–1600개
샘플 프레임만 받는다. 실패는 sequence/sample counter를 진행시키지 않는다. 보관은 최대64개
청크/32000개 샘플이다. wire는 정수 문자열 Int64 sequence·누적 샘플·청크 offset, publisher
GUID,전체 PCM SHA256과 canonical base64url로 검증한다. 이전 샘플을 요청하지 않은 첫 관측은
현재 cursor만 반환한다. 보관 범위를 넘긴 요청은 명시적 gap/reset이며 유실 샘플을 만들거나
이전 재생을 반복하지 않는다. 새 청크가 없는 반복 읽기는 예약된 소리를 중단하거나 다시 예약하지 않는다. publisher 교체/과거 publisher 재등장도 검증한다.

`ProjectExecution.Audio`는 이미 실행에 발급된 같은 사용자 FrameControl pipe의 인증·소유
handle·runtime envelope를 검증한다. 별도 socket·자격증명·권한 부여는 없다. 활성
ProjectContext/view/lease/handle과 읽기 scope는 원래 Run 경계에서 검사한다. `runAudio`는
비보관 observation이며 보통 invoke/update의 완료 결과에 PCM을 보관하지 않는다. 읽기는
frame ACK·heartbeat·Resume·Step을 발생시키지 않는다. source/실행/권한/Review/Confirm/CAS
계약을 변경하지 않는다. 실제 작업의 clock은 producer가 소유하며, 소리나 캐릭터 위치가
작업의 실행 조건이 되지 않는다.

## 사용자 동작과 수명

처음에는 Off다. 실제 producer가 관측된 창에서 사용자가 스위치를 클릭할 때만 해당 창의
실제 AudioContext를 만들고 resume한다. 지원이 없거나 context 시작이 거절되면 재생을
꾸미지 않는다. browser queue는 기존 대기량과 새 묶음을 합해 최대12000개 샘플(.75초)이고 오래된 적체는 명시적으로
건너뛴다. 네트워크/스케줄링 지연을 보상하는 무음·합성 sample이나 실행 제어는 넣지 않는다.
원본 `테스트` 버튼은 사용자가 켠 context에서만 별도의 짧은440Hz 로컬 장치 테스트다.
이 신호는 프로젝트에서 온 오디오라는 증거로 쓰지 않는다.

Off·숨김·접기·창 닫기 시도·소유 프로젝트 변경·실행 중단/새 handle·관측 오류는 해당
로컬 graph만 중지/해제한다. 요청 serial과 owner를 재검사하여 늦은 응답·이전 handler가
다른 창을 재생하지 못하게 한다. 닫기가 거절돼 실제 프로세스/입력이 남아도 소리는 안전하게
Off이며 사용자가 다시 켠다. cold 복원은 레이아웃/입력을 보존하고 process/오디오 cursor/
AudioContext를 재생하지 않는다. 다른 기존 저장 입력·Undo·Review/Confirm은 그대로다.

## 호환성과 남은 범위

새 imports를 사용하는 프로젝트에는 새 RunAudio와 확장 FrameControl/ProjectExecution
provider가 함께 필요하다. 과거 rollback은 새 imports를 컴파일하지 못할 수 있다. 기존
imports와 함수/override 계약을 자동 변경하거나 기존 C#을 재작성하지 않는다.

이 기능은 제한된 소프트웨어 미리듣기다. 다채널/다른 sample rate·장치 선택·native audio
sink·실시간 품질/출력 지연·GPU/실제 Windows WebView2/모바일 스피커 검증은 완료하지 않았다.
현재 환경에 `/dev/snd`가 없으므로 실제 native PCM 전송과 Chromium의 실제 AudioContext/
BufferSource graph를 검증해도 물리적 소리를 들었다고 표현하지 않는다. API의 running state는
물리 스피커의 audibility 보증이 아니다([Web Audio 명세](https://www.w3.org/TR/webaudio/)).
자동/preset 해상도·큰 영상/GPU/FPS·진행 중 I/O와 나머지 고정 신원/권한·자산·참여자/대화
항목은 이 단위로 완료되지 않는다. 검증·패키지 증거는 [검증 기록](VALIDATION_V666_RUN_AUDIO.md)에 연결한다.
