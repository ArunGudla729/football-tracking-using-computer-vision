"""Heat map generation for player movement analysis."""

import cv2
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class HeatmapGenerator:
    """Generate heat maps to visualize player movement patterns."""
    
    def __init__(self, frame_width: int = 1920, frame_height: int = 1080, 
                 grid_size: int = 20, alpha: float = 0.6):
        """
        Initialize heat map generator.
        
        Args:
            frame_width: Width of the video frame
            frame_height: Height of the video frame
            grid_size: Size of each grid cell for heat map
            alpha: Transparency of heat map overlay (0-1)
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.grid_size = grid_size
        self.alpha = alpha
        
        self.grid_width = frame_width // grid_size
        self.grid_height = frame_height // grid_size
        
        logger.info(f"HeatmapGenerator initialized: {self.grid_width}x{self.grid_height} grid")
    
    def generate_player_heatmap(self, tracks: Dict, player_id: int, 
                                team: int = None) -> np.ndarray:
        """
        Generate heat map for a specific player.
        
        Args:
            tracks: Dictionary containing player tracking data
            player_id: ID of the player to generate heat map for
            team: Optional team filter
            
        Returns:
            Heat map as numpy array
        """
        heatmap = np.zeros((self.grid_height, self.grid_width), dtype=np.float32)
        
        for frame_data in tracks.get('players', []):
            if player_id in frame_data:
                player_data = frame_data[player_id]
                
                # Filter by team if specified
                if team is not None and player_data.get('team') != team:
                    continue
                
                # Get position
                if 'position' in player_data:
                    x, y = player_data['position']
                elif 'bbox' in player_data:
                    bbox = player_data['bbox']
                    x = int((bbox[0] + bbox[2]) / 2)
                    y = int((bbox[1] + bbox[3]) / 2)
                else:
                    continue
                
                # Update heat map
                grid_x = min(int(x / self.grid_size), self.grid_width - 1)
                grid_y = min(int(y / self.grid_size), self.grid_height - 1)
                
                if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                    heatmap[grid_y, grid_x] += 1
        
        # Normalize
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()
        
        return heatmap
    
    def generate_team_heatmap(self, tracks: Dict, team: int) -> np.ndarray:
        """
        Generate combined heat map for an entire team.
        
        Args:
            tracks: Dictionary containing player tracking data
            team: Team identifier (1 or 2)
            
        Returns:
            Heat map as numpy array
        """
        heatmap = np.zeros((self.grid_height, self.grid_width), dtype=np.float32)
        
        for frame_data in tracks.get('players', []):
            for player_id, player_data in frame_data.items():
                # Filter by team
                if player_data.get('team') != team:
                    continue
                
                # Get position
                if 'position' in player_data:
                    x, y = player_data['position']
                elif 'bbox' in player_data:
                    bbox = player_data['bbox']
                    x = int((bbox[0] + bbox[2]) / 2)
                    y = int((bbox[1] + bbox[3]) / 2)
                else:
                    continue
                
                # Update heat map
                grid_x = min(int(x / self.grid_size), self.grid_width - 1)
                grid_y = min(int(y / self.grid_size), self.grid_height - 1)
                
                if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                    heatmap[grid_y, grid_x] += 1
        
        # Normalize
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()
        
        return heatmap
    
    def apply_heatmap_to_frame(self, frame: np.ndarray, 
                               heatmap: np.ndarray,
                               colormap: int = cv2.COLORMAP_JET) -> np.ndarray:
        """
        Overlay heat map on a video frame.
        
        Args:
            frame: Original video frame
            heatmap: Generated heat map
            colormap: OpenCV colormap to use
            
        Returns:
            Frame with heat map overlay
        """
        # Resize heat map to frame size
        heatmap_resized = cv2.resize(heatmap, (self.frame_width, self.frame_height))
        
        # Convert to 8-bit and apply colormap
        heatmap_8bit = (heatmap_resized * 255).astype(np.uint8)
        heatmap_colored = cv2.applyColorMap(heatmap_8bit, colormap)
        
        # Blend with original frame
        output = cv2.addWeighted(frame, 1 - self.alpha, heatmap_colored, self.alpha, 0)
        
        return output
    
    def save_heatmap(self, heatmap: np.ndarray, output_path: str,
                     colormap: int = cv2.COLORMAP_JET) -> None:
        """
        Save heat map as an image file.
        
        Args:
            heatmap: Generated heat map
            output_path: Path where to save the heat map image
            colormap: OpenCV colormap to use
        """
        # Resize to standard size
        heatmap_resized = cv2.resize(heatmap, (self.frame_width, self.frame_height))
        
        # Convert to 8-bit and apply colormap
        heatmap_8bit = (heatmap_resized * 255).astype(np.uint8)
        heatmap_colored = cv2.applyColorMap(heatmap_8bit, colormap)
        
        cv2.imwrite(output_path, heatmap_colored)
        logger.info(f"Heatmap saved to {output_path}")
    
    def generate_possession_heatmap(self, tracks: Dict, team: int) -> np.ndarray:
        """
        Generate heat map showing where ball possession occurred for a team.
        
        Args:
            tracks: Dictionary containing tracking data
            team: Team identifier
            
        Returns:
            Possession heat map as numpy array
        """
        heatmap = np.zeros((self.grid_height, self.grid_width), dtype=np.float32)
        
        for frame_idx, frame_data in enumerate(tracks.get('players', [])):
            for player_id, player_data in frame_data.items():
                # Check if player has ball and is on the specified team
                if player_data.get('has_ball') and player_data.get('team') == team:
                    # Get position
                    if 'position' in player_data:
                        x, y = player_data['position']
                    elif 'bbox' in player_data:
                        bbox = player_data['bbox']
                        x = int((bbox[0] + bbox[2]) / 2)
                        y = int((bbox[1] + bbox[3]) / 2)
                    else:
                        continue
                    
                    # Update heat map
                    grid_x = min(int(x / self.grid_size), self.grid_width - 1)
                    grid_y = min(int(y / self.grid_size), self.grid_height - 1)
                    
                    if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                        heatmap[grid_y, grid_x] += 1
        
        # Normalize
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()
        
        return heatmap
    
    def get_hotspot_regions(self, heatmap: np.ndarray, 
                           threshold: float = 0.7) -> List[Tuple[int, int]]:
        """
        Identify hotspot regions in the heat map.
        
        Args:
            heatmap: Generated heat map
            threshold: Minimum intensity threshold (0-1)
            
        Returns:
            List of (x, y) coordinates of hotspot regions
        """
        hotspots = []
        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if heatmap[y, x] >= threshold:
                    # Convert grid coordinates to frame coordinates
                    frame_x = x * self.grid_size + self.grid_size // 2
                    frame_y = y * self.grid_size + self.grid_size // 2
                    hotspots.append((frame_x, frame_y))
        
        logger.info(f"Found {len(hotspots)} hotspot regions (threshold: {threshold})")
        return hotspots
