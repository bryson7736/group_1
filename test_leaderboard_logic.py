
import unittest
import os
import json
import sys

# Add the project directory to sys.path so we can import RDproject
sys.path.append('/home/sutender/rdproject/group_1')

from RDproject.leaderboard import LeaderboardManager

class TestLeaderboard(unittest.TestCase):
    def setUp(self):
        self.test_file = "/home/sutender/rdproject/group_1/test_leaderboard_logic.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.lb = LeaderboardManager(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_duplicate_name_higher_score(self):
        self.lb.save_score("Alice", 10)
        self.lb.save_score("Bob", 5)
        
        # Alice submits a higher score
        self.lb.save_score("Alice", 15)
        
        scores = self.lb.get_top_scores()
        # With current implementation, it will probably append, so we expect failure here
        # But I want to see it fail first or just verify current behavior
        
        # Current behavior: appends
        # Desired behavior: updates
        
        names = [s["name"] for s in scores]
        # If logic is not implemented, Alice will appear twice
        alice_count = names.count("Alice")
        print(f"Alice count: {alice_count}")
        
        # This assertion expects the NEW behavior
        self.assertEqual(alice_count, 1, "Alice should only appear once")
        self.assertEqual(scores[0]["waves"], 15, "Alice's score should be updated to 15")

    def test_duplicate_name_lower_score(self):
        self.lb.save_score("Alice", 10)
        
        # Alice submits a lower score
        self.lb.save_score("Alice", 5)
        
        scores = self.lb.get_top_scores()
        names = [s["name"] for s in scores]
        alice_count = names.count("Alice")
        
        self.assertEqual(alice_count, 1, "Alice should only appear once")
        self.assertEqual(scores[0]["waves"], 10, "Alice's score should remain 10")

if __name__ == '__main__':
    unittest.main()
