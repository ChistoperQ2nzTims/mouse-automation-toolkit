#!/usr/bin/env python3
"""
Advanced Transformation Example - Mouse Automation Toolkit

This example demonstrates advanced transformation capabilities including
chained transformations, batch operations, and complex geometric transformations.
"""

import sys
import os
import json
import math

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.transformer import CoordinateTransformer
    from src.recorder import MouseRecorder
except ImportError:
    print("Error: Could not import required modules. Please ensure pynput is installed.")
    print("Run: pip install pynput")
    sys.exit(1)


def create_sample_actions():
    """Create a complex pattern of sample actions for transformation demos"""
    actions = []
    
    # Create a square pattern
    square_size = 100
    center_x, center_y = 300, 300
    
    # Square corners
    corners = [
        (center_x - square_size//2, center_y - square_size//2),  # Top-left
        (center_x + square_size//2, center_y - square_size//2),  # Top-right
        (center_x + square_size//2, center_y + square_size//2),  # Bottom-right
        (center_x - square_size//2, center_y + square_size//2),  # Bottom-left
    ]
    
    # Add corner clicks
    for i, (x, y) in enumerate(corners):
        actions.append({
            'type': 'click',
            'x': x,
            'y': y,
            'button': 'left',
            'timestamp': i * 0.5,
            'absolute_time': f'2024-01-01T12:00:0{i}'
        })
    
    # Add center click
    actions.append({
        'type': 'click',
        'x': center_x,
        'y': center_y,
        'button': 'right',
        'timestamp': 2.0,
        'absolute_time': '2024-01-01T12:00:04'
    })
    
    # Add circular pattern around center
    for i in range(8):
        angle = i * (360 / 8)
        radius = 30
        x = center_x + radius * math.cos(math.radians(angle))
        y = center_y + radius * math.sin(math.radians(angle))
        
        actions.append({
            'type': 'click',
            'x': int(x),
            'y': int(y),
            'button': 'middle',
            'timestamp': 2.5 + i * 0.2,
            'absolute_time': f'2024-01-01T12:00:0{5 + i}'
        })
    
    return actions


def demonstrate_basic_transformations(actions):
    """Demonstrate each transformation type individually"""
    print("=== Basic Transformations Demo ===")
    
    transformer = CoordinateTransformer()
    original_bbox = transformer.get_bounding_box(actions)
    
    print(f"Original pattern: {len(actions)} actions")
    print(f"Bounding box: {original_bbox['width']:.0f}x{original_bbox['height']:.0f}")
    print(f"Center: ({original_bbox['center_x']:.0f}, {original_bbox['center_y']:.0f})")
    
    # 1. Translation
    print("\n1. Translation (+200, +100):")
    trans = transformer.create_translation_transform(200, 100)
    translated = transformer.transform_actions(actions, [trans])
    trans_bbox = transformer.get_bounding_box(translated)
    print(f"   New center: ({trans_bbox['center_x']:.0f}, {trans_bbox['center_y']:.0f})")
    
    # 2. Scaling
    print("\n2. Scaling (1.5x, 0.8x) around center:")
    scale = transformer.create_scale_transform(1.5, 0.8, (original_bbox['center_x'], original_bbox['center_y']))
    scaled = transformer.transform_actions(actions, [scale])
    scale_bbox = transformer.get_bounding_box(scaled)
    print(f"   New size: {scale_bbox['width']:.0f}x{scale_bbox['height']:.0f}")
    
    # 3. Rotation
    print("\n3. Rotation (45° around center):")
    rotate = transformer.create_rotation_transform(45, (original_bbox['center_x'], original_bbox['center_y']))
    rotated = transformer.transform_actions(actions, [rotate])
    rotate_bbox = transformer.get_bounding_box(rotated)
    print(f"   New bounding box: {rotate_bbox['width']:.0f}x{rotate_bbox['height']:.0f}")
    
    # 4. Mirroring
    print("\n4. Horizontal mirroring:")
    mirror = transformer.create_mirror_transform('horizontal', (original_bbox['center_x'], original_bbox['center_y']))
    mirrored = transformer.transform_actions(actions, [mirror])
    mirror_bbox = transformer.get_bounding_box(mirrored)
    print(f"   Center after mirror: ({mirror_bbox['center_x']:.0f}, {mirror_bbox['center_y']:.0f})")
    
    return translated, scaled, rotated, mirrored


def demonstrate_chained_transformations(actions):
    """Demonstrate chaining multiple transformations"""
    print("\n=== Chained Transformations Demo ===")
    
    transformer = CoordinateTransformer()
    original_bbox = transformer.get_bounding_box(actions)
    
    # Create a complex transformation chain
    transformations = [
        # 1. First, translate to origin
        transformer.create_translation_transform(-original_bbox['center_x'], -original_bbox['center_y']),
        
        # 2. Scale down
        transformer.create_scale_transform(0.5, 0.5),
        
        # 3. Rotate 90 degrees
        transformer.create_rotation_transform(90),
        
        # 4. Mirror horizontally
        transformer.create_mirror_transform('horizontal'),
        
        # 5. Scale back up asymmetrically
        transformer.create_scale_transform(2.0, 1.5),
        
        # 6. Translate to new position
        transformer.create_translation_transform(500, 200)
    ]
    
    print(f"Applying {len(transformations)} chained transformations:")
    for i, trans in enumerate(transformations, 1):
        print(f"  {i}. {trans['type']}: {trans}")
    
    # Apply all transformations
    result = transformer.transform_actions(actions, transformations)
    result_bbox = transformer.get_bounding_box(result)
    
    print(f"\nResult:")
    print(f"  Original center: ({original_bbox['center_x']:.0f}, {original_bbox['center_y']:.0f})")
    print(f"  Final center: ({result_bbox['center_x']:.0f}, {result_bbox['center_y']:.0f})")
    print(f"  Original size: {original_bbox['width']:.0f}x{original_bbox['height']:.0f}")
    print(f"  Final size: {result_bbox['width']:.0f}x{result_bbox['height']:.0f}")
    
    return result


def demonstrate_batch_operations(actions):
    """Demonstrate batch transformation operations"""
    print("\n=== Batch Operations Demo ===")
    
    transformer = CoordinateTransformer()
    
    # 1. Fit to screen
    print("1. Fit to screen (1920x1080 with 50px margin):")
    fitted = transformer.fit_to_screen(actions, 1920, 1080, margin=50)
    fitted_bbox = transformer.get_bounding_box(fitted)
    print(f"   Fitted to: ({fitted_bbox['min_x']:.0f}, {fitted_bbox['min_y']:.0f}) - "
          f"({fitted_bbox['max_x']:.0f}, {fitted_bbox['max_y']:.0f})")
    
    # 2. Center on screen
    print("\n2. Center on 800x600 screen:")
    screen_center_x, screen_center_y = 400, 300
    current_bbox = transformer.get_bounding_box(actions)
    offset_x = screen_center_x - current_bbox['center_x']
    offset_y = screen_center_y - current_bbox['center_y']
    
    center_transform = transformer.create_translation_transform(offset_x, offset_y)
    centered = transformer.transform_actions(actions, [center_transform])
    centered_bbox = transformer.get_bounding_box(centered)
    print(f"   Centered at: ({centered_bbox['center_x']:.0f}, {centered_bbox['center_y']:.0f})")
    
    # 3. Create multiple copies with different transformations
    print("\n3. Create multiple transformed copies:")
    copies = []
    
    # Original
    copies.append(("Original", actions))
    
    # Translated copies
    for i, (offset_x, offset_y) in enumerate([(100, 0), (200, 0), (300, 0)]):
        trans = transformer.create_translation_transform(offset_x, offset_y)
        copy = transformer.transform_actions(actions, [trans])
        copies.append((f"Copy {i+1} (+{offset_x}, +{offset_y})", copy))
    
    # Scaled copies
    for i, (scale_x, scale_y) in enumerate([(0.5, 0.5), (1.5, 1.5), (2.0, 0.5)]):
        scale = transformer.create_scale_transform(scale_x, scale_y, (400, 400))
        trans = transformer.create_translation_transform(0, 200 * (i + 1))
        copy = transformer.transform_actions(actions, [scale, trans])
        copies.append((f"Scaled {scale_x}x{scale_y}", copy))
    
    print(f"   Created {len(copies)} copies with different transformations")
    
    # Combine all copies into one action set
    combined_actions = []
    timestamp_offset = 0
    
    for name, copy in copies:
        for action in copy:
            new_action = action.copy()
            new_action['timestamp'] += timestamp_offset
            combined_actions.append(new_action)
        timestamp_offset += 5.0  # 5 second delay between copies
        print(f"   Added {name}: {len(copy)} actions")
    
    print(f"   Combined total: {len(combined_actions)} actions over {timestamp_offset:.1f} seconds")
    
    return combined_actions


def demonstrate_geometric_patterns(actions):
    """Demonstrate creating geometric patterns through transformations"""
    print("\n=== Geometric Patterns Demo ===")
    
    transformer = CoordinateTransformer()
    
    # 1. Create a star pattern by rotating the original pattern
    print("1. Creating star pattern (8 rotated copies):")
    star_actions = []
    center = (400, 300)
    
    for i in range(8):
        angle = i * 45  # 45 degrees apart
        
        # First translate to origin, then rotate, then translate to center
        transformations = [
            transformer.create_translation_transform(-300, -300),  # Move to origin
            transformer.create_rotation_transform(angle),         # Rotate
            transformer.create_translation_transform(center[0], center[1])  # Move to center
        ]
        
        rotated = transformer.transform_actions(actions, transformations)
        star_actions.extend(rotated)
    
    star_bbox = transformer.get_bounding_box(star_actions)
    print(f"   Star pattern: {len(star_actions)} total actions")
    print(f"   Pattern size: {star_bbox['width']:.0f}x{star_bbox['height']:.0f}")
    
    # 2. Create a spiral pattern
    print("\n2. Creating spiral pattern (10 scaled & rotated copies):")
    spiral_actions = []
    
    for i in range(10):
        scale_factor = 0.2 + (i * 0.08)  # Gradually increase size
        angle = i * 36  # 36 degrees apart
        
        transformations = [
            transformer.create_translation_transform(-300, -300),  # Move to origin
            transformer.create_scale_transform(scale_factor, scale_factor),  # Scale
            transformer.create_rotation_transform(angle),         # Rotate
            transformer.create_translation_transform(center[0], center[1])  # Move to center
        ]
        
        spiral_copy = transformer.transform_actions(actions, transformations)
        spiral_actions.extend(spiral_copy)
    
    spiral_bbox = transformer.get_bounding_box(spiral_actions)
    print(f"   Spiral pattern: {len(spiral_actions)} total actions")
    print(f"   Pattern size: {spiral_bbox['width']:.0f}x{spiral_bbox['height']:.0f}")
    
    # 3. Create a kaleidoscope pattern
    print("\n3. Creating kaleidoscope pattern (mirroring + rotation):")
    kaleidoscope_actions = []
    
    # Create 6 segments, each mirrored and rotated
    for i in range(6):
        angle = i * 60  # 60 degrees apart
        
        # First create horizontal mirror
        mirror_h = transformer.create_mirror_transform('horizontal', (300, 300))
        mirrored = transformer.transform_actions(actions, [mirror_h])
        
        # Then rotate
        transformations = [
            transformer.create_translation_transform(-300, -300),
            transformer.create_rotation_transform(angle),
            transformer.create_translation_transform(center[0], center[1])
        ]
        
        rotated = transformer.transform_actions(mirrored, transformations)
        kaleidoscope_actions.extend(rotated)
        
        # Also add the original (non-mirrored) rotated version
        original_rotated = transformer.transform_actions(actions, transformations)
        kaleidoscope_actions.extend(original_rotated)
    
    kaleidoscope_bbox = transformer.get_bounding_box(kaleidoscope_actions)
    print(f"   Kaleidoscope pattern: {len(kaleidoscope_actions)} total actions")
    print(f"   Pattern size: {kaleidoscope_bbox['width']:.0f}x{kaleidoscope_bbox['height']:.0f}")
    
    return star_actions, spiral_actions, kaleidoscope_actions


def save_transformed_patterns(patterns):
    """Save all transformed patterns to files"""
    print("\n=== Saving Patterns ===")
    
    pattern_names = [
        "star_pattern",
        "spiral_pattern", 
        "kaleidoscope_pattern"
    ]
    
    for name, pattern in zip(pattern_names, patterns):
        filename = f"examples/{name}.json"
        
        data = {
            'metadata': {
                'version': '1.0',
                'pattern_name': name,
                'total_actions': len(pattern),
                'created_by': 'advanced_transform.py'
            },
            'actions': pattern
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"   Saved {name}: {len(pattern)} actions to {filename}")
        except Exception as e:
            print(f"   Error saving {name}: {e}")


def demonstrate_transformation_preview():
    """Demonstrate transformation preview functionality"""
    print("\n=== Transformation Preview Demo ===")
    
    transformer = CoordinateTransformer()
    actions = create_sample_actions()
    
    # Create some transformations to preview
    transformations = [
        transformer.create_translation_transform(100, 50),
        transformer.create_scale_transform(1.5, 1.2),
        transformer.create_rotation_transform(30)
    ]
    
    # Get preview
    preview = transformer.preview_transformation(actions, transformations)
    
    print("Transformation preview:")
    print(f"  Original bounding box: {preview['original_bbox']['width']:.0f}x{preview['original_bbox']['height']:.0f}")
    print(f"  Transformed bounding box: {preview['transformed_bbox']['width']:.0f}x{preview['transformed_bbox']['height']:.0f}")
    print(f"  Sample transformations:")
    
    for i, point in enumerate(preview['sample_points'][:5]):  # Show first 5
        orig = point['original']
        trans = point['transformed']
        print(f"    Point {i+1}: ({orig[0]:.0f}, {orig[1]:.0f}) → ({trans[0]:.0f}, {trans[1]:.0f})")


def main():
    """Main example function"""
    print("Mouse Automation Toolkit - Advanced Transformation Examples")
    print("=" * 60)
    
    # Create sample data
    actions = create_sample_actions()
    print(f"Created sample pattern with {len(actions)} actions")
    
    # Demonstrate basic transformations
    transformed_variants = demonstrate_basic_transformations(actions)
    
    # Demonstrate chained transformations
    chained_result = demonstrate_chained_transformations(actions)
    
    # Demonstrate batch operations
    batch_result = demonstrate_batch_operations(actions)
    
    # Demonstrate geometric patterns
    patterns = demonstrate_geometric_patterns(actions)
    
    # Demonstrate preview functionality
    demonstrate_transformation_preview()
    
    # Save patterns to files
    save_transformed_patterns(patterns)
    
    print("\n=== Advanced Transformation Examples Completed ===")
    print("Check the generated JSON files to see the transformed patterns!")


if __name__ == "__main__":
    main()