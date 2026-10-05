"""Small locators, lazy owned documents, inheritance and scope-aware linking."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path

from .declarations import BuildError, Parser, owned_path, signature_key


def digest(value) -> str:
    raw = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".{os.getpid()}.tmp")
    temp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


class Documents:
    """Per-file change stamps avoid reading unrelated, unchanged declaration layers.

    Includes ctime, inode and device, so restoring an old mtime is not enough to
    reuse stale text. Contents are hashed whenever a stamp changes. State is a
    performance cache, never a distributable pack or source of semantic identity.
    """
    FORMAT = "declarations-v3"

    def __init__(self, cache: Path, stats: dict):
        self.cache, self.stats = cache, stats

    def read(self, path: Path, role: str):
        path = path.resolve()
        try:
            st = path.stat()
        except OSError as ex:
            raise BuildError("MISSING_FILE", f"Cannot read {path}: {ex}", {"file": str(path)}) from ex
        stamp = [st.st_mtime_ns, st.st_ctime_ns, st.st_size, st.st_ino, st.st_dev]
        key = digest([self.FORMAT, str(path), role])
        cache_file = self.cache / (key + ".json")
        try:
            cached = json.loads(cache_file.read_text())
            if cached["stamp"] == stamp and cached.get("checksum") == digest(cached["data"]):
                return copy.deepcopy(cached["data"])
        except (OSError, ValueError, KeyError, TypeError):
            pass
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8")
        except (OSError, UnicodeError) as ex:
            raise BuildError("SOURCE_READ", f"Cannot read UTF-8 source {path}: {ex}", {"file": str(path)}) from ex
        self.stats["readDocuments"].append(str(path))
        if role == "manifest":
            data = Parser(text, path).manifest()
        elif role == "element":
            data = Parser(text, path).element()
        else:
            data = {"text": text, "hash": digest(raw)}
        if role != "body":
            self.stats["parsedDocuments"].append(str(path))
        atomic_json(cache_file, {"stamp": stamp, "contentHash": digest(raw),
                                 "checksum": digest(data), "data": data})
        return copy.deepcopy(data)


class Registry:
    def __init__(self, project_path: Path, documents: Documents, stats: dict):
        self.documents, self.stats = documents, stats
        self.project_path = project_path.resolve()
        project = documents.read(self.project_path, "manifest")
        if project["kind"] != "project":
            raise BuildError("PROJECT_INPUT", "Build input must be a ProjectPack", project["loc"])
        self.project = project
        self.packs = {}
        self.paths = {}
        self.elements = {}
        self.effective_cache = {}
        self.warnings = []
        self._register(self.project_path, project, project["namespace"])
        for ns, locator in project["registry"].items():
            if ns in self.packs:
                raise BuildError("DUPLICATE_NAMESPACE", f"Namespace {ns} is registered more than once", locator["loc"])
            path = (self.project_path.parent / locator["path"]).resolve()
            self._register(path, documents.read(path, "manifest"), ns)
        for ns, pack in self.packs.items():
            for dep, expectation in pack["dependencies"].items():
                if dep == ns:
                    raise BuildError("DEPENDENCY", "A pack must not depend on itself", expectation["loc"])
                if dep not in self.packs:
                    raise BuildError("MISSING_NAMESPACE", f"Dependency {dep} is not registered", expectation["loc"])
                requested = expectation["version"]
                actual = self.packs[dep]["version"]
                if requested != "*" and requested != actual:
                    self.warnings.append({"severity": "warning", "code": "VERSION_MISMATCH",
                                          "message": f"{ns} expects {dep} {requested}; selected {actual}",
                                          "location": expectation["loc"]})

    def _register(self, path, manifest, expected):
        ns = manifest["namespace"]
        if ns in self.packs:
            raise BuildError("DUPLICATE_NAMESPACE", f"Duplicate namespace {ns}", manifest["loc"])
        if ns != expected:
            raise BuildError("REGISTRY_ID", f"Registry {expected} points to namespace {ns}", manifest["loc"])
        if manifest["kind"] == "project" and self.packs:
            raise BuildError("PROJECT_INPUT", "Nested ProjectPacks are not pack registry entries", manifest["loc"])
        self.packs[ns], self.paths[ns] = manifest, path
        for locator in manifest["elements"].values():
            owned_path(path.parent, locator["path"], locator["loc"])

    def get(self, ident: str, expected: str | None = None, source: str | None = None, loc=None):
        ns, local = ident.split("::")
        if source:
            owner = source.split("::")[0]
            if ns != owner and ns not in self.packs[owner]["dependencies"]:
                raise BuildError("UNDECLARED_DEPENDENCY", f"{source} refers to {ns} without a direct dependency", loc)
        if ns not in self.packs:
            raise BuildError("MISSING_NAMESPACE", f"Namespace {ns} is not registered", loc)
        locator = self.packs[ns]["elements"].get(local)
        if not locator:
            raise BuildError("MISSING_ELEMENT", f"No declaration for {ident}", loc)
        if expected and locator["kind"] != expected:
            raise BuildError("ELEMENT_KIND", f"{ident} is {locator['kind']}, expected {expected}", loc or locator["loc"])
        if ident not in self.elements:
            path = owned_path(self.paths[ns].parent, locator["path"], locator["loc"])
            e = self.documents.read(path, "element")
            if e["id"] != ident or e["kind"] != locator["kind"]:
                raise BuildError("LOCATOR_MISMATCH", f"Locator {ident} {locator['kind']} points to {e['id']} {e['kind']}", e["loc"])
            self.elements[ident] = e
        return self.elements[ident]

    def effective(self, ident: str, stack=()):
        if ident in stack:
            raise BuildError("INHERITANCE_CYCLE", "Inheritance cycle: " + " -> ".join((*stack, ident)), self.get(ident)["loc"])
        if ident in self.effective_cache:
            return self.effective_cache[ident]
        e = copy.deepcopy(self.get(ident))
        if e["parent"]:
            parent = self.get(e["parent"], e["kind"], ident, e["loc"])
            p = self.effective(parent["id"], (*stack, ident))
            if e["signature"] and signature_key(e["signature"]) != signature_key(p["signature"]):
                raise BuildError("CONTRACT_MISMATCH", "Inherited function/implementation signature changed", e["loc"])
            if e["kind"] == "implementation" and e["for"] != p["for"]:
                raise BuildError("IMPLEMENTATION_ID", "Implementation inheritance cannot change function identity", e["loc"])
            for key in ("values", "provides", "requires", "defaults", "imports", "bodies", "options"):
                e[key] = {**copy.deepcopy(p[key]), **e[key]}
            for key in ("modules", "includes", "uses", "contains"):
                e[key] = copy.deepcopy(p[key]) + e[key]
            if not e["descriptionPresent"]:
                e["description"] = p["description"]
            if e["tool"] is None and p["tool"] is not None:
                e["tool"] = p["tool"]
                e["toolOrigin"] = p.get("toolOrigin", p["id"])
        self.effective_cache[ident] = e
        return e

    def signature(self, ident, expected, source, loc):
        fn = self.get(ident, "function", source, loc)
        if signature_key(fn["signature"]) != signature_key(expected):
            raise BuildError("CONTRACT_MISMATCH", f"Incompatible signature for {ident}: expected {signature_key(expected)}, actual {signature_key(fn['signature'])}", loc)
        if ident not in self.stats["checkedContracts"]:
            self.stats["checkedContracts"].append(ident)
        return fn

    def implementation(self, fn: str, impl: str, source: str, loc):
        f = self.get(fn, "function", source, loc)
        i = self.effective(self.get(impl, "implementation", source, loc)["id"])
        if i["for"] != fn:
            raise BuildError("IMPLEMENTATION_ID", f"{impl} implements {i['for']}, not {fn}", loc)
        self.signature(fn, i["signature"], i["id"], i["loc"])
        for imported in i["imports"].values():
            origin = imported.get("origin", impl)
            self.signature(imported["id"], imported["signature"], origin, imported["loc"])
            if imported["scope"]:
                scope = self.get(imported["scope"], source=origin, loc=imported["loc"])
                if scope["kind"] in {"implementation", "module", "buildtarget"}:
                    raise BuildError("SCOPE_KIND", "Function import scope must be a consumer element", imported["loc"])
        return i


class Planner:
    def __init__(self, registry: Registry, target: str):
        self.r, self.target = registry, target
        self.reached = set()
        self.bindings = {}
        self.implementations = {}
        self.module_cache = {}
        self.structural_done = set()
        self.visited = set()

    def structural(self, ident, stack=()):
        if ident in stack:
            raise BuildError("STRUCTURAL_CYCLE", "Structural cycle: " + " -> ".join((*stack, ident)), self.r.get(ident)["loc"])
        if ident in self.structural_done:
            return
        e = self.r.get(ident)
        edges = [(e["parent"], e["kind"], e["loc"])] if e["parent"] else []
        edges += [(x["id"], x["kind"], x["loc"]) for x in e["contains"]]
        edges += [(x["id"], "module", x["loc"]) for x in e["includes"] + e["modules"]]
        for ref, kind, loc in edges:
            self.r.get(ref, kind, ident, loc)
            self.structural(ref, (*stack, ident))
        self.structural_done.add(ident)

    def module(self, ident, stack=()):
        if ident in stack:
            raise BuildError("MODULE_CYCLE", "Module inclusion cycle: " + " -> ".join((*stack, ident)), self.r.get(ident)["loc"])
        if ident in self.module_cache:
            return self.module_cache[ident]
        e = self.r.effective(self.r.get(ident, "module")["id"])
        self.structural(ident)
        required, defaults = {}, {}
        for child in e["includes"]:
            self.r.get(child["id"], "module", child.get("origin", ident), child["loc"])
            req, defs = self.module(child["id"], (*stack, ident))
            required.update(req)
            for fn, choices in defs.items():
                defaults.setdefault(fn, {}).update(choices)
        for fn, contract in e["requires"].items():
            self.r.signature(fn, contract["signature"], contract.get("origin", ident), contract["loc"])
            required[fn] = contract
        for fn, provider in e["defaults"].items():
            if fn not in required:
                raise BuildError("MODULE_CONTRACT", f"Default {fn} is not required by module {ident}", provider["loc"])
            self.r.implementation(fn, provider["id"], provider.get("origin", ident), provider["loc"])
            defaults.setdefault(fn, {})[provider["id"]] = provider
        self.module_cache[ident] = required, defaults
        return required, defaults

    def modules_for(self, owner):
        requirements, defaults = {}, {}
        for ref in self.r.effective(owner)["modules"]:
            self.r.get(ref["id"], "module", ref.get("origin", owner), ref["loc"])
            req, defs = self.module(ref["id"])
            requirements.update(req)
            for fn, choices in defs.items():
                defaults.setdefault(fn, {}).update(choices)
        return requirements, defaults

    def visit(self, ident, expected=None, source=None, loc=None, active=True):
        e = self.r.get(ident, expected, source, loc)
        if (ident, active) in self.visited:
            return
        self.visited.add((ident, active))
        self.reached.add(ident)
        self.structural(ident)
        effective = self.r.effective(ident)
        if e["parent"]:
            self.visit(e["parent"], e["kind"], ident, e["loc"], active=False)
        for ref in effective["uses"] + effective["contains"]:
            self.visit(ref["id"], ref["kind"], ref.get("origin", ident), ref["loc"], active=active and ref["kind"] != "function")
            if active and ref["kind"] == "function":
                self.bind(ident, ref["id"])
        for ref in effective["modules"] + effective["includes"]:
            self.visit(ref["id"], "module", ref.get("origin", ident), ref["loc"], active=False)
        for fn, provider in effective["provides"].items():
            self.r.implementation(fn, provider["id"], provider.get("origin", ident), provider["loc"])
        if e["kind"] == "module":
            self.module(ident)
        elif active and e["kind"] not in {"implementation", "buildtarget"}:
            requirements, _ = self.modules_for(ident)
            for fn in requirements:
                self.bind(ident, fn)

    def bind(self, owner, fn):
        key = (owner, fn)
        if key in self.bindings:
            return
        owner_e = self.r.effective(owner)
        function = self.r.get(fn, "function")
        function_e = self.r.effective(fn)
        # Explicit scope binding, then independently declared function binding.
        declared = owner_e["provides"].get(fn) or function_e["provides"].get(fn)
        if declared:
            provider = declared
            source = declared.get("origin", owner if fn in owner_e["provides"] else fn)
        else:
            _, defaults = self.modules_for(owner)
            choices = dict(defaults.get(fn, {}))
            if owner != fn:
                _, function_defaults = self.modules_for(fn)
                choices.update(function_defaults.get(fn, {}))
            if not choices:
                raise BuildError("MISSING_IMPLEMENTATION", f"No implementation for {fn} in scope {owner}", function["loc"])
            if len(choices) > 1:
                raise BuildError("DEFAULT_CONFLICT", f"Conflicting defaults for {fn} in {owner}: {', '.join(sorted(choices))}", owner_e["loc"])
            provider = next(iter(choices.values()))
            # Already checked the default's direct dependency in its owner module.
            source = provider["id"]
        impl = self.r.implementation(fn, provider["id"], source, provider["loc"])
        body = impl["bodies"].get(self.target) or impl["bodies"].get("common")
        if not body:
            raise BuildError("MISSING_TARGET_IMPLEMENTATION", f"{impl['id']} has neither {self.target} nor common body", impl["loc"])
        node = {"owner": owner, "function": fn, "implementation": impl["id"], "imports": {}}
        # Publish the graph node before following imports: recursive calls are valid.
        self.bindings[key] = node
        self.implementations[impl["id"]] = impl
        self.visit(owner)
        self.visit(fn, "function", active=False)
        self.visit(impl["id"], "implementation")
        for alias, imported in impl["imports"].items():
            scope = imported["scope"] or owner
            self.visit(imported["id"], "function", imported.get("origin", impl["id"]), imported["loc"], active=False)
            if imported["scope"]:
                self.visit(scope, source=imported.get("origin", impl["id"]), loc=imported["loc"])
            self.bind(scope, imported["id"])
            node["imports"][alias] = (scope, imported["id"])

    def plan(self):
        p = self.r.project
        if not p["entry"]:
            raise BuildError("MISSING_ENTRY", "ProjectPack must declare an entry function", p["loc"])
        entry = self.r.get(p["entry"], "function", p["namespace"] + "::<project>", p["loc"])
        sig = entry["signature"]
        if sig["args"] or sig["return"] not in {"int", "void"}:
            raise BuildError("ENTRY_CONTRACT", "Entry contract must be () -> int or () -> void", entry["loc"])
        self.bind(p["entry"], p["entry"])
        for ref in p["always"]:
            self.visit(ref["id"], source=p["namespace"] + "::<project>", loc=ref["loc"])
            if self.r.get(ref["id"])["kind"] == "function":
                self.bind(ref["id"], ref["id"])
        return self
