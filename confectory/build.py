"""Plan + artifact reuse + out-of-process target protocol; no target compiler code."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from .declarations import BuildError, owned_path
from .generation import ABI, contract_source, implementation_source, final_source, public_catalog, symbol
from .resolution import Documents, Registry, Planner, atomic_json, digest


PROTOCOL = 1


class TargetTool:
    def __init__(self, registry, target):
        self.registry, self.target = registry, target
        ref = registry.project["targets"].get(target)
        if not ref:
            raise BuildError("MISSING_TARGET", f"No build-target mapping for {target}", registry.project["loc"])
        self.element = registry.effective(registry.get(ref["id"], "buildtarget", registry.project["namespace"] + "::<project>", ref["loc"])["id"])
        Planner(registry, target).structural(self.element["id"])
        root = registry.paths[self.element.get("toolOrigin", self.element["id"]).split("::")[0]].parent
        if not self.element["tool"]:
            raise BuildError("MISSING_TOOL", "Build-target pack must declare its tool", self.element["loc"])
        self.path = owned_path(root, self.element["tool"], self.element["loc"])
        if not self.path.is_file():
            raise BuildError("MISSING_TOOL", f"Build-target tool not found: {self.path}", self.element["loc"])
        tool_hash = digest(self.path.read_bytes())
        info = self.invoke("fingerprint")
        if not isinstance(info.get("fingerprint"), str) or not info["fingerprint"]:
            raise BuildError("TOOL_PROTOCOL", "Tool did not return a configuration fingerprint", self.element["loc"])
        self.identity = digest([PROTOCOL, tool_hash, self.element["options"], target, info["fingerprint"]])
        self.info = info

    def invoke(self, operation, **payload):
        request = {"protocol": PROTOCOL, "operation": operation, "target": self.target,
                   "options": self.element["options"], **payload}
        command = [sys.executable, str(self.path)] if self.path.suffix == ".py" else [str(self.path)]
        try:
            r = subprocess.run(command, input=json.dumps(request), text=True, capture_output=True,
                               cwd=self.path.parent, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as ex:
            raise BuildError("TOOL_EXECUTION", f"Target tool failed: {ex}", self.element["loc"]) from ex
        try:
            result = json.loads(r.stdout)
        except ValueError as ex:
            raise BuildError("TOOL_PROTOCOL", f"Target tool returned invalid JSON: {r.stderr or r.stdout}", self.element["loc"]) from ex
        if not isinstance(result, dict) or result.get("protocol") != PROTOCOL:
            raise BuildError("TOOL_PROTOCOL", "Target tool protocol mismatch", self.element["loc"])
        if r.returncode or result.get("ok") is not True:
            raise BuildError("TARGET_FAILURE", str(result.get("error", r.stderr or "Tool failed")), self.element["loc"])
        if operation.startswith("compile-") and not isinstance(result.get("artifacts"), dict):
            raise BuildError("TOOL_PROTOCOL", "Compile tool must return artifact paths", self.element["loc"])
        return result


class Artifacts:
    def __init__(self, root):
        self.root = root

    def get(self, key):
        folder = self.root / key
        try:
            record = json.loads((folder / "artifact.json").read_text())
            if record["key"] != key or not record["files"]:
                return None
            artifacts = {}
            for name, item in record["files"].items():
                path = owned_path(folder, item["path"])
                if digest(path.read_bytes()) != item["hash"]:
                    return None
                artifacts[name] = str(path)
            return artifacts
        except (OSError, ValueError, KeyError, TypeError, BuildError):
            return None

    def produce(self, key, callback):
        work = self.root / (key + "." + uuid.uuid4().hex + ".pending")
        work.mkdir(parents=True)
        try:
            artifacts = callback(work)
            if not isinstance(artifacts, dict) or not artifacts:
                raise BuildError("TOOL_PROTOCOL", "Compiler did not return artifacts")
            files = {}
            for name, value in artifacts.items():
                if not isinstance(value, str):
                    raise BuildError("TOOL_PROTOCOL", "Compiler artifact path must be a string")
                path = owned_path(work, value)
                if not path.is_file():
                    raise BuildError("TOOL_PROTOCOL", f"Compiler artifact is missing: {path}")
                files[name] = {"path": str(path.relative_to(work)), "hash": digest(path.read_bytes())}
            atomic_json(work / "artifact.json", {"key": key, "files": files})
            dest = self.root / key
            # Only an invalid, generated content-addressed entry is replaced.
            if dest.exists():
                if self.get(key):
                    shutil.rmtree(work)
                    return self.get(key)
                shutil.rmtree(dest)
            os.replace(work, dest)
            return self.get(key)
        except Exception:
            shutil.rmtree(work, ignore_errors=True)
            raise


class Builder:
    def __init__(self, project, target):
        self.project = Path(project).resolve()
        self.target = target
        self.state = self.project.parent / ".confectory"
        self.stats = {"readDocuments": [], "parsedDocuments": [], "checkedContracts": [],
                      "compiledContracts": [], "reusedContracts": [], "compiledPacks": [],
                      "reusedPacks": [], "fullRebuilds": 0}
        self.documents = Documents(self.state / "cache" / "declarations", self.stats)
        self.registry = Registry(self.project, self.documents, self.stats)
        self.tool = TargetTool(self.registry, target)
        self.cache = Artifacts(self.state / "cache" / "artifacts")
        self.contracts = {}

    def contract(self, ident):
        if ident in self.contracts:
            return self.contracts[ident]
        fn = self.registry.get(ident, "function")
        code = contract_source(fn)
        name = "Contract_" + symbol(ident)
        key = digest([ABI, self.tool.identity, "contract", code])
        artifact = self.cache.get(key)
        if artifact:
            self.stats["reusedContracts"].append(ident)
        else:
            def produce(work):
                source = work / (name + ".cs")
                source.write_text(code, encoding="utf-8")
                return self.tool.invoke("compile-contract", output=str(work), name=name,
                                        sources=[str(source)], references=[])["artifacts"]
            artifact = self.cache.produce(key, produce)
            self.stats["compiledContracts"].append(ident)
        if not artifact or "assembly" not in artifact or "reference" not in artifact:
            raise BuildError("TOOL_PROTOCOL", "Contract compilation must return assembly and reference")
        self.contracts[ident] = {"key": key, **artifact}
        return self.contracts[ident]

    def compile_pack(self, namespace, implementations):
        sources, refs, metadata = [], {}, []
        for e in sorted(implementations, key=lambda item: item["id"]):
            self.registry.implementation(e["for"], e["id"], e["id"], e["loc"])
            body = e["bodies"].get(self.target) or e["bodies"].get("common")
            if not body:
                raise BuildError("MISSING_TARGET_IMPLEMENTATION", f"No {self.target}/common body for {e['id']}", e["loc"])
            body_owner = body.get("origin", e["id"]).split("::")[0]
            path = owned_path(self.registry.paths[body_owner].parent, body["path"], body["loc"])
            text = self.documents.read(path, "body")["text"]
            sources.append((symbol(e["id"]) + ".cs", implementation_source(e, text, path)))
            for ident in [e["for"], *(x["id"] for x in e["imports"].values())]:
                refs[ident] = self.contract(ident)
            metadata.append(e["id"])
        key = digest([ABI, self.tool.identity, "pack", namespace, sources,
                      [(ident, artifact["key"]) for ident, artifact in sorted(refs.items())]])
        artifact = self.cache.get(key)
        if artifact:
            self.stats["reusedPacks"].append(namespace)
        else:
            def produce(work):
                paths = []
                for name, text in sources:
                    path = work / name
                    path.write_text(text, encoding="utf-8")
                    paths.append(str(path))
                return self.tool.invoke("compile-pack", output=str(work), name="Pack_" + symbol(namespace),
                                        sources=paths, references=[r["reference"] for r in refs.values()])["artifacts"]
            artifact = self.cache.produce(key, produce)
            self.stats["compiledPacks"].append(namespace)
        if not artifact or "assembly" not in artifact:
            raise BuildError("TOOL_PROTOCOL", "Pack compilation must return an assembly")
        return {"key": key, "implementations": metadata, **artifact}

    def check(self, namespace):
        if namespace not in self.registry.packs:
            raise BuildError("MISSING_NAMESPACE", f"Pack {namespace} is not selected")
        pack = self.registry.packs[namespace]
        implementations = []
        planner = Planner(self.registry, self.target)
        for local, locator in pack["elements"].items():
            if locator["kind"] == "implementation":
                ident = namespace + "::" + local
                e = self.registry.effective(ident)
                planner.structural(ident)
                implementations.append(self.registry.implementation(e["for"], ident, ident, e["loc"]))
        if not implementations:
            raise BuildError("LOCAL_INPUT", f"No implementation declarations in {namespace}", pack["loc"])
        result = self.compile_pack(namespace, implementations)
        return {"mode": "contract-only", "pack": namespace, "target": self.target,
                "artifact": result, "warnings": self.registry.warnings, "statistics": self.stats}

    def build(self):
        plan = Planner(self.registry, self.target).plan()
        by_pack = {}
        for e in plan.implementations.values():
            by_pack.setdefault(e["id"].split("::")[0], []).append(e)
        packs = {ns: self.compile_pack(ns, implementations) for ns, implementations in sorted(by_pack.items())}
        for node in plan.bindings.values():
            self.contract(node["function"])
        code = final_source(plan)
        key = digest([ABI, self.tool.identity, "link", code,
                      {ns: a["key"] for ns, a in packs.items()},
                      {ns: a["key"] for ns, a in self.contracts.items()}])
        output_root = self.state / "outputs" / self.target
        work = output_root / (key + "." + uuid.uuid4().hex + ".pending")
        work.mkdir(parents=True)
        try:
            source = work / "Bindings.cs"
            source.write_text(code, encoding="utf-8")
            catalog = work / "sources/public-linkage.json"
            atomic_json(catalog, public_catalog(plan, packs, self.contracts, self.target))
            assemblies = [a["assembly"] for a in self.contracts.values()] + [a["assembly"] for a in packs.values()]
            result = self.tool.invoke("link", output=str(work), name="Confectory.App",
                                      sources=[str(source)], references=assemblies,
                                      resources=[{"path": str(catalog), "name": "public-linkage.json"}])
            if not isinstance(result.get("run"), list) or not result["run"] or not all(isinstance(x, str) for x in result["run"]):
                raise BuildError("TOOL_PROTOCOL", "Link tool must return an executable command")
            artifacts = result.get("artifacts")
            if not isinstance(artifacts, dict) or "application" not in artifacts:
                raise BuildError("TOOL_PROTOCOL", "Link tool must return an application artifact")
            for path in artifacts.values():
                if not owned_path(work, path).is_file():
                    raise BuildError("TOOL_PROTOCOL", f"Missing final artifact {path}")
            if "publicCatalog" not in artifacts or digest(owned_path(work, artifacts["publicCatalog"]).read_bytes()) != digest(catalog.read_bytes()):
                raise BuildError("TOOL_PROTOCOL", "Target must preserve the public linkage catalog")
            dest = output_root / (key + "-" + uuid.uuid4().hex[:12])
            os.replace(work, dest)
            # Commands/paths reported by the tool must use the output root for its products.
            run = [part.replace(str(work), str(dest)) for part in result["run"]]
            reached = {ident.split("::")[0] for ident in plan.reached}
            included = sorted(reached)
            report = {"mode": "final", "project": self.registry.project["namespace"], "target": self.target,
                      "entry": self.registry.project["entry"], "key": key, "output": str(dest), "run": run,
                      "publicCatalog": artifacts["publicCatalog"].replace(str(work), str(dest)),
                      "registeredPacks": sorted(self.registry.packs), "includedPacks": included,
                      "excludedPacks": sorted(set(self.registry.packs) - reached),
                      "implementationArtifacts": packs, "contractArtifacts": self.contracts,
                      "bindings": list(plan.bindings.values()), "warnings": self.registry.warnings,
                      "statistics": self.stats, "tool": self.tool.info}
            atomic_json(dest / "build-report.json", report)
            # This is the only pointer to the latest complete result; failures never update it.
            atomic_json(output_root / "latest.json", report)
            return report
        except Exception:
            shutil.rmtree(work, ignore_errors=True)
            raise

    def validate(self):
        planner = Planner(self.registry, self.target)
        for ns, manifest in self.registry.packs.items():
            for local, locator in manifest["elements"].items():
                ident = ns + "::" + local
                e = self.registry.effective(ident)
                planner.structural(ident)
                if e["kind"] == "implementation":
                    self.registry.implementation(e["for"], ident, ident, e["loc"])
                elif e["kind"] == "module":
                    planner.module(ident)
                for ref in e["uses"] + e["contains"]:
                    self.registry.get(ref["id"], ref["kind"], ref.get("origin", ident), ref["loc"])
                for fn, provider in e["provides"].items():
                    self.registry.implementation(fn, provider["id"], provider.get("origin", ident), provider["loc"])
        return {"mode": "validate", "warnings": self.registry.warnings, "statistics": self.stats}
