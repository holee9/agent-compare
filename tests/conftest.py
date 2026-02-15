"""
Pytest configuration for AigenFlow project.
"""

import sys
from pathlib import Path

# 프로젝트 루트 디렉토리 경로
root_dir = Path(__file__).parent.parent
src_dir = root_dir / "src"

# src 폴더를 Python 경로에 추가
sys.path.insert(0, str(src_dir))
