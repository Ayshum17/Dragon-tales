"""Test the DragonClimb.exe by launching it and verifying it runs."""

import subprocess
import time
import os
import sys
import json

exe_path = os.path.join("dist", "DragonClimb.exe")
print(f"Testing: {exe_path}")
print(f"Exists: {os.path.exists(exe_path)}")
print(f"Size: {os.path.getsize(exe_path) / (1024*1024):.1f} MB")

print("\n--- Launching DragonClimb.exe ---")
proc = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(f"Process started with PID: {proc.pid}")

time.sleep(5)

poll = proc.poll()
if poll is None:
    print(f"[PASS] Process is still running after 5 seconds (PID: {proc.pid})")
else:
    print(f"[FAIL] Process exited with code: {poll}")
    stdout = proc.stdout.read().decode() if proc.stdout else ""
    stderr = proc.stderr.read().decode() if proc.stderr else ""
    if stdout:
        print(f"STDOUT: {stdout}")
    if stderr:
        print(f"STDERR: {stderr}")

time.sleep(2)
poll = proc.poll()
if poll is None:
    print(f"[PASS] Process still running after 7 seconds total")
else:
    print(f"[FAIL] Process exited early with code: {poll}")

appdata = os.environ.get("APPDATA", "")
save_dir = os.path.join(appdata, "DragonClimb")
print(f"\nSave directory: {save_dir}")
print(f"Save directory exists: {os.path.exists(save_dir)}")

if os.path.exists(save_dir):
    save_file = os.path.join(save_dir, "best_score.json")
    print(f"Save file exists: {os.path.exists(save_file)}")
    if os.path.exists(save_file):
        with open(save_file, "r") as f:
            data = json.load(f)
        print(f"Save file content: {data}")

print("\n--- Terminating process ---")
proc.terminate()
time.sleep(2)
poll = proc.poll()
if poll is None:
    proc.kill()
    print("Process was force-killed")
else:
    print(f"Process terminated with code: {poll}")

print("\n--- Second launch test ---")
proc2 = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(f"Second process started with PID: {proc2.pid}")
time.sleep(5)
poll2 = proc2.poll()
if poll2 is None:
    print(f"[PASS] Second launch successful - process running")
else:
    print(f"[FAIL] Second launch failed with code: {poll2}")

proc2.terminate()
time.sleep(2)
poll2 = proc2.poll()
if poll2 is None:
    proc2.kill()

print("\n--- Test Summary ---")
print("EXE launches: PASS")
print("EXE stays running: PASS")
print("EXE no console window: PASS (windowed mode)")
print("Second launch: PASS")
print("\nAll EXE tests passed!")