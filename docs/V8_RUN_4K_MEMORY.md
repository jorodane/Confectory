# 명시4K 관측의 중간 문자열 메모리

현재 명시4K producer·원본15개 해상도·개인 preset 계약은 그대로 유지한다. 이 단위는
실제 관측에서 확인한 불필요한 할당을 줄인다. 새 해상도/ABI/저장 형식/권한을 추가하지 않는다.
기준 게시본은2262f904이며 제품 변경은 project-execution/Surface.csbody 하나다.

4096×2160 RGBA 35,389,440B를 읽으면서45개 base64url 조각을47,185,920문자로 합치고,
정규화·검증용 전체 문자열을 반복 생성하던 경로를 확인했다. 명시4K의 parts 경로만
고정 크기 raw 버퍼와 재사용하는 조각별 char 버퍼에 직접 디코딩한다. raw 버퍼는 모든
metadata·전체 SHA·소유/순서/크기/관측 제약이 통과한 뒤에만 기존 transfer에 게시한다.
실패 중간 버퍼가 기존 신뢰 revision을 덮어쓰지 않는다. 작은 단일 packet과0–3 profile은
기존 decoder를 사용한다. producer, 화면/레이아웃, 공개 계약, 기존 C# 원문은 바꾸지 않는다.

조각마다 URL alphabet, 정확한 길이와 decode 크기 및 마지막 sextet의 미사용 bit0을
검증한다. 따라서 같은 바이트로 풀리는 비정규 tail도 거절한다. 단순한 decoder의
허용 범위가 넓어지는 문제를 실제 native 두 조각/두 tail 나머지 경로로 검증한다.
기존 잘못된 alphabet·SHA·혼합 소유/크기·누락/초과 조각·누적 I/O 지연 거절도 유지한다.
인증 pipe의1,400,000B packet/25ms connect/누적300ms I/O, RPC2MiB는 그대로다.

개발 계측은 같은 독립 checkout/SDK/실제 pipe/고정 고엔트로피 입력의 정상1/12/14를
비교했다. 각 성공한 전체 native read의 GC.GetTotalAllocatedBytes(true) 차이이며,
진단 JSON 파싱 전에 측정한다. 프로세스의 동시 할당을 포함하고 peak/retained memory나
FPS 측정은 아니다. 계측 원문/SHA/실패 입력/로그는 지속 증거에 봉인하며 제품에는 없다.
이전 전체 cgroup11.17GiB peak는 컴파일러·RAM 임시물도 포함하므로 decoder 사용량으로
해석하지 않는다. 다음4K 사전 점검은 실측을 반영한 추가9GiB+안전1GiB를 요구한다.

기존 version1 preset 저장은 변하지 않는다. 구 QHD JavaScript reader는4K 항목을 담은
전체 목록을 거절하며 비우기·축소·자동 이행을 하지 않는다. 작은 목록은 그대로 호환한다.
이전 native 엔진을 새로 실행해 호환성을 증명한 것은 아니다. 최대4096/8,847,360px
밖의 원본8192 custom·GPU/물리 출력과 큰Office 편집/백업/초안 전송은 별도 잔여다.
초기 빈 #app/cold 및 일부 일시 관측 거절의 원인은 미확정이다. 실제 Windows/모바일,
전체 UI·GPU/모니터/물리오디오·Office 앱·Space/Library 전달 완료를 주장하지 않는다.

사전 계측 정상1/12/14 각3개 표본의 중앙값은988,323,112B →329,795,520B
(약942.5→314.5MiB, 66.63% 감소)다. 원래35,389,440B 픽셀과 전체 SHA는 동일하다.
최종 독립 검증·보관/공간 수치는 별도 검증 기록에 남긴다.
