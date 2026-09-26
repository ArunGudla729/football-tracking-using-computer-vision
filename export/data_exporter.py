"""Data export functionality for analytics and statistics."""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataExporter:
    """Export analytics data in various formats."""
    
    def __init__(self, output_dir: str = "analytics_output"):
        """
        Initialize data exporter.
        
        Args:
            output_dir: Directory where to save exported data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DataExporter initialized (output_dir={output_dir})")
    
    def export_to_json(self, data: Dict[str, Any], 
                      filename: str = None) -> str:
        """
        Export data to JSON format.
        
        Args:
            data: Dictionary containing data to export
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analytics_export_{timestamp}.json"
        
        output_path = self.output_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Data exported to JSON: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise
    
    def export_to_csv(self, data: List[Dict[str, Any]], 
                     filename: str = None) -> str:
        """
        Export tabular data to CSV format.
        
        Args:
            data: List of dictionaries containing tabular data
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to the exported file
        """
        if not data:
            logger.warning("No data to export to CSV")
            return ""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analytics_export_{timestamp}.csv"
        
        output_path = self.output_dir / filename
        
        try:
            # Get all unique keys from all dictionaries
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            fieldnames = sorted(fieldnames)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Data exported to CSV: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise
    
    def export_player_statistics(self, player_stats: Dict, 
                                 format: str = 'json') -> str:
        """
        Export player statistics.
        
        Args:
            player_stats: Dictionary with player statistics
            format: Export format ('json' or 'csv')
            
        Returns:
            Path to the exported file
        """
        if format == 'json':
            return self.export_to_json(
                player_stats,
                filename="player_statistics.json"
            )
        elif format == 'csv':
            # Convert to list of dictionaries for CSV
            csv_data = []
            for player_id, stats in player_stats.items():
                row = {'player_id': player_id}
                row.update(stats)
                csv_data.append(row)
            
            return self.export_to_csv(
                csv_data,
                filename="player_statistics.csv"
            )
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_team_statistics(self, team_stats: Dict, 
                              format: str = 'json') -> str:
        """
        Export team statistics.
        
        Args:
            team_stats: Dictionary with team statistics
            format: Export format ('json' or 'csv')
            
        Returns:
            Path to the exported file
        """
        if format == 'json':
            return self.export_to_json(
                team_stats,
                filename="team_statistics.json"
            )
        elif format == 'csv':
            # Convert to list format for CSV
            csv_data = []
            for team_id, stats in team_stats.items():
                row = {'team_id': team_id}
                row.update(stats)
                csv_data.append(row)
            
            return self.export_to_csv(
                csv_data,
                filename="team_statistics.csv"
            )
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_pass_data(self, passes: List[Dict], 
                        format: str = 'json') -> str:
        """
        Export pass detection data.
        
        Args:
            passes: List of detected passes
            format: Export format ('json' or 'csv')
            
        Returns:
            Path to the exported file
        """
        if format == 'json':
            return self.export_to_json(
                {'passes': passes},
                filename="pass_data.json"
            )
        elif format == 'csv':
            # Flatten position data for CSV
            csv_data = []
            for pass_info in passes:
                row = pass_info.copy()
                if 'from_position' in row:
                    row['from_x'] = row['from_position'][0]
                    row['from_y'] = row['from_position'][1]
                    del row['from_position']
                if 'to_position' in row:
                    row['to_x'] = row['to_position'][0]
                    row['to_y'] = row['to_position'][1]
                    del row['to_position']
                csv_data.append(row)
            
            return self.export_to_csv(
                csv_data,
                filename="pass_data.csv"
            )
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_formation_data(self, formation_data: Dict, 
                             format: str = 'json') -> str:
        """
        Export formation detection data.
        
        Args:
            formation_data: Dictionary with formation information
            format: Export format ('json' or 'csv')
            
        Returns:
            Path to the exported file
        """
        if format == 'json':
            return self.export_to_json(
                formation_data,
                filename="formation_data.json"
            )
        elif format == 'csv':
            # Convert formation history to CSV format
            csv_data = []
            for team_id, formations in formation_data.items():
                for frame_idx, formation in formations:
                    csv_data.append({
                        'team_id': team_id,
                        'frame': frame_idx,
                        'formation': formation
                    })
            
            return self.export_to_csv(
                csv_data,
                filename="formation_data.csv"
            )
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_match_summary(self, summary: Dict) -> str:
        """
        Export comprehensive match summary report.
        
        Args:
            summary: Dictionary with match summary data
            
        Returns:
            Path to the exported JSON file
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = {
            'report_generated': timestamp,
            'match_summary': summary,
            'report_version': '1.0'
        }
        
        return self.export_to_json(
            report,
            filename="match_summary_report.json"
        )
    
    def export_comprehensive_report(self, 
                                   player_stats: Dict = None,
                                   team_stats: Dict = None,
                                   pass_data: List = None,
                                   formation_data: Dict = None,
                                   match_summary: Dict = None,
                                   formats: List[str] = None) -> Dict[str, str]:
        """
        Export comprehensive analytics report in multiple formats.
        
        Args:
            player_stats: Player statistics dictionary
            team_stats: Team statistics dictionary
            pass_data: Pass detection data
            formation_data: Formation detection data
            match_summary: Match summary data
            formats: List of formats to export ('json', 'csv')
            
        Returns:
            Dictionary mapping data type to export paths
        """
        if formats is None:
            formats = ['json']
        
        exported_files = {}
        
        try:
            # Export player statistics
            if player_stats:
                for fmt in formats:
                    path = self.export_player_statistics(player_stats, fmt)
                    exported_files[f'player_stats_{fmt}'] = path
            
            # Export team statistics
            if team_stats:
                for fmt in formats:
                    path = self.export_team_statistics(team_stats, fmt)
                    exported_files[f'team_stats_{fmt}'] = path
            
            # Export pass data
            if pass_data:
                for fmt in formats:
                    path = self.export_pass_data(pass_data, fmt)
                    exported_files[f'pass_data_{fmt}'] = path
            
            # Export formation data
            if formation_data:
                for fmt in formats:
                    path = self.export_formation_data(formation_data, fmt)
                    exported_files[f'formation_data_{fmt}'] = path
            
            # Export match summary (JSON only)
            if match_summary:
                path = self.export_match_summary(match_summary)
                exported_files['match_summary'] = path
            
            logger.info(f"Comprehensive report exported: {len(exported_files)} files")
            
        except Exception as e:
            logger.error(f"Error exporting comprehensive report: {e}")
            raise
        
        return exported_files
    
    def export_tracking_data(self, tracks: Dict, 
                            filename: str = "tracking_data.json") -> str:
        """
        Export raw tracking data.
        
        Args:
            tracks: Dictionary containing tracking data
            filename: Output filename
            
        Returns:
            Path to the exported file
        """
        # Convert numpy arrays and other non-serializable objects
        serializable_tracks = self._make_serializable(tracks)
        
        return self.export_to_json(
            serializable_tracks,
            filename=filename
        )
    
    def _make_serializable(self, obj: Any) -> Any:
        """
        Convert object to JSON-serializable format.
        
        Args:
            obj: Object to convert
            
        Returns:
            Serializable version of the object
        """
        import numpy as np
        
        if isinstance(obj, dict):
            return {key: self._make_serializable(value) 
                   for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._make_serializable(item) for item in obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        else:
            return obj
