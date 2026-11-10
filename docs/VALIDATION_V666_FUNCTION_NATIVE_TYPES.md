# v666 함수 native 타입 선택·보호 초안 검증

검증한 runtime source는 `3990e5dfb96fe85a753f19e846b6f93b4fd4d0e9`다. [지원 범위](V666_FUNCTION_NATIVE_TYPES.md)는 직접
소유 정보의 새 함수 첫 계약에서 struct/enum/interface·입력/out/반환/배열을 선택하는 흐름이다.
원본 460px 카드와 420px 상세창, 기본형 카드 12영역의 치수·배치·폰트를 유지했다.
기존 프로젝트 C# 본문 bytes·정의 ID·권한·원자 Save·Review/Confirm·최종 CAS를 보존했다.

최종 **신규41단계, 결과 재사용0**이 모두 통과했다. 개발 검증과 첫 최종 시도의 통과 결과를
새 최종 통과 수에 합산하지 않았다. LF14, CRLF17, IPC1, 새 패키지/전체 복원9 단계다.
검증 환경은 Linux .NET 10.0.401과 공유 Chromium이며 실제 Windows/모바일 기기 실행이 아니다.

- 타입 목록: 지원하는 정보·종류·모듈, 이미 선언된 외부 dependency, 등록만 된 namespace의 미노출.
- 생성: 입력/out/반환과 module 배열, 표시 이름, 검색, 비활성 타입, 취소·Undo/Redo·cold 복원.
- 저장: 선택 후 정의 변경, 누락/변조/과잉 proof, storage 실패, 반복 Save, 응답 유실 및 receipt-only 복구, 늦은 입력과 후속 Save.
- Review/Confirm: 소유·등록/정의 읽기 증거, 복원·재시도, Review 후 소유/프로젝트 밖 등록 원본 변경, 불완전 receipt 거절.
- 초안 호환: 일반 v1 유지, 보호 v2 cold 복원, 위장 v1/알 수 없는 profile 거절과 원본 checkpoint bytes 보존, 새 입력만 취소하고 저장된 생성 그룹 보존.
- 회귀: 기본형 함수 편집과 원본 geometry, 같은 계약 nominal 본문 storage, 실제 generated module/struct/enum C# dispatch(result37), 기존 편집 IPC/패키지 실패 수명 관리.

구 reader의 실제 바이너리는 실행하지 않았다. 보관한 `3896252e:Restore.csbody`의 엄격한
`version != 1` 거절과 새 reader의 실제 복원/거절을 구분했다. 새 v2 보호 초안은 이전 reader에서
복구할 수 없다. 이전 parser/compiler가 generated nominal 타입이나 v2 enum을 읽지 못하는
제한도 유지하며 자동 migration/C# 재작성은 없다.

## 보관한 실패와 수정

첫 개발은25단계 중5실패를 보존했다. 기존 Rules와 겹친 fixture, 초안만 비교하던 source proof,
최종 receipt에 읽기를 보존하지 못한 초기 구현, 컴파일 오타, cold의 미로딩 draft overlay가
각각 확인·수정됐다. 마지막 API/기본·별도 창 검사는 수정된 제품으로 통과했다.
첫 최종14단계 중 기본형 fixture1개가 실패했다. 이미 편집 가능한 반환 이름을 out으로 잘못 고르던
선택자를 `data-signature-id != return` 역할 기준으로 수정했다. 해당 primitive 동작은 제품에서 바꾸지 않았다.
호환 보강 개발14단계의3실패도 보존했다: 예상 오류 문구, v1만 받던 browser-draft consumer,
취소가 저장된 생성 함수를 제거할 것이라는 fixture의 잘못된 가정이다. 실제 저장 계약대로
새 설명만 취소하고 기존 저장 그룹을 보존하도록 검사했으며 최종 코드에서 모두 새로 검증했다.

| 기록 | SHA256 |
|---|---|
| 최종41단계 | `cf6f5bb087d0f59f7f6df66f337c2506a7ad98e33c19cd199ba0c7db8fadfec6` |
| 타입 선택 개발25단계 | `3c6ef8fa8bb3f709603f4f454466bdc61cb0bc61130244791dbafef21c58ceea` |
| 첫 최종14단계 | `a20a3c9617043789584c85239b52da71ed94d7c8681133cab8680c90452b61fd` |
| 호환 보강 개발14단계 | `d8e1258bd6d130928887c7993d35587545db17aea2ff27b53fd007d083a99982` |

최종 기록: `/workspace/artifacts/v536-verification-managed/runs/15733b230a574f54ba276560b2bb3fe8.json`. Evidence ZIP 3,132,426B의 전 파일 해시와
manifest를 재검사했다. 각 owned RAM workspace는 증거 보관 뒤 정상 정리됐다.

## 패키지와 공간

| 세대 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 3990e5dfb96fe85a753f19e846b6f93b4fd4d0e9 | 7a79f5978ba0284e94c401a8f253959d49d6d4e158cb12ee80fc34e867ca078a | 53,966,845 |
| rollback | 24d9493dc6924d866dcc42c217dc71c89b402595 | 7308bbf4fab52a4d719480523e1321b74d4694448f07a3e3a0c226a10e73eacb | 53,959,822 |

새 package 생성·구조/무결성 probe·패키지의 실제 Linux engine UI·전체 압축 복원·복원본의
API/호환/UI/storage/응답 유실·실패 수명 관리를 새로 확인한 뒤 승격했다. 이전 latest를 rollback으로
유지했고 기존 rollback ZIP 한 세대만 승인된 managed rotation으로 교체했다. 과거 evidence는 유지했다.
SDK/seed와 알려진 관리 archive에 대한 읽기 FD cache advice만 사용했으며 전역 cache는 건드리지 않았다.
9GiB 추가 메모리·1GiB 여유, RAM4GiB·512MiB 여유, evidence512MiB·디스크64MiB 여유 기준은 같다.
공간은 25,631,666,176B에서 25,617,383,424B(약 23.86GiB), 관측 cgroup peak는 8,805,347,328B다.

## 유한 잔여

기존 연결 함수의 고급 nominal 계약 변환 UI, 살아 있는 reference 접근/수명,
module의 async/공개 실행 계약 및 기존9행의 multiple/함수 필드·고급 Blueprint 대응은 미완료다.
모듈 고급 계약은 이미 있는 Task/실행 결과 ABI와 계약 DLL 의존성에 연결해야 하며 기본형으로
묵시 치환하지 않는다. M11/M12/M4 완료 범위를 다시 열거나 선택적 조합을 필수로 늘리지 않았다.
초기 빈 화면 원인은 미확정이며 전체 UI/실제 기기 수용 완료를 주장하지 않는다.
