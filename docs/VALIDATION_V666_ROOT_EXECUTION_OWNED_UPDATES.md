# M12 — 같은 공개 계약 copy·자식의 전체 정의 갱신

원본 v666 ZIP `dist/blueprint.js:969–976`의 공개 실행 분기 정의/반환 편집, `:135`의 참조 호출 포트와 기존 A4–A6·같은 계약 구현 배정 요구를 따른다. copy/자식의 기존 분기 반환 편집과 공개 선언 변경의 전체 영향 거래는 구별한다. 공개 IO·override 계약과 독립 계약 복제 제외 합의는 유지한다. 가능한 타입/문맥 곱을 새 요구로 추가하지 않는다.

직접 소유 공개 함수를 편집하면 저장된 같은 계약 copy와 로컬 자식의 **직접 선언한** Blueprint target도 기존 명시 target/반환 대응에 포함한다. 상속받기만 한 본문은 부모 선언의 소스를 그대로 사용하며 새 본문·node ID·C#을 만들지 않는다. 로컬 부모 체인의 함수/입출력이 같아야 하며 effective import 문맥을 기존 상속 규칙으로 유지한다. 원본 graph/코드/배정·copy donor provenance·연결·profile을 보존한다. 원래 enum ID/할당 값을 바꾸거나 자동 원문 재작성은 하지 않는다.

copy를 포함한 전체 갱신은 해당 프로젝트의 owner/schema/object/module·manifest와 로컬 상속 선언을 readonly 관측한다. 전체 소유 배정 영역과 manifest를 확인해 저장 중 새/shared 배정이 생겨도 동일 최종 CAS에서 거절한다. 실제 소유 target·모든 caller는 기존 UI에서 명시 대응한다. 비소유 부모/외부 원본을 writable member로 넣지 않는다. 등록 외부 import/ancestry의 읽기 receipt 결합은 별도 유한 잔여이며 이 단위에서 접근권한을 추가하지 않는다. opaque/구형 profile 자동 migration도 추가하지 않는다.

저장된 전체 후보는 한 checkpoint·전체 Review/Confirm·최종 raw CAS에 결합한다. 그룹 복원은 checkpoint에 이미 알려진 source ID만 bounded read하며, 관측 경로나 checkpoint 텍스트가 새 source를 등록하거나 외부 파일 읽기를 허용하지 않는다. 기존 copy/child 반환 전용 guard는 먼저 검증된 공개 정의 전체 거래를 구분한다. 원문과 readonly 관측은 유지하며 일반 반환 편집의 기존 보호를 약화하지 않는다. UI 레이아웃·팝오버·CSS/HTML은 바꾸지 않는다.

집중 검사와 최종 LF/CRLF·패키지/전체 복원·실패 수명관리 결과는 완료 후 아래에 기록한다. 실제 Windows apphost/WebView2·모바일·전체 UI·Space 전달은 별도이며 live AI·자격증명·유료 호출은 사용하지 않는다. 승인된 실행별 임시물 수명관리와 최신/정상 롤백 보관만 적용한다.


## 최종 동결 검증 — 2026-11-03

제품·검사 동결 source는 `448f1605d48ccf1773527ffdbee6bdb2eaeb757a`다. 독립 LF 19·CRLF 16·새 Windows 내용 교차 패키지/전체 복원/실패 수명관리 6, 총 **41단계(신규 28·동등 근거 재사용 13)**가 통과했다. 새 독립 빌드·수정한 다중 target 회귀·CRLF의 후보/저장/복원/UI·패키지는 신규다. 인자 수정 전 같은 제품에서 통과한 LF 근거는 아래에 구분한다. 실제 배정된 copy, 직접 자식, 부모 본문을 그대로 상속하는 provider를 구별하여 out10→선택 분기→다음 실행을 확인했다. 대상/호출자 선택 누락, 알 수 없는 분기/기존 할당값 변조, owner/module/project·상속/provenance 변조, Save 전 및 Review 뒤 경합은 전체 미적용한다.

UI normal/storage/conflict/loss/late는 기존 루트 계약·각 target 반환·명시 caller 선택을 사용한다. private Undo/Redo·미선택 저장 거절·저장 전 cold, 실제 checkpoint 권한 실패·owner 변경 경합, 응답 유실 뒤 receipt 재조회, 저장 중 늦은 분기명 입력 보존·별도 Save, Review 취소/Confirm·확정 후 cold를 검증했다. 생성 패키지의 copy 정상 UI와 전체 압축 복원본의 직접 자식 late UI도 새로 실행했다. 실제 기기·독립 편집 창/프로젝트 왕복·전체 UI·Space 전달을 이번에 새로 검사한 것으로 표시하지 않는다.

재사용 중4단계는 `7cbc199b1170d94a48d9b47f49bcf92aba00c8c6`의 직접 Core runtime 17개·소유 경계 2개씩, 합계38개다. `src`, `tests/Confectory.Tests`, `targets/dotnet` Git 객체와 SDK/NuGet/configuration/RID가 동일하며 해당 직접 검사는 변경한 element-authoring·pack/UI를 호출하지 않는다. informational-version 바이트 동일성을 주장하지 않는다. 증거의 `core-source-equivalence.json`, `reusedFrom`·기존 로그 SHA/controller로 범위를 구분한다. 기본 harness는 이 단계도 새로 실행한다.

나머지9개 재사용은 `bae86a494051c72397745e3eec0ae4c7b172b11c`의 LF 기본 스크립트2·copy/직접 자식 API2·normal/storage/conflict UI3·공개 wrapper/비void saved-copy 회귀2다. 이 실행 `52bdc53dd75542989e6a797a6e889c74`는 이 검사들이 통과한 뒤 다중 target fixture 호출에서 `--out-root`가 빠져 제품에 진입하기 전에 실패했다. 해당 인자만 수정한 현재 source와 `src`·`targets`·`packs`·`examples`·`tests` Git 객체, SDK/NuGet/configuration/RID 및 정규화한 재사용 검사 인자가 같음을 확인했다. 동일하게 복구된 환경에서 수행됐으며 생성 바이너리/informational-version 바이트 동일성을 주장하지 않는다. `lf-source-equivalence.json`·이전 지속 증거 SHA·개별 로그 SHA를 보관했다. 이 실행의 재사용 판정은 최종 `reusedValidations`의13개 목록과 두 소스 비교 기록을 따른다. 전체 실패 실행을 성공으로 표시하거나 실패 단계를 재사용하지 않았다. 수정한 여러 target, 등록 외부 부모의 자식 반환·일반 비void와 최종 읽기 CAS는 신규 영향 회귀다.

집중 검사에서 copy API6·직접 자식 API6·UI4 확인이 먼저 통과했다. 최초 cold 실패는 아직 읽지 않은 다른 선언이 새 거래 검증에 섞인 null 오류였다. 이미 알려진 source ID만 읽고 해당 완전한 그룹을 검증하도록 수정했다. 진단용 오류 노출은 실행이 소유한 복사본에만 적용했고 저장소 UI는 바꾸지 않았다. 다음 실패는 Review 전 checkpoint를 Review 뒤와 비교한 테스트 기대값이었으며 제품 CAS는 정상 거절했다. Review 직후를 기준으로 고친 뒤 통과했다. 초기 진단 helper의 설정/빈 로그 충돌도 재현 자료에 남기며 성공으로 세지 않았다.

이후 첫 최종 실행 `0a236d9357484835bc4f58ece1e797ac`은 환경 연결 해제/재시작으로 RAM 임시 root와 실행 프로세스·로그를 잃었다. 완료 목록만 남은8개 신규 단계는 성공 근거로 재사용하지 않았다. 기존 로컬 source와 지속 집중 증거·최신/롤백은 보존됐고 동일 환경이 복구된 뒤 같은 제품 코드로 재개하고 위의 검사 인자만 수정해 이번 최종 검증을 마감했다. 중단 메타데이터와 root/process 부재 확인은 `environment-interruption.json`에 보존했다. 새 환경이나 대체 저장소를 만들지 않았다.

- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/ac2c2a65861c471288c8d571af381e1d.json`.
- 최종 지속 증거: `/workspace/artifacts/v536-verification-managed/runs/ac2c2a65861c471288c8d571af381e1d.zip`, SHA-256 `6ef81a3356b6c89f4f2195a6a997f5b91a2c6c28544ac1745ad1bc602dd7f9ed`.
- 집중 지속 증거: `/workspace/artifacts/v536-verification-managed/runs/86f6041e31dd4c8fb607624ee6fa6bff.zip`, SHA-256 `cae3b1efc1b5bb705fd0a7bb26de62591d00024200d35f498ee9dbac941f6783`.
- 최신 source `448f1605d48ccf1773527ffdbee6bdb2eaeb757a`, archive/SHA `b8eb752e9351ea14c3db22ba1f9ae8010cde885b1860d1c1e6da4a0d25286ac1`, 2372파일·147디렉터리, 51,367,724 bytes, manifest SHA `ef604b1ef1f8aa43241333f0ea0f6f58deaf480b22196707d0a24043f4952632`.
- 정상 롤백 source `7cbc199b1170d94a48d9b47f49bcf92aba00c8c6`, archive/SHA `e346972caa5f54e9d580792cc62dd74d1c4d63311e215cf1c1231b7bd6ce2207`, manifest SHA `cb3931fbf1897269db1477296ba3f2df94856f74c2665a61427f4ccd234eb0ec`.

전체 파일·디렉터리 mode/크기/SHA와 압축 복원을 대조한 뒤 최신/정상 롤백 두 세대를 원자 승격했다. 구버전 검증기는 copy/자식 전체 정의 그룹을 거절하므로 새 미확정 거래를 구버전에서 이어갈 수 있다고 보장하지 않는다. 이는 이전 source 검증기와의 대조이며 구버전 binary 실행은 새로 하지 않았다. 자동 역변환·구형 profile migration이나 override IO 변경은 추가하지 않는다.

집중/이번 최종 실행의 소유 임시물은 자식 종료·지속 증거 검증 뒤 정리했다. 중단 실행의 RAM root는 환경 복구 시 이미 없었으며 이를 cleanup 성공으로 세지 않는다. 승인된 최신/롤백 승격 외 기존 자료 삭제는 없었다. 최종 전 여유 1842.74MiB·정리/승격 후 1839.65MiB, 신규 단계 표본 최소 1842.68MiB·cgroup 메모리 표본 최고 3888.76MiB다. 표본은 모든 순간의 최소/최대를 보장하지 않는다. 지속144MiB(안전64MiB 포함)·RAM3GiB+512MiB·추가메모리7GiB+1GiB 예산은 낮추지 않았다. 단위 시작→최종 종료 디스크 순증가 6.37MiB에는 코드/Git·집중/최종/중단 메타데이터와 보관본 차이가 포함된다. 보고/게시 쓰기는 이후 별도 측정한다.

로컬 소유 copy·직접 자식/borrowed provider의 전체 갱신 흐름을 마감하고, 남은 M12는 기존 등록 외부 import/manifest/scope의 readonly 관측을 전체 거래와 최종 CAS에 결합하는 한 흐름이다. 비소유 부모/참조 쓰기나 독립 override 계약·구형 자동 migration은 잔여가 아니다. 등록된 ancestry/원본은 기존 receipt 경계를 유지하며 새 접근권한을 만들지 않는다. 이후 M4의 명시 async caller 오류 규칙과 실제 await→출력→완료→결과 분기→다음 실행, 고정 V2–V9/UI를 따른다. M11은 구체적 회귀가 없어 닫혀 있다.

후속 보고 문서 커밋은 동결 제품·검사 트리를 유지하고 work/current만 정상 게시한다. 원격 SHA·clean과 main 보존은 별도로 확인한다.
