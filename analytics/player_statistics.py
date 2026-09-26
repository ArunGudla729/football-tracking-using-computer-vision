"""Player statistics calculation and tracking."""

import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class PlayerStatistics:
    """Calculate and track comprehensive player statistics."""
    
    def __init__(self):
        """Initialize player statistics tracker."""
        self.stats = defaultdict(lambda: {
            'total_distance': 0.0,
            'max_speed': 0.0,
            'avg_speed': 0.0,
            'sprints': 0,
            'time_with_ball': 0,
            'touches': 0,
            'passes_attempted': 0,
            'passes_completed': 0,
            'position_history': [],
            'speed_history': []
        })
        
        logger.info("PlayerStatistics initialized")
    
    def update_from_tracks(self, tracks: Dict) -> None:
        """
        Update statistics from tracking data.
        
        Args:
            tracks: Dictionary containing player tracking data
        """
        for frame_idx, frame_data in enumerate(tracks.get('players', [])):
            for player_id, player_data in frame_data.items():
                # Distance
                if 'distance' in player_data:
                    self.stats[player_id]['total_distance'] += player_data['distance']
                
                # Speed
                if 'speed' in player_data:
                    speed = player_data['speed']
                    self.stats[player_id]['speed_history'].append(speed)
                    
                    if speed > self.stats[player_id]['max_speed']:
                        self.stats[player_id]['max_speed'] = speed
                    
                    # Count sprints (speed > 7 m/s / ~25 km/h)
                    if speed > 7.0:
                        self.stats[player_id]['sprints'] += 1
                
                # Ball possession
                if player_data.get('has_ball', False):
                    self.stats[player_id]['time_with_ball'] += 1
                    self.stats[player_id]['touches'] += 1
                
                # Position history
                if 'position' in player_data:
                    self.stats[player_id]['position_history'].append(
                        player_data['position']
                    )
    
    def calculate_average_speed(self, player_id: int) -> float:
        """
        Calculate average speed for a player.
        
        Args:
            player_id: Player identifier
            
        Returns:
            Average speed in m/s
        """
        speed_history = self.stats[player_id]['speed_history']
        if not speed_history:
            return 0.0
        
        avg_speed = np.mean(speed_history)
        self.stats[player_id]['avg_speed'] = avg_speed
        return avg_speed
    
    def get_player_stats(self, player_id: int) -> Dict:
        """
        Get comprehensive statistics for a player.
        
        Args:
            player_id: Player identifier
            
        Returns:
            Dictionary containing all player statistics
        """
        if player_id not in self.stats:
            return {}
        
        # Calculate averages if not already done
        if self.stats[player_id]['avg_speed'] == 0.0:
            self.calculate_average_speed(player_id)
        
        stats = self.stats[player_id].copy()
        
        # Remove raw history data for summary
        stats.pop('position_history', None)
        stats.pop('speed_history', None)
        
        # Calculate pass accuracy
        if stats['passes_attempted'] > 0:
            stats['pass_accuracy'] = (stats['passes_completed'] / 
                                     stats['passes_attempted'] * 100)
        else:
            stats['pass_accuracy'] = 0.0
        
        return stats
    
    def get_team_stats(self, tracks: Dict, team: int) -> Dict:
        """
        Get aggregate statistics for a team.
        
        Args:
            tracks: Dictionary containing tracking data
            team: Team identifier
            
        Returns:
            Dictionary containing team statistics
        """
        team_stats = {
            'total_distance': 0.0,
            'avg_team_speed': 0.0,
            'total_sprints': 0,
            'total_passes_attempted': 0,
            'total_passes_completed': 0,
            'possession_time': 0,
            'player_count': 0
        }
        
        player_ids = set()
        
        # Collect all players from the team
        for frame_data in tracks.get('players', []):
            for player_id, player_data in frame_data.items():
                if player_data.get('team') == team:
                    player_ids.add(player_id)
        
        # Aggregate statistics
        for player_id in player_ids:
            if player_id in self.stats:
                stats = self.stats[player_id]
                team_stats['total_distance'] += stats['total_distance']
                team_stats['total_sprints'] += stats['sprints']
                team_stats['total_passes_attempted'] += stats['passes_attempted']
                team_stats['total_passes_completed'] += stats['passes_completed']
                team_stats['possession_time'] += stats['time_with_ball']
        
        team_stats['player_count'] = len(player_ids)
        
        # Calculate averages
        if team_stats['player_count'] > 0:
            team_stats['avg_distance_per_player'] = (
                team_stats['total_distance'] / team_stats['player_count']
            )
        
        if team_stats['total_passes_attempted'] > 0:
            team_stats['pass_accuracy'] = (
                team_stats['total_passes_completed'] / 
                team_stats['total_passes_attempted'] * 100
            )
        else:
            team_stats['pass_accuracy'] = 0.0
        
        return team_stats
    
    def get_top_performers(self, metric: str = 'total_distance', 
                          top_n: int = 5) -> List[Tuple[int, float]]:
        """
        Get top N players for a specific metric.
        
        Args:
            metric: Metric to rank by (e.g., 'total_distance', 'max_speed')
            top_n: Number of top players to return
            
        Returns:
            List of (player_id, value) tuples sorted by metric
        """
        rankings = []
        
        for player_id, stats in self.stats.items():
            if metric in stats:
                rankings.append((player_id, stats[metric]))
        
        # Sort by metric value (descending)
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        return rankings[:top_n]
    
    def calculate_work_rate(self, player_id: int, 
                           total_frames: int, fps: int = 24) -> float:
        """
        Calculate player work rate (distance per minute).
        
        Args:
            player_id: Player identifier
            total_frames: Total number of frames
            fps: Frames per second
            
        Returns:
            Work rate in meters per minute
        """
        if player_id not in self.stats:
            return 0.0
        
        total_distance = self.stats[player_id]['total_distance']
        total_seconds = total_frames / fps
        total_minutes = total_seconds / 60
        
        if total_minutes > 0:
            return total_distance / total_minutes
        return 0.0
    
    def get_sprint_statistics(self, player_id: int) -> Dict:
        """
        Get detailed sprint statistics for a player.
        
        Args:
            player_id: Player identifier
            
        Returns:
            Dictionary containing sprint statistics
        """
        if player_id not in self.stats:
            return {}
        
        speed_history = self.stats[player_id]['speed_history']
        
        if not speed_history:
            return {
                'total_sprints': 0,
                'sprint_percentage': 0.0,
                'max_sprint_speed': 0.0
            }
        
        sprint_threshold = 7.0  # m/s
        sprints = [s for s in speed_history if s > sprint_threshold]
        
        return {
            'total_sprints': len(sprints),
            'sprint_percentage': (len(sprints) / len(speed_history)) * 100,
            'max_sprint_speed': max(sprints) if sprints else 0.0,
            'avg_sprint_speed': np.mean(sprints) if sprints else 0.0
        }
