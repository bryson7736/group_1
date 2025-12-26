# -*- coding: utf-8 -*-
import pygame
from colors import WHITE, DICE_COLORS, DARK, ACCENT

class Loadout:
    """Holds selected dice types for a run (up to 5; default selects the first 3)."""
    def __init__(self, available_types, *, max_slots=5):
        self.available = list(available_types)
        self.max_slots = max_slots
        self.selected = list(self.available[:min(5, max_slots)])

    def toggle(self, t):
        if t in self.selected:
            self.selected.remove(t)
        else:
            if len(self.selected) < self.max_slots:
                self.selected.append(t)

    def draw_chip(self, surf, rect, t, font, active):
        from dice import get_die_image
        color = DICE_COLORS.get(t, (150,150,150))
        
        # 1. Draw Stylized Square Icon on the left side of the rect
        icon_size = rect.height
        icon_rect = pygame.Rect(rect.x, rect.y, icon_size, icon_size)
        
        # Background
        pygame.draw.rect(surf, color if active else (40, 40, 50), icon_rect, border_radius=10)
        
        # Glossy Highlight (Top half-ish)
        highlight = pygame.Surface((icon_size, icon_size // 2), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 30))
        surf.blit(highlight, (icon_rect.x, icon_rect.y))
        
        # Border
        border_col = WHITE if active else (100, 100, 110)
        pygame.draw.rect(surf, border_col, icon_rect, width=3, border_radius=10)
        
        # Icon
        img = get_die_image(t)
        if img:
            io = int(icon_size * 0.7)
            isurf = pygame.transform.smoothscale(img, (io, io))
            surf.blit(isurf, (icon_rect.centerx - io//2, icon_rect.centery - io//2))
            
        # 2. Draw Name Label to the right of the icon
        name_txt = font.render(t.capitalize(), True, WHITE if active else (180, 180, 190))
        surf.blit(name_txt, (icon_rect.right + 15, icon_rect.centery - name_txt.get_height() // 2))
