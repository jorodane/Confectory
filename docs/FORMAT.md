# Declaration format and target protocol

This is a dedicated structure language, not XML, JSON pack data or a new general-purpose programming language. UTF-8 `.cpack` and `.celem` files support `//` comments, quoted JSON strings and semicolon-terminated statements. Identifiers currently use ASCII letters, digits and underscores; namespaces additionally use dots. Cross-pack references always use `Namespace::Element`.

## Manifests and locations

```text
project Example.App version "0.1.0" {
    entry Example.App::Main;
    registry Example.Api "../api/pack.cpack";
    registry Example.Provider "../provider/pack.cpack";
    registry Confectory.Build.DotNet "../../targets/dotnet/pack.cpack";
    dependency Example.Api version "0.1.0";
    dependency Example.Provider version "0.1.0";
    dependency Confectory.Build.DotNet version "0.1.0";
    target portable Confectory.Build.DotNet::Portable;
    element Main function "main.celem";
    element MainBody implementation "main_body.celem";
    // always Example.App::Extra;
}
```

A regular `pack Namespace version "..." { ... }` has dependency and element declarations but no project registry, target selection or entry. The namespace is the pack ID in this first format. Registry paths locate selected packs; they do not author a function/object connection. All element/body/tool locations stay inside their owning pack, including symlink resolution. A ProjectPack may locate external selected pack directories.

An entry must be a function with `() -> int` (exit status) or `() -> void`. Target mappings refer to `buildtarget` elements. `always` adds a validated root, not an exception to uniqueness or contract checking. Build traversal reads the linked graph; `validate` additionally inspects every registered declaration for otherwise-unreached errors, without compiling unused bodies.

## Functions and C# bodies

```text
function Example.Api::Greeting (string name) -> string {
    description "A greeting contract with no required implementation provider at authoring time";
}

implementation Example.Provider::GreetingBody
    for Example.Api::Greeting (string name) -> string {
    body common "greeting.csbody";
    body linux "greeting_linux.csbody";
}

function Example.App::Main () -> int {
    provide Example.App::Main with Example.App::MainBody;
    provide Example.Api::Greeting with Example.Provider::GreetingBody;
}

implementation Example.App::MainBody for Example.App::Main () -> int {
    import Example.Api::Greeting as Greeting (string) -> string;
    body common "main.csbody";
}
```

`main.csbody` contains ordinary C# statements:

```csharp
Console.WriteLine(calls.Greeting.Invoke("Confectory"));
return 0;
```

Generated imports expose typed interfaces, not provider classes. Parameter/import names are C# identifiers; `calls` is reserved for the generated imports object. Public signatures support primitive types and one-dimensional arrays. No author-supplied implementation DLL references, raw C# class declarations, asynchronous/generic signatures or implicit conversions between declared contracts are supported. C# within the selected body is type-checked by the target compiler; a broken target body does not fall back to common.

## Modules, inheritance and references

```text
module Example.App::Greeter {
    require Example.Api::Greeting (string) -> string;
    default Example.Api::Greeting with Example.Provider::GreetingBody;
    // include Example.App::AnotherModule;
}

object Example.App::Base {
    module Example.App::Greeter;
    value enabled = true;
    provide Example.Api::Greeting with Example.Provider::GreetingBody;
}

object Example.App::Child extends Example.App::Base {
    value enabled = false;
    value label = "";
    value count = 0;
    use object Example.App::Related;
}
```

`extends` accepts exactly one parent of the same kind. Fields omitted by the child inherit; explicit values and function bindings override, and new fields append. Module registrations/references compose without an implicit deletion operation. Effective values/bindings retain their declaration origin, including that origin's direct dependencies and owned body paths. Parent and sibling source models remain unchanged.

`use kind ID;` is an ordinary dependency/reference edge; `contain kind ID;` is a structural inclusion edge. `category`, `concept`, `schema`, `object`, `view` and `stage` use these same ownership/reference primitives, without implementing their future runtime/editor interpretation. Inheritance, containment and module inclusion must not cycle. Ordinary references and function calls can cycle.

Modules gather required functions and other modules. Functions retain independent IDs. An effective explicit binding (including an inherited one) wins over defaults; otherwise a unique default is required. Distinct provider IDs conflict. Repeated paths to the same provider ID count once. The independently declared function's own explicit provider applies when the consuming scope has no explicit binding. Selected implementations always match the required function identity and signature.

For a specific consumer scope, write an import such as:

```text
import Example.Api::Greeting as Greeting (string) -> string in Example.App::Child;
```

Without `in`, calls resolve in the current consumer scope. The final linker creates different typed adapters when independent objects bind the same function differently. It does not make global runtime state or infer object lifetimes.

## Build-target tool protocol

```text
buildtarget Confectory.Build.DotNet::Portable {
    tool "bin/Release/net8.0/Confectory.Build.DotNet.dll";
    option mode "portable";
}
```

Tools are executable owned files. A `.dll` tool is launched using `CONFECTORY_DOTNET`, the current .NET host, `DOTNET_ROOT`, or `dotnet` on PATH; other files are launched directly. The bundled target tool is built by `dotnet build Confectory.sln -c Release`. The core hashes its executable plus adjacent `.deps.json`/`.runtimeconfig.json` files; tools must fingerprint any further implementation dependencies. Requests use protocol `1` and one JSON object on stdin. Return one JSON object on stdout. Errors have `{"protocol":1,"ok":false,"error":"..."}` and a nonzero process exit status. The tool is a trusted compiler/packager, not a sandbox.

| Operation | Core supplies | Tool returns |
| --- | --- | --- |
| `fingerprint` | Target key and options | `fingerprint` covering compiler, references, tool settings and relevant host/runtime inputs |
| `compile-contract` | Generated source paths, name, output root and references | `artifacts.assembly` (interface definitions) and `artifacts.reference` (compile-time image) |
| `compile-pack` | Owned generated sources and public contract reference images | At least `artifacts.assembly`; no consumer implementation references |
| `link` | Actual generated bindings, executable contract/provider assemblies, catalog resource and output root | `artifacts.application`, preserved `artifacts.publicCatalog`, other package files and executable `run` array |

Every artifact must exist beneath the requested output root. Cache records hash all returned local artifacts. Final packaging copies executable contract assemblies, not reference-only images. The current .NET pack calls SDK `csc.dll` directly, emits .NET 8 runtime configuration, copies dependencies and optionally creates a Linux launcher. None of those compiler/package decisions lives in `src/Confectory.Core/Build.cs`.

## Public linkage catalog

Each successful result includes `public-linkage.json` with format version, ABI version, qualified entry/element IDs, linked pack versions, function signatures and generated interface mappings, actual provider mappings, selected target/common bodies, inheritance/metadata provenance and per-scope bindings. The catalog contains no absolute source paths. It describes `linked-elements`, not every unlinked project declaration, and grants no external mod inheritance rights. `coreProvidesRuntimeModLoader: false` describes the core boundary; it does not inspect or classify arbitrary user C# or negotiate loader-pack capabilities. Complete authoring exports and runtime loading remain separate pack responsibilities in [the mod extension requirement](MOD_EXTENSION_BOUNDARY.md).

Reference: Microsoft documents [reference assemblies](https://learn.microsoft.com/en-us/dotnet/standard/assembly/reference-assemblies) and [C# compiler output options](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/compiler-options/output). This implementation keeps reference-only images separate from executable interface assemblies.
