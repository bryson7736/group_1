# -*- coding: utf-8 -*-
import pygame, random
from colors import GRAY, ACCENT, BLUE
from settings import GRID_COLS, GRID_ROWS, CELL_SIZE, GRID_X, GRID_Y, DIE_COST, MERGE_REFUND, MAX_DIE_LEVEL
from dice import DIE_TYPES, make_die

class Grid:
    def __init__(self, game):
        self.game = game
        self.start_x = GRID_X
        self.start_y = GRID_Y
        
        # Check if in Story Mode
        if hasattr(self.game, 'state') and self.game.state == 'story':
            # Dynamic grid for story mode
            from settings import SCREEN_W, SCREEN_H
            self.cols = SCREEN_W // CELL_SIZE
            self.rows = SCREEN_H // CELL_SIZE
            self.start_x = 0
            self.start_y = 0
            
            # Calculate valid cells based on path
            self.valid_cells = set()
            self._calculate_valid_cells()
        else:
            # Default Practice Mode Grid
            self.cols = GRID_COLS
            self.rows = GRID_ROWS
            self.valid_cells = None  # None means all cells in bounds are valid

        self.cells = [[None for _ in range(self.rows)] for _ in range(self.cols)]
        self.selected = None  # (c, r)

    def _calculate_valid_cells(self):
        """Calculate valid grid cells that surround the path with a gap."""
        if not self.game.level or not self.game.level.path:
            return

        path = self.game.level.path
        # Reduced gap and tighten distribution as requested
        min_dist = CELL_SIZE * 0.45   # Closer to path (< half cell)
        max_dist = CELL_SIZE * 1.5    # Tighter spread
        
        # Mission Panel Rect (approximate based on main.py)
        # Avoid placement in top-left UI area + margin
        ui_rect = pygame.Rect(20, 10, 370, 280)

        for c in range(self.cols):
            for r in range(self.rows):
                # Calculate cell center
                cx = self.start_x + c * CELL_SIZE + CELL_SIZE // 2
                cy = self.start_y + r * CELL_SIZE + CELL_SIZE // 2
                
                # Check collision with UI
                cell_rect = self.rect_at(c, r)
                if cell_rect.colliderect(ui_rect):
                    continue
                
                # Check distance to path segments
                min_dist_to_path = float('inf')
                for i in range(len(path) - 1):
                    p1 = path[i]
                    p2 = path[i+1]
                    d = self._point_segment_msg_dist(cx, cy, p1, p2)
                    if d < min_dist_to_path:
                        min_dist_to_path = d
                
                if min_dist < min_dist_to_path < max_dist:
                    self.valid_cells.add((c, r))

    def _point_segment_msg_dist(self, px, py, p1, p2):
        """Distance from point (px, py) to segment p1-p2."""
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return ((px - x1)**2 + (py - y1)**2)**0.5

        t = ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))
        
        nx = x1 + t * dx
        ny = y1 + t * dy
        return ((px - nx)**2 + (py - ny)**2)**0.5

    def in_bounds(self, c, r):
        in_grid = 0 <= c < self.cols and 0 <= r < self.rows
        if not in_grid:
            return False
        if self.valid_cells is not None:
            return (c, r) in self.valid_cells
        return True

    def rect_at(self, c, r):
        x = self.start_x + c * CELL_SIZE
        y = self.start_y + r * CELL_SIZE
        return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    def center_of(self, c, r):
        rct = self.rect_at(c, r)
        return rct.centerx, rct.centery

    def get(self, c, r):
        if not self.in_bounds(c, r):
            return None
        return self.cells[c][r]

    def set(self, c, r, obj):
        if self.in_bounds(c, r):
            self.cells[c][r] = obj

    def remove(self, c, r):
        self.set(c, r, None)

    def iterate(self):
        for c in range(self.cols):
            for r in range(self.rows):
                if self.in_bounds(c, r):
                    yield c, r, self.cells[c][r]

    def get_empty_cells(self):
        empty = []
        for c in range(self.cols):
            for r in range(self.rows):
                if self.in_bounds(c, r) and self.cells[c][r] is None:
                    empty.append((c, r))
        return empty

    def update(self, dt):
        for c, r, d in self.iterate():
            if d:
                d.update(dt)

    def draw(self, surf):
        mx, my = pygame.mouse.get_pos()
        hover_cell = None
        
        # Check hover
        for c in range(self.cols):
            for r in range(self.rows):
                if not self.in_bounds(c, r):
                    continue
                rect = self.rect_at(c, r)
                if rect.collidepoint(mx, my):
                    hover_cell = (c, r)

        for c in range(self.cols):
            for r in range(self.rows):
                if not self.in_bounds(c, r):
                    continue
                    
                rect = self.rect_at(c, r)
                # Darker, more subtle grid borders
                pygame.draw.rect(surf, (40, 45, 60), rect, width=2, border_radius=10)
                die = self.get(c, r)
                if die:
                    # Only draw as selected if actually selected, not just hovered
                    selected = (self.selected == (c, r))
                    die.draw(surf, selected)
                    
        # Draw hover effect (blue border only, like selection)
        if hover_cell and hover_cell != self.selected:
            pygame.draw.rect(surf, BLUE, self.rect_at(*hover_cell).inflate(-12, -12), width=3, border_radius=14)

    def handle_click(self, event):
        if event.button != 1:
            return
        mx, my = event.pos
        
        # Determine clicked cell
        c = (mx - self.start_x) // CELL_SIZE
        r = (my - self.start_y) // CELL_SIZE
        
        if not self.in_bounds(c, r):
            return

        clicked = self.get(c, r)

        if self.game.trash_active:
            if clicked is not None:
                self.set(c, r, None)
            self.game.trash_active = False
            self.selected = None
            return

        if clicked is None:
            # Left-click spawn disabled. Use Spacebar.
            pass
        else:
            sel = self.selected
            if sel is None:
                self.selected = (c, r)
            else:
                sc, sr = sel
                if (c, r) == (sc, sr):
                    self.selected = None
                else:
                    a = self.get(sc, sr)
                    b = clicked
                    if a and b and a.can_merge_with(b):
                        new_lv = min(a.level + 1, MAX_DIE_LEVEL)
                        ttype = a.type
                        self.set(c, r, make_die(self.game, c, r, ttype, new_lv))
                        self.set(sc, sr, None)
                        self.game.money += MERGE_REFUND
                        self.selected = None
                    else:
                        self.selected = None
