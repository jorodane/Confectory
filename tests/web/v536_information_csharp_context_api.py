"""Reuses the complete engine/checkpoint/compiler acceptance with raw C# callers."""
import sys
import v536_information_csharp_context_fixture as fixture
sys.modules['v536_information_csharp_fixture'] = fixture
import v536_information_csharp_api
