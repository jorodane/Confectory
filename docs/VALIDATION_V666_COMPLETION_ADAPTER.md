# v666 · Result 없는 ordinary 동작 완료 복귀 검증

최종 구현은 `76f9837d16bf8df822acbe2aa96d2e81de627aa7`(tree `6e52d9c0197806de9d402e3ad9cddff42920ff89`)이다. 게시 시 추가한 종료 문서는 구현·검사 코드와 분리하며, 게시 HEAD와 이 동결본의 `src/targets/packs/examples/tests/tools` 트리가 같은지 확인한다. main은 사용자의 검토·병합 대상으로 보존한다.

## 지원 범위

직접 소유한 기존 ordinary Root의 `next` C# 동작을 완료 연결을 보존하는 동기 동작으로 복귀한다. 원문/helper/Execute 이름·source marker, void/native 반환·out, 기존 핀·연결·완료 ID를 유지한다. 원문과 별도 클래스의 readonly 입력/출력 snapshot 선택기를 사용하며 기본 `Result.None`과 명시 완료 선택을 구분한다. 원래 `Result` helper도 충돌하지 않는다. 같은 ID로 async 재활성화하며 원문을 자동 재작성하지 않는다.

원문·선택기 편집은 기존 C# 팝업과 전체 관측·원자 저장·Review→Confirm·최종 CAS를 재사용한다. 창 숨김에서 팝업 입력을 보존하고, 이미 수락한 저장 뒤의 늦은 입력은 정확한 영수증과 원래 ID/bytes가 일치할 때만 현재 기준에 연결한다. 다른 소스/누락/변조 proof는 거절한다. 새 텍스트는 이전 응답으로 바뀌거나 자동 저장되지 않으며 별도 Save로 한 번 반영한다. [정확한 의미와 호환 경계](M4_COMPLETION_ADAPTER.md)를 따른다.

## 최종 결과

| 구간 | 신규 실행 | 동일 근거 재사용 | 합계 |
| --- | ---: | ---: | ---: |
| 독립 LF checkout·캐시 | 15 | 6 | 21 |
| 독립 CRLF checkout·캐시 | 15 | 3 | 18 |
| 새 교차 패키지·전체 복원·실패 수명관리 | 9 | 0 | 9 |
| 전체 | **39** | **9** | **48** |

48단계 모두 통과했다. 두 checkout의 새 Release 빌드는 경고·오류 0이다. 모든 UI 검사, 두 새 빌드, 새 패키지와 전체 복원은 이번 동결본에서 실행했다. UI는 정상/취소·Undo/Redo·창 숨김/cold·반복 저장, checkpoint 실패·원문 경합, 응답 유실·늦은 입력, Review 취소/Confirm·실제 CLR 실행과 원문 CRLF/helper·출력/연결을 확인한다. copy와 속성 UI 회귀도 새로 실행했다. 선택기의 readonly 영역 탈출은 compiler body 검사로 거절하며 source marker를 별도로 유지한다.

재사용 9단계는 이전 동결 `bf276b1eebfd3cc02d17ab820d22a9234efcce16`의 **통과 결과만** 사용한다. LF의 runtime/metadata 거절/API/기존 완료 API/공개 완료 API/영수증 6단계와 CRLF의 runtime/metadata 거절/API 3단계다. Core/runtime 20개 검사는 각 EOL에서 기존 실행 근거를 재사용했다. 재사용한 Core/targets/packs의 C# 실행 코드와 API 검사 입력·SDK/NuGet 전체 SHA가 동일하다. 이후 변경은 browser proof 연결·WebBundle의 자산 manifest 데이터·해당 UI/직접 검사·문서뿐이다. API는 browser 코드를 실행하지 않는다. 이전에 미실행인 CRLF의 기존 완료·공개 완료·영수증 회귀는 새로 실행했다.

이 판정은 최종 증거의 `reuse-audit.json`, `harness/audited_verify.py`, 각 `*.result.json`에 원래 commit·명령·로그 SHA·의존성 및 허용된 소스 차이와 함께 보존했다. 재사용을 신규 실행으로 세지 않는다. 실패했던 늦은 입력 검사는 재사용하지 않았다.

## 중단·실패 및 수정 근거

첫 최종 실행에서 늦은 선택기 입력은 남았지만 cold 뒤 재저장이 원본 변경 오류로 막혔다. 원래 입력 proof의 이전 process revision과 실제 요청 proof의 새 revision 차이가 원인이었다. 영수증 확인 뒤 같은 입력 key/node/종류·원본 ID/SHA가 일치할 때만 연결하도록 수정했다. peer/누락/중복/다른 원문·변조 proof 거절은 새 직접 검사와 실제 UI로 확인했다. 첫 클릭이 항상 조회만 해야 한다는 검사의 과도한 가정도 고쳐, 이미 영수증이 확인된 경우 별도 Save 한 번으로 새 입력만 한 번 반영하는지 확인한다.

- 실패 실행: `/workspace/artifacts/v536-verification-managed/runs/984ea10d96de41b8aa5385f9b1ada874.zip`
- 실패 증거 SHA-256: `210895f1bddab4fd5d8d7ea4db044f9c8301db25cd7c7d2d0b689d7978185dad`
- 최종 실행: `/workspace/artifacts/v536-verification-managed/runs/75f3aafac4594c87af5993d33b0480aa.json`
- 최종 증거 ZIP SHA-256: `b8f2fb95eedbbfcbedeec8a2f1b0e15c43a6998941b08764460757eda9f1f7bc`

실패 시 최신/롤백은 승격하지 않았다. 개발 중 fixture 수정 및 제품 수정의 입력·로그·source overlay도 별도 관리 실행 `8d1948b4b50b4e6ab47df00efead2bcb`와 `7bea8014ae3146aeb687981960f95935`에 보존했다. 환경 재연결 후 실제 Git/증거 SHA를 확인해 중복 실행과 결과 추정을 피했다.

## 패키지·복원·공간

`/workspace/artifacts/v536-verification-managed/packages/index.json`에서 다음 두 세대를 지속 보관한다. 각각 보관본 SHA를 다시 확인했다.

| 역할 | 구현 출처 | 보관 ZIP SHA-256 | bytes |
| --- | --- | --- | ---: |
| 최신 | `76f9837d16bf8df822acbe2aa96d2e81de627aa7` | `719fefc5f8222b28cbd1f09242aea990203b41b6132f97e2f372d813ca82a156` | 51,478,724 |
| 롤백 | `e4c0646ac22cbe3f73c251064b1095565a4f0399` | `f3e74fd601800894723dc4e43cc3385ab322056987e965e01629942ea857be7e` | 51,456,853 |

최신 archive는 manifest 자체를 포함한 파일 2,377개와 디렉터리 147개의 SHA/크기/모드를 검증하고 전체 복원했다. package manifest SHA-256은 `1c81cea88791ca30d329eeb0833f9cc6a2ad2568a54545a40e72a30ba4c60c39`다. 생성본에서 실제 엔진 UI/Task runtime을, 전체 복원본에서 늦은 입력·저장 실패 UI와 Task runtime을 실행했다. 마지막 실패 수명관리도 통과했다. 원자 승격 후 이전 최신을 정상 롤백으로 유지했다.

사전 추가 디스크 예산은 안전 여유 64MiB를 포함한 144MiB였다. 최종 실행 전 여유 1,860,096,000B에서 보관·정리 후 1,855,647,744B(약 1.728GiB)로, 이 최종 실행의 순증가는 약 4.24MiB다. 앞선 개발/실패 증거를 포함한 이번 단위 전체는 최초 측정 대비 약 11.05MiB 증가했다(종료 문서/게시 전 측정). 실패 증거도 보존하므로 정상 1회 증가량과 구분한다. `/tmp/cv-q3yznemw` 제거와 record `cleaned`를 확인했다. 기존 자료의 추가 정리 없이 해당 실행 소유 임시물 및 승인된 최신/롤백 교체만 수행했다.

## 남은 유한한 경계

M4의 instance/native whole-body 소유 문맥과 새/직접 소유 내부 본문의 명시 전환은 다음 단위다. 이 문서가 그 완료를 주장하지 않는다. 비소유/override IO/ref/호환되지 않는 기존 C#·legacy 자동 전환 거절을 새 필수 기능으로 늘리지 않는다. M11/M12는 구체적 회귀 없이 다시 열지 않는다. V1의 독립 창/프로젝트 왕복 등 검증 후속, V2–V9·별도 팩/backend·종류 C# 표현과 사용 중 삭제 대응은 기존 [고정 수용 목록](V666_ACCEPTANCE.md)을 유지한다.

구버전이 새 completionAdapter 그래프를 읽거나 실행한다고 보장하지 않는다. 코드 롤백과 데이터/초안 복구는 다르며 유일한 사용자 자료를 자동 변환하지 않는다. 실제 Windows/WebView2·Android/iOS 기기 실행, 전체 UI 및 Library/Space 전달은 미완료다. live AI/자격증명/유료 호출은 사용하지 않았다.
