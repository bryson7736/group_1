
import json
import sys
import os

# Add project path
sys.path.append('/home/sutender/rdproject/group_1')

from RDproject.leaderboard import LeaderboardManager

def fix_leaderboard():
    filepath = "/home/sutender/rdproject/group_1/leaderboard.json"
    
    if not os.path.exists(filepath):
        print("Leaderboard file not found.")
        return

    with open(filepath, 'r') as f:
        data = json.load(f)

    print("Original data:", data)

    # Deduplicate keeping highest score
    best_scores = {}
    for entry in data:
        name = entry['name']
        waves = entry['waves']
        if name in best_scores:
            if waves > best_scores[name]:
                best_scores[name] = waves
        else:
            best_scores[name] = waves

    # Convert back to list
    new_scores = [{"name": n, "waves": w} for n, w in best_scores.items()]
    
    # Add sutender
    sutender_score = 274
    if "sutender" in best_scores:
        if sutender_score > best_scores["sutender"]:
             best_scores["sutender"] = sutender_score
    else:
        best_scores["sutender"] = sutender_score
        
    # Rebuild list
    final_scores = [{"name": n, "waves": w} for n, w in best_scores.items()]
    
    # Sort
    final_scores.sort(key=lambda x: x["waves"], reverse=True)
    
    # Keep top 10
    final_scores = final_scores[:10]
    
    print("New data:", final_scores)

    with open(filepath, 'w') as f:
        json.dump(final_scores, f, indent=4)

if __name__ == "__main__":
    fix_leaderboard()
