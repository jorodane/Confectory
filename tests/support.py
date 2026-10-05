from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from confectory.resolution import Documents, Planner, Registry


REPO = Path(__file__).resolve().parents[1]


class Fixture:
    def __init__(self):
        self.temp = tempfile.TemporaryDirectory(prefix="confectory-test-")
        self.root = Path(self.temp.name)
        self.packs = {}
        self.entry = "App::Main"
        self.always = []
        self.targets = {"portable": "Confectory.Build.DotNet::Portable", "linux": "Confectory.Build.DotNet::Linux"}
        self.extra_registry = {}
        self.new_pack("App", {"Api": "1", "Provider": "1", "Confectory.Build.DotNet": "0.1.0"})
        self.new_pack("Api")
        self.new_pack("Provider", {"Api": "1"})
        self.new_pack("Unused")
        shutil.copytree(REPO / "targets/dotnet", self.root / "target")
        self.extra_registry["Confectory.Build.DotNet"] = self.root / "target/pack.cpack"
        self.add("App", "function", "Main", """function App::Main () -> int {
            provide App::Main with App::MainBody;
            provide Api::Value with Provider::ValueBody;
        }""")
        self.add("App", "implementation", "MainBody", """implementation App::MainBody for App::Main () -> int {
            import Api::Value as Value (int) -> int;
            body common "main.csbody";
        }""")
        self.body("App", "main.csbody", 'Console.WriteLine(calls.Value.Invoke(2)); return 0;')
        self.add("Api", "function", "Value", 'function Api::Value (int n) -> int {}')
        self.add("Provider", "implementation", "ValueBody", """implementation Provider::ValueBody for Api::Value (int n) -> int {
            body common "value.csbody";
            body linux "value_linux.csbody";
        }""")
        self.body("Provider", "value.csbody", "return n + 3;")
        self.body("Provider", "value_linux.csbody", "return n + 30;")
        self.add("Unused", "object", "Dormant", 'object Unused::Dormant { value note = "unused"; }')
        self.sync()

    def close(self):
        self.temp.cleanup()

    @property
    def project(self):
        return self.packs["App"]["root"] / "project.cpack"

    def new_pack(self, namespace, dependencies=None, version="1"):
        root = self.root / namespace.replace(".", "_")
        root.mkdir(parents=True, exist_ok=True)
        self.packs[namespace] = {"root": root, "dependencies": dependencies or {}, "version": version, "elements": {}}

    def add(self, namespace, kind, local, text):
        pack = self.packs[namespace]
        filename = local + ".celem"
        pack["elements"][local] = {"kind": kind, "path": filename}
        path = pack["root"] / filename
        path.write_text(text + "\n", encoding="utf-8")
        return path

    def body(self, namespace, filename, text):
        path = self.packs[namespace]["root"] / filename
        path.write_text(text + "\n", encoding="utf-8")
        return path

    def sync(self):
        for ns, pack in self.packs.items():
            project = ns == "App"
            lines = [f'{"project" if project else "pack"} {ns} version {json.dumps(pack["version"])} {{']
            if project:
                if self.entry:
                    lines.append(f"entry {self.entry};")
                registrations = {other: p["root"] / "pack.cpack" for other, p in self.packs.items() if other != "App"}
                registrations.update(self.extra_registry)
                lines += [f"registry {other} {json.dumps(str(path))};" for other, path in registrations.items()]
                lines += [f"target {name} {ident};" for name, ident in self.targets.items()]
                lines += [f"always {ident};" for ident in self.always]
            lines += [f'dependency {dep} version {json.dumps(ver)};' for dep, ver in pack["dependencies"].items()]
            lines += [f'element {local} {item["kind"]} {json.dumps(item["path"])};' for local, item in pack["elements"].items()]
            lines.append("}")
            (pack["root"] / ("project.cpack" if project else "pack.cpack")).write_text("\n".join(lines) + "\n")

    def registry(self):
        stats = {"readDocuments": [], "parsedDocuments": [], "checkedContracts": []}
        documents = Documents(self.root / "document-cache", stats)
        registry = Registry(self.project, documents, stats)
        return registry, stats

    def plan(self, target="portable"):
        r, stats = self.registry()
        return Planner(r, target).plan(), stats

    def main(self, extras=""):
        return self.add("App", "function", "Main",
                        "function App::Main () -> int { provide App::Main with App::MainBody; " + extras + " }")

    def module(self, name, provider="Provider::ValueBody", includes=""):
        text = f"module App::{name} {{ require Api::Value (int) -> int; {includes}"
        if provider:
            text += f"default Api::Value with {provider};"
        return self.add("App", "module", name, text + "}")

    def second_provider(self):
        self.add("Provider", "implementation", "Second", """implementation Provider::Second for Api::Value (int n) -> int {
            body common "second.csbody";
        }""")
        self.body("Provider", "second.csbody", "return n + 100;")


def execute(report):
    return subprocess.run(report["run"], text=True, capture_output=True, timeout=15)
