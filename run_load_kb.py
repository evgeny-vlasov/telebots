#!/usr/bin/env python3
"""Wrapper to run load_kb.py with stdlib platform preloaded"""
import sys
import importlib.util

# Preload stdlib platform module to prevent shadowing
spec = importlib.util.spec_from_file_location(
    '_platform_stdlib',
    '/usr/lib/python3.11/platform.py'
)
stdlib_platform = importlib.util.module_from_spec(spec)
sys.modules['platform'] = stdlib_platform
spec.loader.exec_module(stdlib_platform)

# Now run the actual script
import bots.anglers.load_kb
bots.anglers.load_kb.main()
