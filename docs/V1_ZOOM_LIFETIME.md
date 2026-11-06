# V1 Workspace 확대 팝오버 수명

고정 v666 ZIP의 `dist/app.js:371–385`와 기존 Workspace 확대 버튼을 따른다.
3.125–500%·직접 입력/프리셋/슬라이더·Enter/바깥 클릭 적용·Escape 취소·레이아웃은
유지한다. 배율은 프로젝트별 개인 presentation이며 source 저장이나 실행 계약이 아니다.

게시 `d11b3f6`와 실행 코드가 같은 보관 패키지 `ba629cd`에서 닫힌 팝오버의
slider/preset/blur/Enter 콜백을 보존해 재개방 후 전달했다. 현재 150%가 400%로
바뀌었다. 이벤트 지연은 검사에서 직접 전달했으며 실제 OS 지연으로 표시하지 않는다.

현재 프로젝트 객체·navigation 설치의 소유 토큰·연결된 버튼·정확한 팝오버 인스턴스를
확인한다. 이전 팝오버의 blur가 새 팝오버의 commit 함수를 호출하지 않도록 그 입력에
속한 commit을 사용하고 닫힐 때 blur를 해제한다. 프로젝트 전환/홈/재개방 뒤의
폐기된 콜백은 아무 배율도 적용하지 않는다. 현재 유효한 컨트롤의 동작은 유지한다.

변경은 `ui/workspace.js`의 확대 setup 구간과 `WebBundle.csbody`의 해당 리소스
canonical pin뿐이다. [정확한 delta](v666-zoom-lifetime-delta.json)로 검사한다.
정의·원문/C#·IO/핀/연결·권한·부모/외부 원본·Review→Confirm·CAS·Undo는 미변경이다.
Blueprint에는 기존 수명 보호를 재사용하고 별도 팝오버나 새 디자인을 추가하지 않는다.

검증은 `tools/verify_desktop.py --suite zoom-lifetime`로 수행한다. 새 LF/CRLF 독립
checkout/cache/build, 실제 Linux managed engine/Chromium의 반복·취소·late callback,
A→홈→B→A·cold, 기존 Blueprint 확대/설명 입력/창 종료를 확인한다. 새 Windows 교차
패키지와 전체 SHA/CRC/권한 복원본을 사용하며 최신/롤백과 증거를 지속 보관한다.
최종 수치는 마감 기록에서 확정한다. 새로운 source Save 거래를 추가하지 않으므로
source 충돌을 이 표시 조작으로 만들어 내거나 기존 CAS 검증을 약화하지 않는다.

독립 정보 편집 창 안의 모든 확대 문맥·DPI/IME·실제 Windows/WebView2·모바일 기기·
전체 UI·Library/Space 전달은 이 단위의 완료가 아니다. V3–V7의 실제 backend/packs,
V8의 실제 renderer/audio provider와 V9의 실제 신원/권한 adapter 잔여도 유지한다.
