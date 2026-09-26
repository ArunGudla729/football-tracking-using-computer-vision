"""Bounding box utility functions for object detection and tracking."""

import numpy as np
from typing import Tuple, List


def get_center_of_bbox(bbox: List[float]) -> Tuple[int, int]:
    """
    Calculate the center point of a bounding box.
    
    Args:
        bbox: Bounding box coordinates [x1, y1, x2, y2]
        
    Returns:
        Tuple of (x, y) coordinates of the center point
    """
    x1, y1, x2, y2 = bbox
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)
    return center_x, center_y


def get_bbox_width(bbox: List[float]) -> int:
    """
    Calculate the width of a bounding box.
    
    Args:
        bbox: Bounding box coordinates [x1, y1, x2, y2]
        
    Returns:
        Width of the bounding box
    """
    return int(bbox[2] - bbox[0])


def get_bbox_height(bbox: List[float]) -> int:
    """
    Calculate the height of a bounding box.
    
    Args:
        bbox: Bounding box coordinates [x1, y1, x2, y2]
        
    Returns:
        Height of the bounding box
    """
    return int(bbox[3] - bbox[1])


def get_foot_position(bbox: List[float]) -> Tuple[int, int]:
    """
    Get the foot position (bottom center) of a bounding box.
    Used for accurate player position tracking.
    
    Args:
        bbox: Bounding box coordinates [x1, y1, x2, y2]
        
    Returns:
        Tuple of (x, y) coordinates of the foot position
    """
    x1, y1, x2, y2 = bbox
    foot_x = int((x1 + x2) / 2)
    foot_y = int(y2)
    return foot_x, foot_y


def measure_distance(point1: Tuple[float, float], 
                     point2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points.
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
        
    Returns:
        Euclidean distance between the two points
    """
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def measure_xy_distance(point1: Tuple[float, float], 
                        point2: Tuple[float, float]) -> Tuple[float, float]:
    """
    Calculate the X and Y distance components between two points.
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
        
    Returns:
        Tuple of (x_distance, y_distance)
    """
    x_distance = point1[0] - point2[0]
    y_distance = point1[1] - point2[1]
    return x_distance, y_distance


def get_bbox_area(bbox: List[float]) -> float:
    """
    Calculate the area of a bounding box.
    
    Args:
        bbox: Bounding box coordinates [x1, y1, x2, y2]
        
    Returns:
        Area of the bounding box
    """
    width = get_bbox_width(bbox)
    height = get_bbox_height(bbox)
    return width * height


def calculate_iou(bbox1: List[float], bbox2: List[float]) -> float:
    """
    Calculate Intersection over Union (IoU) between two bounding boxes.
    
    Args:
        bbox1: First bounding box [x1, y1, x2, y2]
        bbox2: Second bounding box [x1, y1, x2, y2]
        
    Returns:
        IoU score between 0 and 1
    """
    x1_inter = max(bbox1[0], bbox2[0])
    y1_inter = max(bbox1[1], bbox2[1])
    x2_inter = min(bbox1[2], bbox2[2])
    y2_inter = min(bbox1[3], bbox2[3])
    
    if x2_inter < x1_inter or y2_inter < y1_inter:
        return 0.0
    
    intersection = (x2_inter - x1_inter) * (y2_inter - y1_inter)
    area1 = get_bbox_area(bbox1)
    area2 = get_bbox_area(bbox2)
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0.0
