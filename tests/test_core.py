from __future__ import annotations

import json
import unittest
from pathlib import Path

from confectory.declarations import BuildError, Parser
from confectory.resolution import Planner
from tests.support import Fixture


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        self.addCleanup(self.f.close)

    def error(self, code, call):
        with self.assertRaises(BuildError) as ctx:
            call()
        self.assertEqual(code, ctx.exception.diagnostic["code"], str(ctx.exception))
        return ctx.exception.diagnostic

    def test_namespace_qualified_same_local_id(self):
        self.f.add("Api", "object", "Same", "object Api::Same {}")
        self.f.add("Provider", "object", "Same", "object Provider::Same {}")
        self.f.main("provide Api::Value with Provider::ValueBody; use object Api::Same; use object Provider::Same;")
        self.f.sync()
        plan, _ = self.f.plan()
        self.assertTrue({"Api::Same", "Provider::Same"} <= plan.reached)

    def test_duplicate_namespace(self):
        self.f.extra_registry["Alias"] = self.f.packs["Api"]["root"] / "pack.cpack"
        self.f.sync()
        self.error("DUPLICATE_NAMESPACE", self.f.registry)

    def test_duplicate_element(self):
        path = self.f.project
        path.write_text(path.read_text().replace('element Main function "Main.celem";', 'element Main function "Main.celem"; element Main object "other.celem";'))
        self.error("DUPLICATE_DECLARATION", self.f.registry)

    def test_wrong_locator_and_source_locations(self):
        self.f.add("Api", "function", "Value", "function Api::Other (int n) -> int {}")
        diag = self.error("LOCATOR_MISMATCH", self.f.plan)
        self.assertTrue(diag["location"]["file"].endswith("Value.celem"))
        self.assertEqual(diag["location"]["line"], 1)

    def test_missing_namespace(self):
        self.f.packs["App"]["dependencies"]["Absent"] = "1"
        self.f.sync()
        self.error("MISSING_NAMESPACE", self.f.registry)

    def test_missing_element(self):
        self.f.main("provide Api::Absent with Provider::ValueBody;")
        self.error("MISSING_ELEMENT", self.f.plan)

    def test_wrong_element_kind(self):
        self.f.main("provide Api::Value with Api::Value;")
        self.error("ELEMENT_KIND", self.f.plan)

    def test_undeclared_cross_pack_dependency(self):
        del self.f.packs["App"]["dependencies"]["Api"]
        self.f.sync()
        self.error("UNDECLARED_DEPENDENCY", self.f.plan)

    def test_provider_signature_mismatch(self):
        self.f.add("Provider", "implementation", "ValueBody", 'implementation Provider::ValueBody for Api::Value (string n) -> int { body common "value.csbody"; }')
        self.error("CONTRACT_MISMATCH", self.f.plan)

    def test_import_signature_mismatch(self):
        self.f.add("App", "implementation", "MainBody", 'implementation App::MainBody for App::Main () -> int { import Api::Value as Value (string) -> int; body common "main.csbody"; }')
        self.error("CONTRACT_MISMATCH", self.f.plan)

    def test_provider_wrong_function_identity(self):
        self.f.add("Api", "function", "Other", "function Api::Other (int n) -> int {}")
        self.f.add("Provider", "implementation", "ValueBody", 'implementation Provider::ValueBody for Api::Other (int n) -> int { body common "value.csbody"; }')
        self.f.sync()
        self.error("IMPLEMENTATION_ID", self.f.plan)

    def test_missing_final_provider(self):
        self.f.main()
        self.error("MISSING_IMPLEMENTATION", self.f.plan)

    def test_missing_target_and_common_body(self):
        self.f.add("Provider", "implementation", "ValueBody", 'implementation Provider::ValueBody for Api::Value (int n) -> int { body other "value.csbody"; }')
        self.error("MISSING_TARGET_IMPLEMENTATION", self.f.plan)

    def test_duplicate_target_body_and_unknown_syntax(self):
        self.error("DUPLICATE_DECLARATION", lambda: Parser('implementation X::F for X::Fn () -> int { body common "a"; body common "b"; }', Path("test.celem")).element())
        self.error("SYNTAX", lambda: Parser('object X::O { delete field; }', Path("test.celem")).element())
        self.error("TYPE", lambda: Parser('function X::F (object data) -> int {}', Path("test.celem")).element())

    def test_single_module_default(self):
        self.f.module("M")
        self.f.main("module App::M;")
        self.f.sync()
        plan, _ = self.f.plan()
        self.assertEqual("Provider::ValueBody", plan.bindings[("App::Main", "Api::Value")]["implementation"])

    def test_explicit_binding_beats_multiple_defaults(self):
        self.f.second_provider()
        self.f.module("M1")
        self.f.module("M2", "Provider::Second")
        self.f.main("module App::M1; module App::M2; provide Api::Value with Provider::ValueBody;")
        self.f.sync()
        plan, _ = self.f.plan()
        self.assertEqual("Provider::ValueBody", plan.bindings[("App::Main", "Api::Value")]["implementation"])

    def test_different_defaults_conflict(self):
        self.f.second_provider()
        self.f.module("M1")
        self.f.module("M2", "Provider::Second")
        self.f.main("module App::M1; module App::M2;")
        self.f.sync()
        self.error("DEFAULT_CONFLICT", self.f.plan)

    def test_same_default_deduplicates_through_nested_modules(self):
        self.f.module("M1")
        self.f.module("M2")
        self.f.add("App", "module", "Combined", "module App::Combined { include App::M1; include App::M2; }")
        self.f.main("module App::Combined;")
        self.f.sync()
        plan, _ = self.f.plan()
        self.assertEqual("Provider::ValueBody", plan.bindings[("App::Main", "Api::Value")]["implementation"])

    def test_module_missing_default(self):
        self.f.module("M", provider=None)
        self.f.main("module App::M;")
        self.f.sync()
        self.error("MISSING_IMPLEMENTATION", self.f.plan)

    def test_invalid_default_cannot_hide_behind_explicit_binding(self):
        self.f.module("M", "Api::Value")
        self.f.main("module App::M; provide Api::Value with Provider::ValueBody;")
        self.f.sync()
        self.error("ELEMENT_KIND", self.f.plan)

    def test_default_not_in_module_contract(self):
        self.f.add("App", "module", "M", "module App::M { default Api::Value with Provider::ValueBody; }")
        self.f.main("module App::M; provide Api::Value with Provider::ValueBody;")
        self.f.sync()
        self.error("MODULE_CONTRACT", self.f.plan)

    def test_module_contract_signature(self):
        self.f.add("App", "module", "M", "module App::M { require Api::Value (long) -> int; }")
        self.f.main("module App::M; provide Api::Value with Provider::ValueBody;")
        self.f.sync()
        self.error("CONTRACT_MISMATCH", self.f.plan)

    def test_inherited_values_and_provenance_without_parent_mutation(self):
        self.f.add("App", "object", "Parent", 'object App::Parent { value enabled = true; value count = 10; value label = "parent"; value inherited = 5; }')
        self.f.add("App", "object", "Child", 'object App::Child extends App::Parent { value enabled = false; value count = 0; value label = ""; value added = 2; }')
        self.f.add("App", "object", "Sibling", 'object App::Sibling extends App::Parent {}')
        self.f.sync()
        r, _ = self.f.registry()
        before = json.dumps(r.get("App::Parent"), sort_keys=True)
        child = r.effective("App::Child")["values"]
        self.assertEqual([False, 0, ""], [child[k]["value"] for k in ["enabled", "count", "label"]])
        self.assertEqual("App::Parent", child["inherited"]["origin"])
        self.assertEqual("App::Child", child["added"]["origin"])
        self.assertEqual(10, r.effective("App::Sibling")["values"]["count"]["value"])
        self.assertEqual(before, json.dumps(r.get("App::Parent"), sort_keys=True))

    def test_inherited_binding_beats_defaults(self):
        self.f.second_provider()
        self.f.module("M", "Provider::Second")
        self.f.add("App", "object", "Parent", "object App::Parent { provide Api::Value with Provider::ValueBody; }")
        self.f.add("App", "object", "Child", "object App::Child extends App::Parent { module App::M; }")
        self.f.main("use object App::Child;")
        self.f.add("App", "implementation", "MainBody", 'implementation App::MainBody for App::Main () -> int { import Api::Value as Value (int) -> int in App::Child; body common "main.csbody"; }')
        self.f.sync()
        plan, _ = self.f.plan()
        self.assertEqual("Provider::ValueBody", plan.bindings[("App::Child", "Api::Value")]["implementation"])

    def test_explicit_empty_description_overrides_parent(self):
        self.f.add("App", "object", "Parent", 'object App::Parent { description "parent"; }')
        self.f.add("App", "object", "Omitted", 'object App::Omitted extends App::Parent {}')
        self.f.add("App", "object", "Empty", 'object App::Empty extends App::Parent { description ""; }')
        self.f.sync()
        r, _ = self.f.registry()
        self.assertEqual("parent", r.effective("App::Omitted")["description"])
        self.assertEqual("", r.effective("App::Empty")["description"])

    def test_changed_text_with_restored_mtime_is_not_a_stale_document_hit(self):
        import os
        p = self.f.add("Unused", "object", "Dormant", "object Unused::Dormant { value n = 1; }")
        self.f.sync()
        before = p.stat()
        r, _ = self.f.registry()
        self.assertEqual(1, r.effective("Unused::Dormant")["values"]["n"]["value"])
        p.write_text(p.read_text().replace("= 1", "= 2"))
        os.utime(p, ns=(before.st_atime_ns, before.st_mtime_ns))
        r, _ = self.f.registry()
        self.assertEqual(2, r.effective("Unused::Dormant")["values"]["n"]["value"])

    def test_parent_missing_wrong_kind_and_multiple_parent_syntax(self):
        self.f.add("App", "object", "Child", "object App::Child extends Api::Missing {}")
        self.f.sync()
        r, _ = self.f.registry()
        self.error("MISSING_ELEMENT", lambda: r.effective("App::Child"))
        self.f.add("App", "object", "Child", "object App::Child extends Api::Value {}")
        r, _ = self.f.registry()
        self.error("ELEMENT_KIND", lambda: r.effective("App::Child"))
        self.error("SYNTAX", lambda: Parser("object App::Child extends App::A extends App::B {}", Path("child.celem")).element())

    def test_inheritance_cycle(self):
        self.f.add("App", "object", "A", "object App::A extends App::B {}")
        self.f.add("App", "object", "B", "object App::B extends App::A {}")
        self.f.sync()
        r, _ = self.f.registry()
        self.error("INHERITANCE_CYCLE", lambda: r.effective("App::A"))

    def test_containment_cycle(self):
        self.f.add("App", "object", "A", "object App::A { contain object App::B; }")
        self.f.add("App", "object", "B", "object App::B { contain object App::A; }")
        self.f.main("provide Api::Value with Provider::ValueBody; use object App::A;")
        self.f.sync()
        self.error("STRUCTURAL_CYCLE", self.f.plan)

    def test_module_inclusion_cycle(self):
        self.f.add("App", "module", "A", "module App::A { include App::B; }")
        self.f.add("App", "module", "B", "module App::B { include App::A; }")
        self.f.main("provide Api::Value with Provider::ValueBody; module App::A;")
        self.f.sync()
        self.error("STRUCTURAL_CYCLE", self.f.plan)

    def test_reference_cycle_is_allowed(self):
        self.f.add("App", "object", "A", "object App::A { use object App::B; }")
        self.f.add("App", "object", "B", "object App::B { use object App::A; }")
        self.f.main("provide Api::Value with Provider::ValueBody; use object App::A;")
        self.f.sync()
        plan, _ = self.f.plan()
        self.assertTrue({"App::A", "App::B"} <= plan.reached)

    def test_transitive_stage_view_inheritance_and_always(self):
        self.f.add("App", "stage", "Stage", "stage App::Stage { contain view App::Screen; }")
        self.f.add("App", "view", "Screen", "view App::Screen extends App::BaseScreen {}")
        self.f.add("App", "view", "BaseScreen", "view App::BaseScreen { use object Api::Thing; }")
        self.f.add("Api", "object", "Thing", "object Api::Thing {}")
        self.f.main("provide Api::Value with Provider::ValueBody; use stage App::Stage;")
        self.f.always = ["Unused::Dormant"]
        self.f.packs["App"]["dependencies"]["Unused"] = "1"
        self.f.sync()
        plan, _ = self.f.plan()
        self.assertTrue({"App::Stage", "App::Screen", "App::BaseScreen", "Api::Thing", "Unused::Dormant"} <= plan.reached)

    def test_unused_documents_are_not_read(self):
        self.f.add("Unused", "object", "Dormant", "not valid declaration text")
        plan, stats = self.f.plan()
        self.assertNotIn("Unused::Dormant", plan.reached)
        self.assertFalse(any(p.endswith("Dormant.celem") for p in stats["readDocuments"]))

    def test_version_mismatch_is_only_warning_and_is_pinned(self):
        self.f.packs["App"]["dependencies"]["Api"] = "999"
        self.f.sync()
        plan, _ = self.f.plan()
        self.assertEqual("VERSION_MISMATCH", plan.r.warnings[0]["code"])
        self.assertEqual("1", plan.r.packs["Api"]["version"])

    def test_owned_source_path_cannot_escape_pack(self):
        self.f.packs["Api"]["elements"]["Value"]["path"] = "../outside.celem"
        self.f.sync()
        self.error("OWNERSHIP", self.f.registry)

    def test_entry_is_required_and_typed(self):
        self.f.entry = None
        self.f.sync()
        self.error("MISSING_ENTRY", self.f.plan)
        self.f.entry = "Api::Value"
        self.f.sync()
        self.error("ENTRY_CONTRACT", self.f.plan)

    def test_project_input_cannot_be_a_regular_pack(self):
        path = self.f.project
        path.write_text('pack App version "1" {}')
        self.error("PROJECT_INPUT", self.f.registry)


if __name__ == "__main__":
    unittest.main()
