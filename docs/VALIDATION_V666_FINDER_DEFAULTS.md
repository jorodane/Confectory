# V666 소유 정보 기본값 검색 검증

제품·검사·도구 동결 `ab66bc2761dc7582c370dcbc791e308cd879d3c1` 이후 마감 commit은 문서만 바꾼다.
[지원 경계와 원본 대조](V9_FINDER_DEFAULTS.md)·[정확한 delta](v666-finder-defaults-delta.json)를 따른다.

## 실제 결함과 범위

이전 게시 엔진에서 typed JSON 기본값의 한글/이모지 검색 누락과 중첩 blob 문자열의
잘못된 색인을 생성 fixture로 재현했다. 저장 metadata 문자열을 이중 포장 그대로 검색한
결과였다. 현재 finderContent만 기존 profile·직접 소유/선언 필드에 맞는 JSON을 투영한다.
기존 token 읽기로 Unicode와 int64 lexeme을 보존하고 중첩 이미지/blob을 색인에서 제외한다.
profile 없음/미지원·orphan·잘못된 JSON·64개/64KiB 초과는 안전한 설명/정의와 정상 값을
남기며 부분 상태로 표시한다. 일반 내용 20,000자 한도의 잘린 검색도 부분 상태가 된다.
이 읽기 예산은 새 영구 저장/UX 정책이 아니며 기존 타입/Save/Confirm 검증을 대신하지 않는다.

일반 Browser Data API와 편집·모든 .celem/공개 실행/override 계약·Core/targets·원본 C#·
ID/연결·부모/외부 원본·권한·Review→Confirm·최종 CAS/Undo·레이아웃/Run은 변경하지
않았다. 추가 파일/상속/외부 원문·컴파일러를 검색을 위해 읽지 않는다. 기존 schema source
revision/hash 전후 검사와 실제 draft version 색인 수명을 그대로 사용한다.

원본 ZIP의 실제 helper를 실행해 저장된 functionDefinition.blueprint.nodes[].text와 깊은
코드가 검색 깊이 4 밖임을 확인했다. 직접 property 문자열·함수 body는 원본 검색 대상이다.
앞선 graph 후보를 모든 깊은 노드의 새 필수 요구로 확장하지 않도록 고정 잔여를 정정했다.

## 최종 검증

독립 LF 22·CRLF 22·새 패키지/전체 복원/IPC·실패 수명관리 17, **총 61단계(신규 61·재사용 0)** 통과했다.
Git 객체·EOL·NuGet/home·엔진 cache를 독립시키고 최종 동결 코드에서 새로 실행했다.
개발 단계/실패/과거 완료 기록은 최종 합계에 포함하지 않는다.

- 실제 Linux .NET/Chromium에서 scalar·배열·복합 기본값의 한글/이모지와 큰 정수를
  검색했다. Record와 그 자식의 기존 유효 상속 값도 유지했다. 중첩 payload·알 수 없는
  profile·unmarked·orphan·깨진 JSON·개수/바이트 예산 초과와 잘린 tail의 부분 상태를 확인했다.
- 검색 결과가 바로 그 소유 정보 정의를 열고, 현재 선택/개인 입력·원본 bytes·일반
  Browser metadata 표현을 보존함을 확인했다. UI 검색이 편집/Save/Confirm/실행/AI를
  요청하지 않았다. native fixture의 명시 draft 변경·Undo/Redo는 UI 검색 요청과 구분했다.
- 필터 밖 기본값 변경·Undo·Redo와 cold/home/동일 namespace·ID의 다른 프로젝트에서
  현재 값만 검색되고 이전 검색어/내용이 채택되지 않았다. 기존 Data/정의/C# target 검색·
  정확한 원문 열기·stale/변조 receipt·UTF-8 BOM/CRLF baseline·외부 변경 충돌·링크/locator
  거절·private 미적용 입력 보존도 새 코드에서 실행했다.
- 기존 controller 배치/프로젝트 세대·실패/명시 재시도·늦은 응답·pending Enter·닫기·
  재시작/Workspace·renderer busy/IME/숨긴 비밀 필드 제외·배치 Ctrl+F·Run 최대화 회귀를
  실행했다. 제어된 fixture는 실제 OS IME·계정 backend·네트워크 장애 증거가 아니다.
- 새 Windows 교차 패키지 구조/무결성과 패키지 엔진의 새 기본값 normal·기존 본문/검색
  흐름을 실행했다. 전체 SHA/CRC/모드로 완전히 복원한 엔진에서 기본값 변경/Undo/Redo·
  cold/프로젝트 격리와 본문/기존 검색을 실행했다. 성공·실패·예외의 증거 보존·자식 종료·
  소유 임시물 정리를 확인했다. Windows apphost를 실제 Windows에서 실행한 것은 아니다.

개발 중 큰 정수 기대 결과에 상속 ChildRecord를 빠뜨린 fixture와 schema 도착 전 null을
읽던 정의 열기 fixture를 수정했다. 해당 실패는 제품 결함/최종 통과로 계산하지 않는다.
수정 fixture와 제품 변경이 없는 상태의 normal/재시작 근거, 기준 누락 재현과 실패 기록을
함께 보존했다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/b4171412300e4e568c7dfc9a27be78eb.json`
개발 증거 SHA `2071a0eb2ce29519928f2f733e1f28cd9c05e0f1fda5ebae02b57e1c859c9c46`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/7fea26d4f195402fb9b26528327391da.json`
최종 증거 `/workspace/artifacts/v536-verification-managed/runs/7fea26d4f195402fb9b26528327391da.zip`
SHA `77df951c273deb998c6ad093338428816b422a80832aa1c51e42c8874a249ca1` (15.62MiB).

## 보관·공간·유한 잔여

Index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: `ab66bc2761dc7582c370dcbc791e308cd879d3c1`, `c2a3383e1277f45b6cb6600f7fa643ea15dc86cde105e4f4dbc487d002baedf4.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `d7ee71d421bbdf7642988d7ae8649fdd20bade6249aa8c737aaeb0f4e24ac320`.
- rollback: `aa52925a01fbb694c5dae41d9dccfc51254005ae`, `6ebdbbd3574db8727849b7517764ae8ec668afc8c9ae90536301bd2150309f2d.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `827e6c2363dc7562b1fb44ca48b49a0358aeaed3443c2ae191d1102058a2a662`.

전체 archive SHA/manifest·복원 확인 뒤 최신/이전 정상 롤백과 증거를 지속 보관했다.
해당 실행이 만든 임시물만 소유/자식 종료 확인 뒤 정리했다. 다른 과거 자료·원본·로그·
프로필·SDK/캐시의 추가 삭제나 보관정책 변경은 없다.

표본 최소 디스크 여유 1457.88MiB, 최대 cgroup 메모리 5034.73MiB.
최종 실행 순증가 16.90MiB, 개발 시작부터 보관 확인까지 23.07MiB,
문서 마감 전 여유 1441.04MiB. 다음 단위의 증가량은 보장하지 않는다.

직접 선언한 소유 정보 기본값의 검색은 마감했다. 깊은 graph 전체 탐색은 원본 깊이 밖이라
새 필수 항목이 아니다. 보존 원문 등 다른 얕은 실제 텍스트는 원본 근거/재현으로 판단한다.
참가자/Helper·연락처/대화(V4/V5)·office(V3), V6/V7 자산·편집과 V8 내장 surface/audio
provider가 기존 고정 잔여다. 현재 provider와 DISPLAY/Xvfb/오디오 장치가 없어 모의 화면/
사운드를 실제 backend 성공으로 채우지 않았다. 종류 C# 표현/사용중 삭제 대응·V1/V2 후속,
실제 Windows/WebView2·모바일·DPI/IME·전체 UI·Library/Space 전달도 미완료다. M11/M12/M4는
구체적 회귀 없이 재개하지 않는다. 3D/권한 별도 팩·이동 연출/실행 분리·명시 async caller
규칙을 유지했다. main을 보존하고 live AI·계정/키·유료 호출·새 외부 접근은 수행하지 않았다.
