# AGENTS.md

## 1. Purpose

This file defines the working rules for AI coding agents such as Codex, Claude Code, or other AI assistants working on this project.

Project:

```text
AI-assisted sheet metal drawing and manufacturing drawing generation system
```

Current development strategy:

```text
Mac environment for MVP development
↓
Cross-platform compatibility
↓
Windows environment for industrial validation and deployment
```

The agent must follow this file before making any change to the project.

---

## 2. Project Background

This project aims to simplify and partially automate the sheet metal drawing workflow used in manufacturing companies.

Original manual workflow:

```text
Customer sends PDF engineering drawings
↓
Engineer manually understands views, sections, dimensions and product structure
↓
Engineer redraws and splits parts in AutoCAD
↓
Engineer reserves dimensions for bending, welding, grinding and painting
↓
CAD/DXF drawings are sent to workers
↓
Laser cutting, bending, welding, grinding and painting are performed
↓
Final product is produced
```

Long-term goal:

```text
Upload customer PDF engineering drawing
↓
AI extracts dimensions, holes, views, structure and manufacturing notes
↓
System generates structured JSON
↓
CAD/DXF generator creates sheet metal flat patterns
↓
Engineer reviews and adjusts
↓
System exports DXF/DWG/PDF manufacturing documents
```

The project does not aim to fully replace engineers at the beginning.

Approach:

```text
AI assistance + CAD automation + engineer review
```

---

## 3. Current MVP Scope

The current MVP does not start from PDF recognition.

The first-stage MVP must focus on:

```text
JSON parameters
↓
Python calculation
↓
ezdxf DXF generation
↓
FreeCAD / AutoCAD inspection
```

First MVP target:

```text
Generate a flat pattern DXF for a simple U-shaped sheet metal bracket.
```

Required DXF layers:

```text
CUT
BEND
TEXT
```

First output target:

```text
output/U_BRACKET_001.dxf
```

---

## 4. Development Environment Strategy

### 4.1 Mac MVP Development

The project is currently developed on macOS / iMac.

The Mac environment is used for:

```text
Python core logic
JSON input
DXF generation
Streamlit prototype
PDF parsing exploration
FreeCAD checking
```

### 4.2 Windows Industrial Validation

Later, the project should be tested on Windows because real manufacturing environments often use:

```text
AutoCAD
SolidWorks
Inventor
FreeCAD for Windows
laser cutting software
CypCut or similar cutting software
factory Windows PCs
```

Strategy:

```text
Mac for research and MVP development
Windows for industrial compatibility and deployment validation
```

---

## 5. General Working Rules

Before making changes, the agent must:

1. Read this `AGENTS.md`.
2. Read `README.md`.
3. Read the `AI_Sheet_Metal_Drawing_Project_Plan.md`.
4. Inspect the current project structure.
5. Understand the current stage before modifying files.
6. Avoid unnecessary large rewrites.
7. Preserve existing files unless explicitly instructed otherwise.
8. Ask before overwriting important files.
9. Keep changes small, testable and well documented.

---

## 6. File Safety Rules

The agent must not delete or overwrite existing files unless clearly instructed.

If a file already exists and the agent needs to modify it, the agent must:

1. Explain what will be changed.
2. Modify only the necessary section.
3. Preserve existing useful content.
4. Avoid replacing the whole file unless necessary.

The agent must never delete these files or folders unless the user explicitly asks:

```text
README.md
AGENTS.md
project plan Markdown file
examples/
src/
output/
requirements.txt
```

---

## 7. Recommended Project Structure

```text
sheet-metal-ai-assistant/
│
├── README.md
├── AGENTS.md
├── requirements.txt
├── AI_Sheet_Metal_Drawing_Project_Plan.md
│
├── examples/
│   └── u_bracket_sample.json
│
├── src/
│   ├── main.py
│   ├── sheet_metal_math.py
│   └── dxf_generator.py
│
├── output/
│   └── U_BRACKET_001.dxf
│
└── docs/
    └── project_notes.md
```

If this structure does not exist, the agent should create missing folders and files only when needed.

---

## 8. Coding Rules

The agent should write code that is:

```text
simple
readable
modular
well commented
easy to test
easy to extend
```

Python code should follow these principles:

1. Keep calculation logic separate from DXF generation.
2. Keep input/output logic separate from core geometry logic.
3. Use clear function names.
4. Use type hints when helpful.
5. Validate input values where possible.
6. Use `pathlib` for file paths.
7. Avoid hard-coded absolute paths.
8. Make the code work on both macOS and Windows where possible.

Recommended separation:

```text
src/main.py               command-line entry point
src/sheet_metal_math.py   bend allowance and flat pattern calculations
src/dxf_generator.py      DXF layer and geometry generation
```

---

## 9. DXF Generation Rules

DXF files should use clear layers.

Required layers:

| Layer | Purpose |
|---|---|
| CUT | Laser cutting outer profile |
| BEND | Bend lines |
| TEXT | Labels, notes and part information |

Future optional layers:

| Layer | Purpose |
|---|---|
| HOLE | Hole geometry |
| WELD_EDGE | Welding edge marks |
| ETCH | Laser marking / engraving |
| CONSTRUCTION | Helper geometry |

DXF output should be saved in:

```text
output/
```

The first target output file is:

```text
output/U_BRACKET_001.dxf
```

---

## 10. Sheet Metal Calculation Rules

For the first MVP, use the bend allowance formula:

```text
BA = angle_rad * (inside_bend_radius + k_factor * thickness)
angle_rad = bend_angle * pi / 180
```

The agent must clearly document that this is a simplified MVP calculation.

The agent should not claim that this formula is production-ready for all real manufacturing cases.

Real-world factors include:

```text
material
thickness
inside bend radius
tooling
press brake setup
springback
K-factor table
bend deduction
factory experience
```

---

## 11. Testing Rules

After completing any coding task, the agent must run a relevant test whenever possible.

For the first MVP, the basic test command is:

```bash
source .venv/bin/activate
python3 src/main.py examples/u_bracket_sample.json
ls -l output/
```

If the project is running on Windows, use the Windows-compatible equivalent.

The agent must confirm whether the expected output exists:

```text
output/U_BRACKET_001.dxf
```

If a test cannot be run, the agent must explain why.

---

## 12. Documentation Rules

After completing a task, the agent must update documentation when relevant.

The agent should update these files when project status, usage, features, dependencies or next steps change:

```text
README.md
AI_Sheet_Metal_Drawing_Project_Plan.md
```

---

## 13. Mandatory Project Plan Update Rule

This rule is mandatory.

After completing each task, the agent must update the project plan Markdown file.

Expected project plan file name:

```text
AI_Sheet_Metal_Drawing_Project_Plan.md
```

If the file has a different name, the agent should find the project plan Markdown file by checking the project root.

The agent must update these sections after each completed task:

```text
## 当前进度
## 下一步行动清单
## 后续建议
```

If these sections do not exist, the agent should add them near the end of the project plan.

The update must include:

1. What was completed in this task.
2. What files were created or modified.
3. Whether tests were run.
4. Whether the test passed or failed.
5. What the next recommended action is.
6. Any risks, blockers or decisions needed from the user.

The agent must not leave the project plan outdated.

---

## 14. Recommended Format for Project Plan Updates

When updating the project plan, use this format:

```markdown
## 当前进度

### YYYY-MM-DD 更新

已完成：

- ...

本次修改的文件：

- ...

测试结果：

- ...

存在问题：

- ...

---

## 下一步行动清单

优先级从高到低：

1. ...
2. ...
3. ...

---

## 后续建议

- ...
```

If there are previous updates, keep them and add the new update above or below them consistently.

---

## 15. README Update Rule

If the way to run the project changes, update `README.md`.

README should always explain:

```text
project purpose
current features
environment requirements
installation steps
how to run
input file format
output file location
current limitations
next steps
```

---

## 16. Dependency Rules

The agent must record Python dependencies in:

```text
requirements.txt
```

If a new Python package is installed, update `requirements.txt`.

Do not add unnecessary dependencies.

For the first MVP, the required package is:

```text
ezdxf
```

Possible later packages:

```text
streamlit
pymupdf
pdfplumber
opencv-python
pillow
pydantic
```

---

## 17. AI Tool Usage Rules

AI tools such as Codex, Claude Code or ChatGPT may be used to:

```text
write code
debug code
refactor files
generate tests
write documentation
create project plans
suggest architecture
```

However, the agent must not treat AI output as engineering truth.

For manufacturing-related output, the agent must clearly mark assumptions and limitations.

The engineer or user must review:

```text
bend dimensions
flat pattern size
hole positions
bend direction
welding edge
material assumptions
DXF output
```

---

## 18. Task Completion Report

After finishing a task, the agent must provide a short completion report.

The report must include:

```text
Task completed:
Files changed:
Test run:
Test result:
Project plan updated:
Recommended next step:
```

Example:

```text
Task completed: Added U-bracket DXF generator.
Files changed: src/main.py, src/dxf_generator.py, src/sheet_metal_math.py, examples/u_bracket_sample.json, README.md.
Test run: python3 src/main.py examples/u_bracket_sample.json.
Test result: Passed. output/U_BRACKET_001.dxf generated successfully.
Project plan updated: Yes.
Recommended next step: Open the DXF in FreeCAD and verify geometry and layer names.
```

---

## 19. What Not To Do

The agent must not:

1. Delete existing project files without permission.
2. Overwrite major documentation without preserving useful content.
3. Skip testing when testing is possible.
4. Ignore the project plan update rule.
5. Generate overly complex architecture too early.
6. Start with full PDF recognition before the DXF generation MVP is stable.
7. Claim that generated DXF files are production-ready without engineering review.
8. Add unnecessary frameworks or dependencies.
9. Assume Windows compatibility without testing.
10. Upload project files or drawings to external services without permission.

---

## 20. Current Recommended Next Task

The current recommended next task is:

```text
Create or complete the first MVP:
JSON input → bend allowance calculation → U-shaped sheet metal DXF output.
```

The expected output is:

```text
output/U_BRACKET_001.dxf
```

After completing this task, update:

```text
README.md
AI_Sheet_Metal_Drawing_Project_Plan.md
```

especially:

```text
## 当前进度
## 下一步行动清单
## 后续建议
```
