"""Two editor peers on an unexposed Docker subnet. Forward only each editor's loopback UI."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import socketserver
import subprocess
import threading
import time
import uuid

DOCKER = ["docker", "--host=unix:///var/run/docker.sock"]
HOST, GUEST, OTHER = "172.29.173.2", "172.29.173.3", "172.29.173.4"
RELAY = """
import os, socket, sys, threading
with socket.create_connection(('127.0.0.1', int(sys.argv[1])), timeout=40) as target:
    def upload():
        try:
            while data := os.read(0, 65536):
                target.sendall(data)
            target.shutdown(socket.SHUT_WR)
        except OSError:
            pass
    threading.Thread(target=upload, daemon=True).start()
    while data := target.recv(65536):
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
"""


def docker(*args, **options):
    return subprocess.run([*DOCKER, *args], check=True, text=True, capture_output=True, **options)


@contextmanager
def internal_network(image, subnet="172.29.173.0/29"):
    image_id = docker("image", "inspect", "--format", "{{.Id}}", image).stdout.strip()
    network = "confectory-editor-lan-" + uuid.uuid4().hex[:12]
    docker("network", "create", "--internal", "--subnet", subnet,
           "--opt", "com.docker.network.bridge.inhibit_ipv4=true", network)
    try:
        settings, = json.loads(docker("network", "inspect", network).stdout)
        assert settings["Internal"] and settings["Options"]["com.docker.network.bridge.inhibit_ipv4"] == "true"
        yield network, image_id
    finally:
        docker("network", "rm", network)


class Peer:
    def __init__(self, network, image, role, address, directory, checkout, tool_repo, dotnet, other_network=None):
        self.network, self.image, self.address = network, image, address
        self.other_network = other_network
        self.name = network + "-" + role
        self.directory = directory
        self.checkout = checkout
        self.mounts = (checkout, tool_repo / "targets", Path(dotnet).parent)
        self.runtime = dotnet

    def __enter__(self):
        self.directory.mkdir()
        machine = self.directory / "machine-id"
        machine.write_text(uuid.uuid4().hex + "\n")
        command = ["run", "--pull=never", "--detach", "--name", self.name, "--network", f"name={self.network},ip={self.address}",
                   "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                   "--user", f"{os.getuid()}:{os.getgid()}", "--workdir", str(self.checkout)]
        for item in self.mounts:
            command.extend(("--mount", f"type=bind,src={item},dst={item},readonly"))
        if self.other_network:
            other, address = self.other_network
            command.extend(("--network", f"name={other},ip={address}", "--sysctl", "net.ipv4.ip_forward=0"))
        command.extend(("--mount", f"type=bind,src={self.directory},dst={self.directory}",
                        "--mount", f"type=bind,src={machine},dst=/etc/machine-id,readonly",
                        self.image, "/usr/bin/python3", "-c", "import time; time.sleep(900)"))
        try:
            docker(*command)
        except subprocess.CalledProcessError as error:
            subprocess.run([*DOCKER, "rm", "--force", self.name], capture_output=True, check=False)
            raise RuntimeError(error.stderr.strip()) from None
        try:
            settings, = json.loads(docker("inspect", self.name).stdout)
            assert not settings["HostConfig"]["PortBindings"]
            networks = {self.network}
            if self.other_network:
                networks.add(self.other_network[0])
            assert set(settings["NetworkSettings"]["Networks"]) == networks
            routes = self.run(["/usr/bin/python3", "-c", "print(open('/proc/net/route').read())"]).stdout
            assert all(row.split()[1] != "00000000" for row in routes.splitlines()[1:] if row.strip())
        except BaseException:
            self.__exit__()
            raise
        return self

    def __exit__(self, *_):
        docker("rm", "--force", self.name)

    def command(self, process, **variables):
        environment = dict(CONFECTORY_DOTNET=self.runtime, CONFECTORY_EDITOR_REPO=str(self.checkout),
                           DOTNET_CLI_HOME=str(self.directory),
                           PATH=str(Path(self.runtime).parent) + ":/usr/bin:/bin",
                           DOTNET_SKIP_FIRST_TIME_EXPERIENCE="1", DOTNET_CLI_TELEMETRY_OPTOUT="1",
                           **variables)
        command = ["exec"]
        for key, value in environment.items():
            command.extend(("--env", f"{key}={value}"))
        return [*command, self.name, *process]

    def run(self, process, **variables):
        try:
            return docker(*self.command(process, **variables), timeout=75)
        except subprocess.CalledProcessError as error:
            raise AssertionError(f"Isolated fixture exited with {error.returncode}: {error.stderr[-2000:]}") from error

    def sockets(self):
        return self.run(["/usr/bin/python3", "-c", "print(open('/proc/net/tcp').read())"]).stdout

    def stop_editor(self, profile):
        pid = int((profile / "owned-editor.pid").read_text())
        docker("exec", self.name, "/usr/bin/python3", "-c",
               "import os,signal,sys; os.kill(int(sys.argv[1]),signal.SIGTERM)", str(pid))

    @contextmanager
    def editor(self, command, profile, manifest, relay_setup=None):
        class Handler(socketserver.BaseRequestHandler):
            def handle(handler):
                with subprocess.Popen([*DOCKER, "exec", "-i", self.name, "/usr/bin/python3", "-u", "-c",
                                       RELAY, str(handler.server.server_address[1])],
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as proxy:
                    def upload():
                        try:
                            while data := handler.request.recv(65536):
                                proxy.stdin.write(data)
                                proxy.stdin.flush()
                        except OSError:
                            pass
                        finally:
                            proxy.stdin.close()

                    sender = threading.Thread(target=upload, daemon=True)
                    sender.start()
                    try:
                        while data := os.read(proxy.stdout.fileno(), 65536):
                            handler.request.sendall(data)
                    except OSError:
                        pass
                    finally:
                        try:
                            handler.request.shutdown(2)
                        except OSError:
                            pass
                        sender.join(timeout=3)

        with socketserver.ThreadingTCPServer(("127.0.0.1", 0), Handler) as browser:
            browser.daemon_threads = True
            port = browser.server_address[1]
            proxy_thread = threading.Thread(target=browser.serve_forever, daemon=True)
            proxy_thread.start()
            log = profile / "lan-editor.log"
            profile.mkdir(exist_ok=True)
            pid_path = profile / "owned-editor.pid"
            # The shell ends at exec, so this PID belongs to this exact editor fixture.
            run = ["/bin/sh", "-c", 'echo "$$" > "$1"; shift; exec "$@"', "fixture", str(pid_path), *command]
            with log.open("w") as output:
                process = self.command(run, CONFECTORY_UI="web",
                    CONFECTORY_TEST_PUBLIC_CHAT_RELAY="1" if relay_setup is not None else "0",
                    CONFECTORY_WEB_PORT=str(port), CONFECTORY_WEB_PROJECT=manifest,
                    CONFECTORY_HOME_STORAGE=str(profile), CONFECTORY_ENTRY_STORAGE=str(profile),
                    CONFECTORY_MCP_DIRECTORY=str(profile / "instances"))
                if relay_setup is not None:
                    process.insert(1, "-i")
                child = subprocess.Popen([*DOCKER, *process], stdout=output, stderr=subprocess.STDOUT,
                                         stdin=subprocess.PIPE if relay_setup is not None else None)
                try:
                    if relay_setup is not None:
                        child.stdin.write((json.dumps(relay_setup) + "\n").encode())
                        child.stdin.close()
                    deadline = time.monotonic() + 45
                    while time.monotonic() < deadline:
                        for line in log.read_text().splitlines():
                            if line.startswith("CONFECTORY_WEB_UI "):
                                yield line.split(" ", 1)[1], log
                                return
                        assert child.poll() is None, log.read_text()[-1000:]
                        time.sleep(.05)
                    raise AssertionError("LAN fixture editor failed to start")
                finally:
                    try:
                        if child.poll() is None:
                            self.stop_editor(profile)
                            child.wait(timeout=20)
                    finally:
                        browser.shutdown()
