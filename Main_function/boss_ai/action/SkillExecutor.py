class SkillExecutor:
    GLOBAL_COOLDOWN = 3.0 # Cooldown between any two skills
    
    def __init__(self, boss, game):
        self.boss = boss
        self.game = game
        self.current_skill = None
        self.skill_timer = 0.0
        self.cooldown_timer = 0.0 # Force interval between skills
        self.cooldowns = {}

    def cast(self, skill_name, duration):
        """Invoke a skill."""
        if self.is_busy():
            return
            
        print(f"[BossAI] Action: Cast {skill_name}")
        self.current_skill = skill_name
        self.skill_timer = duration
        
        # Trigger animation/visuals if needed
        if hasattr(self.boss, 'on_skill_start'):
            self.boss.on_skill_start(skill_name)

    def cancel_current_skill(self):
        if self.current_skill:
            print(f"[BossAI] Action: Cancelled {self.current_skill}")
            self.current_skill = None
            self.skill_timer = 0.0
            # Also reset cooldown if cancelled? 
            # Usually keep it to prevent spamming after cancel.

    def update(self, dt):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

        if self.current_skill:
            self.skill_timer -= dt
            if self.skill_timer <= 0:
                self._apply_effect(self.current_skill)
                self.current_skill = None
                self.cooldown_timer = self.GLOBAL_COOLDOWN # Start cooldown after effect

    def _apply_effect(self, skill_name):
        """Apply the actual game logic effect of the skill."""
        print(f"[BossAI] Action: Effect Applied {skill_name}")
        if hasattr(self.boss, 'apply_skill_effect'):
            self.boss.apply_skill_effect(skill_name)

    def is_busy(self):
        """Busy if casting OR in post-skill cooldown."""
        return self.current_skill is not None or self.cooldown_timer > 0
