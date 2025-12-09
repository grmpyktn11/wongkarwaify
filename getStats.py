import analyzeData
import json

# Run your analyses
faStats = analyzeData.analyzeFrames("frameFA")
mlStats = analyzeData.analyzeFrames("frameITMFL")

# Save to JSON
stats = {
    "fa": faStats,
    "ml": mlStats
}

with open("movie_stats.json", "w") as f:
    json.dump(stats, f, indent=4)

print("Saved stats to movie_stats.json")
