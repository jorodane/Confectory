"""Actual mixed native/Blueprint targets and callers, one checkpoint/CAS."""
import sys
import v536_information_mixed_target_fixture as fixture
sys.modules['v536_information_csharp_fixture'] = fixture
import v536_information_csharp_api
