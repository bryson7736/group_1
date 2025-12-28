# -*- coding: utf-8 -*-
import pygame
from colors import WHITE, DARK, DARKER, GRAY, ACCENT, SLATE, DICE_COLORS
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
    """Draw dots (pips) for levels 1-7."""
    import pygame
    
    pip_radius = max(3, int(rect.width / 12))
    gap = rect.width // 4
    
    patterns = {
        1: [(0, 0)],
        2: [(-gap, -gap), (gap, gap)],
        3: [(-gap, -gap), (0, 0), (gap, gap)],
        4: [(-gap, -gap), (gap, -gap), (-gap, gap), (gap, gap)],
        5: [(-gap, -gap), (gap, -gap), (0, 0), (-gap, gap), (gap, gap)],
        # Level 6: Two columns of 3 pips each (3x2 grid)
        6: [(-gap, -gap), (-gap, 0), (-gap, gap), (gap, -gap), (gap, 0), (gap, gap)],
        # Level 7: 1-3-3 pyramid pattern (top center, middle row 3, bottom row 3)
        7: [(0, -gap), (-gap, 0), (0, 0), (gap, 0), (-gap, gap), (0, gap), (gap, gap)],
    }
    
    # For level 7+, use star
    if level > 7:
        font_size = int(rect.height * 0.6)
        try:
            star_font = pygame.font.SysFont(["segoe uiemoji", "segoe ui symbol", "arial"], font_size, bold=True)
        except:
            star_font = pygame.font.SysFont("arial", font_size, bold=True)
            
        star = star_font.render("★", True, color)
        surf.blit(star, (rect.centerx - star.get_width()//2, rect.centery - star.get_height()//2))
        return
    
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
        self.w, self.h = 700, 650
        self.x = (SCREEN_W - self.w) // 2
        self.y = (SCREEN_H - self.h) // 2
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        
        # Close Button
        self.close_btn = Button(
            rect=(self.rect.centerx - 60, self.rect.bottom - 50, 120, 40),
            text="Close",
            font=self.font,
            on_click=lambda: None, # Handled externally or we can return a signal
            bg=(200, 50, 50),
            fg=WHITE,
            hover=(220, 70, 70),
            radius=8
        )

    def draw(self, screen):
        # Draw background
        pygame.draw.rect(screen, (40, 40, 50), self.rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, self.rect, width=2, border_radius=12)
        
        # Title
        title = self.font_big.render("How to Play", True, WHITE)
        screen.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 20))
        
        py = self.rect.y + 60
        for tip in self.tips:
            t = self.font_small.render(tip, True, WHITE)
            screen.blit(t, (self.rect.x + 30, py))
            py += 25
            
        # Synergies Section
        py += 10
        syn_title = self.font_big.render("Synergies (Place Adjacent)", True, (255, 215, 0))
        screen.blit(syn_title, (self.rect.centerx - syn_title.get_width() // 2, py))
        py += 40
        
        # Helper to draw die icon
        def draw_icon(x, y, color, label):
            r = pygame.Rect(x, y, 30, 30)
            pygame.draw.rect(screen, color, r, border_radius=5)
            pygame.draw.rect(screen, WHITE, r, width=2, border_radius=5)
            # Initial letter
            l = self.font_small.render(label[0].upper(), True, WHITE)
            screen.blit(l, (r.centerx - l.get_width()//2, r.centery - l.get_height()//2))
            return r.right
            
        synergies = [
            ("fire", "wind", "Inferno: Fire +Splash, Wind +Speed", (255, 69, 0)),
            ("iron", "poison", "Toxic Spikes: Iron poisons, Poison +Dmg", (138, 43, 226)),
            ("freeze", "multi", "Frost Volley: Multi slows, Freeze +Range", (0, 255, 255)),
            ("single", "wind", "Sniper Nest: Single +Range/Dmg, Wind +Speed", (50, 205, 50)),
            ("fire", "iron", "Magma: Fire +Dmg, Iron Explodes", (220, 20, 60)),
            ("poison", "multi", "Plague: Poison AOE, Multi poisons", (0, 128, 0))
        ]
        
        start_x = self.rect.x + 40
        
        for t1, t2, desc_text, color in synergies:
            lx = start_x
            lx = draw_icon(lx, py, DICE_COLORS.get(t1, (100,100,100)), t1) + 5
            plus = self.font_small.render("+", True, WHITE)
            screen.blit(plus, (lx, py+5))
            lx += 15
            lx = draw_icon(lx, py, DICE_COLORS.get(t2, (100,100,100)), t2) + 15
            
            # Draw link line
            pygame.draw.line(screen, color, (start_x + 15, py+35), (start_x + 15 + 30 + 15, py+35), 3)
            
            # Draw Dot Indicator explanation
            dot_x = lx + 15
            pygame.draw.circle(screen, color, (dot_x, py + 15), 6)
            pygame.draw.circle(screen, WHITE, (dot_x, py + 15), 7, width=1)
            
            desc = self.font_small.render(desc_text, True, color)
            screen.blit(desc, (dot_x + 15, py + 5))
            py += 45

        # Close Button
        self.close_btn.draw(screen)

    def handle_input(self, event):
        if self.close_btn.handle(event):
            return "close"
        return None

def draw_wave_title(screen, font_huge, wave):
    """Draw the artistic WAVE X title at top center."""
    # Calculate wave number (1-based for display)
    current_wave = max(1, wave + 1)
    text_str = f"WAVE {current_wave}"
    
    # Stylized font rendering
    # Shadow
    shadow = font_huge.render(text_str, True, (0, 0, 0))
    # Main Text (Gold/Orange gradient simulated with color)
    # Using a bright orange-gold
    main_color = (255, 180, 0)
    text = font_huge.render(text_str, True, main_color)
    
    # Position: Top Center
    cx = SCREEN_W // 2
    cy = 50
    
    # Draw shadow offset
    screen.blit(shadow, (cx - shadow.get_width() // 2 + 3, cy - shadow.get_height() // 2 + 3))
    # Draw text
    screen.blit(text, (cx - text.get_width() // 2, cy - text.get_height() // 2))
    
    # Simple underline
    lw = text.get_width() + 40
    pygame.draw.rect(screen, main_color, (cx - lw//2, cy + 25, lw, 3), border_radius=2)

def draw_boss_state(screen, font_huge, enemies):
    """Draw the current state of the Boss if active."""
    from boss import TrueBoss
    boss = None
    for e in enemies:
        if isinstance(e, TrueBoss):
            boss = e
            break
    
    if boss:
        state_text = f"BOSS: {boss.state.upper()}"
        # Color coding based on state
        color = WHITE
        if boss.state == "defense":
            color = (100, 100, 255) # Blueish
        elif boss.state == "attack":
            color = (255, 50, 50) # Red
        elif boss.state == "heal":
            color = (50, 255, 50) # Green
        
        txt = font_huge.render(state_text, True, color)
        # Bottom Right
        x = SCREEN_W - txt.get_width() - 30
        y = SCREEN_H - txt.get_height() - 30
        
        screen.blit(txt, (x, y))

class AdsPopup:
    def __init__(self, font_big, font_small):
        self.font_big = font_big
        self.font_small = font_small
        
        # Popup dimensions
        self.w, self.h = 500, 400
        self.x = (SCREEN_W - self.w) // 2
        self.y = (SCREEN_H - self.h) // 2
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        
        # Close button (top right)
        self.close_btn_size = 30
        self.close_rect = pygame.Rect(self.rect.right - self.close_btn_size - 10, 
                                      self.rect.top + 10, 
                                      self.close_btn_size, 
                                      self.close_btn_size)

    def draw(self, screen):
        # Draw background (White interface as requested)
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=12)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, width=2, border_radius=12)
        
        # Placeholder text
        title = self.font_big.render("Advertisement", True, DARK)
        screen.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 50))
        
        msg = self.font_small.render("(Future Ads Content)", True, GRAY)
        screen.blit(msg, (self.rect.centerx - msg.get_width() // 2, self.rect.centery))

        # Close button (X)
        pygame.draw.rect(screen, (200, 50, 50), self.close_rect, border_radius=4)
        # Draw X
        start_pos = (self.close_rect.left + 8, self.close_rect.top + 8)
        end_pos = (self.close_rect.right - 8, self.close_rect.bottom - 8)
        pygame.draw.line(screen, WHITE, start_pos, end_pos, 3)
        start_pos2 = (self.close_rect.right - 8, self.close_rect.top + 8)
        end_pos2 = (self.close_rect.left + 8, self.close_rect.bottom - 8)
        pygame.draw.line(screen, WHITE, start_pos2, end_pos2, 3)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                return "close"
        return None

class RemoveAdsPopup:
    def __init__(self, font_big, font_small):
        self.font_big = font_big
        self.font_small = font_small
        
        # Popup dimensions
        self.w, self.h = 400, 350
        self.x = (SCREEN_W - self.w) // 2
        self.y = (SCREEN_H - self.h) // 2
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        
        # Input Field
        self.card_number = ""
        self.input_rect = pygame.Rect(0, 0, 300, 40)
        self.input_rect.center = (self.rect.centerx, self.rect.centery + 20)
        self.active = True  # Auto-focus
        
        # Pay Button
        self.btn_w, self.btn_h = 160, 50
        self.pay_rect = pygame.Rect(0, 0, self.btn_w, self.btn_h)
        self.pay_rect.center = (self.rect.centerx, self.rect.bottom - 60)
        
        # Close button (top right)
        self.close_btn_size = 30
        self.close_rect = pygame.Rect(self.rect.right - self.close_btn_size - 10, 
                                      self.rect.top + 10, 
                                      self.close_btn_size, 
                                      self.close_btn_size)

    def draw(self, screen):
        # Draw background
        pygame.draw.rect(screen, (40, 40, 50), self.rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, self.rect, width=2, border_radius=12)
        
        # Title
        title = self.font_big.render("Remove Ads", True, WHITE)
        screen.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 30))
        
        # Message
        msg1 = self.font_small.render("Enter 16-digit Credit Card Number:", True, WHITE)
        screen.blit(msg1, (self.rect.centerx - msg1.get_width() // 2, self.rect.y + 100))

        # Input Box
        box_color = WHITE if self.active else (200, 200, 200)
        pygame.draw.rect(screen, box_color, self.input_rect, border_radius=5)
        
        # Render text with formatting (groups of 4)
        display_text = " ".join([self.card_number[i:i+4] for i in range(0, len(self.card_number), 4)])
        
        if not self.card_number and not self.active:
            txt_surf = self.font_big.render("0000 0000 0000 0000", True, (180, 180, 180))
        else:
            txt_surf = self.font_big.render(display_text, True, DARK)
            
        screen.blit(txt_surf, (self.input_rect.x + 10, self.input_rect.y + (self.input_rect.height - txt_surf.get_height()) // 2))
        
        # Cursor
        if self.active and (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = self.input_rect.x + 10 + txt_surf.get_width()
            # Adjust cursor if text is empty
            if not self.card_number:
                cursor_x = self.input_rect.x + 10
            cursor_y = self.input_rect.y + 10
            pygame.draw.line(screen, DARK, (cursor_x, cursor_y), (cursor_x, cursor_y + 20), 2)
        
        # Pay Button
        can_pay = len(self.card_number) == 16
        btn_color = (100, 200, 100) if can_pay else (100, 100, 100)
        
        pygame.draw.rect(screen, btn_color, self.pay_rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.pay_rect, width=2, border_radius=8)
        t_pay = self.font_big.render("Confirm", True, WHITE)
        screen.blit(t_pay, (self.pay_rect.centerx - t_pay.get_width()//2, self.pay_rect.centery - t_pay.get_height()//2))

        # Close button (X)
        pygame.draw.rect(screen, (200, 50, 50), self.close_rect, border_radius=4)
        # Draw X
        start_pos = (self.close_rect.left + 8, self.close_rect.top + 8)
        end_pos = (self.close_rect.right - 8, self.close_rect.bottom - 8)
        pygame.draw.line(screen, WHITE, start_pos, end_pos, 3)
        start_pos2 = (self.close_rect.right - 8, self.close_rect.top + 8)
        end_pos2 = (self.close_rect.left + 8, self.close_rect.bottom - 8)
        pygame.draw.line(screen, WHITE, start_pos2, end_pos2, 3)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.input_rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False

            if self.close_rect.collidepoint(event.pos):
                return "close"
            if self.pay_rect.collidepoint(event.pos):
                if len(self.card_number) == 16:
                    return "pay"

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if len(self.card_number) == 16:
                    return "pay"
            elif event.key == pygame.K_BACKSPACE:
                self.card_number = self.card_number[:-1]
            elif event.unicode.isdigit() and len(self.card_number) < 16:
                self.card_number += event.unicode
        return None

class CoinPurchasePopup:
    def __init__(self, font_big, font_small):
        self.font_big = font_big
        self.font_small = font_small
        
        self.w, self.h = 600, 400
        self.x = (SCREEN_W - self.w) // 2
        self.y = (SCREEN_H - self.h) // 2
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        
        self.close_btn_size = 30
        self.close_rect = pygame.Rect(self.rect.right - self.close_btn_size - 10, 
                                      self.rect.top + 10, 
                                      self.close_btn_size, 
                                      self.close_btn_size)
        
        # Packages: (Coins, Price, Rect)
        self.packages = [
            {"coins": 100, "price": "$0.99", "rect": None, "color": (100, 200, 100)},
            {"coins": 500, "price": "$4.99", "rect": None, "color": (50, 150, 255)},
            {"coins": 1000, "price": "$9.99", "rect": None, "color": (200, 100, 255)}
        ]
        
        # Layout packages
        btn_w, btn_h = 160, 200
        gap = 20
        start_x = self.rect.x + (self.w - (3 * btn_w + 2 * gap)) // 2
        start_y = self.rect.y + 100
        
        for i, pkg in enumerate(self.packages):
            pkg["rect"] = pygame.Rect(start_x + i * (btn_w + gap), start_y, btn_w, btn_h)

    def draw(self, screen):
        # Background
        pygame.draw.rect(screen, DARK, self.rect, border_radius=15)
        pygame.draw.rect(screen, (255, 215, 0), self.rect, width=3, border_radius=15) # Gold border
        
        # Title
        title = self.font_big.render("Need More Coins?", True, (255, 215, 0))
        screen.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 30))
        
        # Packages
        for pkg in self.packages:
            r = pkg["rect"]
            # Card bg
            pygame.draw.rect(screen, (40, 40, 50), r, border_radius=10)
            pygame.draw.rect(screen, pkg["color"], r, width=2, border_radius=10)
            
            # Coin Amount
            amt_txt = self.font_big.render(f"{pkg['coins']}", True, WHITE)
            screen.blit(amt_txt, (r.centerx - amt_txt.get_width()//2, r.y + 30))
            
            lbl_txt = self.font_small.render("Coins", True, (200, 200, 200))
            screen.blit(lbl_txt, (r.centerx - lbl_txt.get_width()//2, r.y + 60))
            
            # Circle Icon placeholder
            pygame.draw.circle(screen, (255, 215, 0), (r.centerx, r.centery + 10), 20)
            
            # Price Button
            price_rect = pygame.Rect(r.x + 10, r.bottom - 50, r.width - 20, 40)
            pygame.draw.rect(screen, pkg["color"], price_rect, border_radius=5)
            
            p_txt = self.font_big.render(pkg["price"], True, WHITE)
            screen.blit(p_txt, (price_rect.centerx - p_txt.get_width()//2, price_rect.centery - p_txt.get_height()//2))

        # Close button
        pygame.draw.rect(screen, (200, 50, 50), self.close_rect, border_radius=4)
        start_pos = (self.close_rect.left + 8, self.close_rect.top + 8)
        end_pos = (self.close_rect.right - 8, self.close_rect.bottom - 8)
        pygame.draw.line(screen, WHITE, start_pos, end_pos, 3)
        start_pos2 = (self.close_rect.right - 8, self.close_rect.top + 8)
        end_pos2 = (self.close_rect.left + 8, self.close_rect.bottom - 8)
        pygame.draw.line(screen, WHITE, start_pos2, end_pos2, 3)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                return "close"
            
            for pkg in self.packages:
                # Check if clicked anywhere on the package card
                if pkg["rect"].collidepoint(event.pos):
                    return pkg["coins"]
        return None
