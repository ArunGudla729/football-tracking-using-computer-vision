"""Performance analysis and insights generation."""

import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analyze performance metrics and generate insights."""
    
    def __init__(self):
        """Initialize performance analyzer."""
        self.insights = []
        logger.info("PerformanceAnalyzer initialized")
    
    def analyze_possession(self, tracks: Dict) -> Dict:
        """
        Analyze ball possession statistics.
        
        Args:
            tracks: Dictionary containing tracking data
            
        Returns:
            Dictionary with possession statistics
        """
        possession_stats = {
            'team_1_frames': 0,
            'team_2_frames': 0,
            'total_frames': 0,
            'team_1_percentage': 0.0,
            'team_2_percentage': 0.0,
            'possession_changes': 0
        }
        
        previous_team = None
        
        for frame_data in tracks.get('players', []):
            possession_stats['total_frames'] += 1
            
            # Find which player has the ball
            current_team = None
            for player_id, player_data in frame_data.items():
                if player_data.get('has_ball', False):
                    current_team = player_data.get('team')
                    break
            
            # Update possession count
            if current_team == 1:
                possession_stats['team_1_frames'] += 1
            elif current_team == 2:
                possession_stats['team_2_frames'] += 1
            
            # Track possession changes
            if previous_team is not None and current_team != previous_team and current_team is not None:
                possession_stats['possession_changes'] += 1
            
            previous_team = current_team
        
        # Calculate percentages
        total = possession_stats['total_frames']
        if total > 0:
            possession_stats['team_1_percentage'] = (
                possession_stats['team_1_frames'] / total * 100
            )
            possession_stats['team_2_percentage'] = (
                possession_stats['team_2_frames'] / total * 100
            )
        
        logger.info(f"Possession analysis: Team 1: {possession_stats['team_1_percentage']:.1f}%, "
                   f"Team 2: {possession_stats['team_2_percentage']:.1f}%")
        
        return possession_stats
    
    def analyze_attacking_thirds(self, tracks: Dict, 
                                 frame_height: int) -> Dict:
        """
        Analyze time spent in different thirds of the pitch.
        
        Args:
            tracks: Dictionary containing tracking data
            frame_height: Height of the video frame
            
        Returns:
            Dictionary with thirds analysis
        """
        third_height = frame_height / 3
        
        thirds_stats = {
            'team_1': {'defensive': 0, 'middle': 0, 'attacking': 0},
            'team_2': {'defensive': 0, 'middle': 0, 'attacking': 0}
        }
        
        for frame_data in tracks.get('players', []):
            for player_id, player_data in frame_data.items():
                team = player_data.get('team')
                if team not in [1, 2]:
                    continue
                
                # Get player position
                if 'position' in player_data:
                    _, y = player_data['position']
                elif 'bbox' in player_data:
                    bbox = player_data['bbox']
                    y = (bbox[1] + bbox[3]) / 2
                else:
                    continue
                
                # Determine third
                if y < third_height:
                    third = 'defensive' if team == 1 else 'attacking'
                elif y < 2 * third_height:
                    third = 'middle'
                else:
                    third = 'attacking' if team == 1 else 'defensive'
                
                thirds_stats[f'team_{team}'][third] += 1
        
        return thirds_stats
    
    def calculate_team_compactness(self, tracks: Dict, 
                                   frame_idx: int, team: int) -> float:
        """
        Calculate team compactness (how spread out players are).
        
        Args:
            tracks: Dictionary containing tracking data
            frame_idx: Frame index to analyze
            team: Team identifier
            
        Returns:
            Compactness score (lower = more compact)
        """
        if frame_idx >= len(tracks.get('players', [])):
            return 0.0
        
        frame_data = tracks['players'][frame_idx]
        positions = []
        
        # Collect positions for team players
        for player_id, player_data in frame_data.items():
            if player_data.get('team') != team:
                continue
            
            if 'position' in player_data:
                positions.append(player_data['position'])
            elif 'bbox' in player_data:
                bbox = player_data['bbox']
                x = (bbox[0] + bbox[2]) / 2
                y = (bbox[1] + bbox[3]) / 2
                positions.append((x, y))
        
        if len(positions) < 2:
            return 0.0
        
        # Calculate average pairwise distance
        positions = np.array(positions)
        center = np.mean(positions, axis=0)
        
        distances = [np.linalg.norm(pos - center) for pos in positions]
        compactness = np.mean(distances)
        
        return compactness
    
    def detect_pressing_moments(self, tracks: Dict, 
                               distance_threshold: float = 100) -> List[int]:
        """
        Detect moments when teams are pressing (players close to opposition).
        
        Args:
            tracks: Dictionary containing tracking data
            distance_threshold: Maximum distance to consider as pressing
            
        Returns:
            List of frame indices where pressing is detected
        """
        pressing_frames = []
        
        for frame_idx, frame_data in enumerate(tracks.get('players', [])):
            team_1_positions = []
            team_2_positions = []
            
            # Separate positions by team
            for player_id, player_data in frame_data.items():
                team = player_data.get('team')
                
                if 'position' in player_data:
                    pos = player_data['position']
                elif 'bbox' in player_data:
                    bbox = player_data['bbox']
                    pos = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
                else:
                    continue
                
                if team == 1:
                    team_1_positions.append(pos)
                elif team == 2:
                    team_2_positions.append(pos)
            
            # Check for close proximity between teams
            close_encounters = 0
            for pos1 in team_1_positions:
                for pos2 in team_2_positions:
                    distance = np.linalg.norm(np.array(pos1) - np.array(pos2))
                    if distance < distance_threshold:
                        close_encounters += 1
            
            # If many close encounters, consider it pressing
            if close_encounters >= 3:
                pressing_frames.append(frame_idx)
        
        logger.info(f"Detected pressing in {len(pressing_frames)} frames")
        return pressing_frames
    
    def generate_match_summary(self, tracks: Dict, 
                              player_stats: Dict) -> Dict:
        """
        Generate comprehensive match summary.
        
        Args:
            tracks: Dictionary containing tracking data
            player_stats: Player statistics dictionary
            
        Returns:
            Dictionary with match summary
        """
        summary = {
            'total_frames': len(tracks.get('players', [])),
            'possession': self.analyze_possession(tracks),
            'insights': []
        }
        
        # Generate insights
        possession = summary['possession']
        
        if possession['team_1_percentage'] > 60:
            summary['insights'].append(
                f"Team 1 dominated possession with {possession['team_1_percentage']:.1f}%"
            )
        elif possession['team_2_percentage'] > 60:
            summary['insights'].append(
                f"Team 2 dominated possession with {possession['team_2_percentage']:.1f}%"
            )
        else:
            summary['insights'].append(
                "Possession was evenly matched between both teams"
            )
        
        if possession['possession_changes'] > 100:
            summary['insights'].append(
                f"High-intensity match with {possession['possession_changes']} possession changes"
            )
        
        return summary
