# v536 일반 enum C# 편집과 불완전 원문 복구

이번은 원본 v536의 일반 소유 static code 중 데이터 반환이 void이고 switch 실행 profile인 문맥이다. 기존 카드·분기 생성/이름/삭제·C# Script·모바일 흐름을 재사용한다. CSS·레이아웃·새 시각적 분기/반복·async 모델을 추가하지 않는다. 슬롯·복사본·private path·다중 target ABI·혼합 Save는 계속 차단한다.

## 변경과 실제 결함

일반 enum 노드는 이전 원본 화면에서 차단됐고 계약 적용 뒤 본문을 따로 재적용해야 했다. 원본 C# enum/body/helpers 편집을 `enum-code` 개인 입력과 독점적인 `enumCode` authorBatch 단계에 연결했다. 서버의 기존 임시 candidate에서 enum 검증/적용 후 최신 정의로 본문/보조 함수를 적용하고, 기존 전체 source proof·checkpoint CAS·WriteChecked로 저장한다. 중간 단계를 live 상태에 순차 반영하지 않는다. 외부 직접 enumCode 호출, 데이터 반환 노드, 슬롯 문맥 및 graph/unit의 copy provenance는 거절한다. 저장은 초안이며 compiler Review/Confirm은 별도의 명시적 동작이다.

원본과 같은 이름 우선 enum ID 대응을 재사용한다. 연결된 case를 삭제하면 거절하고 기존 핀·연결을 유지한다. 실패한 저장의 개인 입력과 복구 journal을 구별해 둘 다 보존한다.

강제 화면 재진입에서 불완전 enum은 `retained-conflict`의 원문 sections로 보관될 수 있는데, 기존 새 어댑터가 이를 정상 executionEnum으로 렌더해 `actionMarkup`의 members 읽기 오류가 발생했다. 수정 전 실제 컨트롤러/Chromium 렌더러에서 재현했다(`reentry-before.log`). 보관 record의 타입/형태를 확인해 불완전 원문을 카드 계약에 적용하지 않고, 원본 C# 창에서 그 enum/body/helpers를 그대로 복구한다. 반복 보관 시 previous를 중첩하지 않으며 기존 proof/basis를 유지한다. 불완전 원문이 있을 때 분기 추가도 toast로 거절해 원문을 덮어쓰거나 처리되지 않은 예외를 내지 않는다. 실제 원본이 바뀐 경우 보관 입력을 새 버전으로 자동 승격하지 않는다.

## 검증과 근거

격리 fixture의 실제 엔진·Chromium 검사는 `tests/web/v536_general_enum.py`다. 390/1480폭에서 연결된 핀 삭제 거절/취소, 이름·값·순서와 enum ID/연결 보존, enum/body/helpers 실제 프로세스 재시작 복원, 한 batch 저장, compiler Review 취소와 새 명시적 Confirm, 일반 void 노드의 분기 생성, 위조·범위 밖 요청 거절, peer source/checkpoint 변경 시 입력·journal·기존 초안 보존을 검사한다. 별도 `copy-boundary` 모드는 graph에 copySource가 있을 때 owner 문맥을 생략해도 해당 enum batch가 거절되고 모든 source/checkpoint가 유지되는지 검사한다. copy ABI 구현 성공 검사가 아니다.

`tests/web/v536_enum_reentry_renderer.py`는 실제 엔진 API를 모사한 **컨트롤러/Chromium 렌더러** 검사다. 서버 성공 검사로 합산하지 않는다. 강제 재진입, 불완전 입력 중 다른 분기 편집 거절, 불완전 원문의 저장 거절/취소, 새 페이지 복구와 enum 수정 후 같은 ID의 정상 개인 초안 회복, 실제 source 변경 차단의5건을 통과했다. `/tmp/confectory-enum-reentry-pp289oqd/evidence.json` 및 `restored-incomplete-csharp.png`를 실제 열어 확인했다.

같은 묶음의 선행 wrapper 모바일 실제8건은 성공 경로를 변경하지 않아 결과를 보존했다(`/tmp/confectory-mobile-enum-pins-plw8syeg`). 기존 속성 쓰기의 잘못된 owner/value/cardinality/hash/unsupported 거절 및 explicit profile/stale schema/value/ref 경계2건도 통과했다. 속성 v536 UI 연결 완료 근거로 사용하지 않는다.

중간 엔진 검사의 화면 밖 노드 클릭은 원본 캔버스를 정상 휠 이동해 조작하도록 fixture를 고쳤다. 충돌 후 저장 시도 journal이 추가되는 것과 tuple/JSON list 비교도 구별해 원래 사용자 cell의 동일성을 확인했다. 보호 조건이나 실제 실패 assertion을 제거하지 않았다.

최종 실행 로그·교차 패키지와 커밋 후 checkout 결과는 아래 최종 검증 기록을 따른다. 실제 계정·토큰·OAuth·유료 추론·프로젝트 Run·사용자 프로젝트는 사용하지 않았다.

## 남은 범위

일반 enum의 데이터 반환과 readonly/native ABI·copy/slot/private graph의 조합 전체를 완료했다고 주장하지 않는다. 속성 값의 실행 없는 평가와 Set의 별도 출력 저장소는 기존 backend와 차이가 있어 `V536_PIN_AND_ATOMIC_NEXT.md`에 원본 증거, 최소 구현, 결정 질문 하나를 기록했다. 원본 UI 복원 전체는 미완료다. 실제 Windows apphost/WebView2와 실제 모바일 기기·가상 키보드는 미검증이다. 로컬 패키지는 Library 전달 성공과 다르다.

## 최종 검증 기록

- 최종 생성 엔진 `build5.json`/`build5.err`: Linux build exit0, stderr 없음.
- 실제 엔진 `actual6.log`: exit0,7건, `/tmp/confectory-general-enum-dmz20f_q/evidence.json`. 원본 C# 일반 enum→cold→원자 저장→명시적 compiler Confirm과 실제 peer 충돌까지 완주했다.
- 별도 실제 엔진 `copy-boundary.log`: exit0,1건, `/tmp/confectory-general-enum-rc8eut_2`. copySource가 있는 graph의 owner 생략 우회 거절이며 복사본 편집 성공 검사가 아니다.
- 최종 복구 렌더러 `reentry-final.log`: exit0,5건. 엔진7건과 별개다.
- JS/Python 구문과 `git diff --check` 통과.
- Windows 교차 패키지 `package-final2.log`: exit0, 선언2305파일. 로컬 실행 파일 `/workspace/artifacts/Confectory-v536-general-enum/Windows-x64/Confectory.exe`.
- `desktop_package.py`: exit0, `/tmp/confectory-desktop-package-931oc2ji`. 66 UI 리소스 구성, 누락/변조 거절, 다른 cwd, 설치 SDK 없는 packaged managed 엔진 웹 기동, 프로필 재사용/명시 override, 최소 로그인 화면을 확인했다. 실제 Windows exe/WebView2는 실행하지 않았다. .NET Desktop Runtime10.0 x64와 Microsoft Edge WebView2 Runtime이 필요하며 자동 설치하지 않는다.
- 커밋 후 clean checkout의 생성 엔진과 CRLF 일반 pull/fresh LF·66 리소스 검사는 게시 전 별도로 수행하고 checkpoint에 결과를 보존한다. 앞선 source의 통과를 새 커밋의 결과로 대체하지 않는다.

모든 검사/원본 대조 로그는 `/workspace/scratch/v536-general-pins/`에 보존한다. 스크린샷은 렌더링 증거이며 전체 v536 정밀 일치 또는 Windows 네이티브 QA의 증거가 아니다.
