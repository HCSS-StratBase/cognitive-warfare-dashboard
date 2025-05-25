#!/usr/bin/env python
# coding: utf-8

"""
Burst detection utilities for temporal analysis.
"""

import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta

def detect_bursts(data: pd.Series, sensitivity: float = 1.0) -> List[Dict]:
    """
    Detect bursts in time series data using statistical methods.
    
    Args:
        data: Time series data (indexed by time)
        sensitivity: Sensitivity parameter (lower = more sensitive)
        
    Returns:
        List[Dict]: List of detected bursts
    """
    if len(data) < 5:
        return []
    
    bursts = []
    
    try:
        # Calculate moving statistics
        window_size = max(3, len(data) // 10)
        rolling_mean = data.rolling(window=window_size, center=True).mean()
        rolling_std = data.rolling(window=window_size, center=True).std()
        
        # Define burst threshold
        threshold_multiplier = 2.0 / sensitivity
        burst_threshold = rolling_mean + (threshold_multiplier * rolling_std)
        
        # Identify burst points
        burst_mask = data > burst_threshold
        
        # Group consecutive burst periods
        burst_groups = []
        current_group = []
        
        for i, is_burst in enumerate(burst_mask):
            if is_burst and not pd.isna(is_burst):
                current_group.append(i)
            else:
                if current_group:
                    burst_groups.append(current_group)
                    current_group = []
        
        # Add final group if it exists
        if current_group:
            burst_groups.append(current_group)
        
        # Create burst objects
        for group in burst_groups:
            if len(group) == 0:
                continue
                
            start_idx = group[0]
            end_idx = group[-1]
            
            # Calculate burst metrics
            burst_values = data.iloc[group]
            baseline_values = rolling_mean.iloc[group]
            
            burst = {
                'start_time': data.index[start_idx],
                'end_time': data.index[end_idx],
                'duration': len(group),
                'peak_value': burst_values.max(),
                'total_excess': (burst_values - baseline_values.fillna(burst_values.mean())).sum(),
                'intensity': calculate_burst_strength(burst_values),
                'baseline': baseline_values.mean() if not baseline_values.isna().all() else burst_values.mean()
            }
            
            bursts.append(burst)
        
        # Sort by intensity
        bursts.sort(key=lambda x: x['intensity'], reverse=True)
        
        logging.info(f"Detected {len(bursts)} bursts with sensitivity {sensitivity}")
        return bursts
        
    except Exception as e:
        logging.error(f"Error in burst detection: {e}")
        return []

def calculate_burst_strength(data: pd.Series) -> float:
    """
    Calculate the strength/intensity of a burst.
    
    Args:
        data: Time series data for the burst period
        
    Returns:
        float: Burst strength
    """
    if len(data) == 0:
        return 0.0
    
    try:
        # Use coefficient of variation and peak-to-mean ratio
        mean_val = data.mean()
        std_val = data.std()
        max_val = data.max()
        
        if mean_val == 0:
            return 0.0
        
        # Combine multiple metrics
        peak_ratio = max_val / mean_val
        cv = std_val / mean_val if mean_val > 0 else 0
        
        # Composite strength measure
        strength = (peak_ratio - 1) * (1 + cv)
        
        return max(0.0, strength)
        
    except Exception as e:
        logging.error(f"Error calculating burst strength: {e}")
        return 0.0

def detect_kleinberg_bursts(data: pd.Series, s: float = 2.0, gamma: float = 1.0) -> List[Dict]:
    """
    Implement simplified Kleinberg burst detection algorithm.
    
    Args:
        data: Time series data
        s: State transition cost parameter
        gamma: Burst intensity parameter
        
    Returns:
        List[Dict]: Detected bursts
    """
    # This is a simplified version - full Kleinberg algorithm is quite complex
    # For now, use the statistical method
    return detect_bursts(data, sensitivity=1.0/s)

def smooth_time_series(data: pd.Series, method: str = 'rolling', window: int = 3) -> pd.Series:
    """
    Smooth time series data to reduce noise.
    
    Args:
        data: Time series data
        method: Smoothing method ('rolling', 'exponential')
        window: Window size for smoothing
        
    Returns:
        pd.Series: Smoothed data
    """
    try:
        if method == 'rolling':
            return data.rolling(window=window, center=True).mean()
        elif method == 'exponential':
            return data.ewm(span=window).mean()
        else:
            return data
            
    except Exception as e:
        logging.error(f"Error smoothing time series: {e}")
        return data

def calculate_burst_statistics(bursts: List[Dict]) -> Dict:
    """
    Calculate summary statistics for detected bursts.
    
    Args:
        bursts: List of detected bursts
        
    Returns:
        Dict: Summary statistics
    """
    if not bursts:
        return {
            'total_bursts': 0,
            'average_duration': 0,
            'average_intensity': 0,
            'total_burst_time': 0
        }
    
    try:
        durations = [burst['duration'] for burst in bursts]
        intensities = [burst['intensity'] for burst in bursts]
        
        stats = {
            'total_bursts': len(bursts),
            'average_duration': np.mean(durations),
            'average_intensity': np.mean(intensities),
            'total_burst_time': np.sum(durations),
            'max_intensity': np.max(intensities),
            'min_intensity': np.min(intensities),
            'std_duration': np.std(durations),
            'std_intensity': np.std(intensities)
        }
        
        return stats
        
    except Exception as e:
        logging.error(f"Error calculating burst statistics: {e}")
        return {'total_bursts': 0}

def validate_burst_parameters(data: pd.Series, sensitivity: float) -> Tuple[bool, str]:
    """
    Validate parameters for burst detection.
    
    Args:
        data: Time series data
        sensitivity: Sensitivity parameter
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if len(data) < 3:
        return False, "Insufficient data points for burst detection (minimum 3 required)"
    
    if sensitivity <= 0:
        return False, "Sensitivity must be positive"
    
    if sensitivity > 10:
        return False, "Sensitivity too high (maximum 10)"
    
    if data.isna().all():
        return False, "All data points are missing"
    
    if (data < 0).any():
        return False, "Negative values not supported in burst detection"
    
    return True, ""

def interpolate_missing_values(data: pd.Series, method: str = 'linear') -> pd.Series:
    """
    Interpolate missing values in time series data.
    
    Args:
        data: Time series data with possible missing values
        method: Interpolation method
        
    Returns:
        pd.Series: Data with interpolated values
    """
    try:
        if method == 'linear':
            return data.interpolate(method='linear')
        elif method == 'forward':
            return data.fillna(method='ffill')
        elif method == 'backward':
            return data.fillna(method='bfill')
        else:
            return data.interpolate()
            
    except Exception as e:
        logging.error(f"Error interpolating missing values: {e}")
        return data