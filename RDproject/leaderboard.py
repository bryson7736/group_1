import json
import os
from typing import List, Dict, Any

class LeaderboardManager:
    """
    Manages the leaderboard data, loading from and saving to a JSON file.
    """
    def __init__(self, filepath: str = "leaderboard.json"):
        self.filepath = filepath
        self.scores: List[Dict[str, Any]] = []
        self.load_leaderboard()

    def load_leaderboard(self) -> None:
        """Load scores from the JSON file."""
        if not os.path.exists(self.filepath):
            self.scores = []
            return

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.scores = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading leaderboard: {e}")
            self.scores = []

    def save_score(self, name: str, waves: int) -> None:
        """
        Add a new score, sort the leaderboard, keep top 10, and save to file.
        """
        self.scores.append({"name": name, "waves": waves})
        # Sort descending by waves
        self.scores.sort(key=lambda x: x["waves"], reverse=True)
        # Keep top 10
        self.scores = self.scores[:10]
        
        self._write_to_file()

    def _write_to_file(self) -> None:
        """Write current scores to file."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, indent=4)
        except IOError as e:
            print(f"Error saving leaderboard: {e}")

    def get_top_scores(self) -> List[Dict[str, Any]]:
        """Return the list of top scores."""
        return self.scores

    def is_high_score(self, waves: int) -> bool:
        """Check if the given wave count qualifies for the leaderboard."""
        if len(self.scores) < 10:
            return True
        return waves > self.scores[-1]["waves"]
