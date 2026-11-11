# 정보 함수 필드 검증 준비

[지원 범위](V666_FUNCTION_FIELDS.md)의 최종 동결 LF/CRLF·패키지 전체 복원 검사를
진행하기 위한 기록이다. 최종 결과는 실행 후 확정하며 준비 상태를 게시 완료로 세지 않는다.

개발 baseline은 게시본 155cbe58adb48e8db635fe0fbe5092d4b1482179의 함수 필드 생성 거절과
이전 게시 runtime f73f1b5098cb540dbb6e3a7fea9983320386df13의 실제 live descriptor다.
후자는 보관 ZIP을 해시 확인해 element-authoring host만 소유 임시 폴더로 추출하여 새로
질의한 비교 입력이다. 이전 통과 증거를 최종 검사에 재사용한 것으로 합산하지 않는다.

확장 fixture 작성 중 reflection nullable unboxing 경고와 두 기존 진단명 예상 오류가
있었다. 컴파일러/구조 검사를 약화하지 않고 fixture만 수정하며 모든 로그를 보존한다.
현재 Linux/.NET/Chromium 검증과 Windows 교차 패키지 생성은 실제 기기·전체 UI와 다르다.
초기 빈 화면의 원인은 미확정이다.

첫 동결 d9986adb15bc796821b4594071f7ed2b53782b48의 LF/CRLF·패키지 UI 등32단계는
통과했으나, 전체 복원 native 검사는 패키지에 포함되지 않는 tests/fixtures 기준 파일을
복원본 내부에서 읽어 FileNotFoundError로 중단됐다. 원래 기록·증거는
`6c2809e083794512a5c02ce49719e677`에 보존한다. 제품 source는 고정하고 기준 파일 경로를
명시 전달하도록 fixture만 수정한다. 변경된 native 검사·빌드·패키지·전체 복원은 새로
실행하고, source/명령/의존성/import closure가 같은 기존 통과14단계만 검증하여 재사용한다.
변경 SDK/제품 거절 및 실패 검사 재사용 금지를 재사용 guard가 확인한다.
