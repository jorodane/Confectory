# BuildParticipation

Generic version-1 plan JSON: outputs each declare unique ID, ProjectPack, entry and target, with optional priority. Priority then ordinal ID determines order. Describe/Validate use public Registry/Planner metadata only, never target fingerprint tools, lifecycle hooks or project runtime. Validate is static contract/planning validation; C# compilation belongs to explicit Build.

Build uses existing public Builder/provider mechanisms for every output, selecting entry in memory without rewriting source. Usage closure decides whether UI or another role is included. No Dedicated/server special case exists. A successful whole plan publishes its artifact receipt under local generated state. A failed output retains the prior successful whole-plan receipt and immutable artifacts; any newly built partial artifacts are reported and are not automatically activated or launched. LastSuccessful reads that receipt without building.

Core and target bootstrap tools remain explicit. Registration/build/runtime load are distinct. Native packaging/device coverage follows the selected target and is never inferred from managed compilation.
