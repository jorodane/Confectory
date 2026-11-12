"""Retain the original native source lease across a multi-row presentation Save."""
import os,pathlib,runpy,sys
check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='native':
 sys.argv.append('--expect=safe');runpy.run_path(str(pathlib.Path(__file__).with_name('v666_native_presentation_followup_probe.py')),run_name='__main__')
elif check in ['api','guards','late','conflict','ui']:
 runpy.run_path(str(pathlib.Path(__file__).with_name('v666_native_presentation_followup_'+check+'.py')),run_name='__main__')
else:raise ValueError(check)
