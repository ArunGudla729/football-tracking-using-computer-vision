# 🚀 Quick Start Guide - Sports Analytics Intelligence System

Get up and running with SAIS in 5 minutes!

## Step 1: Installation (2 minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/sports-analytics-system.git
cd sports-analytics-system

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Setup Directories (30 seconds)

```bash
python setup_directories.py
```

This creates all necessary folders for the project.

## Step 3: Prepare Your Data (1 minute)

1. **Add Your Model**
   - Download or train a YOLOv8 model
   - Place it in `models/` folder
   - Name it `best.pt` or update config

2. **Add Your Video**
   - Place your football match video in `input_videos/`
   - Supported formats: MP4, AVI, MOV

## Step 4: Configure (Optional)

Edit `config/config.yaml` to customize:

```yaml
video:
  input_path: "input_videos/your_match.mp4"  # Change this
  output_path: "output_videos/analyzed_match.mp4"

analytics:
  generate_heatmaps: true
  track_formations: true
  analyze_passes: true
```

## Step 5: Run Analysis (1-10 minutes depending on video length)

```bash
python main.py
```

## 📊 What You'll Get

After processing, check these folders:

### `output_videos/`
- Annotated video with player tracking, team colors, speed, and possession

### `analytics_output/`
- `player_statistics.json` - Individual player metrics
- `team_statistics.json` - Team-level statistics  
- `pass_data.json` - All detected passes
- `formation_data.json` - Formation tracking
- `match_summary_report.json` - Overall match insights
- `team_1_heatmap.jpg` - Team 1 heat map
- `team_2_heatmap.jpg` - Team 2 heat map

### `logs/`
- Detailed execution logs

## 🎯 Example Output

### Player Statistics
```json
{
  "player_5": {
    "total_distance": 10234.56,
    "max_speed": 9.2,
    "avg_speed": 3.5,
    "sprints": 47,
    "passes_attempted": 42,
    "pass_accuracy": 85.7
  }
}
```

### Team Statistics
```json
{
  "team_1": {
    "possession_percentage": 58.3,
    "total_passes": 324,
    "pass_accuracy": 82.4,
    "dominant_formation": "4-3-3"
  }
}
```

## 🔧 Troubleshooting

### Model Not Found
```bash
# Error: models/best.pt not found
# Solution: Place your YOLOv8 model in models/ folder
```

### Video Not Found
```bash
# Error: input video not found
# Solution: Update config.yaml with correct path
```

### Out of Memory
```bash
# Solution: Reduce batch size in tracker.py or use smaller video
```

### Slow Processing
```bash
# Solution: Use GPU acceleration (requires CUDA)
# Or process shorter video clips
```

## 💡 Pro Tips

1. **Start with a short clip** (30-60 seconds) to test
2. **Check logs/** if something goes wrong
3. **Adjust confidence threshold** in config for better detection
4. **Use GPU** for 10x faster processing
5. **Export in multiple formats** (JSON & CSV) for flexibility

## 📚 Next Steps

- Read full [README.md](README.md) for detailed features
- Explore [config/config.yaml](config/config.yaml) for all options
- Check [CHANGELOG.md](CHANGELOG.md) for recent updates
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## 🆘 Need Help?

- Check the logs in `logs/sports_analytics.log`
- Open an issue on GitHub
- Review the documentation

---

**Ready to analyze some football! ⚽🎉**
