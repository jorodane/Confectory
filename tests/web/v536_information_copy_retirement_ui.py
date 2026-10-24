"""Reuse the actual original delete/recovery controls with an exclusive saved copy.

Only fixture setup differs from shared binding tests; no production test bypass.
"""
import v536_information_binding_api as a
from v536_information_copy_retirement_api import setup as setup_copy

a.archive_copy = True
a.setup = setup_copy
import v536_information_binding_ui  # executes its real renderer scenarios
