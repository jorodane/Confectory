# v536 저장 copy의 Root 카드에서 복수 호출 갱신

기준 게시 `aa7fbc8`, 저장소 원본 `196c605`의 기존 호출 카드와 고정 7행 경계를 따른다. 이번 단위는 **단독 직접 배정·단일 target same-contract 저장 copy의 Root 호출 카드에서, 한 프로젝트 소유 callee의 여러 기존 ordinary wrapped use 갱신을 명시적으로 시작**하는 연결이다. 완료한 새 copy 초안·private 진입을 다시 구현하거나 호출/타입 조합을 새 요구로 늘리지 않는다.

## 연결과 보호

Root read도 기존 `BlueprintCallAbiUses`의 한 전체 후보를 관측한다. qualified Root key와 private key를 구분해 원래 대응창에 넘기고, 사용자가 선택한 Root 계획과 전체 계획이 같아야 저장한다. 보관된 copy 소유권·직접 배정·target·출처·현재 callee/graph/import/records hash와 전체 source closure를 그대로 확인한다.

Root 진입은 기존 copy의 atomic review group과 한 authorBatch/checkpoint CAS에 결합한다. 어떤 호출의 대응이 부적합해도 import·wrapper·앞선 호출만 적용하지 않는다. Root에서도 물리 원본 hash·링크 경계를 재확인하며 stale source/CP, 잘못된 owner/nonce/경로/target/출처와 혼합 입력은 전체 거절한다. 응답 유실은 기존 receipt 조회를 먼저 하고 미적용·기준 불변일 때만 사용자의 새 명시 대응을 허용한다.

독립 정보 창 어댑터는 관측된 Root graph와 copy implementation을 명시한 use-group 요청만 기존 서버 검증으로 전달한다. 새로운 파일 권한이나 외부 source authority는 부여하지 않는다. 공개 override 계약·copy 출처·원래 C# 본문·부모/외부 원본·기존 값/설명을 유지한다. 자동 C# 재작성·독립 계약 복제·새 UI/레이아웃은 없다. 74개 canonical UI 리소스/descriptor/HTML/CSS는 기준 게시와 byte 동일하다.

## 유한한 수용 표본

격리 fixture의 Root `native`, `frame/native`, `other/native`는 같은 local ID를 사용한다. 원래 `ref long amount -> long`을 현재 `int step, double renamed, out long total -> bool`에 명시 대응한다. Root/첫 frame의 직접 값3과 다른 frame의5, 기존 실행선·소비자와 정확한 int64 local을 보존한다. 공개 copy 계약은 바꾸지 않는다.

기본/독립 창에서 Root 직접 열기·대응 취소/불완전 값/cold 복원·Undo·저장·Review 취소/compiler Confirm을 확인한다. 마지막 호출의 잘못된 대응·누락/위조/다른 owner와 nonce, 실제 쓰기 실패·물리 source/CP 경합·응답 유실·Undo 후 명시 재시도는 기존 격리 검사로 검증한다. 저장 copy private 진입과 새 copy 초안은 영향 회귀로만 확인한다. 확정 결과는 후속 evidence에 기록하고 진단 실패는 통과 수에 포함하지 않는다.

## 공간과 실제 잔여

시작 여유874.6MiB에서 디스크200MiB·RAM 임시 출력768MiB의 순차 검사 예산을 확인했다. 기존 독립 checkout을 FF하고 새 clone을 만들지 않는다. 이번 검사 소유 임시 fixture/package만 증거 보관 후 승인된 수명관리로 정리한다. 기존 원본/SDK/보관 빌드/로그/프로필/사용자 자료는 삭제하지 않는다.

- 등록 callee/all-target source receipt 결합은 별도 실제 잔여다. 등록 단일 호출의 기존 지원과 정상 보호를 유지한다.
- 별도 frame 계약/본문 동시 변경과 opaque/whole-body 수동 C# closure는 기존 4/8행·A4–A6의 같은 항목으로 관리한다. 조합별 새 요구로 분해하지 않는다.
- 9행 고급 타입/표시명, I6/B2, M4/M11/M12와 신규 이미지·협의·렌더 backend는 별도 미완료다.
- 전체7행/I5/UI 완료, 실제 Windows apphost/WebView2·모바일 기기/터치 수용·Library 전달은 이번 검증 결과가 아니다. 새 RAM 교차 패키지는 전달 가능한 보관 빌드가 아니다.

## 확정 집중 검사

최종 제품의 실제 엔진/렌더러 10흐름 78확인과 순수 closure4확인이 통과했다. 기본/독립 창의 취소·cold·C# compiler Confirm, 누락/위조/마지막 비호환 대응의 전체 미적용, 쓰기 실패·물리 source/CP 충돌·응답 유실·Undo 후 새 대응 재시도 및 동일 local ID의 Root/private 문맥과 기존 입력 보존을 확인했다. 저장 private/새-copy 기존 지원은 영향 회귀로 지켰다. 독립 checkout/새 패키지는 별도 후속 evidence다.

## 독립 checkout·새 교차 패키지

소스 커밋 `8547632d38a01ed73235649d1feae7c2aed7903a`의 변경7개 Git blob과 기존 autocrlf/clean을 확인했다. Native/CLI Release·Linux 엔진 및 독립 UI2흐름20확인·closure 순수4확인이 통과했다. 새 RAM Windows x64 교차 패키지의 restore·Release·MCP·생성·probe·패키지 자체 독립 창 UI12확인까지 6단계가 통과했다. 전체 2348개/manifest 2347개 목록·SHA·Core/Native DLL 및 소스 바이트를 확인했다.

manifest SHA `b40e49a9d346f4bfb9a0aee25acbbf2f3f97aa430bee7ccd23362dd75a5e336a`, Native DLL `3f5dca59f515ea958c21c6ed36030a675fcb175af7c0ad51121f46ebe9242b5e`다. 전체 manifest·fixture/로그/프로필 증거를 보관한 후 이번 임시 패키지만 정리했다. 보관 패키지/SDK/원본/기존 자료는 그대로다. 다운로드 가능한 새 보관 패키지나 Library 전달이 아니며 실제 Windows apphost/WebView2·모바일 기기는 미검증이다. 후속 최종 커밋은 문서/evidence만 바뀌므로 실행 소스는 이 소스 커밋과 같다.

최종 제품의 통과 검사만 집계했다. UI리소스와 레이아웃은 기준 게시와 동일하며 미완료와 실제 기기 검증을 구별한다.
