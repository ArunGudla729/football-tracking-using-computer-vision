"""Pass detection and accuracy analysis."""

import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PassDetector:
    """Detect and analyze passes between players."""
    
    def __init__(self, max_pass_distance: float = 50.0, 
                 min_ball_speed: float = 2.0,
                 max_time_between_touches: float = 3.0,
                 fps: int = 24):
        """
        Initialize pass detector.
        
        Args:
            max_pass_distance: Maximum distance for a valid pass (meters)
            min_ball_speed: Minimum ball speed to detect a pass (m/s)
            max_time_between_touches: Maximum time between touches (seconds)
            fps: Frames per second
        """
        self.max_pass_distance = max_pass_distance
        self.min_ball_speed = min_ball_speed
        self.max_time_between_touches = max_time_between_touches
        self.max_frames_between_touches = int(max_time_between_touches * fps)
        self.fps = fps
        
        self.passes = []
        self.pass_network = {}  # {(from_player, to_player): count}
        
        logger.info(f"PassDetector initialized (max_distance={max_pass_distance}m)")
    
    def detect_passes(self, tracks: Dict) -> List[Dict]:
        """
        Detect all passes in the tracking data.
        
        Args:
            tracks: Dictionary containing tracking data
            
        Returns:
            List of detected passes with metadata
        """
        self.passes = []
        previous_possessor = None
        frames_since_possession = 0
        
        for frame_idx, frame_data in enumerate(tracks.get('players', [])):
            current_possessor = None
            current_team = None
            
            # Find who has the ball
            for player_id, player_data in frame_data.items():
                if player_data.get('has_ball', False):
                    current_possessor = player_id
                    current_team = player_data.get('team')
                    break
            
            # Detect pass
            if current_possessor is not None and previous_possessor is not None:
                if current_possessor != previous_possessor:
                    # Check if it's a valid pass (same team)
                    if frames_since_possession <= self.max_frames_between_touches:
                        pass_info = self._analyze_pass(
                            tracks, frame_idx, 
                            previous_possessor, current_possessor,
                            frames_since_possession
                        )
                        
                        if pass_info:
                            self.passes.append(pass_info)
                            
                            # Update pass network
                            pass_key = (previous_possessor, current_possessor)
                            self.pass_network[pass_key] = \
                                self.pass_network.get(pass_key, 0) + 1
                    
                    frames_since_possession = 0
            
            if current_possessor is not None:
                previous_possessor = current_possessor
                frames_since_possession = 0
            else:
                frames_since_possession += 1
        
        logger.info(f"Detected {len(self.passes)} passes")
        return self.passes
    
    def _analyze_pass(self, tracks: Dict, frame_idx: int,
                     from_player: int, to_player: int,
                     frames_elapsed: int) -> Optional[Dict]:
        """
        Analyze a detected pass.
        
        Args:
            tracks: Dictionary containing tracking data
            frame_idx: Frame where pass was received
            from_player: Player who made the pass
            to_player: Player who received the pass
            frames_elapsed: Frames between possession changes
            
        Returns:
            Dictionary with pass information or None if invalid
        """
        if frame_idx >= len(tracks.get('players', [])):
            return None
        
        # Get player positions
        current_frame = tracks['players'][frame_idx]
        
        if from_player not in current_frame or to_player not in current_frame:
            return None
        
        from_data = current_frame[from_player]
        to_data = current_frame[to_player]
        
        # Check if same team
        if from_data.get('team') != to_data.get('team'):
            return None
        
        # Get positions
        from_pos = self._get_position(from_data)
        to_pos = self._get_position(to_data)
        
        if from_pos is None or to_pos is None:
            return None
        
        # Calculate pass distance
        distance = np.linalg.norm(np.array(from_pos) - np.array(to_pos))
        
        # Check if within valid distance
        if distance > self.max_pass_distance:
            return None
        
        # Calculate pass speed
        time_elapsed = frames_elapsed / self.fps
        pass_speed = distance / time_elapsed if time_elapsed > 0 else 0
        
        pass_info = {
            'frame': frame_idx,
            'from_player': from_player,
            'to_player': to_player,
            'from_position': from_pos,
            'to_position': to_pos,
            'distance': distance,
            'duration': time_elapsed,
            'speed': pass_speed,
            'team': from_data.get('team'),
            'successful': True  # If detected, it was completed
        }
        
        return pass_info
    
    def _get_position(self, player_data: Dict) -> Optional[Tuple[float, float]]:
        """
        Extract player position from tracking data.
        
        Args:
            player_data: Player tracking data for a frame
            
        Returns:
            (x, y) position tuple or None
        """
        if 'position' in player_data:
            return player_data['position']
        elif 'bbox' in player_data:
            bbox = player_data['bbox']
            x = (bbox[0] + bbox[2]) / 2
            y = (bbox[1] + bbox[3]) / 2
            return (x, y)
        return None
    
    def calculate_pass_accuracy(self, team: int = None) -> float:
        """
        Calculate pass completion accuracy.
        
        Args:
            team: Optional team filter
            
        Returns:
            Pass accuracy percentage
        """
        if not self.passes:
            return 0.0
        
        if team is not None:
            team_passes = [p for p in self.passes if p.get('team') == team]
            successful = sum(1 for p in team_passes if p.get('successful', False))
            total = len(team_passes)
        else:
            successful = sum(1 for p in self.passes if p.get('successful', False))
            total = len(self.passes)
        
        accuracy = (successful / total * 100) if total > 0 else 0.0
        
        logger.info(f"Pass accuracy (team={team}): {accuracy:.1f}%")
        return accuracy
    
    def get_pass_statistics(self, team: int = None) -> Dict:
        """
        Get comprehensive pass statistics.
        
        Args:
            team: Optional team filter
            
        Returns:
            Dictionary with pass statistics
        """
        if team is not None:
            passes = [p for p in self.passes if p.get('team') == team]
        else:
            passes = self.passes
        
        if not passes:
            return {
                'total_passes': 0,
                'completed_passes': 0,
                'pass_accuracy': 0.0,
                'avg_pass_distance': 0.0,
                'avg_pass_speed': 0.0,
                'short_passes': 0,
                'medium_passes': 0,
                'long_passes': 0
            }
        
        distances = [p['distance'] for p in passes]
        speeds = [p['speed'] for p in passes]
        
        # Categorize passes by distance
        short_passes = sum(1 for d in distances if d < 10)
        medium_passes = sum(1 for d in distances if 10 <= d < 30)
        long_passes = sum(1 for d in distances if d >= 30)
        
        stats = {
            'total_passes': len(passes),
            'completed_passes': sum(1 for p in passes if p.get('successful', False)),
            'pass_accuracy': self.calculate_pass_accuracy(team),
            'avg_pass_distance': np.mean(distances),
            'max_pass_distance': max(distances),
            'avg_pass_speed': np.mean(speeds),
            'short_passes': short_passes,
            'medium_passes': medium_passes,
            'long_passes': long_passes,
            'short_pass_percentage': (short_passes / len(passes) * 100),
            'medium_pass_percentage': (medium_passes / len(passes) * 100),
            'long_pass_percentage': (long_passes / len(passes) * 100)
        }
        
        return stats
    
    def get_player_pass_stats(self, player_id: int) -> Dict:
        """
        Get pass statistics for a specific player.
        
        Args:
            player_id: Player identifier
            
        Returns:
            Dictionary with player pass statistics
        """
        passes_made = [p for p in self.passes if p['from_player'] == player_id]
        passes_received = [p for p in self.passes if p['to_player'] == player_id]
        
        stats = {
            'passes_made': len(passes_made),
            'passes_received': len(passes_received),
            'successful_passes': sum(1 for p in passes_made if p.get('successful', False)),
            'pass_accuracy': 0.0,
            'avg_pass_distance': 0.0,
            'total_involvement': len(passes_made) + len(passes_received)
        }
        
        if passes_made:
            stats['pass_accuracy'] = (stats['successful_passes'] / len(passes_made) * 100)
            stats['avg_pass_distance'] = np.mean([p['distance'] for p in passes_made])
        
        return stats
    
    def get_pass_network(self, team: int = None, 
                        min_passes: int = 3) -> Dict[Tuple[int, int], int]:
        """
        Get pass network (connections between players).
        
        Args:
            team: Optional team filter
            min_passes: Minimum passes to include in network
            
        Returns:
            Dictionary mapping (from_player, to_player) to pass count
        """
        if team is not None:
            # Filter network by team
            team_network = {}
            for (from_player, to_player), count in self.pass_network.items():
                # Check if both players are from the team
                for pass_info in self.passes:
                    if (pass_info['from_player'] == from_player and 
                        pass_info['to_player'] == to_player and
                        pass_info.get('team') == team):
                        if count >= min_passes:
                            team_network[(from_player, to_player)] = count
                        break
            return team_network
        
        # Return full network filtered by min_passes
        return {k: v for k, v in self.pass_network.items() if v >= min_passes}
    
    def get_most_frequent_pass_combination(self, team: int = None) -> Optional[Tuple]:
        """
        Get the most frequent pass combination.
        
        Args:
            team: Optional team filter
            
        Returns:
            Tuple of (from_player, to_player, count) or None
        """
        network = self.get_pass_network(team, min_passes=1)
        
        if not network:
            return None
        
        most_frequent = max(network.items(), key=lambda x: x[1])
        return (*most_frequent[0], most_frequent[1])
    
    def analyze_passing_patterns(self, team: int) -> Dict:
        """
        Analyze passing patterns for a team.
        
        Args:
            team: Team identifier
            
        Returns:
            Dictionary with passing pattern analysis
        """
        team_passes = [p for p in self.passes if p.get('team') == team]
        
        if not team_passes:
            return {}
        
        # Analyze pass directions
        forward_passes = 0
        backward_passes = 0
        lateral_passes = 0
        
        for pass_info in team_passes:
            from_y = pass_info['from_position'][1]
            to_y = pass_info['to_position'][1]
            
            y_diff = to_y - from_y
            
            if abs(y_diff) < 5:  # Threshold for lateral
                lateral_passes += 1
            elif y_diff < 0:  # Moving up (forward in most videos)
                forward_passes += 1
            else:
                backward_passes += 1
        
        total = len(team_passes)
        
        return {
            'forward_passes': forward_passes,
            'backward_passes': backward_passes,
            'lateral_passes': lateral_passes,
            'forward_percentage': (forward_passes / total * 100) if total > 0 else 0,
            'backward_percentage': (backward_passes / total * 100) if total > 0 else 0,
            'lateral_percentage': (lateral_passes / total * 100) if total > 0 else 0,
            'pass_network_complexity': len(self.get_pass_network(team, min_passes=1))
        }
