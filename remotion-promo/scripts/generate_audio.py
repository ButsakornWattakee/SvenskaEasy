# -*- coding: utf-8 -*-
"""Generate a 24s music bed and short SFX for the Remotion promo."""
from __future__ import annotations

import math
import os
import random
import struct
import wave

SR = 44100
OUT = os.path.join(os.path.dirname(__file__), "..", "public")


def write_wav(path: str, samples: list[float]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SR)
        frames = b"".join(
            struct.pack("<h", max(-32767, min(32767, int(s * 32767)))) for s in samples
        )
        wav.writeframes(frames)


def env(i: int, n: int, attack: float = 0.01, release: float = 0.2) -> float:
    a = int(SR * attack)
    r = int(SR * release)
    if i < a:
        return i / max(a, 1)
    if i > n - r:
        return max(0.0, (n - i) / max(r, 1))
    return 1.0


def sine(freq: float, i: int) -> float:
    return math.sin(2 * math.pi * freq * i / SR)


def make_whoosh(seconds: float = 0.45) -> list[float]:
    n = int(SR * seconds)
    rng = random.Random(3)
    out = []
    for i in range(n):
        t = i / n
        noise = rng.uniform(-1, 1)
        tone = sine(180 + 1400 * t, i) * 0.25
        out.append((noise * (0.15 + 0.55 * t) + tone) * env(i, n, 0.02, 0.18) * 0.7)
    return out


def make_pop() -> list[float]:
    n = int(SR * 0.12)
    out = []
    for i in range(n):
        s = sine(620, i) * 0.55 + sine(1240, i) * 0.2
        out.append(s * env(i, n, 0.002, 0.08))
    return out


def make_ding() -> list[float]:
    n = int(SR * 0.55)
    out = []
    for i in range(n):
        s = sine(880, i) * 0.45 + sine(1320, i) * 0.28 + sine(1760, i) * 0.12
        out.append(s * env(i, n, 0.004, 0.4))
    return out


def make_click() -> list[float]:
    n = int(SR * 0.06)
    rng = random.Random(9)
    out = []
    for i in range(n):
        s = sine(1900, i) * 0.4 + rng.uniform(-0.2, 0.2)
        out.append(s * env(i, n, 0.001, 0.04))
    return out


def make_music(seconds: float = 24.0) -> list[float]:
    n = int(SR * seconds)
    bpm = 108
    beat = 60 / bpm
    # Am – F – C – G
    chords = [
        [220.00, 261.63, 329.63],
        [174.61, 220.00, 261.63],
        [130.81, 164.81, 196.00],
        [196.00, 246.94, 293.66],
    ]
    melody = [440, 523.25, 493.88, 392, 349.23, 392, 440, 523.25]
    out = [0.0] * n
    for i in range(n):
        t = i / SR
        bar = int(t / (beat * 4))
        chord = chords[bar % 4]
        pad = sum(sine(f, i) for f in chord) / 3 * 0.16
        kick_phase = (t % beat) / beat
        kick = math.sin(2 * math.pi * (70 * (1 - kick_phase * 0.6)) * t) * (1 - kick_phase) ** 2 * 0.28
        if (t % (beat * 2)) < 0.04:
            hat = random.Random(i).uniform(-0.08, 0.08)
        else:
            hat = 0.0
        note = melody[int(t / (beat * 0.5)) % len(melody)]
        lead = sine(note, i) * 0.09 * (0.4 + 0.6 * math.sin(t * 2))
        sample = (pad + kick + hat + lead) * 0.85
        fade = 1.0
        if t < 0.4:
            fade = t / 0.4
        if t > seconds - 1.2:
            fade = max(0.0, (seconds - t) / 1.2)
        out[i] = max(-1.0, min(1.0, sample * fade))
    return out


def main() -> None:
    public = os.path.abspath(OUT)
    os.makedirs(public, exist_ok=True)
    write_wav(os.path.join(public, "music.wav"), make_music())
    write_wav(os.path.join(public, "whoosh.wav"), make_whoosh())
    write_wav(os.path.join(public, "pop.wav"), make_pop())
    write_wav(os.path.join(public, "ding.wav"), make_ding())
    write_wav(os.path.join(public, "click.wav"), make_click())
    print("audio written to", public)


if __name__ == "__main__":
    main()
