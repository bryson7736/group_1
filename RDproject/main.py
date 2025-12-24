# -*- coding: utf-8 -*-
import pygame
import sys
import random
import math
from typing import List, Tuple, Optional, Dict, Any

from settings import *
from ui import Button, draw_panel, Segmented
from grid import Grid
from level_manager import LevelManager
from loadout import Loadout
from upgrades import UpgradeState
from enemy import Enemy, BigEnemy, TrueBoss
from dice import DIE_TYPES, make_die
from colors import WHITE, DARKER, GRAY, RED, DARK
from story_mode import StoryManager
from ingame_upgrades import InGameUpgrades
from effects import TelegraphZone
from colors import DICE_COLORS


STATE_LOBBY = "lobby"
STATE_PLAY = "play"
STATE_GAMEOVER = "gameover"
STATE_HELP = "help"
STATE_LOADOUT = "loadout"
STATE_UPGRADES = "upgrades"
STATE_STORY_SELECT = "story_select"
STATE_STORY = "story"


class Game:
    """
    Main Game class handling the game loop, state transitions, and rendering.
    """

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22)
        self.font_small = pygame.font.SysFont("arial", 16)
        self.font_big = pygame.font.SysFont("arial", 28, bold=True)
        self.font_huge = pygame.font.SysFont("arial", 48, bold=True)

        self.state: str = STATE_LOBBY
        self.level_mgr = LevelManager()
        self.level: Any = None  # Level object
        self.story_mgr = StoryManager()
        self.current_story_stage: Any = None  # StoryStage object
        self.story_max_waves: int = 0  # Max waves for current story stage

        self.grid = Grid(self)
        self.loadout = Loadout(["single", "iron", "fire", "multi", "freeze"])
        self.upgrades = UpgradeState()
        self.ingame_upgrades = InGameUpgrades()  # In-game upgrades
        self.enemies: List[Enemy] = []
        self.bullets: List[Any] = []  # Projectile objects
        self.telegraphs: List[TelegraphZone] = []
        self.money: int = START_MONEY
        self.base_hp: int = BASE_HP
        self.wave: int = -1
        self.to_spawn: int = 0
        self.spawn_cd: float = 0.0
        self.spawn_interval: float = 0.9
        self.is_big_enemy_wave: bool = False
        self.is_true_boss_wave: bool = False
        
        # Auto-wave system
        self.wave_timer: float = 0.0
        self.wave_delay: float = 5.0  # seconds until next wave

        self.speed_index: int = DEFAULT_SPEED_INDEX
        self.speed_mult: float = GAME_SPEEDS[self.speed_index]
        self.target_mode: str = "nearest"  # nearest / first / weak / strong
        self.trash_active: bool = False

        self.speed_ctrl = Segmented(
            (SCREEN_W - 420, 24, 360, 40),
            ["0.5×", "1×", "2×", "4×", "8×"],
            self.font_big,
            self.speed_index,
            self.on_speed_change
        )
        self.btn_trash = Button(
            (SCREEN_W - 820, 24, 120, 40),
            "Trash",
            self.font_big,
            self.toggle_trash
        )

        self._build_lobby()

    # --------------- Lobby ---------------
    def _build_lobby(self) -> None:
        """Initialize lobby UI elements."""
        self.buttons: List[Button] = []
        
        # Center layout configuration
        btn_w, btn_h = 340, 60
        gap = 20
        start_y = 200
        center_x = SCREEN_W // 2 - btn_w // 2

        # Practice Mode Section (endless waves)
        for i, lvl in enumerate(self.level_mgr.levels):
            self.buttons.append(
                Button(
                    (center_x, start_y + i * (btn_h + gap), btn_w, btn_h),
                    f"Practice: {lvl.name}",
                    self.font_big,
                    lambda i=i: self.start_level(i)
                )
            )
        
        # Story Mode Button
        y_offset = start_y + len(self.level_mgr.levels) * (btn_h + gap) + 20
        self.buttons.append(
            Button((center_x, y_offset, btn_w, btn_h), "Story Mode: Hell", self.font_big, self.goto_story_select)
        )
        
        # Secondary Actions
        y_offset += (btn_h + gap)
        
        self.buttons.append(
            Button((center_x, y_offset, btn_w, btn_h), "Carry Team", self.font_big, self.goto_loadout)
        )
        self.buttons.append(
            Button((center_x, y_offset + (btn_h + gap), btn_w, btn_h), "Upgrades", self.font_big, self.goto_upgrades)
        )
        
        # Bottom Actions
        bottom_y = SCREEN_H - 100
        self.buttons.append(
            Button((center_x - 180, bottom_y, 170, 60), "Help", self.font_big, self.goto_help)
        )
        self.quit_btn = Button((center_x + 180 + btn_w - 170, bottom_y, 170, 60), "Quit", self.font_big, self.quit)
        # Adjust quit button position logic if needed, but let's keep it simple for now:
        # Actually, let's put Help and Quit side-by-side below Upgrades
        
        # Re-calculating for side-by-side
        row_y = y_offset + 2 * (btn_h + gap) + 20
        self.buttons.pop() # Remove Help from previous append
        self.buttons.append(
            Button((center_x, row_y, btn_w // 2 - 10, btn_h), "Help", self.font_big, self.goto_help)
        )
        self.quit_btn = Button((center_x + btn_w // 2 + 10, row_y, btn_w // 2 - 10, btn_h), "Quit", self.font_big, self.quit)


    def start_level(self, idx: int) -> None:
        """Start a specific level."""
        self.level = self.level_mgr.get(idx)
        self.reset_runtime()
        self.state = STATE_PLAY

    def goto_help(self) -> None:
        """Switch to help screen."""
        self.state = STATE_HELP
        self.help_back = Button(
            (24, SCREEN_H - 94, 260, 64), "Back to Lobby", self.font_big, self.back_to_lobby
        )

    def goto_loadout(self) -> None:
        """Switch to loadout screen."""
        self.state = STATE_LOADOUT
        self.loadout_back = Button(
            (24, SCREEN_H - 94, 260, 64), "Back", self.font_big, self.back_to_lobby
        )

    def goto_upgrades(self) -> None:
        """Switch to upgrades screen."""
        self.state = STATE_UPGRADES
        self.upg_back = Button(
            (24, SCREEN_H - 94, 260, 64), "Back", self.font_big, self.back_to_lobby
        )
    
    def goto_story_select(self) -> None:
        """Switch to story stage selection screen."""
        self.state = STATE_STORY_SELECT
        self.story_back = Button(
            (24, SCREEN_H - 94, 260, 64), "Back", self.font_big, self.back_to_lobby
        )
    
    def start_story_stage(self, stage_id: str) -> None:
        """Start a specific story stage."""
        stage = self.story_mgr.get_stage(stage_id)
        if stage:
            self.current_story_stage = stage
            self.story_max_waves = stage.waves
            # Use stage's path as the level path
            from level_manager import Level
            self.level = Level(stage.name, stage.path_points, stage.difficulty)
            self.reset_runtime()
            self.state = STATE_STORY

    def back_to_lobby(self) -> None:
        """Return to lobby screen."""
        self.state = STATE_LOBBY
        self._build_lobby()

    def reset_runtime(self) -> None:
        """Reset game state for a new run."""
        self.grid = Grid(self)
        self.enemies = []
        self.bullets = []
        self.telegraphs = []
        self.money = START_MONEY
        self.base_hp = BASE_HP
        self.wave = -1
        self.to_spawn = 0
        self.spawn_cd = 0.0
        self.is_big_enemy_wave = False
        self.is_true_boss_wave = False
        self.trash_active = False
        self.ingame_upgrades.reset()  # Reset in-game upgrades

    # --------------- Events ---------------
    def on_speed_change(self, idx: int) -> None:
        """Handle game speed change."""
        self.speed_index = idx
        self.speed_mult = GAME_SPEEDS[idx]

    def toggle_trash(self) -> None:
        """Toggle trash mode for deleting dice."""
        self.trash_active = not self.trash_active
    
    def purchase_ingame_upgrade(self, upgrade_type: str) -> None:
        """Purchase an in-game upgrade with money."""
        success, new_money, message = self.ingame_upgrades.purchase_upgrade(upgrade_type, self.money)
        if success:
            self.money = new_money
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")

    def handle_play(self, event: pygame.event.Event) -> None:
        """Handle events during gameplay."""
        if event.type == pygame.KEYDOWN:
            if event.unicode in ('1', '2', '3', '4', '5'):
                idx = int(event.unicode) - 1
                self.on_speed_change(idx)
                return
            elif event.key == pygame.K_t:
                order = ["nearest", "first", "weak", "strong"]
                i = order.index(self.target_mode)
                self.target_mode = order[(i + 1) % len(order)]
            elif event.key == pygame.K_r:
                self.reset_runtime()
                self.state = STATE_PLAY
            elif event.key == pygame.K_ESCAPE:
                self.back_to_lobby()
            elif event.key == pygame.K_n:
                if self.to_spawn <= 0 and len(self.enemies) == 0:
                    self.start_wave()
            elif event.key == pygame.K_SPACE:
                # Random spawn
                if self.money >= DIE_COST:
                    empties = self.grid.get_empty_cells()
                    if empties:
                        c, r = random.choice(empties)
                        pool = self.loadout.selected or DIE_TYPES
                        t = random.choice(pool)
                        die = make_die(self, c, r, t, level=1)
                        self.grid.set(c, r, die)
                        self.money -= DIE_COST
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.grid.selected = None
            self.trash_active = False
            return
        self.speed_ctrl.handle(event)
        self.btn_trash.handle(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check for upgrade button clicks
            if event.button == 1:  # Left click
                mx, my = event.pos
                # New Grid Layout Logic
                btn_size = 60
                gap = 10
                panel_x = 20
                panel_y = SCREEN_H - (btn_size * 2 + gap + 20)
                
                dice_types = self.loadout.selected
                
                # Check if click is generally in the panel area
                if panel_x <= mx <= panel_x + (btn_size + gap) * 3 and \
                   panel_y <= my <= panel_y + (btn_size + gap) * 2:
                    
                    col = (mx - panel_x) // (btn_size + gap)
                    row = (my - panel_y) // (btn_size + gap)
                    
                    # Check if click is inside the button (not in gap)
                    rel_x = (mx - panel_x) % (btn_size + gap)
                    rel_y = (my - panel_y) % (btn_size + gap)
                    
                    if rel_x < btn_size and rel_y < btn_size:
                        idx = row * 3 + col
                        if 0 <= idx < len(dice_types):
                            self.purchase_ingame_upgrade(dice_types[idx])
                            return
            
            self.grid.handle_click(event)

    def gameover_handle(self, event: pygame.event.Event) -> None:
        """Handle events during game over screen."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_runtime()
                self.state = STATE_PLAY
            elif event.key == pygame.K_ESCAPE:
                self.back_to_lobby()

    def help_handle(self, event: pygame.event.Event) -> None:
        """Handle events during help screen."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.back_to_lobby()
        self.help_back.handle(event)

    def loadout_handle(self, event: pygame.event.Event) -> None:
        """Handle events during loadout screen."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.back_to_lobby()
        self.loadout_back.handle(event)
        # click on chips
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            bx, by, w, h, gap = 420, 200, 220, 60, 16
            for i, t in enumerate(DIE_TYPES):
                r = pygame.Rect(bx, by + i * (h + gap), w, h)
                if r.collidepoint(mx, my):
                    self.loadout.toggle(t)

    def upgrades_handle(self, event: pygame.event.Event) -> None:
        """Handle events during upgrades screen."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.back_to_lobby()
        self.upg_back.handle(event)
        # simple buttons per type & stat
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            base_x, base_y = 420, 200
            btn_w, btn_h = 220, 50
            gap_x, gap_y = 30, 16
            types = DIE_TYPES
            labels = [("Damage +10%", "dmg"), ("Fire rate +8%", "fire"), ("Cost -10%", "cost")]
            for row, t in enumerate(types):
                for col, (lab, kind) in enumerate(labels):
                    r = pygame.Rect(base_x + col * (btn_w + gap_x), base_y + row * (btn_h + gap_y), btn_w, btn_h)
                    if r.collidepoint(mx, my):
                        if kind == "dmg":
                            self.upgrades.upgrade_damage(t)
                        elif kind == "fire":
                            self.upgrades.upgrade_fire(t)
                        else:
                            self.upgrades.upgrade_cost(t)
    
    def story_select_handle(self, event: pygame.event.Event) -> None:
        """Handle events during story stage selection screen."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.back_to_lobby()
        self.story_back.handle(event)
        
        # Click on stage buttons
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            btn_w, btn_h = 320, 70
            gap = 16
            start_x, start_y = 420, 180
            
            hell_stages = self.story_mgr.get_chapter_stages("hell")
            for i, stage in enumerate(hell_stages):
                r = pygame.Rect(start_x, start_y + i * (btn_h + gap), btn_w, btn_h)
                if r.collidepoint(mx, my):
                    # Check if unlocked
                    if self.story_mgr.is_stage_unlocked(stage.stage_id):
                        self.start_story_stage(stage.stage_id)
                    break
    
    def story_handle(self, event: pygame.event.Event) -> None:
        """Handle events during story mode gameplay."""
        # Similar to play mode but with story-specific logic
        if event.type == pygame.KEYDOWN:
            if event.unicode in ('1', '2', '3', '4', '5'):
                idx = int(event.unicode) - 1
                self.on_speed_change(idx)
                return
            elif event.key == pygame.K_t:
                order = ["nearest", "first", "weak", "strong"]
                i = order.index(self.target_mode)
                self.target_mode = order[(i + 1) % len(order)]
            elif event.key == pygame.K_r:
                # Restart current story stage
                if self.current_story_stage:
                    self.start_story_stage(self.current_story_stage.stage_id)
            elif event.key == pygame.K_ESCAPE:
                self.goto_story_select()
            elif event.key == pygame.K_SPACE:
                # Random spawn
                if self.money >= DIE_COST:
                    empties = self.grid.get_empty_cells()
                    if empties:
                        c, r = random.choice(empties)
                        pool = self.loadout.selected or DIE_TYPES
                        t = random.choice(pool)
                        die = make_die(self, c, r, t, level=1)
                        self.grid.set(c, r, die)
                        self.money -= DIE_COST
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.grid.selected = None
            self.trash_active = False
            return
        self.speed_ctrl.handle(event)
        self.btn_trash.handle(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check for upgrade button clicks
            if event.button == 1:  # Left click
                mx, my = event.pos
                # New Grid Layout Logic
                btn_size = 60
                gap = 10
                panel_x = 20
                panel_y = SCREEN_H - (btn_size * 2 + gap + 20)
                
                dice_types = self.loadout.selected
                
                # Check if click is generally in the panel area
                if panel_x <= mx <= panel_x + (btn_size + gap) * 3 and \
                   panel_y <= my <= panel_y + (btn_size + gap) * 2:
                    
                    col = (mx - panel_x) // (btn_size + gap)
                    row = (my - panel_y) // (btn_size + gap)
                    
                    # Check if click is inside the button (not in gap)
                    rel_x = (mx - panel_x) % (btn_size + gap)
                    rel_y = (my - panel_y) % (btn_size + gap)
                    
                    if rel_x < btn_size and rel_y < btn_size:
                        idx = row * 3 + col
                        if 0 <= idx < len(dice_types):
                            self.purchase_ingame_upgrade(dice_types[idx])
                            return
            
            self.grid.handle_click(event)

    # --------------- Flow ---------------
    def start_wave(self) -> None:
        """Start the next wave of enemies."""
        self.telegraphs = []
        self.wave += 1
        self.wave_timer = 0.0  # Reset timer
        
        # Story Mode: Use story-specific wave configuration
        if self.state == STATE_STORY and self.current_story_stage:
            # Simple scaling for story mode: base count + wave number
            count = 10 + self.wave * 3  # Increased difficulty
        else:
            # Practice Mode: Use level manager's wave info
            count, is_boss = self.level_mgr.wave_info(self.wave)
            count = int(count * self.level.difficulty)
        
        self.to_spawn = count
        self.spawn_cd = 0.0
        # is_big_enemy_wave and is_true_boss_wave are already set by the auto-wave logic

    def spawn_enemy(self) -> None:
        """Spawn a single enemy."""
        # Polynomial HP scaling: Base * (Wave^1.3) * Difficulty
        # Using Base=30 as recommended for balanced difficulty
        wave_num = max(1, self.wave + 1)
        hp = 30 * (wave_num ** 1.3) * self.level.difficulty
        speed = (36 + min(140, self.wave * 6)) * (0.9 + 0.2 * random.random())
        path = list(self.level.path)
        if self.is_true_boss_wave and self.to_spawn == 1:
            hp *= BIG_ENEMY_HP_MULT * 2.0 # TrueBoss has more HP
            e = TrueBoss(path, hp, speed * 0.7, game=self)
        elif self.is_big_enemy_wave and self.to_spawn == 1:
            hp *= BIG_ENEMY_HP_MULT
            e = BigEnemy(path, hp, speed * 0.85)
        else:
            e = Enemy(path, hp, speed)
        if self.to_spawn == 1:
            e.carries_coin = True
        if len(path) == 2:
            e.y += random.randint(-60, 60)
        self.enemies.append(e)

    def spawn_telegraph(self, px: float, py: float) -> None:
        """Spawn a telegraph zone for big enemy attacks."""
        rpx = CELL_SIZE * (BIG_ENEMY_DESTROY_RADIUS + 0.5)
        z = TelegraphZone(
            px, py, rpx, BIG_ENEMY_TELEGRAPH_WARN, BIG_ENEMY_DEBUFF_DURATION,
            enemy_speed_mult=BIG_ENEMY_ZONE_SLOW_ENEMY, dice_period_mult=BIG_ENEMY_ZONE_SLOW_DICE
        )
        self.telegraphs.append(z)

    # --------------- Update ---------------
    def update(self, dt: float) -> None:
        """Update game logic."""
        if self.state not in (STATE_PLAY, STATE_STORY):
            return

        if self.to_spawn > 0:
            self.spawn_cd += dt * self.speed_mult
            if self.spawn_cd >= self.spawn_interval:
                self.spawn_cd = 0.0
                self.to_spawn -= 1
                self.spawn_enemy()

        # telegraphs
        for z in list(self.telegraphs):
            z.update(dt * self.speed_mult)
            if not z.active():
                self.telegraphs.remove(z)

        # enemies
        for e in list(self.enemies):
            zone_mult = 1.0
            for z in self.telegraphs:
                if z.in_effect_phase() and z.contains(e.x, e.y):
                    zone_mult *= z.enemy_speed_mult
            e.update(dt, speed_mult=self.speed_mult, zone_mult=zone_mult)
            if isinstance(e, BigEnemy):
                if e.ability_cd >= BIG_ENEMY_TELEGRAPH_WARN + BIG_ENEMY_DEBUFF_DURATION + 5.0:
                    e.ability_cd = 0.0
                    e.try_ability(self)
            elif isinstance(e, TrueBoss):
                # Update game ref if needed, though passed in init
                pass

            if e.dead:
                self.money += int(e.money_drop + self.wave)
                if getattr(e, "carries_coin", False):
                    self.upgrades.add_coin(1)
                self.enemies.remove(e)
            elif e.reached:
                self.base_hp -= 1
                self.enemies.remove(e)

        # Auto-wave logic
        if self.to_spawn <= 0 and len(self.enemies) == 0:
            # Story Mode: Check for victory or next wave
            if self.state == STATE_STORY and self.current_story_stage:
                # Check if stage is complete
                if self.wave >= self.story_max_waves - 1:  # All waves including boss defeated
                    # Victory!
                    self.story_mgr.complete_stage(self.current_story_stage.stage_id)
                    # Go back to stage select
                    self.goto_story_select()
                    return
                elif self.wave >= self.story_max_waves - 2:  # This was the final regular wave
                    # If this stage has a big enemy or true boss, spawn it next
                    if self.current_story_stage.has_true_boss:
                        self.wave_timer += dt * self.speed_mult
                        if self.wave_timer >= self.wave_delay:
                            self.is_true_boss_wave = True
                            self.start_wave()
                    elif self.current_story_stage.has_big_enemy:
                        self.wave_timer += dt * self.speed_mult
                        if self.wave_timer >= self.wave_delay:
                            self.is_big_enemy_wave = True
                            self.start_wave()
                    else:
                        self.wave_timer += dt * self.speed_mult
                        if self.wave_timer >= self.wave_delay:
                            self.start_wave()
                else:
                    # Regular wave progression
                    self.wave_timer += dt * self.speed_mult
                    if self.wave_timer >= self.wave_delay:
                        self.start_wave()
            else:
                # Practice mode: endless waves
                self.wave_timer += dt * self.speed_mult
                if self.wave_timer >= self.wave_delay:
                    self.start_wave()

        # bullets
        for b in list(self.bullets):
            if b.update(dt):
                self.bullets.remove(b)

        # dice
        self.grid.update(dt)

        # end
        if self.base_hp <= 0:
            self.state = STATE_GAMEOVER

    # --------------- Draw ---------------
    def lobby_draw(self) -> None:
        """Draw the lobby screen."""
        self.screen.fill(DARK)
        
        # Title
        title = self.font_huge.render("RANDOM DICE DEFENSE", True, WHITE)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 100))
        for b in self.buttons:
            b.draw(self.screen)
        self.quit_btn.draw(self.screen)

    def play_draw(self) -> None:
        """Draw the gameplay screen."""
        self.screen.fill(DARK)
        if self.level:
            pygame.draw.lines(self.screen, GRAY, False, self.level.path, 6)

        self.grid.draw(self.screen)
        for e in self.enemies:
            e.draw(self.screen, self.font)
        for b in self.bullets:
            b.draw(self.screen)

        # telegraph swirl
        for z in self.telegraphs:
            color = (255, 60, 60) if not z.in_effect_phase() else (255, 120, 120)
            pygame.draw.circle(self.screen, color, (int(z.x), int(z.y)), int(z.r), width=4)
            for i in range(6):
                ang = (z.t * 3 + i * math.pi / 3)
                rx = int(z.x + (z.r - 10) * math.cos(ang))
                ry = int(z.y + (z.r - 10) * math.sin(ang))
                pygame.draw.circle(self.screen, color, (rx, ry), 6)

        panel_rect = pygame.Rect(20, 10, 370, 280)

        def _body() -> None:
            y = panel_rect.y + 60
            pairs = [
                ("Money", f"${self.money}"),
                ("Wave", str(max(0, self.wave))),
                ("Base HP", str(self.base_hp)),
                ("Speed", f"{self.speed_mult}×"),
                ("Target", {"nearest": "Nearest", "first": "Front", "weak": "Weak", "strong": "Strong"}[self.target_mode]),
                ("Coins", str(self.upgrades.coins)),
            ]
            for name, val in pairs:
                txt = self.font.render(f"{name}: {val}", True, WHITE)
                self.screen.blit(txt, (panel_rect.x + 20, y))
                y += 26

            y += 10
            tips = [
                "Hotkeys: 1~5 speed, T target, N next wave",
                "Right click cancels / exits Trash",
                "Press ESC for lobby",
            ]
            for s in tips:
                t = self.font.render(s, True, WHITE)
                self.screen.blit(t, (panel_rect.x + 20, y))
                y += 22

        draw_panel(self.screen, panel_rect, "Status", self.font_big, _body)

        self.speed_ctrl.draw(self.screen)
        self.btn_trash.draw(self.screen)

        if self.to_spawn <= 0 and len(self.enemies) == 0:
            time_left = max(0.0, self.wave_delay - self.wave_timer)
            msg = f"Next wave in {time_left:.1f}s (Press N to skip)"
            top = self.font_big.render(msg, True, WHITE)
            self.screen.blit(top, (GRID_X, 42))
        
        # Draw in-game upgrades
        self.draw_ingame_upgrades()
    
    def draw_ingame_upgrades(self) -> None:
        """Draw the in-game upgrade panel (2x3 grid)."""
        # Position: Bottom Left
        btn_size = 60
        gap = 10
        panel_x = 20
        panel_y = SCREEN_H - (btn_size * 2 + gap + 20)  # Align to bottom
        
        # Use current loadout dice
        dice_types = self.loadout.selected
        
        for i, die_type in enumerate(dice_types):
            col = i % 3
            row = i // 3
            x = panel_x + col * (btn_size + gap)
            y = panel_y + row * (btn_size + gap)
            rect = pygame.Rect(x, y, btn_size, btn_size)
            
            # Get upgrade info
            current_level = self.ingame_upgrades.get_level(die_type)
            can_upgrade = self.ingame_upgrades.can_upgrade(die_type)
            cost = self.ingame_upgrades.get_upgrade_cost(die_type)
            has_money = self.money >= cost
            
            # Button color (based on dice color)
            base_color = DICE_COLORS.get(die_type, GRAY)
            
            if current_level >= 5:
                # Maxed out: Darker version of base color
                btn_color = (max(0, base_color[0]-100), max(0, base_color[1]-100), max(0, base_color[2]-100))
                border_color = (100, 100, 100)
            elif has_money:
                # Available: Bright base color
                btn_color = base_color
                border_color = WHITE
            else:
                # Too expensive: Desaturated/Darker
                btn_color = (max(0, base_color[0]-60), max(0, base_color[1]-60), max(0, base_color[2]-60))
                border_color = (100, 100, 100)
            
            # Draw button
            pygame.draw.rect(self.screen, btn_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=8)
            
            # Draw Text
            # Level (Large, Center)
            lvl_txt = self.font_big.render(f"Lv{current_level}", True, WHITE)
            self.screen.blit(lvl_txt, (rect.centerx - lvl_txt.get_width()//2, rect.y + 5))
            
            # Cost (Small, Bottom)
            if current_level >= 5:
                cost_txt = self.font_small.render("MAX", True, WHITE)
            else:
                cost_color = WHITE if has_money else (255, 100, 100)
                cost_txt = self.font_small.render(f"${cost}", True, cost_color)
            self.screen.blit(cost_txt, (rect.centerx - cost_txt.get_width()//2, rect.bottom - 18))

    def gameover_draw(self) -> None:
        """Draw the game over screen."""
        self.screen.fill((15, 15, 25))
        t = self.font_huge.render("GAME OVER", True, RED)
        self.screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, SCREEN_H // 2 - 100))
        sub = self.font_big.render("R: Restart   ESC: Lobby", True, WHITE)
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 2))

    def help_draw(self) -> None:
        """Draw the help screen."""
        self.screen.fill((22, 24, 36))
        title = self.font_huge.render("Help", True, (255, 255, 255))
        self.screen.blit(title, (40, 60))
        lines = [
            "• Left click empty: place Lv1 die",
            "• Left click die: select / merge (same TYPE & LEVEL)",
            "• Right click: cancel selection / exit Trash",
            "• Speed: top-right control or 1~5 keys",
            "• Target mode: press T to cycle (Nearest / Front / Weak / Strong)",
            "• When field is clear press N to start next wave",
            "• R to restart; ESC for lobby",
        ]
        y = 140
        for s in lines:
            t = self.font.render(s, True, (230, 230, 240))
            self.screen.blit(t, (40, y))
            y += 30
        self.help_back.draw(self.screen)

    def loadout_draw(self) -> None:
        """Draw the loadout screen."""
        self.screen.fill(DARKER)
        title = self.font_huge.render("Carry Team", True, (255, 255, 255))
        self.screen.blit(title, (40, 60))
        sub = self.font.render("Pick up to 5 dice types for this run.", True, WHITE)
        self.screen.blit(sub, (40, 120))

        bx, by, w, h, gap = 420, 200, 220, 60, 16
        types = DIE_TYPES
        dice_brief = {
            "single": "Single: High base damage, fast fire.",
            "multi": "Multi: Hits multiple enemies in chain.",
            "freeze": "Freeze: Slows enemies on hit.",
            "wind": "Wind: Very rapid fire, low damage.",
            "poison": "Poison: Deals damage over time.",
            "iron": "Iron: Huge damage, bonus vs bosses.",
            "fire": "Fire: Splash damage to nearby enemies."
        }
        for i, t in enumerate(types):
            r = pygame.Rect(bx, by + i * (h + gap), w, h)
            active = (t in self.loadout.selected)
            self.loadout.draw_chip(self.screen, r, t, self.font_big, active)
            # Draw brief info to the right
            info_txt = dice_brief.get(t, "")
            info_surf = self.font.render(info_txt, True, (220, 220, 220))
            self.screen.blit(info_surf, (bx + w + 24, by + i * (h + gap) + h // 2 - info_surf.get_height() // 2))
        sel = ", ".join(self.loadout.selected) if self.loadout.selected else "(none)"
        info = self.font.render(f"Selected: {sel}", True, WHITE)
        # Move info to top right, above the chips
        info_x = bx + 10
        info_y = by - 60
        self.screen.blit(info, (info_x, info_y))

        self.loadout_back.draw(self.screen)

    def upgrades_draw(self) -> None:
        """Draw the upgrades screen."""
        self.screen.fill(DARKER)
        title = self.font_huge.render("Upgrades", True, (255, 255, 255))
        self.screen.blit(title, (40, 60))
        coins = self.font_big.render(f"Coins: {self.upgrades.coins}", True, WHITE)
        self.screen.blit(coins, (40, 120))
        base_x, base_y = 420, 200
        btn_w, btn_h = 220, 50
        gap_x, gap_y = 30, 16
        types = DIE_TYPES
        labels = [("Damage +10% (2c)", "dmg"), ("Fire rate +8% (2c)", "fire"), ("Cost -10% (2c)", "cost")]
        for row, t in enumerate(types):
            name = self.font_big.render(t.capitalize(), True, WHITE)
            self.screen.blit(name, (base_x - 150, base_y + row * (btn_h + gap_y) + 8))
            for col, (lab, kind) in enumerate(labels):
                r = pygame.Rect(base_x + col * (btn_w + gap_x), base_y + row * (btn_h + gap_y), btn_w, btn_h)
                Button(r, lab, self.font, lambda t=t, kind=kind: (
                    self.upgrades.upgrade_damage(t) if kind == "dmg" else
                    (self.upgrades.upgrade_fire(t) if kind == "fire" else self.upgrades.upgrade_cost(t))
                )).draw(self.screen)

        self.upg_back.draw(self.screen)
    
    def story_select_draw(self) -> None:
        """Draw the story stage selection screen."""
        self.screen.fill((12, 10, 22))  # Darker theme for hell
        
        # Title with fire theme
        title = self.font_huge.render("🔥 HELL CHAPTER 🔥", True, (255, 100, 50))
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 60))
        
        # Subtitle
        sub = self.font_big.render("Select a stage to begin", True, (200, 200, 200))
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 130))
        
        # Stage buttons
        btn_w, btn_h = 320, 70
        gap = 16
        start_x, start_y = 420, 180
        
        hell_stages = self.story_mgr.get_chapter_stages("hell")
        for i, stage in enumerate(hell_stages):
            r = pygame.Rect(start_x, start_y + i * (btn_h + gap), btn_w, btn_h)
            unlocked = self.story_mgr.is_stage_unlocked(stage.stage_id)
            completed = stage.stage_id in self.story_mgr.progress.completed_stages
            
            # Button color based on state
            if completed:
                color = (50, 150, 50)  # Green for completed
                text_color = WHITE
            elif unlocked:
                color = (200, 80, 40)  # Orange/red for unlocked
                text_color = WHITE
            else:
                color = (60, 60, 60)  # Gray for locked
                text_color = (120, 120, 120)
            
            pygame.draw.rect(self.screen, color, r, border_radius=8)
            pygame.draw.rect(self.screen, (255, 150, 100) if unlocked else (100, 100, 100), r, width=3, border_radius=8)
            
            # Stage text
            stage_text = f"{stage.stage_id} {stage.name}"
            if completed:
                stage_text += " ✓"
            elif not unlocked:
                stage_text = f"{stage.stage_id} 🔒 Locked"
            
            txt = self.font_big.render(stage_text, True, text_color)
            self.screen.blit(txt, (r.centerx - txt.get_width() // 2, r.centery - txt.get_height() // 2))
        
        self.story_back.draw(self.screen)
    
    def story_draw(self) -> None:
        """Draw the story mode gameplay screen."""
        # Reuse play_draw but with story-specific UI elements
        self.screen.fill(DARK)
        if self.level:
            pygame.draw.lines(self.screen, GRAY, False, self.level.path, 6)

        self.grid.draw(self.screen)
        for e in self.enemies:
            e.draw(self.screen, self.font)
        for b in self.bullets:
            b.draw(self.screen)

        # telegraph swirl
        for z in self.telegraphs:
            color = (255, 60, 60) if not z.in_effect_phase() else (255, 120, 120)
            pygame.draw.circle(self.screen, color, (int(z.x), int(z.y)), int(z.r), width=4)
            for i in range(6):
                ang = (z.t * 3 + i * math.pi / 3)
                rx = int(z.x + (z.r - 10) * math.cos(ang))
                ry = int(z.y + (z.r - 10) * math.sin(ang))
                pygame.draw.circle(self.screen, color, (rx, ry), 6)

        panel_rect = pygame.Rect(20, 10, 370, 320)

        def _body() -> None:
            y = panel_rect.y + 60
            
            # Story stage info
            if self.current_story_stage:
                stage_txt = self.font_big.render(f"Stage: {self.current_story_stage.stage_id}", True, (255, 150, 50))
                self.screen.blit(stage_txt, (panel_rect.x + 20, y))
                y += 32
                
                # Wave description
                wave_desc = self.current_story_stage.get_wave_description(max(0, self.wave + 1))
                desc_txt = self.font.render(wave_desc, True, WHITE)
                self.screen.blit(desc_txt, (panel_rect.x + 20, y))
                y += 28
            
            pairs = [
                ("Money", f"${self.money}"),
                ("Wave", f"{max(0, self.wave + 1)}/{self.story_max_waves}"),
                ("Base HP", str(self.base_hp)),
                ("Speed", f"{self.speed_mult}×"),
            ]
            for name, val in pairs:
                txt = self.font.render(f"{name}: {val}", True, WHITE)
                self.screen.blit(txt, (panel_rect.x + 20, y))
                y += 24

            y += 10
            tips = [
                "Story Mode: Complete all waves!",
                "ESC to return to stage select",
            ]
            for s in tips:
                t = self.font.render(s, True, WHITE)
                self.screen.blit(t, (panel_rect.x + 20, y))
                y += 20

        draw_panel(self.screen, panel_rect, "Mission", self.font_big, _body)

        self.speed_ctrl.draw(self.screen)
        self.btn_trash.draw(self.screen)

        if self.to_spawn <= 0 and len(self.enemies) == 0:
            time_left = max(0.0, self.wave_delay - self.wave_timer)
            if self.wave < self.story_max_waves - 1:
                msg = f"Next wave in {time_left:.1f}s"
            else:
                msg = "Victory! Returning to stage select..."
            top = self.font_big.render(msg, True, (255, 200, 100))
            self.screen.blit(top, (GRID_X, 42))
        
        # Draw in-game upgrades
        self.draw_ingame_upgrades()

    # --------------- Frame ---------------
    def draw(self) -> None:
        """Render the current frame."""
        if self.state == STATE_LOBBY:
            self.lobby_draw()
        elif self.state == STATE_PLAY:
            self.play_draw()
        elif self.state == STATE_GAMEOVER:
            self.gameover_draw()
        elif self.state == STATE_HELP:
            self.help_draw()
        elif self.state == STATE_LOADOUT:
            self.loadout_draw()
        elif self.state == STATE_UPGRADES:
            self.upgrades_draw()
        elif self.state == STATE_STORY_SELECT:
            self.story_select_draw()
        elif self.state == STATE_STORY:
            self.story_draw()
        pygame.display.flip()

    def run(self) -> None:
        """Main game loop."""
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # don't auto-quit on game over; here only explicit window close
                    self.quit()
                if self.state == STATE_LOBBY:
                    for b in self.buttons:
                        b.handle(event)
                    self.quit_btn.handle(event)
                elif self.state == STATE_PLAY:
                    self.handle_play(event)
                elif self.state == STATE_GAMEOVER:
                    self.gameover_handle(event)
                elif self.state == STATE_HELP:
                    self.help_handle(event)
                elif self.state == STATE_LOADOUT:
                    self.loadout_handle(event)
                elif self.state == STATE_UPGRADES:
                    self.upgrades_handle(event)
                elif self.state == STATE_STORY_SELECT:
                    self.story_select_handle(event)
                elif self.state == STATE_STORY:
                    self.story_handle(event)

            self.update(dt)
            self.draw()

    def quit(self) -> None:
        """Quit the game."""
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    Game().run()
