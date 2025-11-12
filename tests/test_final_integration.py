#!/usr/bin/env python3
"""Test final GUI + UI Messages"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import UI_MESSAGES, get_message, safe_print

safe_print("\n=== TEST FINAL: GUI + UI Messages ===\n")
safe_print(f"✅ UI_MESSAGES loaded")
safe_print(f"✅ Title: {UI_MESSAGES['gui']['title']}")
safe_print(f"✅ Tabs: {len(UI_MESSAGES['gui']['tabs'])} defined")
safe_print(f"✅ Buttons: {len(UI_MESSAGES['gui']['buttons'])} defined")
safe_print(f"✅ Console messages: {len(UI_MESSAGES['console'])} defined")

safe_print("\n📝 Test get_message():")
safe_print(f"   {get_message('console.workflow_start')}")
safe_print(f"   {get_message('console.download_success', ok=10, total=15)}")
safe_print(f"   {get_message('gui.buttons.start_training')}")

safe_print("\n✅ All systems operational!\n")
