# 소유 callee·opaque 호출자 공동 저장 검증

게시 `c460ce29a7a2e63dc72eaf71c6105a1b382f12ad`와 증거를 보존하고 runtime `dd9518b2dd4d1a894b2d45d0926e484c76556b0b`를 새 실행21·재사용22·실패0(총43)으로 검증했다. 제품 source는 최초 고정 `af90e7addee961226a7999f214d83daf02eceb46`와 동일하다. 독립 LF21(새6+재사용15)·CRLF13(새6+재사용7), 새 package와 전체 ZIP 복원9다. clone·restore·Release·MCP·engine 및 package/전체 복원은 모두 새로 실행했다. 개발 실행과 아래 실패 진단은 이 최종43건과 구분한다. 첫 시도는 LF/CRLF34와 package 생성 명령의35건 모두 통과한 뒤 대기 출력 연결 단절에 따른 Broken pipe로 관리자가 종료됐다. 보관된 같은 소스·테스트·SDK/NuGet·명령·독립 LF/CRLF의 source 검사22건만 재사용했다. 이전 package 생성물이나 빌드 결과는 재사용하지 않았다. 최초 record `/workspace/artifacts/v536-verification-managed/runs/748c413ab2af498189f259bf1cc4628a.json`, evidence SHA `c8ee54b23baa6efd74c41e907a3b21322b0cdae027de69c30db21b3debb772c8`를 유지한다. 재사용 거절/새 빌드 위임 검사1건은 별도 record `/workspace/artifacts/v536-verification-managed/runs/50846094ec004e84b2c6641675d3cc10.json`, SHA `402a9db154ffc8d5092ec4fda1c3d6b39f81ae5866c4ed1f57dff0b24327973d`에 보관했다. 복구 실행은 분리된 파일 stdout/stderr로 대기 세션 수명에 의존하지 않는다.

고정 7/8행의 실제 사용자 흐름을 대조해, 반복적인 private primitive 조합 대신 정보 창의 callee 계약·본문과 소유 root opaque C# 호출자 본문 및 다른 native 함수 본문의 한 Save를 우선했다. 온전한 직전 패키지는 원래76을 실행하고 두 개별 계획을 수용했지만 공동 후보를 거절했다. 기존 UI도 whole-caller 때문에 callee 역할 입력을 보호해 이 흐름을 작성할 수 없었다.

사용자가 callee의 둘째 long 값 인자를 out으로 바꾸고 직접 할당하는 본문, 호출자의 calls.Selected.Invoke(left,out assigned) 본문, peer 본문을 직접 작성했다. 일반 호출선의 원래 count 입력 해제와 return 유지도 명시했다. 한 후보·Save/cold·Review/Confirm 뒤45를 실행했다. opaque caller의 공개/native/frame 계약과 left/right·Selected·원래 arg0/arg1 import 철자, 독립 계산·exact64 local·실행선·배치·선택 밖 C#과 원래 csbody bytes/mtime를 보존했다. 앱이 out 저장소·본문·cast·연결을 자동 작성하지 않았다.

실제 Linux engine/Chromium에서 원래 소스 선택창, native 역할/본문과 보호된 caller 헤더, Cancel·재진입·Undo/Redo, 기본/독립 창·프로젝트 경계·실패 재시도·응답 유실을 확인했다. 늦은 설명 입력은 지연된 Save 응답 뒤에도 남고 cold 복원·두 번째 명시 Save·Review 취소·새 Confirm을 통과했다. LF 후속 저장과 trusted UI 경합은 첫 시도의 같은 source 증거를 재사용했고 전체 ZIP 복원 뒤 늦은 입력은 새로 실행했다. UI가 편집한 내부 줄 LF와 바꾸지 않은 마지막 CRLF를 보존한 사실은 직접 API가 명시한 CRLF 원문과 구분한다. 모의 DOM의 보호 영역·draft 복원 검사는 실제 컴파일/기기 검증과 구분한다. 화면 검토 SHA `8e8d6b8a8f7cd37d2aac662599738d400b5cc043a34102a06b2c3bab84e38d3c`.

API는 누락·stale source/context·foreign/copy·헤더/반환/helper 변조·잘못된 호출선 해제/출력 대응·미할당 out·수정하지 않은 호출자·마지막 peer 컴파일 오류를 전체 거절했다. metadata-only peer는 정상 수용해 선택하지 않은 C#을 유지한다. 영수증의 원본 계획·멤버·읽기·owner·source/proof 변조도 거절했다. Review 뒤 graph·caller header·caller C# record·callee body·독립 retained source의 다섯 경합은 Confirm을 차단하고 checkpoint/peer/input을 유지했다. 정확한 복원 뒤 새 Review/Confirm과45 실행이 통과했다. trusted UI 경합 클릭도 별도로 확인했다.

후속 본문 Save에서 현재 whole receipt를 확인하면서 최초 before 계약·source/graph 해시·물리 읽기 버전을 유지한다. 이를 위해 callee의 편집 행에 있는 외부 caller를 실제 implementation Function/import로 식별했다. 정보/function 설명의 후속 Save도 기존 계획과 읽기 scope를 유지했다. 최초 저장과 최종 CAS의 보호는 완화하지 않았다.

제품 변경은 WholeBodies·feature-authoring.js·WebBundle의3파일이다. 복구 추가 변경은 엄격 재사용 helper·거절 검사·driver 연결뿐이며 제품과 통과한 source 검사 bytes·기존 경로·예산은 그대로다. 나머지 추적 제품 source3118개와 번들의 다른 행은 baseline bytes와 같다. workspace1·receipt3/nativeBodyContexts를 확인했고 schema/profile/receipt 필드·권한을 추가하지 않았다. 기존 단일-source typed import·소유권·compiler 검사, Review/Confirm·최종 CAS, 정의별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다.

개발 31건 중 정상 종료 23건이다. 실패8건과 원본 로그·checkpoint를 보존했다. 두 baseline fixture의 metadata kind/비동기 picker 기대, 강화한 검사의 위치 인자 철자 및 metadata-only peer 기대를 교정했다. 실제 제품 결함인 foreign caller의 후속 whole 판별은 수정했다. 그 뒤 현재 본문 요청에 과거 호출선 해시를 복사한 API fixture와, 기존 마지막 CRLF 보존을 전체 LF로 기대한 UI fixture를 교정했다. 뒤 두 항목은 source/읽기 보호를 풀어 해결하지 않았다. forwarding 회귀의 잘못 지정한 파일명은 fixture/engine 실행 전 exit2였고 기존 --check=native 진입으로 바로잡았다. 준비 단계의 두 driver 선택 assertion은 파일 반영·빌드 전에 멈춘 진단으로 별도 보관했다.

직전 온전한 runtime `0ef25fdd139a5e2a39b19e742aa78f85ef48cc68`의 archive와 전체 추출 파일/directory/hash/mode를 확인했다. 현재 guard는 새 pending을 수용하고 직전 guard는 거절했다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 직전 CLI/providers로 새 build·45 실행을 확인했다. 검사용 복사본의 build provider 경로만 직전 온전한 패키지로 명시했으며, 실제 원본 manifest와 패키지는 수정하지 않았다. 원본 source inode/hash/mode/mtime와 직전 package는 유지했다. 일반 Reference reader migration이나 downgrade 수용을 주장하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | dd9518b2dd4d1a894b2d45d0926e484c76556b0b | 435c7d1f7f6345e47b24e852697d4dd639ff353a2de0a7eb6647df4e2f471097 | 54164516 |
| rollback | 0ef25fdd139a5e2a39b19e742aa78f85ef48cc68 | 4e9b666ebfa7f5b6191c694271849e2ddb0a793cdfc50a7e26e7bb5c9a662cb5 | 54164968 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/208d2f892c354d3a84498ac758a73ac4.json`, evidence SHA `5ad756b7bf02e74a33ee36414c1918da20002629f5787bc15fc12cbf92186fb8`. 개발 record `/workspace/artifacts/v536-verification-managed/runs/d1ebee37b67c4ccbb6472bfe9af0e8bd.json`, evidence SHA `be10f86db3aada8a7672a1409f9b6072f5200669e43c7dc0f69773f9a89a9073`. 두 package와 개발·첫 시도·복구 guard·최종 evidence 네 개의 hash를 확인했다. 기존 원본 checkout, 미인증 IPC 보관본과 과거 증거를 보존했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 23616749568bytes.

다음 우선순위는 여러 변경 계약이 같은 retained 호출자 소스를 공유하는 명시 일치 계획, 소비되는 private 반환의 명시 대응, copy/registered/forwarded 원본 관측 closure다. 이번 값→out 표본 밖 역할·고급 타입·다중 caller/target 조합을 전부 검증했다고 보지 않는다. 구 reader migration, 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. 초기 빈 화면과 과거 시간 초과·전송 오류 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
