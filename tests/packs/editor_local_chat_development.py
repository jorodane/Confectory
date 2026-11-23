"""Exercise development invitations in two real editor processes and local Chromium contexts."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import time

from playwright.sync_api import expect, sync_playwright

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / "tests/web"))
from editor_navigation import goto_editor

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("checkout", nargs="?", type=Path, default=repo)
parser.add_argument("--isolated-lan-image", help="local Linux fixture image with .NET system dependencies, sh and Python at /usr/bin/python3")
parser.add_argument("--isolated-relay-image", help="run the editor on two isolated subnets with a separately provisioned relay")
args = parser.parse_args()
tool_repo = args.checkout.resolve()
dotnet = os.environ.get("CONFECTORY_DOTNET") or shutil.which("dotnet")
cli = tool_repo / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"
assert dotnet and cli.is_file()
env = dict(os.environ, CONFECTORY_DOTNET=dotnet, PATH=str(Path(dotnet).parent) + os.pathsep + os.environ["PATH"])

seed_body = r'''
string root=Environment.GetEnvironmentVariable("CONFECTORY_DEV_TEST_ROOT")!;
string repo=Environment.GetEnvironmentVariable("CONFECTORY_EDITOR_REPO")!;
var result=new System.Text.Json.Nodes.JsonObject();
string projects=System.IO.Path.Combine(root,"projects");
System.IO.Directory.CreateDirectory(projects);
foreach(string title in new[]{"HostOwner","GuestWorkspace","EySameProject"}){
 string session=calls.CreateSession.Invoke(repo,System.IO.Path.Combine(root,title));
 try{
  var opened=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(session,"create",
   System.Text.Json.JsonSerializer.Serialize(new{title,directory=projects})))!;
  result[title]=opened["selected"]?["path"]?.DeepClone()??throw new InvalidOperationException("Fixture create failed");
  bool host=title=="HostOwner", shared=title=="EySameProject";
  {
   void Run(string operation,object input){
    var response=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(session,operation,System.Text.Json.JsonSerializer.Serialize(input)))!;
    if(response["status"]!.ToString().StartsWith("Error:",StringComparison.Ordinal))throw new InvalidOperationException(response["status"]!.ToString());
   }
   string id="Project."+title+(shared?"::MainBody":"::Main");
   Run("workspace",new{action="open"});
   Run("workspace",new{action="select",id});
   Run("yogi",new{action="exactly",id});
   for(int i=0;i<(host?2:1);i++){
    byte[] pixels=new byte[512*512*3];
    Array.Fill(pixels,host?(byte)(59+i):shared?(byte)67:(byte)65);
    Run("yogi",new{action="capture",id,view="",image=new{width=512,height=512,encoding="rgb24-base64",
     pixels=Convert.ToBase64String(pixels),hash=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(pixels)).ToLowerInvariant()}});
   }
   Run("yogi",new{action="text",text=host?"첨부 시점의 봉인 설명":shared?"같은 원본의 봉인 설명":"게스트의 봉인 설명"});
   Run("yogi",new{action="seal",@sealed=true});
  }
 }finally{calls.CloseSession.Invoke(session);}
}
System.IO.File.WriteAllText(System.IO.Path.Combine(root,"fixture.json"),result.ToJsonString());
return 0;
'''


def build(manifest, target="linux"):
    result = subprocess.run([dotnet, str(cli), "build", str(manifest), target], capture_output=True,
                            text=True, timeout=240, env=env)
    assert result.returncode == 0, result.stdout[-5000:] + result.stderr[-5000:]
    return json.loads(result.stdout)


@contextmanager
def editor(command, checkout, storage, project, enabled):
    log = storage / f"editor-{Path(project).parent.name}-{'enabled' if enabled else 'disabled'}.log"
    with log.open("w") as output:
        process = subprocess.Popen(command, cwd=checkout, stdout=output, stderr=subprocess.STDOUT, start_new_session=True,
            env=dict(env, CONFECTORY_UI="web", CONFECTORY_WEB_PROJECT=project, CONFECTORY_WEB_PORT="0",
                     CONFECTORY_EDITOR_REPO=str(checkout), CONFECTORY_HOME_STORAGE=str(storage),
                     CONFECTORY_ENTRY_STORAGE=str(storage), CONFECTORY_MCP_DIRECTORY=str(storage / "instances"),
                     CONFECTORY_DEV_PUBLIC_CHAT_LOOPBACK="1" if enabled else "0"))
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                for line in log.read_text().splitlines():
                    if line.startswith("CONFECTORY_WEB_UI "):
                        yield line.split(" ", 1)[1], log
                        return
                assert process.poll() is None, "Editor startup failed"
                time.sleep(0.05)
            raise AssertionError("Editor startup timed out")
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=20)


def route_page(browser, url, calls, send_attempts, drop_ack=None):
    context = browser.new_context(viewport={"width": 1440, "height": 1000})
    page = context.new_page()
    origin = url.split("/#")[0]

    def handle(route):
        if not route.request.url.startswith(origin + "/"):
            route.abort()
            return
        if route.request.method == "POST" and route.request.url.endswith("/api/request"):
            request = route.request.post_data_json
            if request.get("endpoint") in ("localChatDevelopment", "localProjectChat"):
                data = request.get("input", {})
                calls.append((request.get("op"), data.get("action")))
                if data.get("action") in ("send", "send-attachment"):
                    send_attempts.append((data["text"], data["id"]))
                    if drop_ack is not None and data["text"] in drop_ack:
                        reply = route.fetch()
                        if reply.json().get("result", {}).get("status") == "committed":
                            drop_ack.remove(data["text"])
                            route.abort()
                        else:
                            route.fulfill(response=reply)
                        return
        route.continue_()

    page.route("**/*", handle)
    goto_editor(page, url)
    return context, page


def menu(page, name):
    page.locator("#title").click()
    page.locator(".context-menu").get_by_role("button", name=name, exact=True).click()


def issue(page):
    menu(page, "로컬 채팅 초대")
    panel = page.get_by_role("dialog", name="로컬 채팅 초대", exact=True)
    panel.get_by_role("button", name="일회용 초대 발급", exact=True).click()
    expect(panel.get_by_role("button", name="초대 텍스트 선택")).to_be_visible(timeout=15000)
    field = panel.get_by_label("일회용 초대")
    card = field.input_value()
    assert set(json.loads(card)) == {"version", "port", "project", "certificate", "code"}
    assert json.loads(card)["code"] not in field.evaluate("element => element.outerHTML")
    return panel, card


def open_join(page, home=False):
    if home:
        page.get_by_role("button", name="로컬 초대 참가", exact=True).click()
    else:
        menu(page, "로컬 초대 참가")
    return page.get_by_role("dialog", name="로컬 초대 참가", exact=True)


def join(panel, card):
    panel.get_by_label("일회용 초대").fill(card)
    panel.get_by_label("참가 이름").fill("테스트 참가자")
    panel.get_by_role("button", name="참가", exact=True).click()


def composer(page, name):
    return page.get_by_role("form", name=name, exact=True)


def send(form, text):
    form.get_by_label("공용 메시지 입력").fill(text)
    form.get_by_role("button", name="공용으로 보내기", exact=True).click()
    expect(form.get_by_label("공용 메시지 입력")).to_have_value("")


def drag_box(page, sealed, form, offset=24):
    field = form.get_by_label("공용 메시지 입력")
    field.scroll_into_view_if_needed()
    assert form.get_by_role("button", name="봉인 YogiBox 첨부", exact=True).is_enabled()
    source, target = sealed.bounding_box(), field.bounding_box()
    assert source and target
    page.mouse.move(source["x"] + source["width"] / 2, source["y"] + source["height"] / 2)
    page.mouse.down()
    # Chromium needs two pointer movements over the drop target.
    page.mouse.move(target["x"] + offset, target["y"] + 12, steps=12)
    page.mouse.move(target["x"] + offset + 8, target["y"] + 14)
    page.mouse.up()


def verify_yogi(viewer, host):
    expect(viewer).to_contain_text("첨부 시점의 봉인 설명")
    if host:
        expect(viewer.get_by_role("button", name="Project.HostOwner::Main", exact=True)).to_be_visible()
    else:
        expect(viewer).to_contain_text("현재 열 수 없는 EY")
        expect(viewer).not_to_contain_text("Project.HostOwner::Main")
    verify_captures(viewer, (59, 60))


def verify_captures(viewer, colors):
    for number, value in enumerate(colors):
        # Clicking an image replaces that button. Check every pixel of each rendered capture.
        viewer.get_by_role("button", name="이미지 보기", exact=True).first.click()
        canvas = viewer.locator("canvas").nth(number)
        expect(canvas).to_be_visible()
        assert canvas.evaluate("""async canvas=>{
          const {width,height}=canvas,pixels=canvas.getContext('2d').getImageData(0,0,width,height).data;
          const rgb=new Uint8Array(width*height*3);
          for(let i=0;i<rgb.length/3;i++)rgb.set(pixels.subarray(i*4,i*4+3),i*3);
          const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',rgb)),
             v=>v.toString(16).padStart(2,'0')).join('');
          return [width,height,hash];
        }""") == [512, 512, hashlib.sha256(bytes([value]) * (512 * 512 * 3)).hexdigest()]



def test_private_lan(root, checkout, seed, command, image):
    from editor_private_lan_fixture import GUEST, HOST, OTHER, Peer, internal_network

    def rows(peer):
        return [row.split() for row in peer.sockets().splitlines()[1:] if row.strip()]

    def listeners(peer):
        result = set()
        for cells in rows(peer):
            if cells[3] != "0A":
                continue
            address, port = cells[1].split(":")
            address = socket.inet_ntoa(struct.pack("<I", int(address, 16)))
            # The editor's diagnostic HTTP UI and Docker's embedded DNS are loopback only.
            if not address.startswith("127."):
                result.add((address, int(port, 16)))
        return result

    def issue_lan(page):
        page.get_by_role("button", name="LAN 채팅 초대", exact=True).click()
        panel = page.get_by_role("dialog", name="LAN 채팅 초대", exact=True)
        panel.get_by_label("내 PC IPv4").fill(HOST)
        issue_button = panel.get_by_role("button", name="일회용 초대 발급", exact=True)
        for ineligible in ("192.0.2.8", "172.29.174.3"):
            panel.get_by_label("참가 PC IPv4").fill(ineligible)
            issue_button.click()
            expect(panel.locator("[data-local-chat-status]")).to_contain_text("발급할 수 없습니다")
            expect(issue_button).to_be_enabled()
            assert not listeners(host)
        panel.get_by_label("참가 PC IPv4").fill(GUEST)
        issue_button.click()
        expect(panel.get_by_role("button", name="초대 텍스트 선택")).to_be_visible(timeout=20000)
        return panel, panel.get_by_label("일회용 초대").input_value()

    def review(page, card):
        menu(page, "LAN 초대 참가")
        panel = page.get_by_role("dialog", name="LAN 초대 참가", exact=True)
        panel.get_by_label("일회용 초대").fill(card)
        panel.get_by_label("참가 이름").fill("격리 참가자")
        panel.get_by_role("button", name="연결 대상 확인", exact=True).click()
        value = json.loads(card)
        target = panel.locator("[data-lan-review]")
        expect(target).to_contain_text(f'{HOST}:{value["port"]}')
        expect(target).to_contain_text(value["project"])
        expect(target).to_contain_text("HostOwner")
        endpoint = socket.inet_aton(HOST)[::-1].hex().upper() + f':{value["port"]:04X}'
        assert not any(cells[3] == "01" and cells[1] == endpoint for cells in rows(host))
        return panel

    with internal_network(image) as (network, image_id), \
         Peer(network, image_id, "host", HOST, root/"lan-host", checkout, tool_repo, dotnet) as host, \
         Peer(network, image_id, "guest", GUEST, root/"lan-guest", checkout, tool_repo, dotnet) as guest, \
         Peer(network, image_id, "observer", OTHER, root/"lan-observer", checkout, tool_repo, dotnet) as observer:
        for peer in (host, guest):
            peer.run(seed, CONFECTORY_DEV_TEST_ROOT=str(peer.directory))
        host_project = json.loads((host.directory/"fixture.json").read_text())["HostOwner"]
        guest_project = json.loads((guest.directory/"fixture.json").read_text())["GuestWorkspace"]
        host_profile, guest_profile = host.directory/"HostOwner", guest.directory/"GuestWorkspace"
        before_host = Path(host_project).read_bytes()
        before_guest = Path(guest_project).read_bytes()
        guest_private = guest_profile/"helper-conversations/fixture.json"
        guest_private.parent.mkdir(exist_ok=True)
        guest_private.write_bytes(b'{"personal":true}')
        with sync_playwright() as playwright, playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser, \
             host.editor(command, host_profile, host_project) as (host_url, host_log), \
             guest.editor(command, guest_profile, guest_project) as (guest_url, guest_log):
            hc, hp = route_page(browser, host_url, [], [])
            gc, gp = route_page(browser, guest_url, [], [])
            hp.locator("#chat").click()
            gp.locator("#chat").click()
            expect(hp.get_by_role("button", name="LAN 채팅 초대", exact=True)).to_be_visible()
            assert not listeners(host) and not listeners(guest)
            host_panel, card = issue_lan(hp)
            details = json.loads(card)
            port, code = details["port"], details["code"]
            assert details["version"] == 2 and details["host"] == HOST and details["guest"] == GUEST
            assert listeners(host) == {(HOST, port)}
            # The third isolated address is dropped before TLS, even on the same subnet.
            observer.run(["/usr/bin/python3", "-c",
                          "import socket,sys; s=socket.create_connection((sys.argv[1],int(sys.argv[2])),3); assert s.recv(1)==b''",
                          HOST, str(port)])
            host_form = composer(hp, "호스트 공용 채팅")
            send(host_form, "참가 이전 기록")
            guest_panel = review(gp, card)
            guest_panel.get_by_role("button", name="이 프로젝트에 참가").click()
            status = guest_panel.locator("[data-local-chat-status]")
            expect(status).to_have_text("새 메시지가 없습니다.", timeout=20000)
            expect(guest_panel).not_to_contain_text("참가 이전 기록")
            print("PASS no LAN listener before issuance; bound interface and single peer; review precedes TLS and empty first inbox", flush=True)

            guest_form = composer(gp, "참가 프로젝트 공용 채팅")
            send(host_form, "LAN 호스트 글")
            expect(guest_panel.locator("[data-local-chat-messages]")).to_contain_text("LAN 호스트 글")
            send(guest_form, "LAN 참가자 글")
            expect(hp.locator("[data-public-chat-rows]")).to_contain_text("LAN 참가자 글")
            hp.locator("#yogi").click()
            sealed = hp.get_by_role("dialog", name="YogiBox", exact=True).locator(".yogi-package")
            expect(sealed).to_be_visible()
            sealed.get_by_role("button", name="YogiBox 닫기", exact=True).click()
            host_form.get_by_role("button", name="봉인 YogiBox 첨부", exact=True).click()
            send(host_form, "LAN 봉인 첨부")
            guest_panel.get_by_role("button", name="YogiBox 보기", exact=True).click()
            viewer = guest_panel.get_by_role("region", name="YogiBox 보기")
            expect(viewer).to_contain_text("첨부 시점의 봉인 설명")
            expect(viewer).to_contain_text("현재 열 수 없는 EY")
            verify_captures(viewer, (59, 60))
            print("PASS bidirectional editor chat and frozen LaY pixels without guest EY", flush=True)

            guest_panel.get_by_role("button", name="닫기", exact=True).click()
            replay = review(gp, card)
            replay.get_by_role("button", name="이 프로젝트에 참가").click()
            expect(replay.locator("[data-local-chat-status]")).to_contain_text("연결할 수 없습니다")
            replay.get_by_role("button", name="닫기", exact=True).click()
            host_panel.get_by_role("button", name="닫기", exact=True).click()
            expect(host_form).to_have_count(0)
            host_panel, fresh = issue_lan(hp)
            guest_panel = review(gp, fresh)
            guest_panel.get_by_role("button", name="이 프로젝트에 참가").click()
            expect(guest_panel.locator("[data-local-chat-status]")).to_have_text("새 메시지가 없습니다.")
            expect(guest_panel.get_by_role("button", name="YogiBox 보기", exact=True)).to_have_count(0)
            host_panel.get_by_role("button", name="닫기", exact=True).click()
            expect(guest_panel.locator("[data-local-chat-status]")).to_contain_text("연결이 종료되었습니다")
            assert not listeners(host)
            guest_panel.get_by_role("button", name="닫기", exact=True).click()

            host_panel, closing = issue_lan(hp)
            guest_panel = review(gp, closing)
            guest_panel.get_by_role("button", name="이 프로젝트에 참가").click()
            expect(guest_panel.locator("[data-local-chat-status]")).to_have_text("새 메시지가 없습니다.")
            host.stop_editor(host_profile)
            expect(guest_panel.locator("[data-local-chat-status]")).to_contain_text("연결이 종료되었습니다")
            assert not listeners(host)
            assert Path(host_project).read_bytes()==before_host and Path(guest_project).read_bytes()==before_guest
            assert guest_private.read_bytes() == b'{"personal":true}' and not (guest_profile/"project-chat").exists()
            journal, = (host_profile/"project-chat").glob("*.json")
            assert sum(row["text"] == "LAN 참가자 글" for row in json.loads(journal.read_text())["messages"]) == 1
            assert all(json.loads(invitation)["code"] not in journal.read_text() + host_log.read_text() + guest_log.read_text()
                       for invitation in (card, fresh, closing))
            hc.close()
            gc.close()
            print("PASS one-use replay rejected, rejoin empty, revoke and host process shutdown disconnect, and the guest has no durable public copy", flush=True)

            copy = guest.directory/"copy"
            source = Path(host_project)
            shutil.copytree(source.parent, copy, ignore=shutil.ignore_patterns(".confectory"))
            copy_manifest = copy/source.name
            # Use the existing creator-host fixture's bound identity shape. A raw
            # copy with the old manifest path would be refused before hosting is checked.
            identity = json.loads((source.parent/".confectory/project-identity.json").read_text())
            identity["manifest"] = str(copy_manifest)
            (copy/".confectory").mkdir()
            (copy/".confectory/project-identity.json").write_text(json.dumps(identity))
            with guest.editor(command, guest.directory/"CopyProfile", str(copy_manifest)) as (copy_url, _):
                cc, cp = route_page(browser, copy_url, [], [])
                cp.locator("#chat").click()
                expect(cp.get_by_role("button", name="LAN 채팅 초대", exact=True)).to_have_count(0)
                assert not listeners(guest)
                cc.close()
            print("PASS a separate editor profile opening a project copy does not become host", flush=True)


def test_isolated_relay(root, checkout, seed, command, image):
    import base64
    from datetime import datetime, timedelta, timezone
    import errno
    import secrets
    import select
    import uuid

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives.serialization import pkcs12
    from cryptography.x509.oid import NameOID
    from editor_private_lan_fixture import DOCKER, Peer, internal_network

    def identity(dns):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, dns)])
        now = datetime.now(timezone.utc)
        certificate = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
                       .serial_number(x509.random_serial_number()).not_valid_before(now - timedelta(minutes=1))
                       .not_valid_after(now + timedelta(hours=1))
                       .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
                       .add_extension(x509.SubjectAlternativeName([x509.DNSName(dns)]), critical=False)
                       .sign(key, hashes.SHA256()))
        bundle = pkcs12.serialize_key_and_certificates(b"fixture", key, certificate, None, serialization.NoEncryption())
        der = certificate.public_bytes(serialization.Encoding.DER)
        return base64.b64encode(bundle).decode(), base64.b64encode(der).decode(), hashlib.sha256(der).hexdigest().upper()

    host_invite, guest_invite = "인터넷 채팅 초대 (시험)", "인터넷 초대 참가 (시험)"
    left, right = "192.0.2.3", "198.51.100.3"
    left_relay, right_relay = "192.0.2.2", "198.51.100.2"
    relay_key, relay_pin, _ = identity("relay.confectory.invalid")
    host_key, host_pin, fingerprint = identity("chat-host.confectory.invalid")

    def no_listener(peer):
        return not any(cells[3] == "0A" and not cells[1].startswith("0100007F") and
                       not cells[1].startswith("0B00007F")
                       for cells in (row.split() for row in peer.sockets().splitlines()[1:] if row.strip()))

    def trial(browser, guest, profile, project, configuration=None):
        with guest.editor(command, profile, project, configuration) as (url, _):
            context, page = route_page(browser, url, [], [])
            page.locator("#chat").click()
            expect(page.get_by_role("button", name="LAN 채팅 초대", exact=True)).to_be_visible()
            expect(page.get_by_role("button", name=host_invite, exact=True)).to_have_count(0)
            page.locator("#title").click()
            expect(page.locator(".context-menu").get_by_role("button", name=guest_invite, exact=True)).to_have_count(0)
            context.close()

    def issue_on(page):
        page.get_by_role("button", name=host_invite, exact=True).click()
        panel = page.get_by_role("dialog", name=host_invite, exact=True)
        panel.get_by_role("button", name="일회용 초대 발급", exact=True).click()
        expect(panel.get_by_role("button", name="초대 텍스트 선택")).to_be_visible(timeout=20000)
        card = panel.get_by_label("일회용 초대").input_value()
        assert set(json.loads(card)) == {"version", "project", "code", "reservation", "title"}
        assert json.loads(card)["version"] == 3
        return panel, card

    def review_on(page, card, port=None):
        menu(page, guest_invite)
        panel = page.get_by_role("dialog", name=guest_invite, exact=True)
        panel.get_by_label("일회용 초대").fill(card)
        panel.get_by_label("참가 이름").fill("격리 중계 참가자")
        panel.get_by_role("button", name="연결 대상 확인", exact=True).click()
        if port is None:
            expect(panel.locator("[data-local-chat-status]")).to_contain_text("사전에 설정된 시험 중계가 일치하는지")
            expect(panel.get_by_role("button", name="이 프로젝트에 참가", exact=True)).to_have_count(0)
        else:
            target = panel.locator("[data-lan-review]")
            expect(target).to_contain_text(f"{right_relay}:{port}")
            expect(target).to_contain_text(json.loads(card)["project"])
            expect(target).to_contain_text("HostOwner")
            expect(target).to_contain_text(fingerprint)
        return panel

    with internal_network(image, "192.0.2.0/29") as (a, image_id), \
         internal_network(image, "198.51.100.0/29") as (b, _), \
         Peer(a, image_id, "host", left, root/"relay-host", checkout, tool_repo, dotnet) as host, \
         Peer(b, image_id, "guest", right, root/"relay-guest", checkout, tool_repo, dotnet) as guest, \
         Peer(a, image_id, "relay", left_relay, root/"relay-service", checkout, tool_repo, dotnet,
              other_network=(b, right_relay)) as relay:
        for peer, other in ((host, right), (guest, left)):
            peer.run(seed, CONFECTORY_DEV_TEST_ROOT=str(peer.directory))
            peer.run(["/usr/bin/python3", "-c", "import socket,sys; s=socket.socket(); s.settimeout(1); "
                      "assert s.connect_ex((sys.argv[1],12345)) == int(sys.argv[2])", other, str(errno.ENETUNREACH)])
        host_project = json.loads((host.directory/"fixture.json").read_text())["HostOwner"]
        guest_project = json.loads((guest.directory/"fixture.json").read_text())["GuestWorkspace"]
        host_profile, guest_profile = host.directory/"HostOwner", guest.directory/"GuestWorkspace"
        before_host, before_guest = Path(host_project).read_bytes(), Path(guest_project).read_bytes()
        private = guest_profile/"helper-conversations/fixture.json"
        private.parent.mkdir(exist_ok=True)
        private.write_bytes(b'{"private_fixture":true}')

        service_command = relay.command(command, CONFECTORY_TEST_PUBLIC_CHAT_RELAY="1")
        service_command.insert(1, "-i")
        service_log = relay.directory/"editor-relay-service.log"
        with service_log.open("w") as errors, subprocess.Popen([*DOCKER, *service_command], text=True,
                                                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors) as service:
            def send_setup(payload):
                service.stdin.write(json.dumps(payload) + "\n")
                service.stdin.flush()

            def reserve(seconds):
                pair, host_grant, guest_grant = uuid.uuid4().hex, secrets.token_hex(32), secrets.token_hex(32)
                send_setup(dict(seconds=seconds, hostHash=hashlib.sha256(bytes.fromhex(host_grant)).hexdigest(),
                                guestHash=hashlib.sha256(bytes.fromhex(guest_grant)).hexdigest()))
                assert select.select([service.stdout], [], [], 15)[0], "Isolated relay did not allocate a port"
                port = int(service.stdout.readline())
                return (dict(id=pair, port=port, grant=host_grant), dict(id=pair, port=port, grant=guest_grant))

            try:
                send_setup(dict(role="relay", identity=relay_key))
                with sync_playwright() as playwright, playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
                    trial(browser, guest, guest_profile, guest_project)
                    # A syntactically valid but out-of-fixture endpoint also
                    # leaves only the established LAN UI available.
                    invalid = dict(role="guest", identity=host_pin, relayPin=relay_pin, address="127.0.0.1",
                                   reservations=[dict(id=uuid.uuid4().hex, port=12345, grant=secrets.token_hex(32))])
                    trial(browser, guest, guest_profile, guest_project, invalid)
                    pairs = [reserve(seconds) for seconds in (20, 240, 240)]
                    config_host = dict(role="host", identity=host_key, relayPin=relay_pin, address=left_relay,
                                       reservations=[pair[0] for pair in pairs])
                    config_guest = dict(role="guest", identity=host_pin, relayPin=relay_pin, address=right_relay,
                                        reservations=[pair[1] for pair in pairs])
                    with host.editor(command, host_profile, host_project, config_host) as (host_url, host_log), \
                         guest.editor(command, guest_profile, guest_project, config_guest) as (guest_url, guest_log):
                        hc, hp = route_page(browser, host_url, [], [])
                        calls = []
                        gc, gp = route_page(browser, guest_url, calls, [])
                        hp.locator("#chat").click()
                        gp.locator("#chat").click()
                        assert no_listener(host) and no_listener(guest)
                        expect(gp.get_by_role("button", name=host_invite, exact=True)).to_have_count(0)
                        expect(hp.get_by_role("button", name="LAN 채팅 초대", exact=True)).to_be_visible()
                        expired_panel, expired_card = issue_on(hp)
                        expect(expired_panel.locator("[data-local-chat-status]")).to_contain_text("연결이 종료되었습니다", timeout=26000)
                        expect(expired_panel.get_by_label("일회용 초대")).to_have_value("")
                        expired_panel.get_by_role("button", name="닫기", exact=True).click()
                        expired = review_on(gp, expired_card, pairs[0][1]["port"])
                        expired.get_by_role("button", name="이 프로젝트에 참가", exact=True).click()
                        expect(expired.locator("[data-local-chat-status]")).to_contain_text("연결할 수 없습니다")
                        expired.get_by_role("button", name="닫기", exact=True).click()
                        print("PASS editor hides unconfigured and untrusted relay, and clears and refuses an expired invitation", flush=True)

                        host_panel, card = issue_on(hp)
                        host_form = composer(hp, "호스트 공용 채팅")
                        send(host_form, "중계 참가 전 기록")
                        fake = review_on(gp, json.dumps(dict(json.loads(card), endpoint="192.0.2.99", certificate=relay_pin)))
                        assert sum(action == "join-relay" for _, action in calls) == 1  # expired attempt only
                        fake.get_by_role("button", name="닫기", exact=True).click()
                        guest_panel = review_on(gp, card, pairs[1][1]["port"])
                        assert sum(action == "join-relay" for _, action in calls) == 1
                        guest_panel.get_by_role("button", name="이 프로젝트에 참가", exact=True).click()
                        expect(guest_panel.locator("[data-local-chat-status]")).to_have_text("새 메시지가 없습니다.", timeout=20000)
                        expect(guest_panel).not_to_contain_text("중계 참가 전 기록")
                        expect(guest_panel.get_by_role("button", name="프로젝트 도구", exact=True)).to_have_count(0)
                        assert no_listener(host) and no_listener(guest)
                        guest_form = composer(gp, "참가 프로젝트 공용 채팅")
                        send(host_form, "중계를 통한 호스트 글")
                        expect(guest_panel.locator("[data-local-chat-messages]")).to_contain_text("중계를 통한 호스트 글")
                        send(guest_form, "중계를 통한 참가자 글")
                        expect(hp.locator("[data-public-chat-rows]")).to_contain_text("중계를 통한 참가자 글")
                        hp.locator("#yogi").click()
                        sealed = hp.get_by_role("dialog", name="YogiBox", exact=True).locator(".yogi-package")
                        expect(sealed).to_be_visible()
                        sealed.get_by_role("button", name="YogiBox 닫기", exact=True).click()
                        host_form.get_by_role("button", name="봉인 YogiBox 첨부", exact=True).click()
                        send(host_form, "중계 봉인 첨부")
                        guest_panel.get_by_role("button", name="YogiBox 보기", exact=True).click()
                        viewer = guest_panel.get_by_role("region", name="YogiBox 보기")
                        expect(viewer).to_contain_text("첨부 시점의 봉인 설명")
                        expect(viewer).to_contain_text("현재 열 수 없는 EY")
                        verify_captures(viewer, (59, 60))
                        print("PASS separated editor networks, pretrusted review before join, two-way public text, frozen LaY and no EY or editor access", flush=True)

                        host_panel.get_by_role("button", name="초대 철회 및 연결 종료", exact=True).click()
                        expect(guest_panel.locator("[data-local-chat-status]")).to_contain_text("연결이 종료되었습니다")
                        expect(guest_panel.locator("[data-local-chat-messages]")).to_be_empty()
                        expect(viewer).to_have_count(0)
                        guest_panel.get_by_role("button", name="닫기", exact=True).click()
                        replay = review_on(gp, card, pairs[1][1]["port"])
                        replay.get_by_role("button", name="이 프로젝트에 참가", exact=True).click()
                        expect(replay.locator("[data-local-chat-status]")).to_contain_text("연결할 수 없습니다")
                        replay.get_by_role("button", name="닫기", exact=True).click()

                        host_panel, fresh = issue_on(hp)
                        guest_panel = review_on(gp, fresh, pairs[2][1]["port"])
                        guest_panel.get_by_role("button", name="이 프로젝트에 참가", exact=True).click()
                        expect(guest_panel.locator("[data-local-chat-status]")).to_have_text("새 메시지가 없습니다.")
                        expect(guest_panel.get_by_role("button", name="YogiBox 보기", exact=True)).to_have_count(0)
                        host.stop_editor(host_profile)
                        expect(guest_panel.locator("[data-local-chat-status]")).to_contain_text("연결이 종료되었습니다")
                        assert no_listener(host)
                        journal, = (host_profile/"project-chat").glob("*.json")
                        assert sum(row["text"] == "중계를 통한 참가자 글" for row in json.loads(journal.read_text())["messages"]) == 1
                        assert not (guest_profile/"project-chat").exists() and private.read_bytes() == b'{"private_fixture":true}'
                        assert Path(host_project).read_bytes() == before_host and Path(guest_project).read_bytes() == before_guest
                        observable = journal.read_text() + host_log.read_text() + guest_log.read_text() + service_log.read_text()
                        assert all(json.loads(value)["code"] not in observable for value in (expired_card, card, fresh))
                        assert all(reservation["grant"] not in observable for pair in pairs for reservation in pair)
                        hc.close()
                        gc.close()
                        print("PASS explicit revoke, one-use replay, empty re-entry, host shutdown, and host-only history without credentials in logs", flush=True)

                        # The role configuration is available, but a copied project
                        # still does not earn an issuance control in the host UI.
                        source = Path(host_project)
                        copy = guest.directory/"relay-copy"
                        shutil.copytree(source.parent, copy, ignore=shutil.ignore_patterns(".confectory"))
                        copied = copy/source.name
                        identity_file = source.parent/".confectory/project-identity.json"
                        project_identity = json.loads(identity_file.read_text())
                        project_identity["manifest"] = str(copied)
                        (copy/".confectory").mkdir()
                        (copy/".confectory/project-identity.json").write_text(json.dumps(project_identity))
                        with guest.editor(command, guest.directory/"RelayCopy", str(copied), config_host) as (copy_url, _):
                            cc, cp = route_page(browser, copy_url, [], [])
                            cp.locator("#chat").click()
                            expect(cp.get_by_role("button", name=host_invite, exact=True)).to_have_count(0)
                            assert no_listener(guest)
                            cc.close()
                        print("PASS configured fixture profile still cannot host a copy of the original project", flush=True)
            finally:
                service.stdin.close()
                service.wait(timeout=20)
                assert service.returncode == 0, "Isolated relay did not shut down cleanly"


with tempfile.TemporaryDirectory(prefix="confectory-dev-invite-") as temp:
    root = Path(temp)
    checkout = root / "checkout"
    home = checkout / "examples/editor-home"
    shutil.copytree(repo / "packs", checkout / "packs", ignore=shutil.ignore_patterns(".confectory"))
    shutil.copytree(repo / "examples/editor-home", home, ignore=shutil.ignore_patterns(".confectory"))
    (checkout / "targets").symlink_to(tool_repo / "targets", target_is_directory=True)
    manifest = home / "project.cpack"
    original = manifest.read_text()
    manifest.write_text(original.replace("entry Confectory.EditorHome::Main;", "entry Confectory.EditorHome::VerifyShell;"))
    (home / "VerifyShell.csbody").write_text(seed_body)
    seed_command = build(manifest)["run"]
    if args.isolated_relay_image:
        manifest.write_text(original)
        main_body = home / "MainBody.celem"
        main_body.write_text(main_body.read_text().replace('body common "Main.csbody";',
            'import Confectory.ProjectChat::OpenOpaqueChatRelay as FixtureRelay (object) -> object;\nbody common "Main.csbody";'))
        entry = home / "Main.csbody"
        fixture = repo / "tests/fixtures/isolated-relay-editor/Setup.csbody"
        entry.write_text(fixture.read_text() + entry.read_text())
        test_isolated_relay(root, checkout, seed_command, build(manifest)["run"], args.isolated_relay_image)
        raise SystemExit(0)
    if args.isolated_lan_image:
        manifest.write_text(original)
        test_private_lan(root, checkout, seed_command, build(manifest)["run"], args.isolated_lan_image)
        sys.exit(0)
    seed = subprocess.run(seed_command, capture_output=True, timeout=90,
        env=dict(env, CONFECTORY_DEV_TEST_ROOT=str(root), CONFECTORY_EDITOR_REPO=str(checkout)))
    assert seed.returncode == 0, seed.stderr.decode()
    projects = json.loads((root / "fixture.json").read_text())
    manifest.write_text(original)
    command = build(manifest)["run"]
    known_codes = []
    calls = []
    send_attempts = []
    drop_ack = set()
    host_storage, guest_storage, shared_storage = [root / name for name in ("HostOwner", "GuestWorkspace", "EySameProject")]
    local_yogi, = (Path(projects["HostOwner"]).parent / ".confectory/yogi").glob("package-*.json")
    saved_yogi = local_yogi.read_bytes()
    guest_yogi_file, = (Path(projects["GuestWorkspace"]).parent / ".confectory/yogi").glob("package-*.json")
    original_guest_box = guest_yogi_file.read_bytes()
    sentinels = {}
    for storage in (host_storage, guest_storage, shared_storage):
        private = storage / "helper-conversations/fixture.json"
        private.parent.mkdir(exist_ok=True)
        private.write_bytes(b'{"private":"fixture"}\n')
        sentinels[private] = private.read_bytes()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        try:
            with editor(command, checkout, host_storage, projects["HostOwner"], True) as (host_url, host_log), \
                 editor(command, checkout, guest_storage, projects["GuestWorkspace"], True) as (guest_url, guest_log):
                hc, host_page = route_page(browser, host_url, calls, send_attempts)
                gc, guest_page = route_page(browser, guest_url, calls, send_attempts, drop_ack)
                try:
                    host_page.locator("#chat").click()
                    host_form = composer(host_page, "호스트 공용 채팅")
                    expect(host_form).to_have_count(0)
                    host_panel, first = issue(host_page)
                    known_codes.append(json.loads(first)["code"])
                    send(host_form, "이전 공용 기록")
                    host_history = host_page.locator("[data-public-chat-rows]")
                    expect(host_history).to_contain_text("이전 공용 기록")

                    guest_page.locator("#chat").click()
                    draft = guest_page.locator("#chat-input")
                    draft.fill("그대로 둘 Helper 작성 중 입력")
                    draft.press("Shift+Enter")
                    draft.press("End")
                    guest_page.keyboard.insert_text("다음 줄")
                    expect(draft).to_have_value("그대로 둘 Helper 작성 중 입력\n다음 줄")
                    guest_panel = open_join(guest_page)
                    broken = dict(json.loads(first), certificate="broken")
                    join(guest_panel, json.dumps(broken))
                    expect(guest_panel.locator("[data-local-chat-status]")).to_contain_text("연결할 수 없습니다")
                    expect(guest_panel.get_by_label("일회용 초대")).to_have_value("")
                    join(guest_panel, first)
                    expect(guest_panel.locator("[data-local-chat-status]")).to_have_text("새 메시지가 없습니다.")
                    expect(guest_panel).not_to_contain_text("이전 공용 기록")
                    guest_form = composer(guest_page, "참가 프로젝트 공용 채팅")
                    expect(guest_form.get_by_role("button", name="봉인 YogiBox 첨부")).to_be_disabled()
                    guest_history = guest_panel.locator("[data-local-chat-messages]")
                    send(host_form, "참가 후 공용 한 줄")
                    expect(guest_history).to_contain_text("참가 후 공용 한 줄")
                    send(guest_form, "게스트가 보낸 공용 글")
                    expect(host_history).to_contain_text("게스트가 보낸 공용 글")
                    expect(guest_history).to_contain_text("게스트가 보낸 공용 글")
                    expect(draft).to_have_value("그대로 둘 Helper 작성 중 입력\n다음 줄")

                    journal, = (host_storage / "project-chat").glob("*.json")
                    original = journal.read_bytes()
                    mode = journal.stat().st_mode & 0o777
                    rejected = "저장 실패 뒤 다시 보낸 글"
                    journal.chmod(0o444)
                    try:
                        guest_form.get_by_label("공용 메시지 입력").fill(rejected)
                        guest_form.get_by_role("button", name="공용으로 보내기").click()
                        expect(guest_form.locator("[data-public-send-status]")).to_contain_text("저장이 거절")
                        expect(guest_form.get_by_label("공용 메시지 입력")).to_have_value(rejected)
                        expect(guest_history).not_to_contain_text(rejected)
                        assert journal.read_bytes() == original
                    finally:
                        journal.chmod(mode)
                    guest_form.get_by_role("button", name="공용으로 보내기").click()
                    expect(guest_form.get_by_label("공용 메시지 입력")).to_have_value("")
                    expect(host_history).to_contain_text(rejected)

                    uncertain = "응답을 받기 전에 끊긴 공용 글"
                    drop_ack.add(uncertain)
                    guest_form.get_by_label("공용 메시지 입력").fill(uncertain)
                    guest_form.get_by_role("button", name="공용으로 보내기").click()
                    expect(guest_form.locator("[data-public-send-status]")).to_contain_text("전송을 확인하지 못했습니다")
                    expect(guest_form.get_by_label("공용 메시지 입력")).to_have_value(uncertain)
                    expect(guest_history).to_contain_text(uncertain)
                    guest_form.get_by_role("button", name="공용으로 보내기").click()
                    expect(guest_form.get_by_label("공용 메시지 입력")).to_have_value("")
                    for retried in (rejected, uncertain):
                        ids = [value for text, value in send_attempts if text == retried]
                        assert len(ids) == 2 and ids[0] == ids[1]
                        assert sum(row["text"] == retried for row in json.loads(journal.read_text())["messages"]) == 1

                    before_attach = journal.read_bytes()
                    host_page.locator("#yogi").click()
                    sealed = host_page.get_by_role("dialog", name="YogiBox", exact=True).locator(".yogi-package")
                    expect(sealed).to_be_visible()
                    host_text = host_form.get_by_label("공용 메시지 입력")
                    drag_box(host_page, sealed, host_form)
                    cancel = host_form.get_by_role("button", name="YogiBox 첨부 취소", exact=True)
                    expect(cancel).to_be_visible()
                    assert journal.read_bytes() == before_attach
                    expect(guest_history.get_by_role("button", name="YogiBox 보기")).to_have_count(0)
                    sealed.get_by_role("button", name="YogiBox 닫기", exact=True).click()
                    cancel.click()
                    expect(host_form.locator("[data-public-send-status]")).to_contain_text("첨부를 취소")
                    assert journal.read_bytes() == before_attach

                    attach = host_form.get_by_role("button", name="봉인 YogiBox 첨부", exact=True)
                    attach.click()
                    expect(cancel).to_be_visible()
                    assert journal.read_bytes() == before_attach
                    attached_text = "봉인 요기박스 공용 첨부"
                    journal.chmod(0o444)
                    try:
                        host_text.fill(attached_text)
                        host_form.get_by_role("button", name="공용으로 보내기").click()
                        expect(host_form.locator("[data-public-send-status]")).to_contain_text("저장이 거절")
                        expect(host_text).to_have_value(attached_text)
                        expect(cancel).to_be_visible()
                        assert journal.read_bytes() == before_attach
                    finally:
                        journal.chmod(mode)
                    host_form.get_by_role("button", name="공용으로 보내기").click()
                    expect(host_text).to_have_value("")
                    records = [row for row in json.loads(journal.read_text())["messages"] if row["text"] == attached_text]
                    ids = [value for text, value in send_attempts if text == attached_text]
                    assert len(records) == 1 and "attachment" in records[0] and len(ids) >= 2 and len(set(ids)) == 1
                    assert local_yogi.read_bytes() == saved_yogi

                    guest_history.get_by_role("button", name="YogiBox 보기", exact=True).click()
                    guest_yogi = guest_panel.get_by_role("region", name="YogiBox 보기", exact=True)
                    verify_yogi(guest_yogi, host=False)
                    host_history.get_by_role("button", name="YogiBox 보기", exact=True).click()
                    host_yogi = host_page.get_by_role("region", name="YogiBox 보기", exact=True)
                    verify_yogi(host_yogi, host=True)
                    expect(host_panel).to_be_visible()
                    host_yogi.get_by_role("button", name="YogiBox 보기 닫기", exact=True).click()
                    expect(draft).to_have_value("그대로 둘 Helper 작성 중 입력\n다음 줄")

                    guest_yogi.get_by_role("button", name="YogiBox 보기 닫기", exact=True).click()
                    public_before_guest = journal.read_bytes()
                    guest_page.locator("#yogi").click()
                    guest_box_window = guest_page.get_by_role("dialog", name="YogiBox", exact=True)
                    guest_sealed = guest_box_window.locator(".yogi-package")
                    expect(guest_sealed).to_be_visible()
                    guest_attach = guest_form.get_by_role("button", name="봉인 YogiBox 첨부", exact=True)
                    guest_cancel = guest_form.get_by_role("button", name="YogiBox 첨부 취소", exact=True)
                    guest_status = guest_form.locator("[data-public-send-status]")
                    guest_input = guest_form.get_by_label("공용 메시지 입력")
                    guest_send = guest_form.get_by_role("button", name="공용으로 보내기", exact=True)
                    guest_attach.click()
                    expect(guest_status).to_contain_text("EY가 담긴 YogiBox는 게스트가 보낼 수 없습니다")
                    expect(guest_cancel).to_have_count(0)
                    assert guest_yogi_file.read_bytes() == original_guest_box
                    assert journal.read_bytes() == public_before_guest

                    guest_sealed.dblclick()
                    guest_box_window.get_by_role("button", name="Exactly Yogi", exact=True).click()
                    guest_box_window.locator('#yogi-items [data-kind="semantic"]').get_by_role("button", name="제거").click()
                    guest_box_window.locator("#yogi-seal").click()
                    expect(guest_sealed).to_be_visible()
                    prepared_guest_box = guest_yogi_file.read_bytes()
                    assert [item["kind"] for item in json.loads(prepared_guest_box)["package"]["items"]] == ["image"]

                    drag_box(guest_page, guest_sealed, guest_form)
                    expect(guest_cancel).to_be_visible()
                    assert journal.read_bytes() == public_before_guest
                    guest_sealed.get_by_role("button", name="YogiBox 닫기", exact=True).click()
                    guest_cancel.click()
                    expect(guest_status).to_contain_text("첨부를 취소")
                    assert journal.read_bytes() == public_before_guest

                    guest_attachment_text = "게스트가 보낸 봉인 LaY"
                    guest_attach.click()
                    expect(guest_cancel).to_be_visible()
                    journal.chmod(0o444)
                    try:
                        guest_input.fill(guest_attachment_text)
                        guest_send.click()
                        expect(guest_status).to_contain_text("저장이 거절")
                        expect(guest_cancel).to_be_visible()
                        expect(guest_input).to_have_value(guest_attachment_text)
                        assert journal.read_bytes() == public_before_guest
                    finally:
                        journal.chmod(mode)
                    drop_ack.add(guest_attachment_text)
                    guest_send.click()
                    expect(guest_status).to_contain_text("전송을 확인하지 못했습니다")
                    expect(guest_history).to_contain_text(guest_attachment_text)
                    guest_send.click()
                    expect(guest_input).to_have_value("")
                    received = [row for row in json.loads(journal.read_text())["messages"]
                                if row["text"] == guest_attachment_text]
                    assert len(received) == 1
                    ids = [value for text, value in send_attempts if text == guest_attachment_text]
                    assert len(ids) >= 3 and set(ids) == {received[0]["id"]}
                    package = received[0]["attachment"]["package"]
                    assert package["text"] == "게스트의 봉인 설명"
                    assert [item["kind"] for item in package["items"]] == ["image"]
                    assert guest_yogi_file.read_bytes() == prepared_guest_box
                    assert local_yogi.read_bytes() == saved_yogi

                    for panel, history in ((guest_panel, guest_history), (host_page, host_history)):
                        row = history.get_by_text(guest_attachment_text, exact=True).locator("..")
                        row.get_by_role("button", name="YogiBox 보기", exact=True).click()
                        viewer = panel.get_by_role("region", name="YogiBox 보기", exact=True)
                        expect(viewer).to_contain_text("게스트의 봉인 설명")
                        expect(viewer.get_by_role("button", name="이미지 보기", exact=True)).to_have_count(1)
                        expect(viewer).not_to_contain_text("Project.GuestWorkspace::Main")
                        verify_captures(viewer, (65,))
                    host_page.get_by_role("region", name="YogiBox 보기", exact=True).get_by_role(
                        "button", name="YogiBox 보기 닫기", exact=True).click()
                    expect(draft).to_have_value("그대로 둘 Helper 작성 중 입력\n다음 줄")

                    guest_panel.get_by_role("button", name="닫기", exact=True).click()
                    expect(guest_yogi).to_have_count(0)
                    guest_panel = open_join(guest_page)
                    join(guest_panel, first)
                    expect(guest_panel.locator("[data-local-chat-status]")).to_contain_text("연결할 수 없습니다")
                    expect(guest_panel.get_by_label("일회용 초대")).to_have_value("")

                    host_panel.get_by_role("button", name="닫기", exact=True).click()
                    host_panel, second = issue(host_page)
                    known_codes.append(json.loads(second)["code"])
                    join(guest_panel, second)
                    expect(guest_panel.locator("[data-local-chat-status]")).to_have_text("새 메시지가 없습니다.")
                    expect(guest_panel).not_to_contain_text("게스트가 보낸 공용 글")
                    expect(guest_panel).not_to_contain_text(guest_attachment_text)
                    expect(guest_panel.get_by_role("button", name="YogiBox 보기", exact=True)).to_have_count(0)
                    menu(guest_page, "프로젝트 나가기")
                    expect(guest_page.locator(".home-grid")).to_be_visible()
                    expect(guest_panel).to_have_count(0)
                    host_panel.get_by_role("button", name="닫기", exact=True).click()

                    host_panel, third = issue(host_page)
                    known_codes.append(json.loads(third)["code"])
                    guest_panel = open_join(guest_page, home=True)
                    join(guest_panel, third)
                    expect(guest_panel.locator("[data-local-chat-status]")).to_have_text("새 메시지가 없습니다.")
                    send(host_form, "재참가 뒤 공용 글")
                    expect(guest_panel.locator("[data-local-chat-messages]")).to_contain_text("재참가 뒤 공용 글")
                    menu(host_page, "프로젝트 나가기")
                    expect(host_page.locator(".home-grid")).to_be_visible()
                    expect(host_panel).to_have_count(0)
                    expect(guest_panel.locator("[data-local-chat-status]")).to_contain_text("연결이 종료되었습니다")
                    expect(guest_panel.locator("[data-local-chat-messages]")).to_be_empty()
                    expect(guest_form.get_by_role("button", name="공용으로 보내기")).to_be_disabled()
                    expect(host_form).to_have_count(0)

                    for page in (host_page, guest_page):
                        visible = page.evaluate("""() => [location.href, document.documentElement.outerHTML,
                            JSON.stringify(localStorage), JSON.stringify(sessionStorage), JSON.stringify(history.state)].join(' ')""")
                        assert all(code not in visible for code in known_codes)
                finally:
                    hc.close()
                    gc.close()

            # Both editors explicitly open the same original file. Only its creator
            # profile can host, and the chat invitation has no declaration-read grant.
            shared_project = Path(projects["EySameProject"])
            shared_yogi_file, = shared_project.parent.glob(".confectory/yogi/package-*.json")
            shared_originals = {path: path.read_bytes() for path in (shared_project, shared_yogi_file)}
            shared_reference = "Project.EySameProject::MainBody"
            with (
                editor(command, checkout, shared_storage, str(shared_project), True) as (shared_host_url, shared_host_log),
                editor(command, checkout, guest_storage, str(shared_project), True) as (other_url, other_log),
            ):
                hc, host_page = route_page(browser, shared_host_url, calls, send_attempts)
                gc, guest_page = route_page(browser, other_url, calls, send_attempts)
                try:
                    for page in (host_page, guest_page):
                        expect(page.locator("#title")).to_contain_text("EySameProject")
                        page.locator("#chat").click()

                    menu(guest_page, "로컬 채팅 초대")
                    refused = guest_page.get_by_role("dialog", name="로컬 채팅 초대", exact=True)
                    refused.get_by_role("button", name="일회용 초대 발급", exact=True).click()
                    expect(refused.locator("[data-local-chat-status]")).to_contain_text("원본 프로젝트를 만든 호스트만")
                    expect(refused.get_by_label("일회용 초대")).to_have_value("")
                    refused.get_by_role("button", name="닫기", exact=True).click()

                    shared_host_panel, shared_card = issue(host_page)
                    known_codes.append(json.loads(shared_card)["code"])
                    guest_panel = open_join(guest_page)
                    join(guest_panel, shared_card)
                    expect(guest_panel.locator("[data-local-chat-status]")).to_have_text("새 메시지가 없습니다.")

                    host_page.locator("#yogi").click()
                    sealed = host_page.get_by_role("dialog", name="YogiBox", exact=True).locator(".yogi-package")
                    sealed.get_by_role("button", name="YogiBox 닫기", exact=True).click()
                    host_form = composer(host_page, "호스트 공용 채팅")
                    host_form.get_by_role("button", name="봉인 YogiBox 첨부", exact=True).click()
                    expect(host_form.get_by_role("button", name="YogiBox 첨부 취소", exact=True)).to_be_visible()
                    send(host_form, "같은 원본의 EY와 LaY")

                    host_history = host_page.locator("[data-public-chat-rows]")
                    host_history.get_by_role("button", name="YogiBox 보기", exact=True).click()
                    host_viewer = host_page.get_by_role("region", name="YogiBox 보기", exact=True)
                    expect(host_viewer.get_by_role("button", name=shared_reference, exact=True)).to_be_visible()

                    guest_history = guest_panel.locator("[data-local-chat-messages]")
                    guest_history.get_by_role("button", name="YogiBox 보기", exact=True).click()
                    guest_viewer = guest_panel.get_by_role("region", name="YogiBox 보기", exact=True)
                    expect(guest_viewer).to_contain_text("같은 원본의 봉인 설명")
                    expect(guest_viewer.get_by_text("현재 열 수 없는 EY", exact=True)).to_have_count(1)
                    expect(guest_viewer).not_to_contain_text(shared_reference)
                    verify_captures(guest_viewer, (67,))

                    shared_host_panel.get_by_role("button", name="닫기", exact=True).click()
                    expect(guest_panel.locator("[data-local-chat-status]")).to_contain_text("연결이 종료되었습니다")
                    expect(guest_viewer).to_have_count(0)
                    assert all(path.read_bytes() == original for path, original in shared_originals.items())
                finally:
                    hc.close()
                    gc.close()

            with editor(command, checkout, guest_storage, projects["GuestWorkspace"], False) as (disabled_url, disabled_log):
                context, page = route_page(browser, disabled_url, calls, send_attempts)
                try:
                    page.locator("#title").click()
                    expect(page.locator(".context-menu").get_by_role("button", name="로컬 채팅 초대")).to_have_count(0)
                    expect(page.locator(".context-menu").get_by_role("button", name="로컬 초대 참가")).to_have_count(0)
                finally:
                    context.close()

            assert calls and all(operation == "transient" for operation, _ in calls)
            assert {"issue", "join", "read", "status", "send", "prepare-attachment", "cancel-attachment",
                    "send-attachment", "attachment", "first-image", "second-image"} <= {action for _, action in calls}
            assert not (guest_storage / "project-chat").exists()
            journal, = (host_storage / "project-chat").glob("*.json")
            assert [row["text"] for row in json.loads(journal.read_text())["messages"]] == [
                "이전 공용 기록", "참가 후 공용 한 줄", "게스트가 보낸 공용 글",
                "저장 실패 뒤 다시 보낸 글", "응답을 받기 전에 끊긴 공용 글", "봉인 요기박스 공용 첨부",
                "게스트가 보낸 봉인 LaY", "재참가 뒤 공용 글",
            ]
            for path in [journal, host_log, guest_log, shared_host_log, other_log, disabled_log, *sentinels]:
                assert all(code.encode() not in path.read_bytes() for code in known_codes)
            assert all(path.read_bytes() == before for path, before in sentinels.items())
        finally:
            browser.close()
    print("PASS same original in separate profiles: host-only EY, guest LaY hash, viewer cleared on disconnect")
    print("PASS two Chromium editors: explicit host/guest attachment, mixed EY refusal, frozen RGB, failed and lost acknowledgement retry, rejoin and private isolation")
