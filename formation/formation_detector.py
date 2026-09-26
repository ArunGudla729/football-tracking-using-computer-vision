"""Formation detection and tactical analysis."""

import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.cluster import KMeans
import logging

logger = logging.getLogger(__name__)


class FormationDetector:
    """Detect and analyze team formations during match play."""
    
    KNOWN_FORMATIONS = {
        '4-4-2': {'defenders': 4, 'midfielders': 4, 'forwards': 2},
        '4-3-3': {'defenders': 4, 'midfielders': 3, 'forwards': 3},
        '4-2-3-1': {'defenders': 4, 'midfielders': 5, 'forwards': 1},
        '3-5-2': {'defenders': 3, 'midfielders': 5, 'forwards': 2},
        '3-4-3': {'defenders': 3, 'midfielders': 4, 'forwards': 3},
        '5-3-2': {'defenders': 5, 'midfielders': 3, 'forwards': 2},
        '4-5-1': {'defenders': 4, 'midfielders': 5, 'forwards': 1},
    }
    
    def __init__(self, min_players: int = 7, update_interval: int = 30):
        """
        Initialize formation detector.
        
        Args:
            min_players: Minimum players needed to detect formation
            update_interval: Number of frames between formation updates
        """
        self.min_players = min_players
        self.update_interval = update_interval
        self.formation_history = {1: [], 2: []}
        
        logger.info(f"FormationDetector initialized (min_players={min_players})")
    
    def detect_formation(self, tracks: Dict, frame_idx: int, 
                        team: int, frame_height: int) -> Optional[str]:
        """
        Detect team formation for a specific frame.
        
        Args:
            tracks: Dictionary containing tracking data
            frame_idx: Frame index to analyze
            team: Team identifier
            frame_height: Height of the video frame
            
        Returns:
            Formation string (e.g., '4-3-3') or None if cannot detect
        """
        if frame_idx >= len(tracks.get('players', [])):
            return None
        
        frame_data = tracks['players'][frame_idx]
        
        # Collect player positions for the team
        positions = []
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
        
        if len(positions) < self.min_players:
            logger.debug(f"Not enough players to detect formation: {len(positions)}")
            return None
        
        positions = np.array(positions)
        
        # Sort by y-coordinate (vertical position)
        positions = positions[positions[:, 1].argsort()]
        
        # Divide into defensive thirds
        third_height = frame_height / 3
        
        defenders = []
        midfielders = []
        forwards = []
        
        for pos in positions:
            x, y = pos
            if y > 2 * third_height:  # Defensive third (bottom)
                defenders.append(pos)
            elif y > third_height:  # Middle third
                midfielders.append(pos)
            else:  # Attacking third (top)
                forwards.append(pos)
        
        # Count players in each line
        def_count = len(defenders)
        mid_count = len(midfielders)
        fwd_count = len(forwards)
        
        # Match to known formation
        formation_str = f"{def_count}-{mid_count}-{fwd_count}"
        
        # Try to match with known formations
        if formation_str in self.KNOWN_FORMATIONS:
            return formation_str
        
        # Return closest match
        return self._find_closest_formation(def_count, mid_count, fwd_count)
    
    def _find_closest_formation(self, defenders: int, 
                               midfielders: int, forwards: int) -> str:
        """
        Find the closest known formation.
        
        Args:
            defenders: Number of defenders
            midfielders: Number of midfielders
            forwards: Number of forwards
            
        Returns:
            Closest formation string
        """
        min_distance = float('inf')
        closest_formation = '4-3-3'  # Default
        
        for formation_name, formation_data in self.KNOWN_FORMATIONS.items():
            distance = (
                abs(formation_data['defenders'] - defenders) +
                abs(formation_data['midfielders'] - midfielders) +
                abs(formation_data['forwards'] - forwards)
            )
            
            if distance < min_distance:
                min_distance = distance
                closest_formation = formation_name
        
        return closest_formation
    
    def track_formations(self, tracks: Dict, 
                        frame_height: int) -> Dict[int, List[Tuple[int, str]]]:
        """
        Track formations throughout the match.
        
        Args:
            tracks: Dictionary containing tracking data
            frame_height: Height of the video frame
            
        Returns:
            Dictionary mapping team to list of (frame_idx, formation) tuples
        """
        formations = {1: [], 2: []}
        
        total_frames = len(tracks.get('players', []))
        
        for frame_idx in range(0, total_frames, self.update_interval):
            for team in [1, 2]:
                formation = self.detect_formation(tracks, frame_idx, team, frame_height)
                if formation:
                    formations[team].append((frame_idx, formation))
        
        self.formation_history = formations
        
        logger.info(f"Tracked formations for {total_frames} frames")
        return formations
    
    def get_dominant_formation(self, team: int) -> Optional[str]:
        """
        Get the most frequently used formation by a team.
        
        Args:
            team: Team identifier
            
        Returns:
            Most common formation string or None
        """
        if team not in self.formation_history or not self.formation_history[team]:
            return None
        
        formations = [f[1] for f in self.formation_history[team]]
        
        if not formations:
            return None
        
        # Count occurrences
        formation_counts = {}
        for formation in formations:
            formation_counts[formation] = formation_counts.get(formation, 0) + 1
        
        # Find most common
        dominant_formation = max(formation_counts, key=formation_counts.get)
        
        logger.info(f"Team {team} dominant formation: {dominant_formation}")
        return dominant_formation
    
    def detect_formation_changes(self, team: int) -> List[Tuple[int, str, str]]:
        """
        Detect when a team changes formation.
        
        Args:
            team: Team identifier
            
        Returns:
            List of (frame_idx, old_formation, new_formation) tuples
        """
        if team not in self.formation_history or not self.formation_history[team]:
            return []
        
        changes = []
        formations = self.formation_history[team]
        
        for i in range(1, len(formations)):
            prev_frame, prev_formation = formations[i - 1]
            curr_frame, curr_formation = formations[i]
            
            if prev_formation != curr_formation:
                changes.append((curr_frame, prev_formation, curr_formation))
        
        logger.info(f"Team {team} had {len(changes)} formation changes")
        return changes
    
    def analyze_formation_width(self, tracks: Dict, frame_idx: int, 
                               team: int) -> float:
        """
        Analyze how wide the formation is spread.
        
        Args:
            tracks: Dictionary containing tracking data
            frame_idx: Frame index to analyze
            team: Team identifier
            
        Returns:
            Formation width in pixels
        """
        if frame_idx >= len(tracks.get('players', [])):
            return 0.0
        
        frame_data = tracks['players'][frame_idx]
        
        x_positions = []
        for player_id, player_data in frame_data.items():
            if player_data.get('team') != team:
                continue
            
            if 'position' in player_data:
                x_positions.append(player_data['position'][0])
            elif 'bbox' in player_data:
                bbox = player_data['bbox']
                x_positions.append((bbox[0] + bbox[2]) / 2)
        
        if len(x_positions) < 2:
            return 0.0
        
        width = max(x_positions) - min(x_positions)
        return width
    
    def get_formation_statistics(self, team: int) -> Dict:
        """
        Get comprehensive formation statistics for a team.
        
        Args:
            team: Team identifier
            
        Returns:
            Dictionary with formation statistics
        """
        if team not in self.formation_history or not self.formation_history[team]:
            return {}
        
        formations = [f[1] for f in self.formation_history[team]]
        
        # Count each formation
        formation_counts = {}
        for formation in formations:
            formation_counts[formation] = formation_counts.get(formation, 0) + 1
        
        total = len(formations)
        
        # Calculate percentages
        formation_percentages = {
            formation: (count / total * 100)
            for formation, count in formation_counts.items()
        }
        
        stats = {
            'dominant_formation': self.get_dominant_formation(team),
            'formation_changes': len(self.detect_formation_changes(team)),
            'formations_used': list(formation_counts.keys()),
            'formation_distribution': formation_percentages,
            'total_samples': total
        }
        
        return stats
