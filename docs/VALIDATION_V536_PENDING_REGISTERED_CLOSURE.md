# v536 새 copy의 등록 복수 호출 결합

기준은 게시 `dec8ea0`와 원본 저장소 v536, 고정7행/A6다. 이번 유한 단위는 **확정 전 단일 target same-contract copy에서 하나의 등록 direct-dependency callee를 쓰는 여러 기존 ordinary wrapped 호출**이다. 저장된 copy의 등록 closure와 새 copy의 소유 callee closure를 재구현하지 않는다. target 자동 선택·독립 계약 복제·공개 override 계약 변경·새 UI는 추가하지 않는다.

## 대조와 실제 수정

기존 `PrivateImplementationCopy`는 등록 callee의 원문·읽기 전용 receipt를 이미 읽고 private binding/guard에 포함했다. 그러나 복수 use helper가 소유 namespace만 허용하여, 기존 두 private 호출의 `원본 계약 갱신` 버튼이 비활성화됐다. 순수 후보에서 stale 계약이 보이면서 `callAbiAvailable=false`인 결과를 재현했다. `BlueprintCallAbiUses` 자체는 namespace-qualified ID와 전체 graph/import/본문·호출별 명시 대응을 이미 처리하므로 이 backend나 레이아웃을 새로 만들지 않았다.

검증된 기존 direct-dependency receipt가 있을 때만 같은 helper로 연결한다. 선택한 모든 use의 계획과 선택 카드의 계획이 같아야 하며 누락·추가·잘못된 qualified 경로·오래된 binding·미대응 소비자·마지막 비호환 출력은 전체 거절한다. 각 호출의 값은 사용자가 직접 선택하고, 원래 immutable seed/snapshot과 현재 계약을 구별한다. 본문·값·설명·기존 연결·다른 target 및 부모/외부 원본은 보존한다.

첫 실제 기본 창의 저장·cold·Review/Confirm은 통과했지만, **혼합 저장/검토 뒤 등록 manifest가 바뀌어도 Confirm이 성공하는 결함**을 추가로 재현했다. 선택 receipt는 메모리 binding에만 남고 생성된 copy의 저장 후보에는 남지 않았다. 다음 기존 경계를 보완했다.

- Native 후보의 끝에서 같은 읽기 규칙으로 등록 receipt를 다시 확인하고, 사용자가 명시 갱신한 등록 계약만 결과에 담는다. 외부 구현/provider 본문을 새로 읽지 않는다.
- `CopyImplementation`은 새 소유 구현의 `privateAbiContracts` metadata에 선택 owner와 원래 receipt를 보관한다. 외부 ID를 owned unit/쓰기 대상으로 만들지 않는다. 원래 생성/owner 혼합 Save의 한 후보·checkpoint CAS·결과 조회를 재사용한다.
- `ValidateReviewSelection`은 아직 확정되지 않은 copy의 creation owner와 원래 manifest/owner 문맥에서 같은 등록 계약을 재조회한다. 기존 receipt를 현재 값으로 자동 덮지 않는다. cold 복원은 metadata와 초안을 보존하고, 외부 변경이면 Review/Confirm을 거절한다.
- 기존 Confirm의 컴파일 전후 selection 검증과 생성 그룹 전체 source CAS를 유지한다. 실제 새 copy 목적지 충돌도 owner/manifest/다른 source를 전부 미적용하고 상대 파일과 저장 후보를 보존한다. 등록 팩은 이 프로젝트의 쓰기 lease 대상이 아니며 읽기 전용 재조회와 프로젝트 소유 쓰기의 최종 CAS를 구별한다.

외부 변경이 발생한 후보를 자동 재기준화하거나 이전 실패/입력 기록을 지우지 않는다. 기존 공개 override는 원래 매개변수·출력 계약을 유지하고 구현만 편집한다. 별도 새 함수 생성이라는 기존 기능은 바꾸지 않는다.

## 수용 표본과 재현

`Lib::Native`를 `frame/native`, `other/native`에서 쓰는 새 common copy다. 원래 `ref long -> long`에서 현재 `int step,double renamed,out long total -> bool`로 명시 갱신하며 값3/5, int64 local `9223372036854775806`, owner 값 `9007199254740993`, 원래/별도 본문 입력·공유 import·wrapper를 구별한다. 이는 기존 조작의 표본이며 모든 타입/모드/target 조합의 전수 지원 주장이 아니다.

```sh
python3 tests/web/v536_general_private_abi_metadata.py "$REPO" nested remap closure registered
python3 tests/web/v536_general_private_abi_ui.py "$REPO" "$ENGINE_REPORT" normal nested remap closure registered
python3 tests/web/v536_general_private_abi_ui.py "$REPO" "$ENGINE_REPORT" normal nested remap closure registered view
```

같은 UI 검사의 기존 첫 인자 `storage`, `response-loss`, `callee-conflict`, `owner-conflict`, `cancel`, `invalid-last`와 이번 `registry-conflict`, `registry-confirm`, `destination-confirm`을 사용한다. 기본/독립 창·불완전 값 cold·Undo/Redo·취소·실제 쓰기 실패/재시도·응답 유실·실제 callee/CP 경합·명시 Review/Confirm 및 원래 snapshot/입력 보존을 확인한다. `destination-confirm`은 등록 manifest 대신 새 소유 구현 파일에 peer 충돌을 만드는 별도 최종 CAS 검사다. 두 거절 모드의 초기 공통 로그 문구와 실제 변경 대상을 혼동하지 않고 명령/단언을 근거로 집계한다.

초기 fixture의 callee ID 문자열 불일치, 새 검증 블록의 C# 지역 변수명 충돌은 실패로 보존하고 수정 뒤 필요한 검사를 재실행한다. 순수 후보의 재현 차단과 검토 뒤 receipt 변경 누락이라는 실제 결함을 이 실패들과 구별한다. 최종 결과·명령·SHA는 `evidence/v536-pending-registered-closure/`의 확정 JSON만 따른다.

## 공간과 정확한 잔여

시작 여유 약690MiB, 디스크200MiB·별도 `/tmp` RAM 임시 출력768MiB 예산을 확인했다. 검사는 순차 실행하며 기존 독립 checkout을 FF한다. 이번 검사 소유 fixture/package만 전체 증거 보관 후 승인된 cleanup을 사용한다. 기존 원본·SDK·보관 빌드·백업·로그·스크린샷·프로필·사용자 자료를 추가 삭제하지 않는다.

이 단위가 닫는 것은 새 단일-target copy의 **기존 ordinary 등록 복수 use**다. 별도 frame 계약/본문의 동시 변경과 opaque/whole-body source closure는 기존7/8행·A4–A6의 동일 잔여다. 이번 두 private use 표본으로 모든 graph 문맥을 완료했다고 일반화하지 않는다. 한 copy의 모든 target 자동 복제를 새 필수 요구로 추가하지 않는다.

8행의 여러 함수 계약과 아직 결합되지 않은 C#/중첩/copy 문맥, 9행 정보/참조/기능 핀 타입 및 표시명/생성 식별자 대응, I6 기호/이모지/사용자 로컬 이미지 아이콘, B2 실제 배정 배지, M4 async·M11 C# 동작의 graph 전환·M12 root 실행 분기는 별도다. 이미지·협의·렌더 신규 backend를 만들지 않는다. 실제 Windows apphost/WebView2·모바일 기기/터치·Library 전달과 전체 UI는 미완료다. 새 교차 패키지는 검증용 임시 산출물이며 전달본으로 표시하지 않는다.

## 확정 집중·영향 검사

최종 고정 소스의 실제 엔진/렌더러11흐름 76확인 및 순수 후보 8확인이 통과했다. 영향 회귀의 확인 수는 `{'owned': 8, 'copy-targets': 3, 'metadata-owned': 7, 'cas': 4}`이며 기존 소유 callee 새 copy·직전 두 target copy 결합·소유 순수 후보와 생산 최종 CAS를 검증했다. 초기 차단/재현 실패를 이 수에 넣지 않는다. 실제 명령·소스 SHA와 실패 구분은 위 evidence에 있다. 독립 checkout/새 교차 패키지는 별도 후속 결과로 기록한다.

## 독립 checkout·새 교차 패키지 확정 결과

실행 소스 커밋 `cf71d4d8277e68b83988501a07984b08a9005966`의 변경 Git blob·기존 autocrlf·clean을 확인했다. 기존 독립 checkout에서 Native/CLI Release·새 Linux 엔진 및 실제 독립 정보 창 9확인·순수 후보8확인이 통과했다. 새 RAM Windows x64 교차 패키지의 restore·Release·MCP·생성·probe·패키지 자체 UI9확인까지 6단계가 통과했다. 전체 2349개/manifest 2348개 목록·SHA·Core/Native DLL과 변경 엔진 소스 바이트를 확인했다.

manifest SHA `5b399df0d96050b032e92e725c86ec8b63bb98194daf07b2ad12073352e49c0d`. 전체 manifest와 fixture/로그/프로필 증거를 보관하고 이번 임시 패키지만 정리했다. 기존 보관 패키지/SDK/원본/사용자 자료는 삭제하지 않았다. 후속 최종 커밋은 문서/evidence만 달라 실행 소스는 위 커밋과 같다. 이 교차 패키지는 실제 Windows apphost/WebView2 실행이나 Library 첨부 성공이 아니며, 네이티브 Windows/mobile·전체 UI·전달은 계속 미완료다.
