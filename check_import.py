#!/usr/bin/env python
"""
Check import status
"""

try:
    from ai_chat.enhanced_ai_service import enhanced_ai_service
    print('✅ Enhanced AI service imported successfully')
except ImportError as e:
    print(f'❌ Enhanced AI service import failed: {e}')
    print('Will fallback to smart_ai')

try:
    from ai_chat.smart_ai_service import smart_ai
    print('✅ Smart AI service imported successfully')
except ImportError as e:
    print(f'❌ Smart AI service import failed: {e}')
