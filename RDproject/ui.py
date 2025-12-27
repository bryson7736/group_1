# -*- coding: utf-8 -*-
import pygame
from colors import WHITE, DARK, DARKER, GRAY, ACCENT, SLATE
from settings import SCREEN_W, SCREEN_H

class Button:
    """Basic button with hover and on-click callback."""
    def __init__(self, rect, text, font, on_click, *, bg=DARK, fg=WHITE, hover=None, radius=12, icon=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.on_click = on_click
        self.bg = bg
        self.fg = fg
        self.hover = hover or ACCENT
        self.radius = radius
        self.icon = icon
        self._hovering = False

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._hovering = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()
                return True
        return False

    def draw(self, surf):
        color = self.hover if self._hovering else self.bg
        # Glow effect on hover
        if self._hovering:
            pygame.draw.rect(surf, (color[0], color[1], color[2], 100), self.rect.inflate(4, 4), border_radius=self.radius)
        
        pygame.draw.rect(surf, color, self.rect, border_radius=self.radius)
        # Subtle border
        pygame.draw.rect(surf, (255, 255, 255), self.rect, width=1, border_radius=self.radius)

        if self.icon:
            ir = self.icon.get_rect(center=self.rect.center)
            surf.blit(self.icon, ir)
        if self.text:
            txt = self.font.render(self.text, True, self.fg)
            surf.blit(txt, (self.rect.centerx - txt.get_width() // 2,
                            self.rect.centery - txt.get_height() // 2))


class Segmented:
    """Segmented control (used for game speed)."""
    def __init__(self, rect, labels, font, index, on_change):
        self.rect = pygame.Rect(rect)
        self.labels = labels
        self.font = font
        self.index = index
        self.on_change = on_change

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                w = self.rect.w // len(self.labels)
                off = (event.pos[0] - self.rect.x) // w
                self.index = int(max(0, min(len(self.labels) - 1, off)))
                self.on_change(self.index)

    def draw(self, surf):
        n = len(self.labels)
        w = self.rect.w // n
        # Background container
        pygame.draw.rect(surf, DARKER, self.rect, border_radius=12)
        pygame.draw.rect(surf, GRAY, self.rect, width=1, border_radius=12)

        for i, lab in enumerate(self.labels):
            r = pygame.Rect(self.rect.x + i * w, self.rect.y, w, self.rect.h)
            active = (i == self.index)
            if active:
                pygame.draw.rect(surf, ACCENT, r.inflate(-4, -4), border_radius=8)
            
            t = self.font.render(lab, True, WHITE if active else SLATE)
            surf.blit(t, (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))


def draw_panel(surf, rect, title, title_font, body_fn=None):
    import pygame
    from colors import WHITE, DARKER, PANEL_GRAD_TOP, PANEL_GRAD_BOTTOM

    # gradient background
    panel = pygame.Surface((rect.w, rect.h))
    # Simple vertical gradient
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        r = int(PANEL_GRAD_TOP[0] * (1 - t) + PANEL_GRAD_BOTTOM[0] * t)
        g = int(PANEL_GRAD_TOP[1] * (1 - t) + PANEL_GRAD_BOTTOM[1] * t)
        b = int(PANEL_GRAD_TOP[2] * (1 - t) + PANEL_GRAD_BOTTOM[2] * t)
        pygame.draw.line(panel, (r, g, b), (0, y), (rect.w, y))
    
    panel.set_alpha(240) # Slight transparency
    panel = panel.convert()
    surf.blit(panel, rect.topleft)

    # frame
    pygame.draw.rect(surf, (60, 60, 80), rect, width=2, border_radius=18)

    if title:
        title_surf = title_font.render(title, True, WHITE)
        surf.blit(title_surf, (rect.x + 20, rect.y + 14))
    if body_fn:
        body_fn()
def draw_pips(surf, rect, level, color=WHITE):
    """Draw dots (pips) for levels 1-6, and a star for level 7."""
    import pygame
    if level >= 7:
        # Star for level 7+
        # Use a large font for the star
        font_size = int(rect.height * 0.6)
        try:
            star_font = pygame.font.SysFont(["segoe uiemoji", "segoe ui symbol", "arial"], font_size, bold=True)
        except:
            star_font = pygame.font.SysFont("arial", font_size, bold=True)
            
        star = star_font.render("★", True, color)
        surf.blit(star, (rect.centerx - star.get_width()//2, rect.centery - star.get_height()//2))
        return

    pip_radius = max(3, int(rect.width / 12))
    gap = rect.width // 4
    patterns = {
        1: [(0, 0)],
        2: [(-gap, -gap), (gap, gap)],
        3: [(-gap, -gap), (0, 0), (gap, gap)],
        4: [(-gap, -gap), (gap, -gap), (-gap, gap), (gap, gap)],
        5: [(-gap, -gap), (gap, -gap), (0, 0), (-gap, gap), (gap, gap)],
        6: [(-gap, -gap), (-gap, 0), (gap, 0), (-gap, gap), (0, gap), (gap, gap)],
    }
    
    for dx, dy in patterns.get(level, []):
        pygame.draw.circle(surf, color, (rect.centerx + dx, rect.centery + dy), pip_radius)

class PauseMenu:
    def __init__(self, font_big, font):
        self.font_big = font_big
        self.font = font
        
        # Popup dimensions
        self.w, self.h = 300, 280
        self.x = (SCREEN_W - self.w) // 2
        self.y = (SCREEN_H - self.h) // 2
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        
        # Buttons
        self.btn_w, self.btn_h = 160, 40
        self.gap = 15
        self.start_y = self.rect.y + 80
        
        cx = self.rect.centerx
        
        # Continue
        self.r_cont = pygame.Rect(0, 0, self.btn_w, self.btn_h)
        self.r_cont.center = (cx, self.rect.top + 100)
        
        # Restart
        self.r_rest = pygame.Rect(0, 0, self.btn_w, self.btn_h)
        self.r_rest.center = (cx, self.rect.top + 155)
        
        # Quit
        self.r_quit = pygame.Rect(0, 0, self.btn_w, self.btn_h)
        self.r_quit.center = (cx, self.rect.top + 210)

    def draw(self, screen):
        # Draw background
        pygame.draw.rect(screen, (40, 40, 50), self.rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, self.rect, width=2, border_radius=12)
        
        # Title
        title = self.font_big.render("Paused", True, WHITE)
        screen.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 30))
        
        # Continue
        pygame.draw.rect(screen, (100, 200, 100), self.r_cont, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.r_cont, width=2, border_radius=8)
        t_cont = self.font.render("Continue", True, WHITE)
        screen.blit(t_cont, (self.r_cont.centerx - t_cont.get_width()//2, self.r_cont.centery - t_cont.get_height()//2))
        
        # Restart
        pygame.draw.rect(screen, (200, 150, 50), self.r_rest, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.r_rest, width=2, border_radius=8)
        t_rest = self.font.render("Restart", True, WHITE)
        screen.blit(t_rest, (self.r_rest.centerx - t_rest.get_width()//2, self.r_rest.centery - t_rest.get_height()//2))

        # Quit
        pygame.draw.rect(screen, (200, 80, 80), self.r_quit, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.r_quit, width=2, border_radius=8)
        t_quit = self.font.render("Lobby", True, WHITE)
        screen.blit(t_quit, (self.r_quit.centerx - t_quit.get_width()//2, self.r_quit.centery - t_quit.get_height()//2))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.r_cont.collidepoint(mx, my):
                return "continue"
            elif self.r_rest.collidepoint(mx, my):
                return "restart"
            elif self.r_quit.collidepoint(mx, my):
                return "quit"
        return None

class HelpPopup:
    def __init__(self, font_big, font, font_small):
        self.font_big = font_big
        self.font = font
        self.font_small = font_small
        
        # Popup dimensions
        self.w, self.h = 400, 300
        self.x = (SCREEN_W - self.w) // 2
        self.y = (SCREEN_H - self.h) // 2
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        
        self.tips = [
            "Hotkeys: 1~5 speed, N next wave",
            "Right click cancels / exits Trash",
            "Press ESC for lobby",
            "Click empty slot to spawn die",
            "Drag same dice to merge",
        ]

    def draw(self, screen):
        # Draw background
        pygame.draw.rect(screen, (40, 40, 50), self.rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, self.rect, width=2, border_radius=12)
        
        # Title
        title = self.font_big.render("How to Play", True, WHITE)
        screen.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 20))
        
        py = self.rect.y + 70
        for tip in self.tips:
            t = self.font.render(tip, True, WHITE)
            screen.blit(t, (self.rect.x + 30, py))
            py += 30
            
        # Close instruction
        close_txt = self.font_small.render("Click Help again to close", True, (200, 200, 200))
        screen.blit(close_txt, (self.rect.centerx - close_txt.get_width() // 2, self.rect.bottom - 30))
