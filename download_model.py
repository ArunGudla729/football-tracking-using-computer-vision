"""
Helper script to download a YOLOv8 model for the Sports Analytics System.
This downloads a standard YOLOv8 model that can detect objects including people and sports balls.

For best results with football analysis, you should use a football-specific trained model.
"""

import os
import sys
from pathlib import Path

def download_model():
    """Download YOLOv8 model and place it in the models directory."""
    
    print("=" * 70)
    print("Sports Analytics Intelligence System (SAIS)")
    print("Model Download Helper")
    print("=" * 70)
    print()
    
    try:
        from ultralytics import YOLO
        import shutil
        
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        target_path = models_dir / "best.pt"
        
        if target_path.exists():
            print(f"⚠️  Model already exists at: {target_path}")
            response = input("Do you want to replace it? (yes/no): ").lower()
            if response not in ['yes', 'y']:
                print("❌ Download cancelled.")
                return
            print()
        
        print("📥 Downloading YOLOv8 medium model...")
        print("   This may take a few minutes depending on your internet speed...")
        print()
        
        # Download YOLOv8 medium model
        model = YOLO('yolov8m.pt')
        
        # Copy to models directory
        if os.path.exists('yolov8m.pt'):
            shutil.copy('yolov8m.pt', str(target_path))
            print(f"✅ Model downloaded successfully!")
            print(f"   Location: {target_path}")
            print()
            
            # Clean up
            try:
                os.remove('yolov8m.pt')
            except:
                pass
        
        print("=" * 70)
        print("✅ SETUP COMPLETE!")
        print("=" * 70)
        print()
        print("⚠️  IMPORTANT NOTE:")
        print("   This is a STANDARD YOLOv8 model (not football-specific).")
        print("   It will work, but for BEST results, use a model trained on")
        print("   football data.")
        print()
        print("Next steps:")
        print("   1. Ensure your video is in: input_videos/")
        print("   2. Run: python main.py")
        print()
        print("=" * 70)
        
    except ImportError:
        print("❌ Error: 'ultralytics' package not found!")
        print()
        print("Please install required packages first:")
        print("   pip install -r requirements.txt")
        print()
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print()
        print("Alternative options:")
        print("1. Download manually from: https://github.com/ultralytics/assets/releases")
        print("2. Train your own using: training/football_training_yolo_v5.ipynb")
        print("3. Check original project repository for pre-trained model")
        print()
        sys.exit(1)


if __name__ == '__main__':
    download_model()
