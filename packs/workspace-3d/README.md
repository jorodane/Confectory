# 3D Workspace 표시 팩

`Confectory.Workspace3D::Bundle`은 사용자 지정 v666 ZIP의 로컬 renderer와 라이선스를
고정 manifest로 제공한다. 리소스는 각 파일의 LF 정규화 후 전체 크기/SHA-256 및 총량을
검사하고 기존 WebUI의 bounded inline resource 계약으로 전달한다. 외부 CDN을 사용하지 않는다.

첫 지원 범위는 실제 활성 프로젝트가 직접 소유한 선언의 방/보관함 표시, 명시적 패널/3D
전환, 개인 카메라 저장·복원과 기존 Browser 진입이다. 소유 선언의 ID를 새로 만들거나
복제하지 않는다. 3D 표시가 비활성화되거나 WebGL을 사용할 수 없어도 기존 편집은 유지된다.
카메라/보기는 기존 프로젝트별 private presentation에만 저장한다. source 저장이나
Review/Confirm의 권한·토큰·CAS를 대신하지 않는다.

기존 공개 Helper/Worker 상태와 철회는 [상태 연결](../../docs/V3_WORKSPACE_WORKERS.md)을
따른다. 활성 개인 Workspace에서 원본 배치 도구를 private presentation에 연결하며,
미확정 geometry는 다른 입력/카메라 checkpoint에 섞이지 않는다. 이 연결의 canArrange/
canWrite는 개인 표시 배치에만 적용하고 source 권한을 부여하지 않는다. canChat은 false다.
개별 read/write 신호와 하위 작업실별 전체 조작 검증은 후속 범위다.
Helpers/Workers에 시연 데이터를 넣지 않는다. 권한 관리는 별도 팩이며 이 팩은 판정이나
허용 API를 제공하지 않는다. 위치·이동·도착은 작업 실행이나 권한 검사의 조건이 아니다.

`ui/UPSTREAM.json`에 원본 출처를 기록한다. Three.js MIT 라이선스는
`ui/assets/three-LICENSE.txt`에 보존한다. renderer 본체의 변경은 import 경로·module
export, 읽기 전용 연결의 불필요한 catalog context 생략, optional 편집 버튼 및 폐기된
zoom popup 보호로 제한한다. CSS는 원본 office 관련 규칙과 media wrapper를 추출한다.
