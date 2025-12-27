import pygame
import os
import struct
import random
import math

class SoundManager:
    def __init__(self):
        # Ensure mixer is initialized with specific settings for our generated sounds
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=1)
        
        self.sounds = {}
        self.enabled = True
        
        # Ensure assets directory exists
        if not os.path.exists(os.path.join("assets", "sounds")):
            os.makedirs(os.path.join("assets", "sounds"), exist_ok=True)

        # Load or generate sounds
        self._load_or_generate("shoot", "shoot.wav", self._gen_shoot)
        self._load_or_generate("merge", "merge.wav", self._gen_merge)
        self._load_or_generate("hit", "hit.wav", self._gen_hit)
        self._load_or_generate("click", "click.wav", self._gen_click)
        self._load_or_generate("spawn", "spawn.wav", self._gen_spawn)
        self._load_or_generate("error", "error.wav", self._gen_error)
        self._load_or_generate("upgrade", "upgrade.wav", self._gen_upgrade)

    def _load_or_generate(self, name, filename, gen_func):
        path = os.path.join("assets", "sounds", filename)
        if os.path.exists(path):
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Failed to load sound {path}: {e}")
                self.sounds[name] = gen_func()
        else:
            self.sounds[name] = gen_func()

    def _gen_tone(self, freq, duration, volume=0.5, decay=True):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        period = sample_rate / freq
        
        amplitude = int(32767 * volume)
        
        for i in range(n_samples):
            # Square wave with decay
            t = i / sample_rate
            current_vol = amplitude
            if decay:
                current_vol = int(amplitude * (1 - (i / n_samples)))
            
            val = current_vol if (i % int(period)) < (period / 2) else -current_vol
            buf.extend(struct.pack('<h', val))
            
        return pygame.mixer.Sound(bytes(buf))

    def _gen_noise(self, duration, volume=0.5):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        amplitude = int(32767 * volume)
        
        for i in range(n_samples):
            val = random.randint(-amplitude, amplitude)
            buf.extend(struct.pack('<h', val))
            
        return pygame.mixer.Sound(bytes(buf))

    def _gen_shoot(self):
        # High pitch short beep
        return self._gen_tone(880, 0.05, 0.2)

    def _gen_merge(self):
        # Ascending tone sequence simulated by a single tone for now
        return self._gen_tone(1200, 0.15, 0.3)

    def _gen_hit(self):
        # Short noise
        return self._gen_noise(0.05, 0.2)

    def _gen_click(self):
        # Very short high click
        return self._gen_tone(2000, 0.02, 0.3)
        
    def _gen_spawn(self):
        # Lower tone
        return self._gen_tone(440, 0.1, 0.3)
        
    def _gen_error(self):
        # Low buzz
        return self._gen_tone(150, 0.2, 0.3, decay=False)

    def _gen_upgrade(self):
        return self._gen_tone(1500, 0.2, 0.3)

    def play(self, name):
        if self.enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except:
                pass
