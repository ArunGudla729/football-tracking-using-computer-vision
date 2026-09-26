"""
Setup script to create necessary directories for SAIS.
Run this before first use.
"""

from pathlib import Path
import sys

def create_directories():
    """Create all necessary directories for the project."""
    
    directories = [
        'input_videos',
        'output_videos',
        'analytics_output',
        'logs',
        'stubs',
        'models',
    ]
    
    print("=" * 60)
    print("Sports Analytics Intelligence System (SAIS)")
    print("Directory Setup")
    print("=" * 60)
    
    created_count = 0
    existed_count = 0
    
    for directory in directories:
        dir_path = Path(directory)
        
        if dir_path.exists():
            print(f"✓ {directory}/ already exists")
            existed_count += 1
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created {directory}/")
            created_count += 1
        
        # Create .gitkeep files to preserve empty directories in git
        gitkeep_path = dir_path / '.gitkeep'
        if not gitkeep_path.exists():
            gitkeep_path.touch()
    
    print("=" * 60)
    print(f"Setup complete!")
    print(f"  - Created: {created_count} directories")
    print(f"  - Already existed: {existed_count} directories")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Place your trained model in models/ directory")
    print("2. Place your match video in input_videos/ directory")
    print("3. Run: python main.py")
    print("=" * 60)


if __name__ == '__main__':
    try:
        create_directories()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)
