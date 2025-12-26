# -*- coding: utf-8 -*-
"""
Story Mode System - Hell Chapter
Manages story stages, progression, and save/load functionality.
"""
import json
import os
from typing import List, Optional, Dict, Any
from settings import BASE_DIR

class StoryStage:
    """Represents a single story stage in a chapter."""
    
    def __init__(self, stage_id: str, name: str, description: str, 
                 waves: int, has_big_enemy: bool, path_points: List[tuple], 
                 has_true_boss: bool = False, difficulty: float = 1.0,
                 path_color: tuple = (80, 85, 100)): # Default GRAY
        self.stage_id = stage_id  # e.g., "1-1", "1-2"
        self.name = name
        self.description = description
        self.waves = waves  # Total waves in this stage
        self.has_big_enemy = has_big_enemy  # BigEnemy appears after final wave
        self.has_true_boss = has_true_boss  # True Boss appears (overrides BigEnemy)
        self.path_points = path_points
        self.difficulty = difficulty
        self.path_color = path_color
        
    def get_wave_description(self, wave_num: int) -> str:
        """Get description text for a specific wave."""
        return f"{self.stage_id} Wave {wave_num}"


class StoryProgress:
    """Tracks player progression through story mode."""
    
    def __init__(self):
        self.completed_stages: List[str] = []
        self.current_stage: Optional[str] = None
        
    def is_stage_unlocked(self, stage_id: str, all_stages: List[StoryStage]) -> bool:
        """Check if a stage is unlocked based on progression. (UNLOCKED FOR TESTING)"""
        return True
    
    def complete_stage(self, stage_id: str):
        """Mark a stage as completed."""
        if stage_id not in self.completed_stages:
            self.completed_stages.append(stage_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving."""
        return {
            'completed_stages': self.completed_stages,
            'current_stage': self.current_stage
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StoryProgress':
        """Load from dictionary."""
        progress = StoryProgress()
        progress.completed_stages = data.get('completed_stages', [])
        progress.current_stage = data.get('current_stage', None)
        return progress


class StoryManager:
    """Manages story mode chapters and stages."""
    
    def __init__(self, save_path: Optional[str] = None):
        self.save_path = save_path or os.path.join(BASE_DIR, "story_progress.json")
        self.progress = StoryProgress()
        self.chapters: Dict[str, List[StoryStage]] = {}
        
        # Initialize Hell Chapter (Chapter 1)
        self._init_hell_chapter()
        
        # Persistence disabled: progression resets on restart
        # self.load_progress()
    
    def _init_hell_chapter(self):
        """Initialize Hell Chapter (1-1 to 1-5)."""
        hell_stages = [
            StoryStage(
                stage_id="1-1",
                name="Hell Gate",
                description="The entrance to the infernal realm. Demons pour forth!",
                waves=5,
                has_big_enemy=True,
                path_points=[
                    (1280, 100), (900, 100), (900, 300), (600, 300), (600, 600), (1280, 600)
                ],
                difficulty=1.0,
                path_color=(60, 160, 255) # BLUE
            ),
            StoryStage(
                stage_id="1-2",
                name="Burning Path",
                description="Walk the scorched path through rivers of lava.",
                waves=5,
                has_big_enemy=True,
                path_points=[
                    # Shifted Right (+250)
                    (350, 100), (650, 100), (650, 400), (450, 400), (450, 650), (1280, 650)
                ],
                difficulty=1.5,
                path_color=(255, 0, 0) # RED
            ),
            StoryStage(
                stage_id="1-3",
                name="Demon Fortress",
                description="A fortress built by the damned. Steel yourself!",
                waves=5,
                has_big_enemy=True,
                path_points=[
                    (1290, 80), (800, 80), (800, 500), (400, 500), (400, 300), (50, 300), (50, 650), (640, 650), (640, 800)
                ],
                difficulty=1.8,
                path_color=(50, 200, 50) # GREEN
            ),
            StoryStage(
                stage_id="1-4",
                name="Chamber of Torment",
                description="The air itself burns. The boss chamber awaits...",
                waves=5,
                has_big_enemy=True,
                path_points=[
                    (1280, 400), (900, 400), (900, 200), (600, 200), (600, 600), (1280, 600)
                ],
                difficulty=2.0,
                path_color=(139, 69, 19) # BROWN
            ),
            StoryStage(
                stage_id="1-5",
                name="Hell Lord's Throne",
                description="Face the Hell Lord himself! Prepare for the ultimate test!",
                waves=5,
                has_big_enemy=True,
                has_true_boss=True,
                path_points=[
                    (1280, 430), (1030, 430), (1030, 110), (430, 110), (430, 630), (1280, 630)
                ],
                difficulty=2.5,
                path_color=(218, 179, 0) # GOLD (R218 G179 B0)
            ),
        ]
        
        self.chapters["hell"] = hell_stages
    
    def get_chapter_stages(self, chapter_name: str) -> List[StoryStage]:
        """Get all stages for a chapter."""
        return self.chapters.get(chapter_name, [])
    
    def get_stage(self, stage_id: str) -> Optional[StoryStage]:
        """Get a specific stage by ID."""
        for chapter_stages in self.chapters.values():
            for stage in chapter_stages:
                if stage.stage_id == stage_id:
                    return stage
        return None
    
    def is_stage_unlocked(self, stage_id: str, chapter_name: str = "hell") -> bool:
        """Check if a stage is unlocked."""
        stages = self.get_chapter_stages(chapter_name)
        return self.progress.is_stage_unlocked(stage_id, stages)
    
    def complete_stage(self, stage_id: str):
        """Mark a stage as completed (session-based)."""
        self.progress.complete_stage(stage_id)
        # Persistence disabled
        # self.save_progress()
    
    def save_progress(self):
        """Save progress to file."""
        try:
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(self.progress.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Failed to save story progress: {e}")
    
    def load_progress(self):
        """Load progress from file."""
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.progress = StoryProgress.from_dict(data)
            except Exception as e:
                print(f"Failed to load story progress: {e}")
                self.progress = StoryProgress()
        else:
            self.progress = StoryProgress()
