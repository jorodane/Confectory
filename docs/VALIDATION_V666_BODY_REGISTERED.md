# 등록 외부 helper와 소유 C# 본문 공동 저장 검증

동결 runtime `34074819eb78e7fd62a99466eafe0cbe7d437a11`의 [한 원본 사용자 흐름](V666_BODY_REGISTERED.md)을 최종 **신규 41단계·재사용0·실패0**으로 검증했다. 개발 검사를 합산하지 않는다.

- 게시 `5f4cca78525dc3e5389d9e14cb555564dcebc508`에서 같은 등록 helper와 부모 계약을 사용하는 두 소유 native 본문은 각각 유효하고 원래 실행은46이지만 공동 후보와 원래 UI Save만 거절하는 것을 재현했다. checkpoint·두 입력·소유/외부 원문·권한을 보존했다.
- 새 등록 없이 기존 직접 등록 조회/receipt와 읽기 전용 계약 사전을 재사용해 두 명시 본문을 한 후보/CAS에 결합했다. 원래 public/native 계약·별칭·필드/핀·shared caller·미선택 C#·외부 provider/부모를 보존했다. 행 역순에도 source/hash/후보가 같다. 실제 Linux 프로그램은 선택한 뺄셈 본문으로26을 반환한다.
- 잘못된 마지막 C# 본문, 누락/변조된 기존 등록 receipt·계약·caller hash·native body hash와 이 단위 밖 public 이름 변경을 거절했다. saved proof/읽기 목록·부모·hash·경로·소유자·외부 write member 변조도 입력 보존 거절이었다. 원래 선언에 완전한 동일 proof가 남은 상태에서 중복 보관 필드만 없는 경우는 동일 읽기 hash로 검증하며 새 원본을 수락하지 않는다.
- Save 전 외부 함수·부모·등록 manifest의 변경을 전체 거절했다. 정상 Save 후 cold와 연속 정보 설명/함수 설명 Save는 원래 등록 proof/read set을 유지했다. metadata 후속 Save도 변경된 부모를 새 기준으로 수락하지 않았다.
- 각각의 새 Review 뒤 외부 함수·부모·등록 manifest를 변경한 세 경우는 최종 Confirm 전체 거절이었다. peer bytes·권한·checkpoint와 두 소유 본문을 보존했다. 정확한 원문 복원과 cold 뒤 새 명시 Review/Confirm은 통과했고 후속 설명과 실행26을 확인했다.
- 실제 원래 UI의 정상/독립 창·취소·Undo/Redo·미저장/cold·checkpoint 쓰기 실패/재시도·저장/조회 응답 유실·반복·다른 창 경합·A/B/A 프로젝트 전환을 검사했다. 지연된 성공 Save 응답 중 입력한 늦은 설명은 보존됐고 cold 뒤 후속 명시 Save·Review 취소/새 Confirm에서도 정확한 원래 외부 proof/read set이 같았다.
- 기존 local import 순수 후보와 project 문맥을 요구하지 않던 local-only guard, native 계약·새 소유 자식 공동 저장·단일 whole-body ABI 저장을 새 회귀 검사했다. LF/CRLF 독립 no-hardlinks checkout·격리 HOME/NuGet 새 restore·Release/MCP·빈 cache 엔진을 사용했다. 새 Windows 교차 package·구조/무결성·packaged UI와 ZIP 전체 추출본의 응답 유실/늦은 설명/독립 창·실패/반복 정리 수명을 새로 검사했다.

개발 managed record는 22번 시도 중 검사 fixture 실패 2회이며 모두 보관했다. 첫 실패는 중복 보관 필드만 삭제해도 원래 선언에 완전한 동일 proof가 남아 있는 안전한 경우를 거절해야 한다고 잘못 기대한 것이다. 둘째는 등록 외부 helper로 바꾸면서 등록에서 제거한 옛 로컬 helper 파일을 읽기 집합에서 삭제하려던 KeyError다. 실제 관측된 caller 헤더를 대상으로 고쳤다. 제품 결함에 의한 최종 Confirm/물리 쓰기 성공 증거가 아니며 실패 로그·요청·수정 전후 검사 hash와 source 증거를 구분했다. 최종 41단계는 동결한 최종 코드/검사에서 모두 새로 실행했다.

첫 최종 실행 `07af53941b6cf7093dde472cdc9e8bfbf3bc01ac`은 20단계 중 19개를 통과한 뒤 기존 단일 whole-body의 cold Review에서 멈췄다. 직전 정상 보관 runtime `7dbe6d3f`의 독립 추출본에서도 같은 실패를 재현했다. 직접 metadata 검사에서는 원래 타입 guard가 전체 proof/read를 유효하게 검사했지만, 일반 본문 guard가 공통 readGuards만 보고 graph node/caller 그룹을 잘못 주장했다. 정확한 단일 소유 typed graph receipt만 원래 타입 guard에 남기는 분류로 고쳤다. 일반 본문 계획/캡처 필드가 있는 등록형 두 함수는 이 분리로 우회하지 않는다. 진단 record는8단계 중 기존 패키지 재현 실패1개와 새 빌드·수정 후 whole-body/native/변조 검사 통과7개다. 수정 후 cold Review/Confirm과 실제 실행30→31, 원래 .csbody 보존, Review 뒤 node 원문 공백 변경 거절을 확인했다. 첫 실행/진단은 최종 신규 41에 합산하거나 재사용하지 않았다. 수정 뒤 최종41단계를 모두 다시 수행했다.

제품 변경은 BodyBatch의 기존 등록 proof 연결, Dependencies의 원래 관측 getter, BodyDependencies의 정확한 기존 proof/read 재검증, BodyGuards 및 ApplySlots의 저장/후속 보관·240 전체 source/read 한도다. 외부 선언은 write units가 아니며 원래 조회는 provider 본문을 새로 읽지 않는다. local-only/단일 typed receipt는 기존 경로를 유지한다. InformationFunctionContracts·원래 등록 조회·SlotBatch/CreationOwners·기존 Review/Confirm/최종 registered lease·C# 생성·authored UI·권한은 byte 동일하다. 기존 version3 receipt의 선택적 `nativeBodyDependencies`/`nativeBodyDependencyReads`를 사용하며 자동 receipt migration은 없다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류·공개 override 계약도 유지한다.

같은 게시 세대의 authoring/runtime을 사용한다. 새 등록형 미확정 receipt의 읽기 증명을 이전 실행기가 검증한다고 보장하지 않는다. 구 Reference reader 제약의 기존 바이너리 증거는 해시 재확인만 했고 신규 41단계에 포함하지 않는다. 자동 downgrade/migration과 외부 provider 본문 감시 확장은 없다. 실제 Linux 엔진·Chromium 자동화와 Windows/WebView2·물리 기기·OS IME·GPU/audio·전체 UI 전수를 구분하며 초기 빈 화면 원인은 미확정이다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 34074819eb78e7fd62a99466eafe0cbe7d437a11 | 3f7b6b74a63b551a3ef9b2d0a1e537e5b3607242cb002d57b343b0591fffdd0c | 54118247 |
| rollback | 7dbe6d3fdaef1a891bae0c2c1c864bd391355549 | 53bbf0d5fb9f4425e15537b67732b1188f5e1ca5a07fd7945564aed1037e3936 | 54112778 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/f962bc380985411da54b290aa240dcc0.json` · evidence SHA256 `8a887dd4f75cc26f40667c241a9e77a521cca238c6156378af2ccc2b5d59fbf4`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/a365cb57b917432881abe26e452c639c.json` · evidence SHA256 `954dc604b007e4989bfb54ad5e0eacdbeabbbce3acc63ec229209cf2c150e016`.
첫 최종 record `/workspace/artifacts/v536-verification-managed/runs/480eeef074c54293a16778fbec1a0ca7.json` · evidence SHA256 `2dde00fc7041e5bdf15980e948963e0334bbbe955327ee49fb1955fb2fbe2d88`.
단일 타입 guard 진단 record `/workspace/artifacts/v536-verification-managed/runs/d41191fc9eff45fcad9e18a002adb8fd.json` · evidence SHA256 `8e192c8f468435468e73ec7edb2293adef77f0727cc20b44af4b2c04e54f7849`.
두 package와 네 실행 증거 SHA를 재확인했다. 기존 latest/직전 정상 rollback 교대와 이번 등록 소유 임시물 정리만 수행하며 원본 checkout·과거 증거·비관리 자료를 보존한다. 디스크 여유 24524652544bytes(22.84GiB)다.

계약 불변 등록 helper 본문 공동 저장의 위 한 사용자 흐름을 닫는다. 남은 고정 갈래는 opaque/private 명시 계획과 실제 계약 변경 callee/import closure다. 가능한 타입·문맥 조합을 새 의무로 늘리지 않는다. M11/M12/M4는 회귀 없이 다시 열지 않고 main은 사용자 검토/merge에 남긴다.
