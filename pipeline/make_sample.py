#!/usr/bin/env python3
"""
Generate synthetic sample data for testing.
Creates slope.npy and grid.json in data/processed/sample/
"""

import json
import numpy as np
from pathlib import Path
import os


def create_sample_data():
    """Create sample slope and grid data."""
    
    # Create output directory
    output_dir = Path("data/processed/sample")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create synthetic slope data (100x100 float32)
    # Smooth terrain with one ridge and one crater
    slope = np.zeros((100, 100), dtype=np.float32)
    
    # Add smooth base (slight slope)
    x = np.linspace(0, 1, 100)
    y = np.linspace(0, 1, 100)
    X, Y = np.meshgrid(x, y)
    slope = 5 * (X + Y) / 2  # Gentle slope across terrain
    
    # Add ridge (diagonal line with higher slope)
    ridge_mask = np.abs(X - Y) < 0.1
    slope[ridge_mask] = np.minimum(slope[ridge_mask] + 15, 30)  # Ridge slopes up to 30°
    
    # Add crater (circular depression with lower slope in center, steep walls)
    crater_center = (70, 30)
    crater_radius = 15
    dy = np.arange(100) - crater_center[0]
    dx = np.arange(100) - crater_center[1]
    DX, DY = np.meshgrid(dx, dy)
    dist = np.sqrt(DX**2 + DY**2)
    
    crater_mask = dist < crater_radius
    slope[crater_mask] = np.maximum(5, 25 * np.exp(-dist[crater_mask] / 5))  # Crater with steep walls, flat center
    
    # Smooth with gaussian to make terrain more realistic
    from scipy.ndimage import gaussian_filter
    slope = gaussian_filter(slope, sigma=2)
    
    # Clamp to 0-30 range
    slope = np.clip(slope, 0, 30).astype(np.float32)
    
    # Save slope data
    slope_path = output_dir / "slope.npy"
    np.save(slope_path, slope)
    
    # Create grid.json with required fields
    grid_data = {
        "source_product_name": "SYNTHETIC SAMPLE - not real data",
        "version": "1.0",
        "pixel_size_m": 5.0,
        "width": 100,
        "height": 100,
        "top_left_coordinate": {
            "latitude": -4.5,
            "longitude": 137.5
        },
        "coordinate_notes": "Synthetic sample data - coordinates are arbitrary for testing purposes"
    }
    
    grid_path = output_dir / "grid.json"
    with open(grid_path, 'w') as f:
        json.dump(grid_data, f, indent=2)
    
    # Print results
    print("Sample data created successfully!\n")
    print(f"slope.npy: {slope_path}")
    print(f"  Size: {os.path.getsize(slope_path)} bytes")
    print(f"  Shape: {slope.shape}")
    print(f"  Data type: {slope.dtype}")
    print(f"  Range: {slope.min():.2f} - {slope.max():.2f} degrees\n")
    
    print(f"grid.json: {grid_path}")
    print(f"  Size: {os.path.getsize(grid_path)} bytes")
    print(f"  Fields: source_product_name, version, pixel_size_m, width, height,")
    print(f"          top_left_coordinate, coordinate_notes")


if __name__ == "__main__":
    create_sample_data()
