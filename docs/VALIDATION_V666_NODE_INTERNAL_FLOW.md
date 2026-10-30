# M11 개별 C# 내부 흐름: 첫 지원 단위 검증

기준 ZIP과 의미·제한은 [지원 경계](BLUEPRINT_NODE_INTERNAL_FLOW.md)를 따른다. 공개 계약을 바꾸는 독립 복제나 자동 C# 역변환은 추가하지 않았다. 원본 카드의 기존 ‘직접 작성’과 모바일의 기존 내부 편집 진입을 사용한다. 새 헤더 버튼/레이아웃은 추가하지 않았다.

## 집중 검사

관리 실행: `/workspace/artifacts/v536-verification-managed/runs/248cf6d218f0411f9282bb6dfd07b21e.json`. 이 실행의 실패 로그도 보존한다. 임시 checkout/캐시/프로필/합성 프로젝트만 사용하며 기존 사용자 자료나 과거 산출물은 삭제하지 않는다.

- 실제 API: 읽기 전용 미리보기, CRLF 원문·helper 보존, 바깥 ID/핀/실행선 유지, 새 leaf 별도 소유, 누락/변조 증거·경로 충돌·구형 profile·whole-body/forwarded/ref/out/분기 문맥 거절.
- 하나의 author 후보·최종 checkpoint CAS, 원본 물리 경합 거절, 그룹 일부 Review 거절, cold 복원, 실제 C# 컴파일 오류와 수정 입력 보존, Review 뒤 원문 경합의 전체 미반영, 정상 컴파일 Confirm 및 전후 CLR 호출 결과.
- 실제 브라우저/엔진: 원본 진입·단일 코드 미리보기, 전환 및 C# 대화상자 취소, Undo/Redo, 편집 후 cold 취소/재실행, Root 왕복 Save, Review 취소와 명시 Confirm, 최종 cold.
- 쓰기 실패·충돌·응답 유실·늦은 입력·동일 namespace/ID의 다른 프로젝트 왕복을 별도 합성 fixture에서 검사했다. 미확정 응답은 receipt로 조회하고 중복 authorBatch를 적용하지 않는다.
- 최종 원본 버튼 연결은 `flow-ui-final-original-buttons`; 컴파일 오류·최종 CAS 수정은 `flow-api-final-cas`로 다시 검사한다. 앞선 집중 흐름 중 공통 저장 체계 검사는 재사용하며 최종 독립 checkout/패키지 검사는 아래 별도 기록한다.

수정한 실제 결함은 cold 창 메타데이터에서 전환 의도가 누락되던 문제와, 변경되지 않는 보존 원문이 최종 파일 CAS에서 빠지던 문제다. 후자는 Review/Confirm 검증 및 CommitPlan의 읽기 전용 checks로 닫았다. 도중의 fixture·고정 선언 영역 입력 방식 문제는 제품 결함과 구분하고 검사 기대를 유지했다.

<!-- final-verification -->
## 최종 독립 검증 및 지속 보관

- 실행 코드·검사 commit: `8269dd7270a2cd5754fd6d0131322f717077b4da`. 실행 소스 변경이 없는 문서 마감 커밋과 구분한다.
- 최종 실행: `/workspace/artifacts/v536-verification-managed/runs/2e54011e46bd4662b8f439f2b26d9704.json`. **107개 단계 전부 통과**(LF 45, CRLF 38, 패키지/복원/수명 관리 24). 기존 작업자 배지 단위의 99단계에 M11 일반 반환/void API, 원본 UI 및 새/복원 패키지 8단계를 더했다.
- LF/CRLF checkout은 Git 객체·엔진 캐시·NuGet 저장소·프로필이 각각 독립이다. 두 checkout의 source/tree 및 LF/CRLF 자산 정규화를 확인했다. 일반 반환과 void의 원문 보존·단일 실행·컴파일 오류·최종 CAS는 모두 새로 실행했다.
- 신규 Windows 교차 패키지와 ZIP 전체 파일 SHA/모드·압축 복원 후 M11 UI/실패 경로 및 기존 회귀를 새로 실행했다. 새 패키지를 사용했으며 이전 패키지 실행 결과로 대체하지 않았다.
- 집중 검사의 쓰기 실패/응답 유실/늦은 입력/프로젝트 왕복과 native 중첩·전체 C# 변환 13개, 상속 소유권 2개는 최종 production 파일 해시 일치 근거로 재사용한다. 최종 실행의 UI normal/loss/storage 검사와 구분한다. 관리 수명주기 구현 자체는 변경하지 않았다.
- 최종 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/2e54011e46bd4662b8f439f2b26d9704.zip`; SHA-256 `a3420b5de56f427ec06d7f1ee833acda304ebd851f0350e3db20ab1c6b700cc3`. 집중 증거 SHA-256 `cae06a613268583950fd5eb62022a7a5f90eda5c6b2930e21268654fa9ffe15b`. 초기 진단 실패 로그도 그대로 남겼다.

| 보관본 | 실행 코드 commit | ZIP SHA-256 | 크기 | manifest SHA-256 |
|---|---|---|---|---|
| 최신 | `8269dd7270a2cd5754fd6d0131322f717077b4da` | `6d5dc695a9f2982849e5a37ca75aeebec5e4c2baf48d31e12d149b74796d5766` | 51,242,377 bytes | `dff8ef0f926d79db5201cd7e2915bc72c8d63c98eab71d96a9d1ab067020ee27` |
| 정상 롤백 | `1d601ad8c3f3bc8fa9186231c67d417233985687` | `c1eb37755c56d8fb3313016a0002b7b3aa382b87a6d3ee0558e0023197d08c3a` | 51,233,552 bytes | `a6954b42da2f3fc724cb964470f21fa2c9d6c350d68a82e3fc408be25a0fd2b7` |

보관 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신 ZIP은 2510개 항목(2363 파일/147 디렉터리)의 전체 manifest로 확인했다. 롤백본은 직전 검증 정상본을 유지했으며 보존 ZIP SHA도 다시 확인했다. 과거 비관리 산출물은 삭제하지 않았다.

최종 실행 전 디스크 여유 2124.43 MiB, 정리 후 2109.51 MiB; 최종 실행 순증가 14.92 MiB. 관측 최소 여유 2123.22 MiB, cgroup 메모리 피크 4537.77 MiB. 집중/최종 실행의 소유 임시 root는 증거 보존 뒤 제거됐으며 RAM을 유일한 보관소로 쓰지 않았다. 이 수치는 해당 실행의 실측이며 이후 단위의 고정 증가량을 보장하지 않는다.

## 미완료 경계

M11 전체 완료가 아니다. 현재 직접 소유 Root 일반 next 지원을 넘어서는 이미 중첩된 graph 안의 C# 전환, whole-body 문맥, ref/out/실행 분기, copy/상속/참조 전환 및 별도 편집된 C#/graph 사이의 재활성화 정책은 원문을 보존한다. 구형 profile 자동 승격은 하지 않는다. 저장 전 전환 Undo와 저장 후 ownership barrier를 구별한다. 독립 슬롯 창의 새 전환은 지원을 주장하지 않는다. M11 모바일 viewport 진입은 이번 검사에서 실행하지 않았다.

B2 다른 사용자/그룹 권한 backend, 종류 C# 표현/사용 중 삭제 대응, M4/M12, 3D/권한 별도 팩 및 나머지 고정 수용 항목은 별도 잔여다. 실제 Windows apphost/WebView2·실제 모바일 기기·전체 UI·Library/Space 전달은 미실행이다. 이번 검사의 CLR 실행과 브라우저 자동화는 Linux에서 수행한다.
