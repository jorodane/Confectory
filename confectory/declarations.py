"""Owned declarations, source locations and a deliberately small structure grammar."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


KINDS = {"function", "implementation", "module", "category", "concept", "schema",
         "object", "stage", "view", "buildtarget"}
TYPES = {"void", "bool", "int", "long", "float", "double", "string"}
KEYWORDS = set("abstract as base bool break byte case catch char checked class const continue "
               "decimal default delegate do double else enum event explicit extern false finally "
               "fixed float for foreach goto if implicit in int interface internal is lock long "
               "namespace new null object operator out override params private protected public "
               "readonly ref return sbyte sealed short sizeof stackalloc static string struct "
               "switch this throw true try typeof uint ulong unchecked unsafe ushort using "
               "virtual void volatile while".split())


class BuildError(Exception):
    def __init__(self, code: str, message: str, loc: dict | None = None):
        self.diagnostic = {"severity": "error", "code": code, "message": message,
                           "location": loc or {}}
        super().__init__(message)

    def __str__(self):
        p = self.diagnostic["location"]
        return f"{p.get('file', '<build>')}({p.get('line', 1)},{p.get('column', 1)}): " \
               f"{self.diagnostic['code']}: {self.diagnostic['message']}"


@dataclass
class Token:
    value: str
    loc: dict
    quoted: bool = False


def lex(text: str, path: Path) -> list[Token]:
    pattern = re.compile(r'(?P<space>\s+)|(?P<comment>//[^\n]*)|'
                         r'(?P<string>"(?:[^"\\]|\\.)*")|(?P<arrow>->)|'
                         r'(?P<qid>[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*'
                         r'::[A-Za-z_][A-Za-z_0-9]*)|'
                         r'(?P<name>[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*)|'
                         r'(?P<number>-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|'
                         r'(?P<punct>[{}();,=\[\]])')
    pos = 0
    line, col = 1, 1
    tokens = []
    while pos < len(text):
        m = pattern.match(text, pos)
        loc = {"file": str(path), "line": line, "column": col}
        if not m:
            raise BuildError("SYNTAX", f"Unexpected character {text[pos]!r}", loc)
        raw = m.group()
        if m.lastgroup not in {"space", "comment"}:
            try:
                value = json.loads(raw) if m.lastgroup == "string" else raw
            except ValueError as e:
                raise BuildError("SYNTAX", f"Invalid quoted string: {e}", loc) from e
            tokens.append(Token(value, loc, m.lastgroup == "string"))
        newlines = raw.count("\n")
        col = len(raw.rsplit("\n", 1)[-1]) + 1 if newlines else col + len(raw)
        line += newlines
        pos = m.end()
    tokens.append(Token("<eof>", {"file": str(path), "line": line, "column": col}))
    return tokens


class Parser:
    def __init__(self, text: str, path: Path):
        self.tokens = lex(text, path)
        self.i = 0

    @property
    def t(self):
        return self.tokens[self.i]

    def pop(self):
        t = self.t
        self.i += 1
        return t

    def eat(self, value: str):
        if self.t.value == value and not self.t.quoted:
            self.pop()
            return True
        return False

    def expect(self, value: str):
        if not self.eat(value):
            raise BuildError("SYNTAX", f"Expected {value!r}; found {self.t.value!r}", self.t.loc)

    def name(self, *, qualified=False, csharp=False):
        t = self.pop()
        pattern = (r"[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*"
                   r"::[A-Za-z_][A-Za-z_0-9]*" if qualified else
                   r"[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*")
        if t.quoted or not re.fullmatch(pattern, t.value):
            raise BuildError("IDENTIFIER", "Expected a namespace-qualified element ID" if qualified
                             else "Expected an identifier", t.loc)
        if csharp and ("." in t.value or t.value in KEYWORDS):
            raise BuildError("IDENTIFIER", "Expected a C# parameter/import identifier", t.loc)
        return t.value

    def string(self):
        t = self.pop()
        if not t.quoted:
            raise BuildError("SYNTAX", "Expected a quoted string", t.loc)
        return t.value

    def kind(self):
        t = self.pop()
        if t.value not in KINDS or t.quoted:
            raise BuildError("KIND", f"Unknown element kind {t.value!r}", t.loc)
        return t.value

    def type(self, parameter=False):
        t = self.pop()
        if t.quoted or t.value not in TYPES or (parameter and t.value == "void"):
            raise BuildError("TYPE", f"Unsupported contract type {t.value!r}", t.loc)
        value = t.value
        if self.eat("["):
            self.expect("]")
            if value == "void":
                raise BuildError("TYPE", "void[] is invalid", t.loc)
            value += "[]"
        return value

    def signature(self, named: bool):
        self.expect("(")
        args = []
        while not self.eat(")"):
            typ = self.type(parameter=True)
            name = self.name(csharp=True) if named else f"arg{len(args)}"
            if name == "calls" or any(a["name"] == name for a in args):
                raise BuildError("DUPLICATE_PARAMETER", f"Duplicate/reserved parameter {name}", self.t.loc)
            args.append({"type": typ, "name": name})
            if self.eat(")"):
                break
            self.expect(",")
        self.expect("->")
        return {"args": args, "return": self.type()}

    def unique(self, mapping, key, value, loc):
        if key in mapping:
            raise BuildError("DUPLICATE_DECLARATION", f"Duplicate declaration {key}", loc)
        mapping[key] = value

    def manifest(self):
        t = self.pop()
        if t.value not in {"pack", "project"} or t.quoted:
            raise BuildError("SYNTAX", "Expected pack or project", t.loc)
        result = {"kind": t.value, "namespace": self.name(), "loc": t.loc,
                  "elements": {}, "dependencies": {}, "registry": {}, "targets": {},
                  "always": [], "version": "", "entry": None, "description": ""}
        self.expect("version")
        result["version"] = self.string()
        self.expect("{")
        seen = set()
        while not self.eat("}"):
            item = self.pop()
            key = item.value
            if key == "element":
                name = self.name()
                if "." in name:
                    raise BuildError("IDENTIFIER", "Element IDs must be simple identifiers", item.loc)
                self.unique(result["elements"], name,
                            {"kind": self.kind(), "path": self.string(), "loc": item.loc}, item.loc)
            elif key == "dependency":
                ns = self.name()
                self.expect("version")
                self.unique(result["dependencies"], ns,
                            {"version": self.string(), "loc": item.loc}, item.loc)
            elif key == "registry":
                ns = self.name()
                self.unique(result["registry"], ns, {"path": self.string(), "loc": item.loc}, item.loc)
            elif key == "target":
                name = self.name()
                self.unique(result["targets"], name,
                            {"id": self.name(qualified=True), "loc": item.loc}, item.loc)
            elif key == "always":
                result["always"].append({"id": self.name(qualified=True), "loc": item.loc})
            elif key in {"entry", "description"}:
                if key in seen:
                    raise BuildError("DUPLICATE_DECLARATION", f"Duplicate {key}", item.loc)
                seen.add(key)
                result[key] = self.name(qualified=True) if key == "entry" else self.string()
            else:
                raise BuildError("SYNTAX", f"Unknown manifest statement {key!r}", item.loc)
            self.expect(";")
        self.expect("<eof>")
        if result["kind"] == "pack" and (result["entry"] or result["registry"] or result["targets"]):
            raise BuildError("PACK_BOUNDARY", "Only a ProjectPack may define registry, entry or targets", t.loc)
        return result

    def element(self):
        start = self.t
        kind = self.kind()
        ident = self.name(qualified=True)
        e = {"kind": kind, "id": ident, "loc": start.loc, "parent": None,
             "modules": [], "includes": [], "requires": {}, "defaults": {}, "provides": {},
             "uses": [], "contains": [], "values": {}, "imports": {}, "bodies": {},
             "options": {}, "description": "", "descriptionPresent": False,
             "signature": None, "for": None, "tool": None}
        if kind == "implementation":
            self.expect("for")
            e["for"] = self.name(qualified=True)
        if kind in {"function", "implementation"}:
            e["signature"] = self.signature(named=True)
        if self.eat("extends"):
            e["parent"] = self.name(qualified=True)
        self.expect("{")
        seen = set()
        while not self.eat("}"):
            t = self.pop()
            key = t.value
            if key == "description":
                if key in seen:
                    raise BuildError("DUPLICATE_DECLARATION", "Duplicate description", t.loc)
                seen.add(key)
                e[key] = self.string()
                e["descriptionPresent"] = True
            elif key == "module":
                e["modules"].append({"id": self.name(qualified=True), "loc": t.loc})
            elif key == "include" and kind == "module":
                e["includes"].append({"id": self.name(qualified=True), "loc": t.loc})
            elif key in {"require", "default"} and kind == "module":
                fn = self.name(qualified=True)
                if key == "require":
                    self.unique(e["requires"], fn, {"signature": self.signature(named=False), "loc": t.loc}, t.loc)
                else:
                    self.expect("with")
                    self.unique(e["defaults"], fn, {"id": self.name(qualified=True), "loc": t.loc}, t.loc)
            elif key == "provide":
                fn = self.name(qualified=True)
                self.expect("with")
                self.unique(e["provides"], fn, {"id": self.name(qualified=True), "loc": t.loc}, t.loc)
            elif key in {"use", "contain"}:
                ref = {"kind": self.kind(), "id": self.name(qualified=True), "loc": t.loc}
                e["uses" if key == "use" else "contains"].append(ref)
            elif key == "value":
                name = self.name()
                self.expect("=")
                value = self.pop()
                try:
                    data = value.value if value.quoted else json.loads(value.value)
                    if data is None or isinstance(data, (list, dict)):
                        raise ValueError("only primitive metadata values are supported")
                except ValueError as ex:
                    raise BuildError("VALUE", f"Invalid metadata value: {ex}", value.loc) from ex
                self.unique(e["values"], name, {"value": data, "origin": ident, "loc": t.loc}, t.loc)
            elif key == "body" and kind == "implementation":
                target = self.name()
                self.unique(e["bodies"], target, {"path": self.string(), "loc": t.loc}, t.loc)
            elif key == "import" and kind == "implementation":
                fn = self.name(qualified=True)
                self.expect("as")
                alias = self.name(csharp=True)
                sig = self.signature(named=False)
                scope = self.name(qualified=True) if self.eat("in") else None
                self.unique(e["imports"], alias,
                            {"id": fn, "signature": sig, "scope": scope, "loc": t.loc}, t.loc)
            elif key == "tool" and kind == "buildtarget":
                if e["tool"] is not None:
                    raise BuildError("DUPLICATE_DECLARATION", "Duplicate target tool", t.loc)
                e["tool"] = self.string()
            elif key == "option" and kind == "buildtarget":
                name = self.name()
                self.unique(e["options"], name, self.string(), t.loc)
            else:
                raise BuildError("SYNTAX", f"Invalid {kind} statement {key!r}", t.loc)
            self.expect(";")
        self.expect("<eof>")
        for key in ("requires", "defaults", "provides", "imports", "bodies"):
            for item in e[key].values():
                item["origin"] = ident
        for key in ("modules", "includes", "uses", "contains"):
            for item in e[key]:
                item["origin"] = ident
        return e


def signature_key(sig: dict) -> tuple:
    return tuple(a["type"] for a in sig["args"]), sig["return"]


def owned_path(root: Path, path: str, loc: dict | None = None) -> Path:
    p = (root / path).resolve()
    try:
        p.relative_to(root.resolve())
    except ValueError as ex:
        raise BuildError("OWNERSHIP", f"Path escapes its owning pack: {path}", loc) from ex
    return p
