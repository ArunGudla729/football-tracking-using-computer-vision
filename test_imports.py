"""
Quick test script to verify all imports work correctly.
Run this before running main.py to catch any import errors early.
"""

import sys
from pathlib import Path

print("=" * 70)
print("Testing Imports - Sports Analytics Intelligence System")
print("=" * 70)
print()

errors = []

# Test utils
try:
    from utils import read_video, save_video
    from utils import get_center_of_bbox, get_bbox_width, get_foot_position
    from utils import measure_distance, measure_xy_distance
    print("✅ utils module - OK")
except Exception as e:
    print(f"❌ utils module - FAILED: {e}")
    errors.append(("utils", e))

# Test trackers
try:
    from trackers import Tracker
    print("✅ trackers module - OK")
except Exception as e:
    print(f"❌ trackers module - FAILED: {e}")
    errors.append(("trackers", e))

# Test team_assigner
try:
    from team_assigner import TeamAssigner
    print("✅ team_assigner module - OK")
except Exception as e:
    print(f"❌ team_assigner module - FAILED: {e}")
    errors.append(("team_assigner", e))

# Test player_ball_assigner
try:
    from player_ball_assigner import PlayerBallAssigner
    print("✅ player_ball_assigner module - OK")
except Exception as e:
    print(f"❌ player_ball_assigner module - FAILED: {e}")
    errors.append(("player_ball_assigner", e))

# Test camera_movement_estimator
try:
    from camera_movement_estimator import CameraMovementEstimator
    print("✅ camera_movement_estimator module - OK")
except Exception as e:
    print(f"❌ camera_movement_estimator module - FAILED: {e}")
    errors.append(("camera_movement_estimator", e))

# Test view_transformer
try:
    from view_transformer import ViewTransformer
    print("✅ view_transformer module - OK")
except Exception as e:
    print(f"❌ view_transformer module - FAILED: {e}")
    errors.append(("view_transformer", e))

# Test speed_and_distance_estimator
try:
    from speed_and_distance_estimator import SpeedAndDistance_Estimator
    print("✅ speed_and_distance_estimator module - OK")
except Exception as e:
    print(f"❌ speed_and_distance_estimator module - FAILED: {e}")
    errors.append(("speed_and_distance_estimator", e))

# Test analytics
try:
    from analytics import HeatmapGenerator, PlayerStatistics, PerformanceAnalyzer
    print("✅ analytics module - OK")
except Exception as e:
    print(f"❌ analytics module - FAILED: {e}")
    errors.append(("analytics", e))

# Test formation
try:
    from formation import FormationDetector
    print("✅ formation module - OK")
except Exception as e:
    print(f"❌ formation module - FAILED: {e}")
    errors.append(("formation", e))

# Test pass_analysis
try:
    from pass_analysis import PassDetector
    print("✅ pass_analysis module - OK")
except Exception as e:
    print(f"❌ pass_analysis module - FAILED: {e}")
    errors.append(("pass_analysis", e))

# Test export
try:
    from export import DataExporter
    print("✅ export module - OK")
except Exception as e:
    print(f"❌ export module - FAILED: {e}")
    errors.append(("export", e))

# Test config
try:
    from config import config
    print("✅ config module - OK")
except Exception as e:
    print(f"❌ config module - FAILED: {e}")
    errors.append(("config", e))

# Test logging_config
try:
    from logging_config import setup_logging, get_logger
    print("✅ logging_config module - OK")
except Exception as e:
    print(f"❌ logging_config module - FAILED: {e}")
    errors.append(("logging_config", e))

print()
print("=" * 70)

if errors:
    print(f"❌ FAILED: {len(errors)} module(s) have import errors")
    print()
    print("Errors:")
    for module, error in errors:
        print(f"  - {module}: {error}")
    print()
    print("Please fix these errors before running main.py")
    sys.exit(1)
else:
    print("✅ SUCCESS: All modules imported successfully!")
    print()
    print("You can now run:")
    print("  python main.py")
    print()
    sys.exit(0)
