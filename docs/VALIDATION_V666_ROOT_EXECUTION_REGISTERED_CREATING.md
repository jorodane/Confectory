# 등록 외부 함수 새 copy의 첫 저장

## 지원 범위

원본 `dist/blueprint.js:969–976`의 readonly 정의에서 기존 반환 배치와 `dist/app.js:2469–2476`의 원계약 우선 구현을 새 등록 외부 함수 copy에 연결한다. 직접 소유 schema·명시 donor/target·기존 execution-exit switch Root, 동기 void·값 입력·선택적인 int out 하나의 범위다. 새 기능/계약 ID를 생성하지 않으며 로컬 implementation copy 생성과 배정만 기존 거래로 처리한다. 외부 함수·donor·C#·핀/ID/연결·권한·원본 레이아웃을 보존한다.

첫 관측 origin과 해시를 owner의 첫 Save 영수증에 묶고, 미확정 copy의 반복 author Save에서도 원래 owner·관측과 새 본문 receipt를 구분한다. 현재 프로젝트/owner 등록을 확인한 뒤 기존 copy registry 경로로 관측을 다시 도출한다. saved 경로는 임의 파일 읽기에 쓰지 않으며 readonly 외부 원시 관측을 최종 typed CAS에 결합한다. Confirm 뒤에는 완료된 생성 origin으로 donor에 새 의존성을 만들지 않는다.

## 동결 소스와 신규/재사용 검증

제품 동결은 `9df807847f259e77e1788a2a2cfa6346cdd4e66b`다. 이후에는 결과 문서·수용 표만 수정한다. 독립 no-hardlinks LF/CRLF checkout·별도 home/NuGet·빈 엔진 캐시의 검증 범위는 **LF 19·CRLF 16·새 교차 패키지/전체 복원/실패 수명관리 6, 총 41단계**다. 재개 실행에서 신규 33단계(LF11·CRLF16·패키지6)가 통과했고, 동일 제품의 첫 시도에서 이미 통과한 LF8개 검증은 명시적 동등 근거로 재사용했다. 재개 실행의 실패는 없다.

- native 38개+소유 경계 2개씩, 총80개를 이번 동결 제품에서 실행했다. LF40개는 동일 제품의 첫 시도, CRLF40개는 재개 실행이다. 이전 출시본의 Core/test 파일만 같다는 이유로 간접 호출을 재사용한 것이 아니다. 이 실행들은 위 검증 범위에 포함된다.
- 양쪽 API는 첫 미리보기/Save·생성/등록/배정/반환·cold 재조회·미확정 copy 반복 본문 Save, 부분 Review·외부 계약/등록 변경·원문 경합·origin/관측 해시 누락/변조·경로 위조를 확인했다. 외부 함수는 writable source가 아니며 raw 관측이 최종 typed CAS에 결합되는 것을 확인했다. LF는 out 없는 함수, 기존 소유 함수 새 copy와 저장 외부 copy 회귀도 새로 실행했다.
- 화면은 동등 근거 LF normal/project와 신규 CRLF loss/독립 창 late다. 새 패키지 normal과 전체 복원본 독립 창 late도 새로 확인했다. 실제 사용자 클릭·선택·Undo/Redo·취소·Review/Confirm·재시작과 실제 out→결과 분기→다음 줄 실행을 포함한다.
- 집중 26단계의 원본 증거를 보존했다. 집중 UI는 lifecycle guard 1행 추가 전 generation이며 원래 guard 소스·metadata DLL SHA와 정확한 diff를 보존했다. 변경은 활성 그룹 없이 원문=초안인 완료 Root만 건너뛰는 것으로, 미생성/미확정 취소·쓰기 실패·경합 경로에 영향이 없음을 대조해 이 근거를 재사용한다. 정상/프로젝트/유실/late는 최종 독립 UI로 다시 확인했고, Confirm 직후 Save와 donor 변경은 마지막 API에서 새 검증했다. 개발 중 진단 실패 4개(`release, creating-final-api, creating-post-confirm-diagnostic, creating-post-confirm-check`)는 최종 통과 수에 섞지 않는다. 지역변수 충돌·해시 혼용·완료 receipt 수명 문제를 수정했다. UI와 잠시 겹친 추가 진단은 소유 worker identity로 중단한 뒤 순차 재실행했고, 모든 원본 로그·완료 행과 복구 근거를 보존했다. 보강 전 통과 API는 최종 제품 근거와 구별했다.
- 첫 최종 시도의 LF no-out API는 실제로 `failure → after`를 실행했으나 fixture가 out 있는 경우의 `after:10`을 기대해 실패했다. 기대값의 out 여부 분기 한 줄만 수정했고 제품·harness·다른 검사 bytes는 바꾸지 않았다. 전체 Git 차이·SDK/NuGet·harness SHA·정규화한 동일 검사 명령을 대조해 LF8개 검증만 재사용했다. bootstrap은 이전 소유 공간이 정리돼 다시 준비했으며 실패한 no-out과 미실행 나머지는 모두 실행했다. 원본 증거 `/workspace/artifacts/v536-verification-managed/runs/7a56704edf424a02ae99023e01cf3f9d.zip`(SHA256 `00b645891d75ebf762ab7ef3ca5a1f1cb23f2676a5f7af8ec80a5aaa2e3261d9`), 새 증거의 `reuse-proof.json`과 `harness/resume_final.py`에 근거를 보존했다. 재사용 단계는 `lf-creating-api, lf-creating-native, lf-creating-ownership, lf-creating-script, lf-creating-ui-normal, lf-creating-ui-project, lf-v536_local_header_image, lf-v536_mixed_declaration`다.
- 실제 production Review/Confirm/CommitPlan의 local/external 최종 경합 4개와 기존 copy 읽기 CAS 4개도 양쪽에서 새 실행했다. 현재 의미/등록/소유 영수증은 별도 실제 API로 검증한다.
- 새 패키지·probe·전체 SHA/CRC·파일/디렉터리 모드 복원·복원본 hosted UI·실패 수명관리를 새 검증했다. 실제 Windows apphost/WebView2나 모바일 실행은 아니다.

## 지속 보관과 공간

| 구분 | source commit | archive SHA256 | manifest SHA256 | bytes / 파일 / 디렉터리 |
|---|---|---|---|---|
| 최신 | `9df807847f259e77e1788a2a2cfa6346cdd4e66b` | `130fdd42a44c1834b007d1adac1cdf908a3907b01a53c27edf2fdca38f988d53` | `47674b9919454f0341f891fd594405f8cf63e817e803a4e54db1240660ff44e5` | 51335454 / 2370 / 147 |
| 정상 롤백 | `8a208174064c56b63e6bfec6caa03e66c97acd1d` | `6a7e165835443b07201954ac62d270cf624651405699dfab28646ee463305360` | `33f4e87b84e50c95014800f700dc75d7003b4e494c62dec11185f0b18964f14f` | 51332130 / 2369 / 147 |

index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신의 전체 복원/실행은 새 검증이며 롤백 실행은 이전 정상 근거를 재사용하고 압축 SHA를 다시 확인했다. 최종 증거 `/workspace/artifacts/v536-verification-managed/runs/e7e32c89bbb3414c9021858b158f5421.zip`(SHA256 `0baa3a0b8d58dd67de542a92a593557da98d9020aec9b44a57968ebd73e581dc`), 집중 증거 `/workspace/artifacts/v536-verification-managed/runs/e2a348cc7c4648c6a1e7fd56325fa143.zip`(SHA256 `0b1860fa42835941660a49b3e3ebf85f79c3e035d65a70b78d5d9dc3cead62e8`)를 지속 보존했다. child 종료·보관 무결성·소유권 확인 뒤 이번 집중·첫 최종 시도·재개 실행의 세 RAM 공간만 정리했다. 기존 승인된 최신/롤백 승격·관리 세대 교체 외에 과거 자료/SDK/캐시/로그/프로필/사용자 데이터 삭제는 없다.

집중 디스크 1924.88→1922.83MiB(순증가 2.05MiB), 최종 1921.43→1918.86MiB(순증가 2.57MiB), 수집 시 여유 1918.86MiB다. 첫 시도 디스크는 1922.56→1921.48MiB(순증가 1.07MiB)이며 fixture 실패 증거 보관 뒤 해당 공간도 정리했다. stage 표본 최소 여유 1921.39MiB, 관측 cgroup memory peak 4082.83MiB다. 기존 추가 persistent144MiB(안전64MiB 포함), RAM3GiB+512MiB, memory7GiB+1GiB 기준을 낮추지 않았다. 다음 실행의 순증가를 보장하는 값이 아니다.

## 실제 잔여와 호환성

M12의 다른 데이터 ABI와 복합 호출 closure 및 M4는 [ABI/비동기 경계](M12_DATA_ABI_AND_M4_BOUNDARIES.md)에 분리한다. 타입·역할·중첩 조합의 곱을 새 필수 목록으로 만들지 않는다. M11은 구체적인 회귀가 없는 한 완료 상태다. 공개 override 원계약 변경·부모/참조 원본 쓰기는 정상 보호이며 독립 새 계약 복제와 legacy 자동 승격은 요구하지 않는다.

이전 미확정 외부 public-copy checkpoint에 origin/최초 관측 해시가 없으면 자동 보충하지 않고 보존·거절한다. 기존 소유 함수 copy와 저장된 외부 copy 지원은 별도 회귀로 유지한다. 실제 Windows/WebView2·모바일 실행, 전체 UI나 Space/Library 전달은 이번 교차 패키지/hosted UI 검증에 포함되지 않는다.
