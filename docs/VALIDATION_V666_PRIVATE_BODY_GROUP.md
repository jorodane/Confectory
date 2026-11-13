# Private C#·보조 함수와 일반 본문 공동 저장 검증

동결 runtime `50cfd5a09aa32dbe7eafed2bc0db5e9f1fc06574`의 [한 사용자 흐름](V666_PRIVATE_BODY_GROUP.md)을 최종 **신규 41단계·재사용0·실패0**으로 검증했다. 개발 검사는 최종 통과 수에 합산하지 않는다.

- LF/CRLF의 격리 checkout·seed restore·Release/MCP·빈 캐시 엔진과 기존 공통 검사를 새로 실행했다.
- 원래 단독 private/helper·일반 native 계획, 공동 후보의 순서 독립성, 오래된 source/flow·계약 및 helpers 경계 침범·잘못된 마지막 C# 거절을 검사했다.
- 기존 상세창·private C# 본문/보조 함수 편집·취소·Undo/Redo·미저장 cold·한 Save·기본/독립 창·장치 저장 실패/재시도·응답 유실과 조회 복원을 검사했다.
- 기존 version3 plan/read scope를 cold·정보/함수 표시 Save·후속 명시 text/helpers Save·늦은 설명과 두 번째 Save까지 유지했다. member/receipt/경로/읽기 범위 변조와 implicit frame/ABI 변경은 거절한다.
- Save 전 caller 원문과 Review 뒤 graph·선택 node·독립 source 경합이 전체 적용을 막고 원본/입력/checkpoint를 보존함을 확인했다. 정확한 원문 복원 후 새 Review/Confirm과 실제 프로그램40→20, 선택 helpers·graph/layout/locals bytes 및 독립 source bytes/mtime를 검사했다.
- 기존 retained/native 후보와 guards·등록 helper·retained 고급 ABI 및 단일 whole 전환을 별도 회귀로 포함했다. 새 package의 정상 UI, 전체 ZIP 추출/hash/구조·응답 유실·늦은 입력·독립 창·실패 수명을 검사했다.

제품 변경은 WholeBodies의 qualified private identity/노드 ABI 구분과 명시 helpers 후속 보존, element-functions의 직접 소유 private 소스 편집 연결, 해당 JS의 WebBundle canonical 크기/hash다. 원래 단독 Contracts/Graphs·C# 생성·SlotBatch·CreationOwners·Review/Confirm·최종 CAS 및 권한/레이아웃은 그대로다. 상위 일반 Blueprint native 계약이 공개 계약과 다른 경우 기존 단독 정규화를 암묵적으로 합치지 않고 거절한다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다. 새 문법/receipt version/권한·자동 source 변환은 없다.

개발 30회와 실패 7건의 로그/원인을 보존했다. 초기 fixture의 feature/contractHash 누락, 같은 후보의 parent 이름 정규화와 진단, private 편집 진입 누락, JS canonical descriptor 누락, 단일 소스가 직접 열리는 기존 동작에 대한 검사 가정을 구분했다. parent/public 계약이 정확히 같은 범위로 제한하고 원래 private 편집 연결 및 descriptor를 수정한 뒤 필요한 재검사를 수행했다. 최종 41단계는 전부 새로 실행했다.

직전 정상 package `c5dbf1cbcd7a5dcf7cd0bc70fbb3cc137a950e7c`를 전체 파일/hash 검증 후 별도 임시 위치에 추출했다. 그 reader에서 최종 fixture의 각 단독 계획과 실행40은 유효하지만 공동 후보는 거절됨을 새로 재현했다. 원래 package UI는 이미 확인된 소유 private C#를 편집창에 연결하지 않고 Blueprint 경로로 가서 거절되며 입력/원본을 보존함을 관찰했다. 직전 reader가 새 private pending receipt를 거절하는 것도 확인했다. 이는 개발 진단이며 최종 41에 재사용하지 않는다. 같은 세대의 authoring/runtime을 사용하며 자동 migration/downgrade를 하지 않는다. 기존 구 Reference parser 제약은 유지한다.

Linux 실제 엔진/portable 실행과 Chromium 자동화다. Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI 검증은 하지 않았다. 현재 canonical descriptor 실패는 위 개발 변경의 확정 원인이며, 과거 초기 빈 화면과 연결해 단정하지 않는다. 과거 초기 빈 화면 원인은 미확정이다. 변환 뒤 미등록 잔존 csbody는 새 관측 대상으로 주장하지 않고 byte 보존만 별도로 검사했다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 50cfd5a09aa32dbe7eafed2bc0db5e9f1fc06574 | 5a1206bcb39dda971ad9ce3a6be4aa091951abe7a60f8fe325825a910a09160c | 54129889 |
| rollback | c5dbf1cbcd7a5dcf7cd0bc70fbb3cc137a950e7c | 25507af5298d28f864459a0a24280bcd647271b9a05d0f96d871dcc38f95bc8f | 54129186 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/7f98c9c4132b4fda95772cea932b6f72.json` · evidence SHA256 `cb25b33387a4a43b481fb30ab97cecc33ae363b9561513841786d5c5b7fd0c3a`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/c0304ac611d34df7adb0afefaced626b.json` · evidence SHA256 `96178dd2ce7320e605e51dfc1446ac97964b7fb356e3a2a51d436a24892dcbb4`.
두 package와 두 실행 증거 SHA를 재확인했다. 기존 latest/직전 정상 rollback 교대와 이번 등록 소유 임시물만 정리했으며 원본 checkout·기존 보관·과거 증거를 보존했다. 디스크 여유 24470544384bytes(22.79GiB)다.

이번 private source-only 한 사용자 흐름을 닫는다. 남은 유한 갈래는 독립 root code 노드 자체 명시 계획과 실제 계약 변경 callee/import·등록 외부 관측 결합이다. 타입/문맥 조합을 새로운 의무로 늘리지 않는다. main은 사용자 검토/merge에 남긴다.
