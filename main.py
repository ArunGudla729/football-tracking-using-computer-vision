"""
Sports Analytics Intelligence System (SAIS)
Advanced Football Match Analysis with Computer Vision and Machine Learning

This system provides comprehensive analytics including:
- Player and ball tracking
- Team formation detection
- Pass detection and analysis
- Heat map generation
- Performance statistics
- Speed and distance measurements
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import read_video, save_video
from trackers import Tracker
from team_assigner import TeamAssigner
from player_ball_assigner import PlayerBallAssigner
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distance_estimator import SpeedAndDistance_Estimator
from analytics import HeatmapGenerator, PlayerStatistics, PerformanceAnalyzer
from formation import FormationDetector
from pass_analysis import PassDetector
from export import DataExporter
from config import config
from logging_config import setup_logging, get_logger
import cv2
import numpy as np

# Setup logging
setup_logging(
    log_level=config.get('logging.level', 'INFO'),
    log_file=config.get('logging.log_file'),
    console_output=config.get('logging.console_output', True)
)

logger = get_logger(__name__)


def main():
    """Main execution function for sports analytics system."""
    
    logger.info("=" * 80)
    logger.info("SPORTS ANALYTICS INTELLIGENCE SYSTEM - STARTING")
    logger.info("=" * 80)
    
    try:
        # Create necessary directories
        config.create_directories()
        
        # Get configuration
        video_path = config.get('video.input_path', 'input_videos/08fd33_4.mp4')
        output_path = config.get('video.output_path', 'output_videos/output_video.mp4')
        model_path = config.get('models.detection_model', 'models/best.pt')
        
        logger.info(f"Input video: {video_path}")
        logger.info(f"Output video: {output_path}")
        logger.info(f"Model: {model_path}")
        
        # Read Video
        logger.info("Reading video frames...")
        video_frames = read_video(video_path)
        frame_height, frame_width = video_frames[0].shape[:2]
        logger.info(f"Loaded {len(video_frames)} frames ({frame_width}x{frame_height})")
        
        # Initialize Tracker
        logger.info("Initializing object tracker...")
        tracker = Tracker(model_path)
        
        # Get object tracks
        logger.info("Detecting and tracking objects...")
        tracks = tracker.get_object_tracks(
            video_frames,
            read_from_stub=config.get('tracking.use_stub', False),
            stub_path=config.get('tracking.stub_path', 'stubs/track_stubs.pkl')
        )
        
        # Add positions to tracks
        logger.info("Calculating object positions...")
        tracker.add_position_to_tracks(tracks)
        
        # Camera movement estimation
        logger.info("Estimating camera movement...")
        camera_movement_estimator = CameraMovementEstimator(video_frames[0])
        camera_movement_per_frame = camera_movement_estimator.get_camera_movement(
            video_frames,
            read_from_stub=config.get('camera.use_stub', False),
            stub_path=config.get('camera.stub_path', 'stubs/camera_movement_stub.pkl')
        )
        camera_movement_estimator.add_adjust_positions_to_tracks(tracks, camera_movement_per_frame)
        
        # View Transformation
        logger.info("Applying perspective transformation...")
        view_transformer = ViewTransformer()
        view_transformer.add_transformed_position_to_tracks(tracks)
        
        # Interpolate Ball Positions
        if config.get('tracking.interpolate_ball', True):
            logger.info("Interpolating ball positions...")
            tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])
        
        # Speed and distance estimation
        logger.info("Calculating speed and distance metrics...")
        speed_and_distance_estimator = SpeedAndDistance_Estimator()
        speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)
        
        # Assign Player Teams
        logger.info("Assigning players to teams...")
        team_assigner = TeamAssigner()
        team_assigner.assign_team_color(video_frames[0], tracks['players'][0])
        
        for frame_num, player_track in enumerate(tracks['players']):
            for player_id, track in player_track.items():
                team = team_assigner.get_player_team(
                    video_frames[frame_num],
                    track['bbox'],
                    player_id
                )
                tracks['players'][frame_num][player_id]['team'] = team
                tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]
        
        # Assign Ball Possession
        logger.info("Analyzing ball possession...")
        player_assigner = PlayerBallAssigner()
        team_ball_control = []
        
        for frame_num, player_track in enumerate(tracks['players']):
            ball_bbox = tracks['ball'][frame_num][1]['bbox']
            assigned_player = player_assigner.assign_ball_to_player(player_track, ball_bbox)
            
            if assigned_player != -1:
                tracks['players'][frame_num][assigned_player]['has_ball'] = True
                team_ball_control.append(tracks['players'][frame_num][assigned_player]['team'])
            else:
                team_ball_control.append(team_ball_control[-1] if team_ball_control else 1)
        
        team_ball_control = np.array(team_ball_control)
        
        # ========== ADVANCED ANALYTICS ==========
        
        # Player Statistics
        if config.get('analytics.export_statistics', True):
            logger.info("Calculating player statistics...")
            player_stats = PlayerStatistics()
            player_stats.update_from_tracks(tracks)
            
            # Calculate averages
            for player_id in player_stats.stats.keys():
                player_stats.calculate_average_speed(player_id)
        
        # Performance Analysis
        logger.info("Analyzing team performance...")
        performance_analyzer = PerformanceAnalyzer()
        possession_stats = performance_analyzer.analyze_possession(tracks)
        match_summary = performance_analyzer.generate_match_summary(tracks, player_stats.stats)
        
        logger.info(f"Team 1 Possession: {possession_stats['team_1_percentage']:.1f}%")
        logger.info(f"Team 2 Possession: {possession_stats['team_2_percentage']:.1f}%")
        
        # Formation Detection
        if config.get('analytics.track_formations', True):
            logger.info("Detecting team formations...")
            formation_detector = FormationDetector(
                min_players=config.get('formation.min_players', 7),
                update_interval=config.get('formation.update_interval', 30)
            )
            formations = formation_detector.track_formations(tracks, frame_height)
            
            for team in [1, 2]:
                dominant = formation_detector.get_dominant_formation(team)
                if dominant:
                    logger.info(f"Team {team} dominant formation: {dominant}")
        
        # Pass Detection
        if config.get('analytics.analyze_passes', True):
            logger.info("Detecting passes...")
            pass_detector = PassDetector(
                max_pass_distance=config.get('pass_detection.max_pass_distance', 50.0),
                min_ball_speed=config.get('pass_detection.min_ball_speed', 2.0),
                max_time_between_touches=config.get('pass_detection.max_time_between_touches', 3.0)
            )
            passes = pass_detector.detect_passes(tracks)
            
            for team in [1, 2]:
                pass_stats = pass_detector.get_pass_statistics(team)
                logger.info(f"Team {team} - Passes: {pass_stats['total_passes']}, "
                          f"Accuracy: {pass_stats['pass_accuracy']:.1f}%")
        
        # Heat Map Generation
        if config.get('analytics.generate_heatmaps', True):
            logger.info("Generating heat maps...")
            heatmap_generator = HeatmapGenerator(
                frame_width=frame_width,
                frame_height=frame_height,
                grid_size=config.get('heatmap.grid_size', 20),
                alpha=config.get('heatmap.alpha', 0.6)
            )
            
            # Generate team heat maps
            for team in [1, 2]:
                team_heatmap = heatmap_generator.generate_team_heatmap(tracks, team)
                heatmap_path = f"analytics_output/team_{team}_heatmap.jpg"
                heatmap_generator.save_heatmap(team_heatmap, heatmap_path)
                logger.info(f"Saved Team {team} heat map: {heatmap_path}")
        
        # ========== VIDEO OUTPUT ==========
        
        logger.info("Rendering annotated video...")
        
        # Draw annotations
        output_video_frames = tracker.draw_annotations(video_frames, tracks, team_ball_control)
        
        # Draw camera movement
        if config.get('visualization.show_annotations', True):
            output_video_frames = camera_movement_estimator.draw_camera_movement(
                output_video_frames,
                camera_movement_per_frame
            )
        
        # Draw speed and distance
        if config.get('visualization.show_speed', True):
            speed_and_distance_estimator.draw_speed_and_distance(output_video_frames, tracks)
        
        # Save video
        logger.info(f"Saving output video to: {output_path}")
        save_video(
            output_video_frames,
            output_path,
            fps=config.get('video.fps', 24)
        )
        
        # ========== EXPORT ANALYTICS ==========
        
        if config.get('analytics.export_statistics', True):
            logger.info("Exporting analytics data...")
            exporter = DataExporter(config.get('export.export_path', 'analytics_output/'))
            
            export_formats = config.get('export.format', ['json'])
            
            # Collect all stats
            team_stats = {
                1: player_stats.get_team_stats(tracks, 1),
                2: player_stats.get_team_stats(tracks, 2)
            }
            
            # Export comprehensive report
            exported_files = exporter.export_comprehensive_report(
                player_stats={pid: player_stats.get_player_stats(pid) 
                             for pid in player_stats.stats.keys()},
                team_stats=team_stats,
                pass_data=passes if config.get('analytics.analyze_passes', True) else None,
                formation_data=formations if config.get('analytics.track_formations', True) else None,
                match_summary=match_summary,
                formats=export_formats
            )
            
            logger.info(f"Exported {len(exported_files)} analytics files")
            for file_type, file_path in exported_files.items():
                logger.info(f"  - {file_type}: {file_path}")
        
        # ========== COMPLETION ==========
        
        logger.info("=" * 80)
        logger.info("ANALYSIS COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"Output video: {output_path}")
        logger.info(f"Analytics data: {config.get('export.export_path', 'analytics_output/')}")
        logger.info("=" * 80)
        
        # Print insights
        if match_summary.get('insights'):
            logger.info("\nKey Insights:")
            for insight in match_summary['insights']:
                logger.info(f"  • {insight}")
        
        return True
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.error("Please ensure input video and model files exist")
        return False
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
