"""Contract-derived C# only; no compiler or platform packaging logic."""
from __future__ import annotations

import json

from .resolution import digest


ABI = "confectory-csharp-interface-v1"


def symbol(ident):
    return "E" + digest(ident)[:24]


def interface(ident):
    return f"global::Confectory.Contracts.{symbol(ident)}.IInvoke"


def implementation(ident):
    ns = ident.split("::")[0]
    return f"global::Confectory.Implementations.{symbol(ns)}.{symbol(ident)}"


def parameters(sig):
    return ", ".join(f"{a['type']} {a['name']}" for a in sig["args"])


def arguments(sig):
    return ", ".join(a["name"] for a in sig["args"])


def contract_source(fn):
    sig = fn["signature"]
    return f"""// Generated public function contract for {fn['id']}; {ABI}
namespace Confectory.Contracts.{symbol(fn['id'])}
{{
    public interface IInvoke
    {{
        {sig['return']} Invoke({parameters(sig)});
    }}
}}
"""


def implementation_source(e, body, path):
    sig = e["signature"]
    imports = "\n".join(f"        {interface(i['id'])} {name} {{ get; }}"
                        for name, i in sorted(e["imports"].items()))
    # The compiler maps body errors to the real owned source and its line number.
    quoted_path = json.dumps(str(path))
    return f"""// Generated implementation boundary for {e['id']}; {ABI}
using System;
namespace Confectory.Implementations.{symbol(e['id'].split('::')[0])}
{{
    public sealed class {symbol(e['id'])} : {interface(e['for'])}
    {{
        public interface IImports
        {{
{imports}
        }}
        private readonly IImports calls;
        public {symbol(e['id'])}(IImports calls) {{ this.calls = calls; }}
        public {sig['return']} Invoke({parameters(sig)})
        {{
#line 1 {quoted_path}
{body}
#line default
        }}
    }}
}}
"""


def binding_symbol(key):
    return "B" + digest(list(key))[:24]


def final_source(plan):
    lines = [f"// Generated actual provider connections; {ABI}"]
    for key, node in sorted(plan.bindings.items()):
        fn = plan.r.get(node["function"], "function")
        sig = fn["signature"]
        name = binding_symbol(key)
        impl = implementation(node["implementation"])
        prefix = "return " if sig["return"] != "void" else ""
        lines += [f"internal sealed class {name} : {interface(fn['id'])}", "{",
                  f"    public {sig['return']} Invoke({parameters(sig)})",
                  "    {", f"        {prefix}new {impl}(new {name}Imports()).Invoke({arguments(sig)});",
                  "    }", "}", f"internal sealed class {name}Imports : {impl}.IImports", "{"]
        for alias, imported_key in sorted(node["imports"].items()):
            lines.append(f"    public {interface(imported_key[1])} {alias} => new {binding_symbol(imported_key)}();")
        lines.append("}")
    entry = plan.r.project["entry"]
    invocation = f"new {binding_symbol((entry, entry))}().Invoke()"
    return_type = plan.r.get(entry)["signature"]["return"]
    lines += ["internal static class Program", "{", "    public static int Main()", "    {",
              f"        return {invocation};" if return_type == "int" else f"        {invocation}; return 0;",
              "    }", "}"]
    return "\n".join(lines) + "\n"


def public_catalog(plan, packs, contracts, target):
    """Versioned linked surface, not a mod loader or an inheritance permission.

    Generated type names are metadata for linkage tools; authored connections
    still use namespace-qualified IDs. Unlinked project exports are future work.
    """
    from pathlib import Path
    elements = []
    for ident in sorted(plan.reached):
        e = plan.r.effective(ident)
        item = {"id": ident, "kind": e["kind"], "parent": e["parent"], "description": e["description"]}
        if e["signature"]:
            item["contract"] = e["signature"]
        if e["values"]:
            item["metadataValues"] = {key: {"value": value["value"], "origin": value["origin"]}
                                      for key, value in e["values"].items()}
        elements.append(item)
    functions = [{"id": ident, "contract": plan.r.get(ident)["signature"],
                  "interfaceType": interface(ident).removeprefix("global::"),
                  "assembly": Path(contracts[ident]["assembly"]).name}
                 for ident in sorted(contracts)]
    implementations = []
    for ident, e in sorted(plan.implementations.items()):
        ns = ident.split("::")[0]
        implementations.append({"id": ident, "function": e["for"],
                                "implementationType": implementation(ident).removeprefix("global::"),
                                "assembly": Path(packs[ns]["assembly"]).name,
                                "bodySelection": target if target in e["bodies"] else "common"})
    namespaces = sorted({i.split("::")[0] for i in plan.reached})
    return {"formatVersion": 1, "abi": ABI, "surface": "linked-elements",
            "project": plan.r.project["namespace"], "entry": plan.r.project["entry"], "target": target,
            "packs": [{"namespace": ns, "version": plan.r.packs[ns]["version"]} for ns in namespaces],
            "elements": elements, "functions": functions, "implementations": implementations,
            "bindings": list(plan.bindings.values()), "coreProvidesRuntimeModLoader": False}
