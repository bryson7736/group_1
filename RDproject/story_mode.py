# -*- coding: utf-8 -*-
"""
Story Mode System - Hell Chapter
Manages story stages, progression, and save/load functionality.
"""
import json
import os
from typing import List, Optional, Dict, Any
from settings import BASE_DIR, SCREEN_W, SCREEN_H

class StoryStage:
    """Represents a single story stage in a chapter."""
    
    def __init__(self, stage_id: str, name: str, description: str, 
                 waves: int, has_big_enemy: bool, path_points: List[tuple], 
                 has_true_boss: bool = False, difficulty: float = 1.0,
                 path_color: tuple = (80, 85, 100), bg_type: Optional[str] = None): # Default GRAY
        self.stage_id = stage_id  # e.g., "1-1", "1-2"
        self.name = name
        self.description = description
        self.waves = waves  # Total waves in this stage
        self.has_big_enemy = has_big_enemy  # BigEnemy appears after final wave
        self.has_true_boss = has_true_boss  # True Boss appears (overrides BigEnemy)
        self.path_points = path_points
        self.difficulty = difficulty
        self.path_color = path_color
        self.bg_type = bg_type
        
    def get_wave_description(self, wave_num: int) -> str:
        """Get description text for a specific wave."""
        return f"{self.stage_id} Wave {wave_num}"


class StoryProgress:
    """Tracks player progression through story mode."""
    
    def __init__(self):
        self.completed_stages: List[str] = []
        self.completed_chapters: List[str] = []
        self.current_stage: Optional[str] = None
        
    def is_stage_unlocked(self, stage_id: str, all_stages: List[StoryStage]) -> bool:
        """Check if a stage is unlocked based on progression. (UNLOCKED FOR TESTING)"""
        return True
    
    def complete_stage(self, stage_id: str):
        """Mark a stage as completed."""
        if stage_id not in self.completed_stages:
            self.completed_stages.append(stage_id)
    
    def complete_chapter(self, chapter_id: str):
        """Mark a chapter as completed."""
        if chapter_id not in self.completed_chapters:
            self.completed_chapters.append(chapter_id)
    
    def is_chapter_completed(self, chapter_id: str) -> bool:
        """Check if a chapter is completed."""
        return chapter_id in self.completed_chapters
    
    def unlock_all_chapters(self):
        """Unlock all chapters for testing/cheats."""
        for i in range(1, 6):
            cid = f"chapter{i}"
            if cid not in self.completed_chapters:
                self.completed_chapters.append(cid)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving."""
        return {
            'completed_stages': self.completed_stages,
            'completed_chapters': self.completed_chapters,
            'current_stage': self.current_stage
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StoryProgress':
        """Load from dictionary."""
        progress = StoryProgress()
        progress.completed_stages = data.get('completed_stages', [])
        progress.completed_chapters = data.get('completed_chapters', [])
        progress.current_stage = data.get('current_stage', None)
        return progress


class StoryChapter:
    """Represents a chapter containing multiple stages to be played continuously."""
    
    def __init__(self, chapter_id: str, name: str, stages: List[StoryStage], icon: Optional[str] = None):
        self.chapter_id = chapter_id
        self.name = name
        self.stages = stages
        self.icon = icon

class StoryManager:
    """Manages story mode chapters and stages."""
    
    def __init__(self, save_path: Optional[str] = None):
        self.save_path = save_path or os.path.join(BASE_DIR, "story_progress.json")
        self.progress = StoryProgress()
        self.chapters: Dict[str, StoryChapter] = {}
        
        # Initialize Chapters 1-5
        self._init_chapters()
        
    def _init_chapters(self):
        """Initialize all 5 chapters based on original maps 1-1 to 1-5."""
        
        # Original map data
        original_maps = [
            {
                "name": "Hell Gate",
                "path": [(1280, 100), (900, 100), (900, 350), (620, 350), (620, 620), (1280, 620)],
                "color": (0, 0, 0), "bg": "hell", "desc": "The entrance to the infernal realm."
            },
            {
                "name": "Burning Path",
                "path": [(0, 100), (630, 100), (630, 350), (450, 350), (450, 450), (630, 450), (630, 550), (450, 550),  (450, 650), (1280, 650)],
                "color": (255, 0, 0), "bg": "burning_path", "desc": "Cross the lava rivers."
            },
            {
                "name": "Demon Fortress",
                "path": [(1290, 80), (770, 80), (770, 500), (350, 500), (350, 320), (50, 320), (50, 650), (650, 650), (650, 800)],
                "color": (255, 128, 0), "bg": "demon_fortress", "desc": "Built by the damned."
            },
            {
                "name": "Chamber of Torment",
                "path": [(1280, 350), (900, 350), (900, 180), (630, 180), (630, 620), (1280, 620)],
                "color": (139, 69, 19), "bg": "torture_chamber", "desc": "The air itself burns."
            },
            {
                "name": "Hell Lord's Throne",
                "path": [(1280, 400), (1030, 400), (1030, 110), (830, 110), (830, 270), (630, 270), (630, 110), (430, 110), (430, 630), (1280, 630)],
                "color": (218, 179, 0), "bg": "hell_lord", "desc": "Face the ultimate test!"
            }
        ]

        # Chapter Names (optional display names)
        chapter_names = ["Hell Gate", "Burning Path", "Demon Fortress", "Chamber of Torment", "Hell Lord's Throne"]

        for i in range(5):
            ch_num = i + 1
            map_data = original_maps[i]
            stages = []
            
            # Create 5 sub-stages for each chapter, all using the same map
            for s_num in range(1, 6):
                stage_id = f"{ch_num}-{s_num}"
                is_last = (s_num == 5)
                # Final sub-stage of EVERY chapter has True Boss
                true_boss = is_last
                
                bg_type = map_data["bg"]

                stages.append(StoryStage(
                    stage_id=stage_id,
                    name=map_data["name"],
                    description=map_data["desc"],
                    waves=5,
                    has_big_enemy=True,
                    path_points=map_data["path"],
                    has_true_boss=true_boss,
                    difficulty=1.0 + i * 0.5 + s_num * 0.1,
                    path_color=map_data["color"],
                    bg_type=bg_type
                ))
            
            self.chapters[f"chapter{ch_num}"] = StoryChapter(
                f"chapter{ch_num}", 
                f"Chapter {ch_num}: {chapter_names[i]}", 
                stages
            )

    def get_chapters(self) -> List[StoryChapter]:
        """Get all available chapters."""
        return [self.chapters[f"chapter{i}"] for i in range(1, 6)]
    
    def get_chapter(self, chapter_id: str) -> Optional[StoryChapter]:
        return self.chapters.get(chapter_id)

    def get_chapter_stages(self, chapter_id: str) -> List[StoryStage]:
        """Get all stages for a chapter."""
        ch = self.chapters.get(chapter_id)
        return ch.stages if ch else []
    
    def get_stage(self, stage_id: str) -> Optional[StoryStage]:
        """Get a specific stage by ID."""
        for chapter in self.chapters.values():
            for stage in chapter.stages:
                if stage.stage_id == stage_id:
                    return stage
        return None
    
    def is_stage_unlocked(self, stage_id: str) -> bool:
        """Check if a stage is unlocked."""
        # For testing, all stages unlocked
        return True
    
    def complete_stage(self, stage_id: str):
        """Mark a stage as completed (session-based)."""
        self.progress.complete_stage(stage_id)
        self.save_progress()
    
    def complete_chapter(self, chapter_id: str):
        """Mark a chapter as completed."""
        self.progress.complete_chapter(chapter_id)
        self.save_progress()
    
    def is_chapter_completed(self, chapter_id: str) -> bool:
        """Check if a chapter is completed."""
        return self.progress.is_chapter_completed(chapter_id)
    
    def unlock_all_chapters(self):
        """Unlock all chapters."""
        self.progress.unlock_all_chapters()
        self.save_progress()
    
    def is_chapter_unlocked(self, chapter_id: str) -> bool:
        """Check if a chapter is unlocked."""
        if chapter_id == "chapter1":
            return True
        
        # Extract number
        try:
            num = int(chapter_id.replace("chapter", ""))
            prev_chapter = f"chapter{num-1}"
            return self.progress.is_chapter_completed(prev_chapter)
        except ValueError:
            return False
    
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
