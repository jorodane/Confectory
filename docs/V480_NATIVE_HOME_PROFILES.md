# IMP1: native 정보·표시 프로필과 도달 팩 조회

기준 소스는 `1a527c2887ad9c9c39f6af191b3bcf7d47fd02c4`다.

이 후속은 기존 [WebUI 정보·프로필 묶음](V480_HOME_PROFILES.md)을 지원되는 native 경로에 연결한다. 이전 통합 235개/ENV4 14개/WebUI 후속 8개와 검사 수를 합산하지 않는다. 정확한 기준 소스와 최종 메서드는 [검증 기록](validation/v480-native-home-profiles.json), 개발 중 실패와 재검사는 [시도 원문](validation/v480-native-home-profiles-attempts.log)에 기록한다.

## 지원 경로와 데이터

Linux의 기본 EditorHome은 GTK3/GtkSourceView4/X11 native 입력을 사용한다. Windows는 기본 embedded WebUI와 별도로 `CONFECTORY_UI=native`로 raw Win32 입력 경로를 선택할 수 있다. 이번에 Linux native 입력은 실제 Xorg에서 실행했고 Windows 구성은 managed 컴파일로 확인했다. Android/browser의 metadata adapter는 desktop CLR fixture로 실행했다. **Windows raw UI 실행, Android 기기/APK, 실제 browser-wasm 실행 결과는 아니다.** 새 도구·SDK·계정 설치나 권한 확장은 수행하지 않았다.

도달 팩 계산을 `Confectory.Core.HomeInclusion`으로 옮겨 desktop authoring과 Android/browser metadata adapter가 같은 코드를 사용한다. 확인된 manifest의 유형·namespace·독립 실행 여부·직접 요구 팩/버전과 타깃별 실제 도달 팩을 반환한다. 라이브러리/entry 없는 경우에는 metadata가 available이어도 도달성이 unsupported다. 파일 부재·손상·소유 루트 밖 읽기는 unavailable로 구분하며 0개로 추측하지 않는다. 기존 문서/바이트 한도·symlink 거부·읽은 파일의 버전 재확인을 유지한다. Adapter의 모든 읽기는 기존 owner-root resolver를 통과한다. compiler·TargetTool·구현 본문·프로젝트 실행은 호출하지 않는다.

native Home 카드 제목의 Info, 현재 프로젝트 메뉴의 Project information에서 같은 모델 조회를 연다. 제목/설명은 Home 목록 표시 값이며 manifest namespace·소스를 변경하지 않는다. native Helper 영역과 프로젝트의 Display profile에서 기존 소속에 맞는 표시 프로필을 연다. Home은 global Helper만, 열린 프로젝트는 global 및 해당 project Helper만 보여 준다. 프로필 열기는 Helper 선택·공통 기억 권한을 바꾸지 않는다. 모집 템플릿·성격·기억 설정은 이 편집 대상이 아니다.

## 저장·취소·수명

- 정보 화면은 요구/유형·타깃 도달성·저장된 Helper 선택과 공통 기억 허용 여부를 읽기 전용 native 스크롤 필드로 보여 준다. 편집 기준 hash와 현재 관측 hash도 표시한다.
- 표시 프로필의 이름·간단 설명·설명과 로컬 미전송 global 입력은 기존 bounded JSON/hash CAS 계약으로 명시 저장한다. global 입력은 프로젝트 대화 버퍼와 분리되고 전역 AI 전송·인격·기억·Agent 소유·Worker 설정으로 전달하지 않는다. 표시 이름은 native 참여자와 Helper 목록에도 반영한다.
- Close는 입력을 현재 세션에 보관하고 Discard는 명시적으로 저장본 기준으로 되돌린다. 기존 위젯 값을 다음 poll이 다시 가져오지 않도록 해당 native 화면의 위젯을 먼저 숨긴 뒤 새 값을 반영한다. 프로젝트 소스/필드/대화 버퍼는 별도 소유로 유지한다. 다른 정보/프로필로 이동할 때 비활성 native 위젯은 해제하고 managed 입력 버퍼를 유지한다. 동일 owner의 저장된 fixture Helper 31개를 왕복해 기존 native 위젯 한도 128을 늘리지 않고 입력을 보존하는지 확인했다.
- native 정보/프로필은 같은 세션의 UI 화면이다. Open/Register/Create로 별도 또는 빈 프로젝트를 만들지 않는다. 프로젝트 ID·context·원래 소스/대화 buffer binding과 미적용 입력을 유지한 채 두 프로젝트를 왕복한다.
- 충돌 시 외부 파일과 입력을 보존한다. 손상된 표시 프로필 저장본은 unavailable로 표시하고 저장을 비활성화한다. WebUI도 프로필을 열 때 새 읽기 전용 조회를 수행하고 관측된 unavailable 상태를 저장 버튼에 반영한다. 이 조회는 현재 shell 메뉴·Helper 선택을 바꾸지 않는다.

**미저장 표시 정보/프로필/global 입력은 세션 수명이다. cold 복원은 명시적 저장본만 대상으로 한다.** 기존 native 소스·프로젝트 대화의 미적용 입력은 살아 있는 컨텍스트 간 전환에서 확인했으며 이 문서는 미저장 native 소스의 process-cold 복원을 주장하지 않는다. 저장/Confirm 또는 전송을 자동 실행하지 않는다.

## 검증 범위

최종 **서로 다른 8개 메서드가 모두 통과했고 실패·건너뜀은 0**이다. native 그룹 3개 257.104초, 계약/fixture/WebUI 그룹 5개 45.835초다. Tests와 element-authoring Release build는 경고/오류 0이다. 메서드는 JSON의 정확한 목록을 따른다. Linux 새 native 시나리오는 실제 GTK 위젯·readonly 속성, project/pack/파일 부재 구분, 값/hash 표기, 정보/프로필 명시 저장·취소·재진입, 목록/프로필 CAS 거부, 손상 파일 보존/저장 비활성화, 참여자 표시 이름, 소스·대화 buffer binding 보존, 두 프로젝트 전환, 새 프로세스의 저장본 복원을 검사한다. 확정 소스 bytes, 카드 3개/실제 프로젝트 manifest 2개, AI/preview/binding/요청 없음도 확인한다.

기존 native Home의 생성·picker·열기/닫기·리소스 정리/locality와 작은/0 client 크기 변경 검사를 포함한다. Windows native 구성은 managed compile, Android/browser adapter는 동일 reply·owner-root 거부·본문 미읽기·unsupported/unavailable fixture로 분리한다. 기존 metadata authoring과 WebUI 전환/cold 회귀도 검사한다. 실제 계정·로그인·설치·유료/외부 AI 호출은 하지 않았다. 4 CPU/16 GiB에서 gate를 최대 2개로 제한했다.

개발 중 잘못된 library fixture 문법, 새 메서드의 harness 등록 누락, native C# LINQ 호출과 이동한 Core 이름 참조 누락을 수정했다. 실제 GTK Discard/poll 순서 문제, 로딩 중 null을 허용하지 않은 fixture 조건, 외부 파일 손상 직후의 WebUI 캐시/저장 버튼 문제도 수정했다. 기존 native 크기 변경 검사의 기본 사용자 데이터 경로는 읽기 전용이라 전용 writable XDG 경로로 재실행했다. 실패를 숨기거나 timeout/assertion을 완화하지 않았다.

[native 표시 프로필](validation/v480-native-profile-saved.png), [프로젝트 미적용 소스/대화](validation/v480-native-project-input-retained.png), [cold 저장본](validation/v480-native-cold-profile.png)은 최종 실행의 실제 화면이다.

## 보존과 다음 범위

main과 원본 ZIP 4개를 보존한다. Android 변경은 metadata adapter의 C# 조회 분기 한 줄이며 manifest·SDK·서명·패키지/빌드 설정은 변경하지 않았다. 41개 WebUI 리소스와 CSP를 유지하고 프로필 조회 보완에 필요한 app.js pin만 갱신한다. 관련 로컬 AGENTS.md/skills는 발견되지 않았다.

IMP1의 이 로컬 연결 구현은 위 범위로 완료한다. 미실행 OS/장치·전체 IME/접근성/픽셀 조합은 ENV1/ENV2에 남기고 완료로 표시하지 않는다. 다음 독립 구현 묶음은 IMP2의 브라우저 전체 tree/category grouping이며 새 category 의미는 DEC1 밖에서 만들지 않는다. 전역 AI 전송·인격/기억 설정·overflow는 이번 변경에서 제외했다. ENV4의 미확정 ButtonGame/Pause/zombie 항목도 기존 재발 시 계측 한계를 유지한다. [단일 남은 목록](V480_REMAINING_WORK.md)을 따른다.
