"""Video processing utilities for reading and writing video files."""

import cv2
import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)


def read_video(video_path: str) -> List[np.ndarray]:
    """
    Read video file and return frames as a list of numpy arrays.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        List of video frames as numpy arrays
        
    Raises:
        FileNotFoundError: If video file doesn't exist
        ValueError: If video cannot be read
    """
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        frames = []
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        logger.info(f"Reading video: {video_path} ({frame_count} frames)")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        
        cap.release()
        logger.info(f"Successfully read {len(frames)} frames")
        return frames
        
    except Exception as e:
        logger.error(f"Error reading video: {str(e)}")
        raise


def save_video(output_video_frames: List[np.ndarray], 
               output_video_path: str,
               fps: int = 24,
               codec: str = 'mp4v') -> None:
    """
    Save video frames to a video file.
    
    Args:
        output_video_frames: List of video frames as numpy arrays
        output_video_path: Path where to save the output video
        fps: Frames per second for output video (default: 24)
        codec: Video codec to use (default: 'mp4v')
        
    Raises:
        ValueError: If frames list is empty or frames have inconsistent dimensions
    """
    if not output_video_frames:
        raise ValueError("No frames to save")
    
    try:
        fourcc = cv2.VideoWriter_fourcc(*codec)
        height, width = output_video_frames[0].shape[:2]
        
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            raise ValueError(f"Cannot create video writer for: {output_video_path}")
        
        logger.info(f"Saving video to: {output_video_path}")
        
        for frame in output_video_frames:
            if frame.shape[:2] != (height, width):
                logger.warning(f"Frame dimension mismatch. Expected {height}x{width}, got {frame.shape[:2]}")
            out.write(frame)
        
        out.release()
        logger.info(f"Video saved successfully: {len(output_video_frames)} frames")
        
    except Exception as e:
        logger.error(f"Error saving video: {str(e)}")
        raise


def get_video_properties(video_path: str) -> dict:
    """
    Get properties of a video file.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Dictionary containing video properties (fps, width, height, frame_count)
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")
    
    properties = {
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    }
    
    cap.release()
    return properties
