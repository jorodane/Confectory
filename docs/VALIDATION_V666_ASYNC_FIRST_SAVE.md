# v666 첫 생성 Save 입력 결합 최종 검증

동결 코드는 `2e58f5929f5887a9d78a02f9b4636614f2da2ae6`다. 이후 게시 마감은 문서만 바꾸며 runtime/source/tests/tools의
동일성을 확인한다. [지원과 유한한 잔여](M4_ASYNC_FIRST_SAVE.md)를 기준으로 한다.

## 최종 검사와 재사용 근거

독립 LF 30·CRLF 29·새 Windows 교차 패키지/전체 압축 복원/실패 수명관리
9, **총 68단계 전부 통과**. 신규 32개, 재사용 36개다.
Core의 AsyncBlueprint/AsyncContext/BlueprintConversion 18개 검사는 이전 동결 `986f581`의
양쪽 실행을 재사용했다. C# backend·관련 직접 검사·빌드 설정·SDK/seed의 동일성을 전체
Git diff와 의존성 SHA로 검증했다. Bundle은 canonical 자원 pin 외 동작/endpoint가 같아야
재사용을 허용한다. 실행 argv와 LF/CRLF 독립 checkout 설정도 동일해야 한다.
`backend-reuse.json`에 항목별 출처와 이전 증거 SHA를 기록한다.
제품 byte가 같은 `25bb57e`에서 통과한 UI 13단계는 별도로 재사용했다. 제품/다른 검사/
SDK/seed/EOL과 호출 argv가 동일해야 하며 UI fixture는 응답 polling 한도 30초→90초
수정만 정규화한 뒤 전체 bytes가 같아야 한다. 클릭·주장·저장 기준은 바꾸지 않았다.
`ui-reuse.json`에 출처를 기록한다. 실패한 새 카드 UI는 신규이며 빌드·새 패키지와
전체 복원·수명관리도 최종 코드에서 신규 실행했다.

- 새 전역 함수와 정보 소유 함수, 기존 직접 소유 내부 본문, 새 ordinary 직렬 동작의
  원문/표시/지역 핀/값/연결과 Task를 한 후보·checkpoint·최종 CAS로 검증했다.
- 잘못된 전환 순서·중복 전환·없는 ID·ref·다른 구조 계획은 전체 거절했다. 원래 C#·helper,
  공개/override IO·ID·기존 호출/연결과 실제 await 뒤 다음 동작을 보존했다.
- 첫 생성 전 Undo/Redo·코드 취소, 선언 자체 미저장 및 checkpoint 없는 cold,
  저장 실패/등록 충돌·생성 응답 유실·저장 응답 유실과 늦은 입력을 새로 검사했다.
  부분 Review/Review 이후 충돌 거절·취소/Confirm·실제 실행·확정 cold도 포함했다.
- 선언 복구는 다른 프로젝트/경로·링크·실제 목적지 충돌·등록/checkpoint 변조를 거절하고,
  원래 타입/이름/원문을 같은 소유 메모리 초안으로만 복구한다. 기존 다른 초안은 덮어쓰지 않는다.

## 개발 중 발견과 구분

원문과 전환을 별도로 저장하던 제한, 새 카드 목록에 없는 미저장 카드의 메뉴 차단,
임시 Task 선택을 실제 완료 계약으로 오인한 취소 차단을 연결했다. intent/핀 변경 뒤에
명시 C#을 기록하여 definition receipt를 일치시킨다. 생성/저장 결과 확인과 헤더의
관측 기반 메모리 복구를 구분해 cold와 늦은 입력을 보존했다.

fixture의 상태 필드/Review 전후 checkpoint 비교와 카드/미니맵 겹침도 수정했다.
개발 중 교차 빌드로 descriptor 입력이 바뀐 검사는 최종 근거에서 제외했다.
첫 최종 실행 `986f581`은 54단계 통과 뒤 정보 함수의 늦은 source/cold에서 막혔다. 입력을
잃지는 않았지만 프로세스 내 revision이 달라 이전의 확인된 자기 저장과 연결되지 않았다.
정확한 캡처 source·노드/입력 종류·전체 원본 hash와 확인된 async receipt에만 재연결을
허용했다. 일반 source의 기존 기본 거절·동료/변조/누락 거절은 유지한다. 실패 증거는
`f3b0d0fcdcb541b8b0829f5a4350e8aa` (ZIP SHA256
`740cea431626f8b8eb6a5ca2ff3d05733eeb7b71e9580bd1d8e77d891a6b63a2`)에 보존했다.
그 실행 전체를 통과로 계산하거나 실패한 UI를 재사용하지 않았다. 다음 실행의 초기
회귀는 cold와 늦은 source의 복구·추가 Save를 통과한 뒤 fixture에서 멈췄다.
정보 함수의 별도 source-only 저장까지 최초 전환의 중복으로 세던 단정을 수정했다.
첫 source+Task 후보는 한 번, 새 입력의 source-only 후보는 다른 attempt인지 확인한다.
이 실행도 통과로 계산하지 않으며 증거 `48f72c13bed0465aa6ed707423c3d207`
(ZIP SHA256 `8371a78bbd87ff93bfea9eb1d18141b3a6f6d75cbd34417ca1792af928713f2c`)에
보존한다.
다음 `25bb57e` 실행은 신규 33·동등 근거 재사용 23단계 뒤 새 카드의 늦은 입력
검사에서 멈췄다. authorBatch 요청은 한 번 관측됐으나 30초 polling 안에 완료 응답을
관측하지 못했다. 테스트를 기존 Save의 90초 한도로 맞추고 실패 검사를 새로 실행했다.
그 실행 전체나 실패 검사를 통과로 계산하지 않으며, 통과한 동일 제품 UI만 엄격히
재사용한다. 증거 `c7cf4dce5948404a9b07fab39020a7da`의 ZIP SHA256은
`bc5550da63a211640526f42ec810bc0fbb2089f70edf846f1aaddef21c674e91`이다.
원본 제품 레이아웃은 변경하지 않았다. 개발 증거는 `/workspace/artifacts/v536-verification-managed/runs/43bcb78b31d34a248614f7243f0dbeb6.json`와
그 검증된 ZIP(`ed056802dcd5f23419f4ed02cb21c9747c6e3914d6b537ae05fec32616967be1`)에 보존했다.

## 지속 보관·공간

최종 record: `/workspace/artifacts/v536-verification-managed/runs/49aec998004c4c7781ad8d1a8cebb9ae.json`
증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/49aec998004c4c7781ad8d1a8cebb9ae.zip`
SHA256: `9cfdac9cff8d01bd46236f4f76dbfcae57f9ef2f81b6c7edcb3054dac0444c4c` (2.41MiB).

최신/롤백은 `/workspace/artifacts/v536-verification-managed/packages/index.json`에 있다.

- latest: 출처 `2e58f5929f5887a9d78a02f9b4636614f2da2ae6`, `376b87627e6831f540322c986d76728fbb2323c3dd86428624f22ea256b1fc27.zip`, 49.12MiB; 전체 파일 2381·디렉터리 147, package manifest `aaacaba688846d0f1199ab5b040627690b2d445f5b3faa0d836f553686bee541`.

- rollback: 출처 `7358ed1ef57ee43f4abcfaac67464c34360fb29e`, `a0c81c5e81e2eea24745671340ad7048e937e088088e50d7f326bc4c6fe149f6.zip`, 49.12MiB; 전체 파일 2381·디렉터리 147, package manifest `f366501e68a586ef6dcd60c9a31272f71b678f434cedc7744c1967486acc74db`.

최신은 새 생성본 및 전체 ZIP 추출본에서 실제 엔진·UI/저장·실행을 확인했다. 롤백은
앞선 [57단계 검증 기록](VALIDATION_V666_ASYNC_PRIVATE_RETURNS.md)의 정상본을 유지하며,
이번 보관 마감에서 ZIP CRC/전체 파일 SHA·모드를 다시 확인했다. 롤백의 기기 실행을
이번에 새로 했다고 계산하지 않는다.

소유 임시 작업공간 `/tmp/cv-ka9gfizm`는
자식 종료·증거 무결성·지속 패키지 승격 확인 뒤 제거했다. 과거 자료 추가 정리는 없다.
검사 단계에서 기록한 최소 디스크 여유는 1683.21MiB, 기록된 최대 cgroup 메모리는
4571.16MiB다. 최종 실행 순증가는 3.32MiB, 개발 증거·중간 실패와
코드/문서가 포함된 검증 정리 시점의 이번 단위 측정 순증가는 29.16MiB다.
마감 측정 여유는 1679.94MiB다. 3–6MiB를 보장값으로 사용하지 않는다.

## 실제 잔여와 미실행

공개 Root IO를 첫 Confirm 전에 함께 바꾸는 거래와, 완료/결과 분기 실행선에 삽입한
새 동작의 첫 Task 선택 결합은 별도 실제 경계다. 직렬 next 생성 지원을 그 흐름들의
완료로 확대하지 않는다. 분기선 생성은 `route:completion`/`route:case` 입력을 만들지만
현재 async 입력 결합은 next `route`만 허용한다. 새 영구 UX 금지나 타입/문맥 조합표를
만드는 대신 이 두 원래 편집 거래의 구현/검증으로 범위를 유지한다.

이번 신규 UI는 기본 Blueprint 창에서 검사했다. 해당 결합의 독립 정보 창·다른 실제
프로젝트 왕복은 새로 실행하지 않았다. 새 private 선언 복구 항목은 이전 에디터에
복구 경로가 없으므로 미확정 입력은 최신본으로 복구한다. 프로젝트 문법·C# 원문을
자동 migration하지 않는다. M11/M12는 구체적 회귀 없이 다시 열지 않는다.
V2–V9·별도 팩/backend·종류 C# 표현/사용 중 삭제 대응·실제 Windows apphost/WebView2·
모바일·전체 UI·Space 전달은 이번 검증으로 완료되지 않는다. live AI/실계정/유료 호출은 하지 않았다.
