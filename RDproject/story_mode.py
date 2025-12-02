# -*- coding: utf-8 -*-
"""
Story Mode System - Hell Chapter
Manages story stages, progression, and save/load functionality.
"""
import json
import os
from typing import List, Optional, Dict, Any

class StoryStage:
    """Represents a single story stage in a chapter."""
    
    def __init__(self, stage_id: str, name: str, description: str, 
                 waves: int, has_boss: bool, path_points: List[tuple], 
                 difficulty: float = 1.0):
        self.stage_id = stage_id  # e.g., "1-1", "1-2"
        self.name = name
        self.description = description
        self.waves = waves  # Total waves in this stage
        self.has_boss = has_boss  # Boss appears after final wave
        self.path_points = path_points
        self.difficulty = difficulty
        
    def get_wave_description(self, wave_num: int) -> str:
        """Get description text for a specific wave."""
        return f"{self.stage_id} Wave {wave_num}"


class StoryProgress:
    """Tracks player progression through story mode."""
    
    def __init__(self):
        self.completed_stages: List[str] = []
        self.current_stage: Optional[str] = None
        
    def is_stage_unlocked(self, stage_id: str, all_stages: List[StoryStage]) -> bool:
        """Check if a stage is unlocked based on progression."""
        # First stage is always unlocked
        if stage_id == all_stages[0].stage_id:
            return True
        
        # Find the index of this stage
        for i, stage in enumerate(all_stages):
            if stage.stage_id == stage_id:
                # Stage is unlocked if previous stage is completed
                if i > 0:
                    prev_stage_id = all_stages[i - 1].stage_id
                    return prev_stage_id in self.completed_stages
                return True
        return False
    
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
    
    def __init__(self, save_path: str = "story_progress.json"):
        self.save_path = save_path
        self.progress = StoryProgress()
        self.chapters: Dict[str, List[StoryStage]] = {}
        
        # Initialize Hell Chapter (Chapter 1)
        self._init_hell_chapter()
        
        # Load saved progress
        self.load_progress()
    
    def _init_hell_chapter(self):
        """Initialize Hell Chapter (1-1 to 1-5)."""
        hell_stages = [
            StoryStage(
                stage_id="1-1",
                name="Hell Gate",
                description="The entrance to the infernal realm. Demons pour forth!",
                waves=5,
                has_boss=False,
                path_points=[
                    (1280, 125),
                    (500, 125),
                    (500, 650),
                    (1280, 650)
                ],
                difficulty=1.0
            ),
            StoryStage(
                stage_id="1-2",
                name="Burning Path",
                description="Walk the scorched path through rivers of lava.",
                waves=5,
                has_boss=False,
                path_points=[
                    (100, 100),
                    (100, 650),
                    (1200, 650)
                ],
                difficulty=1.1
            ),
            StoryStage(
                stage_id="1-3",
                name="Demon Fortress",
                description="A fortress built by the damned. Steel yourself!",
                waves=5,
                has_boss=False,
                path_points=[
                    (1200, 80),
                    (100, 80),
                    (100, 650),
                    (600, 650)
                ],
                difficulty=1.2
            ),
            StoryStage(
                stage_id="1-4",
                name="Chamber of Torment",
                description="The air itself burns. The boss chamber awaits...",
                waves=5,
                has_boss=False,
                path_points=[
                    (1280, 400),
                    (500, 400),
                    (500, 650),
                    (1280, 650)
                ],
                difficulty=1.3
            ),
            StoryStage(
                stage_id="1-5",
                name="Hell Lord's Throne",
                description="Face the Hell Lord himself! Prepare for the ultimate test!",
                waves=5,
                has_boss=True,  # Boss appears after wave 5
                path_points=[
                    (1200, 80),
                    (500, 80),
                    (500, 400),
                    (1200, 400),
                    (1200, 650)
                ],
                difficulty=1.5
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
        """Mark a stage as completed and save progress."""
        self.progress.complete_stage(stage_id)
        self.save_progress()
    
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
