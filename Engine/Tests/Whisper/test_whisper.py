import time
import psutil
import os
from faster_whisper import WhisperModel

audio_path = r"C:\Users\owena\Downloads\Eerie Unsolved Mysteries That Cannot Be Explained A Compilation.mp4"

process = psutil.Process(os.getpid())

print("Loading base model...")
model = WhisperModel("base", device="cpu", compute_type="int8")

print("Starting transcription in 30-second chunks...")
start = time.time()

segments, info = model.transcribe(
    audio_path,
    beam_size=5,
    vad_filter=True,
    chunk_length=30
)

peak_ram = 0
line_count = 0

for segment in segments:
    current_ram = process.memory_info().rss / (1024 * 1024)
    peak_ram = max(peak_ram, current_ram)
    line_count += 1
    print(f"[{segment.start:.0f}s] {segment.text}")
    if line_count % 10 == 0:
        print(f"   ...RAM so far: {peak_ram:.0f} MB")

elapsed = time.time() - start

print("\n--- RESULTS ---")
print(f"Processing time: {elapsed:.1f}s")
print(f"Peak RAM: {peak_ram:.1f} MB")
print(f"Total lines: {line_count}")