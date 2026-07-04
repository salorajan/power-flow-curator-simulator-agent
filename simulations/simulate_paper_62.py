# Copyright (c) 2026 MyCompany LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Simulation Script for Paper ID 62
DOI: 10.1109/tpwrs.2026.3674771
Title: Probabilistic Optimal Power Flow Calculation Using Weighted Quasi-Monte Carlo Method Based on Homotopy Algorithm and Correlation Correction
Description: DC Optimal Power Flow (DCOPF) Economic Dispatch on IEEE 9-bus grid.
"""
import sys
import os
import subprocess

# Paths discovery
POWER_PROJECT_DIR = r"C:\users\robert\power\g5\project"
python_executable = sys.executable

print("=========================================================================")
print("RUNNING SIMULATION FOR PAPER ID 62")
print("Title: Probabilistic Optimal Power Flow Calculation Using Weighted Quasi-Monte Carlo Method Based on Homotopy Algorithm and Correlation Correction")
print("Algorithm: DCOPF (DC Optimal Power Flow (DCOPF) Economic Dispatch on IEEE 9-bus grid.)")
print("=========================================================================")

cmd = [
    python_executable,
    os.path.join(POWER_PROJECT_DIR, "power_cli.py"),
    "9",
    "dcopf"
]

print(f"Executing command: {' '.join(cmd)}\n")
result = subprocess.run(cmd, cwd=POWER_PROJECT_DIR, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errors/Warnings:")
    print(result.stderr)
