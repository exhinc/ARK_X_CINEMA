"""Manual local Whisper benchmark; not a portable CI test."""

import pytest

pytest.skip("Manual local Whisper benchmark; requires local media/model and is not a CI test", allow_module_level=True)

# Kept below the module-level skip for manual execution on the Windows workstation.
import os
import time
import psutil
from faster_whisper import WhisperModel

audio_path = r"C:\Users\owena\Downloads\Eerie Unsolved Mysteries That Cannot Be Explained A Compilation.mp4"

process = psutil.Process(os.getpid())
model = WhisperModel("base", device="cpu", compute_type="int8")
start = time.time()
segments, info = model.transcribe(audio_path, beam_size=5, vad_filter=True, chunk_length=30)
peak_ram = 0
line_count = 0
for segment in segments:
    current_ram = process.memory_info().rss / (1024 * 1024)
    peak_ram = max(peak_ram, current_ram)
    line_count += 1
    print(f"[{segment.start:.0f}s] {segment.text}")
    if line_count % 10 == 0:
        print(f"...RAM so far: {peak_ram:.0f} MB")
print(f"Processing time: {time.time() - start:.1f}s")
print(f"Peak RAM: {peak_ram:.1f} MB")
print(f"Total lines: {line_count}")
