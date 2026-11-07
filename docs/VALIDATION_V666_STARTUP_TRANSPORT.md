# 초기화 HTTP 전송 정체 검증

[구현 범위와 한계](V2_STARTUP_TRANSPORT.md).
코드/검사/도구 동결 `89337ae84959a5f7200acf56e32e41968ec36cac` 이후는 문서만 변경한다.
최종 **37단계: 신규32 / 동등 근거 재사용5**. LF15 · CRLF14 · 패키지/전체 복원/수명관리8.
독립 Git 객체·NuGet/home·빈 엔진 cache와 출력을 사용했다.

과거 배치 검사에서 reload 후 빈 `#app`이 남은 실패의 직접 원인은 미확정이다.
그 실패에는 모듈 요청/응답 기록이 없다. 같은 runtime의 보관 패키지에서 요청·응답·페이지
수명을 추가 수집한 실제3D reload24회는 정상 초기화됐다. 재실행 통과를 원인 해결로 보지 않는다.

별도 실제 소켓 검사에서는 읽지 않는 큰 이미지 응답이 단일 host loop를 막아 다른 창
초기화도3초 넘게 멈췄으며, 연결을 끊자 Broken pipe가 전파돼 호스트가 종료됐다.
이 controlled stall과 과거 간헐 실패의 원인이 같다고 단정하지 않는다.

- 소켓 입력/출력 대기만 분리했다. 원래 owner Request/Resource는 같은 host 스레드에서
  직렬로 호출한다. 실제4MiB 미수신 응답·부분 POST·단절이 다른 요청을 막지 않았고,
  성공한 응답의 연결 재사용과 API 중복 실행 없음·기존 Unicode/MIME/ETag/CSP/캐시를 확인했다.
  초과32개 연결은 owner 작업 전에503/종료하며 실제30초 만료 후 슬롯을 회수했다.
  종료 시 미완료 입력/출력을 취소하고 owner는1회 닫았다. 이 exact-body HTTP probe의
  owner는 test double이며 실제 편집기 검사는 아래와 구분한다.
- 실제 엔진/Chromium에서는 느린 이미지 클라이언트와 인증된 부분 POST를 유지한 채
  3D reload·새 입력·단절 후 재초기화·child/root·프로젝트 A/B/A·새 엔진 cold를 확인했다.
  API 응답을 합성하지 않았다. 원본 파일과 기존 실행/Review/Confirm 권한은 보존했다.
- 지연된 helper 메타데이터와 함수 창의 현재 UI/선택 ID 복원 순서를 검사했다.
  기존 저장의 Undo/Redo·취소·응답 유실·늦은 입력·동료 checkpoint 충돌·cold, compiler
  Review 취소·최종 CAS 거절·새 Confirm·실제 C# 실행이 통과했다. UI 레이아웃과 원문/계약은 유지했다.
- 3D 배치 정상/쓰기 거절·잃은 응답·새 입력·취소/Undo·프로젝트/cold 회귀를 통과했다.
  실제 이동/도착을 작업 실행 조건으로 연결하지 않았다.
- 새 Windows 교차 패키지 구조·전체 SHA·누락/변조 거절과 관리형 엔진 시작, 패키지 및
  ZIP 전체 파일/디렉터리 mode 복원 후의 실제 초기화·cold/배치 회귀를 검사했다.
  성공 반복·복사/UI 실패의 증거 보존과 소유 임시물 수명관리도 통과했다.
  Linux 관리형 엔진/Chromium 자동화이며 Windows apphost/WebView2·모바일/물리 장치 실행은 아니다.

재사용5개는 통과한 LF 전송 probe·client·전송 UI와 초기화 복원·배치 UI뿐이다.
봉인된 직전 기록의 전체 SHA/CRC·manifest·결과/명령을 확인했다. 원본 commit부터 최종
commit까지 제품/선택 검사 입력이 동일하며 차이는 독립된 레거시 복원 검사와 그 호출 도구
수정뿐임을 Git으로 대조했다. SDK/NuGet·구성·대상과 명령도 일치한다. 실패한 검사·빌드나
패키지는 재사용하지 않았다. CRLF와 새 패키지/전체 복원은 모두 신규다.

최종 기록 `/workspace/artifacts/v536-verification-managed/runs/4fdf700a981843a9944fbfc353d9f3f5.json`.
증거 ZIP `/workspace/artifacts/v536-verification-managed/runs/4fdf700a981843a9944fbfc353d9f3f5.zip` · SHA256 `0b6f9847213ca70553bc57680383728d50840130323da59d45ca9eff94a87627` · 5937266bytes.
전체 manifest/CRC/파일 mode와 실행 소유 RAM root 제거를 확인했다.

| 역할 | 출처 commit | ZIP SHA256 | bytes / files / dirs | 전체 manifest SHA256 |
|---|---|---|---|---|
| latest | `89337ae84959a5f7200acf56e32e41968ec36cac` | `6c3b07935b44e180eb956672993f56f0dbc99d8b53a26f78469b45975b9608c4` | 51855586 / 2471 / 152 | `262108c2535f7b7e7bbbb4495850f878d34f0067550c79c3c7b924cfae05f4cd` |
| rollback | `87e62a3da052f6af47206d3702aed161d07fb681` | `48927abd242608b5133dedd9c24613072dc67f5d7f670d71bb0a7070223e090a` | 51852221 / 2471 / 152 | `d5ffad25a70e55bc9c11a4974c4148818c7a88cf0703a48e2fbee047ada3dcf1` |

최신과 직전 검증본의 승인된2세대 승격/자체 임시물 정리만 사용했다. rollback은 위 원래
전송 결함을 재현한 직전 runtime이기도 하므로 그 결함의 수정본으로 오해하지 않는다.
과거 자료·원본/SDK·사용자 데이터·기존 로그/프로필은 추가 삭제하지 않았다.
계획160MiB(안전64MiB 포함)·RAM3GiB+512MiB·추가 메모리7GiB+1GiB 기준을 유지했다. 최종 실행 순증가 6.55MiB, 단위 순증가 12.00MiB,
측정 여유 1354.30MiB, 단계 표본 최소 여유 1360.82MiB, peak 메모리 4936.79MiB다. 이후 증가량의 보장값이 아니다.

조사/집중 검사와 실패 기록은 최종37단계에 중복 합산하지 않았다.

| 기록 | SHA256 | 구분 |
|---|---|---|
| `74352046e446459ea3a63c260be9ff6a` | `3bd610e939f27c68c81811c81a85f3b9b86289a6c89a1f39bdf2d00e0d4d7268` | 원래 패키지 실제 reload24회: 정상, 최초 간헐 실패의 원인 미확정 |
| `b590b73d20c443d69c08653046437958` | `1646fb86a137ca63f3fa6200011a78ae55f4afacf114819327a48771e38f9081` | 원래 패키지 실제 slow peer: 초기화 정체/단절 시 호스트 종료 재현 |
| `01b27e460978464bbc566782dacd8162` | `b0d67536a2c587de3d1f920e6ef92debf5a041fccc0258a0a9126712a73b75f0` | 집중 검사: DOTNET_CLI_HOME 미지정으로 build 전 실패 |
| `e5a1c6bb60d14bb4a318f3dd04af7681` | `67cd81b2acfabfc809504b3a8fe4e5e10aa9b587916458b3c3b735d3dfc364a2` | 집중 검사: 초과 연결 빈200 발견,503으로 수정 |
| `736403b679904d3c8777021081d48d89` | `ade5941ea17394d5a7e1ddd43b60602a70438633c177128da837f039c2a59aca` | 집중 검사: exact-body HTTP 통과, 최종 코드 동결 전 |
| `4c60fdca9998444c95bccc919f9b6270` | `f3a6235389f683fe6d92a81fa8491c04e5b584caa6142499ef4e3d3a15b143eb` | 제품 native 생성: 암시 using이 없는 Dictionary 누락을 완전한 이름으로 수정 |
| `72af04f3ec054c77889f29f022ac246c` | `eb611ed8c0580fdb159de1917b4fa313540d5be4ffda0783f87f99fc9c3665fd` | 레거시 복원 검사: 숨겨진 nav 대신 현재 프로젝트 도구 메뉴 사용 |
| `1d78a790208b4bdfa8a7cf5254ae5325` | `8de85923852332ad4872a1bf84717557a9298ff33f33821bb18678482f106d96` | 레거시 복원 검사: 이전 폼 대신 현재 함수 헤더/정확한 선택 ID 사용 |
| `125833ef2ab143ebbdb046dde220fa52` | `bf47d25d10b5f646df035ee45c49f9c3547359a8b51bb7cedbb91089aff6280d` | 실행 검사: 원래(7,after)를 out Root의(10,edited:10)와 비교한 인수 오류; 기존 회귀와 같은 --out-root로 고정 |

초기 집계 도구의 보조 상태 파일 record/id 키 차이는 집계 스크립트에서 바로잡았으며
완료 검증을 재실행하거나 제품/보관본을 변경하지 않았다. 모든 상기 기록의 archive를 재확인했다.

진행 중 OS I/O/공유 잠금의 전체 UI 관측, Run HD 이상·GPU/FPS/물리 오디오, 실제 신원/권한·
자산/참여자/대화 및 실제 기기·전체 UI·Space/Library 전달은 기존 고정 잔여다.
M11/M12/M4는 구체적 회귀 없이 재개하지 않으며 임의 조합/새 필수 요구를 추가하지 않았다.
라이브 AI/자격증명·과금·새 외부 grant·main 변경은 없다.
