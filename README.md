# Notty Card Game 

This repository contains a desktop version of the **Notty** card game built with **Python** and **Pygame**. The application allows a human player to compete against up to two computer opponents. 

This project was built by a team of 5 people.


## Team setup & my contributions

We split our 5-member team into two main groups to work on the logic and the user interface concurrently. 

* **Logic sub-team (3 Members):**
  * **My role:** I worked closely with one other teammate to design and build the **main game loop, turn transitions** (`GameLogic.py`). I was specifically responsible for **designing how moves work and writing the constraint-checking logic**. I also led the debugging phase.
  * **Our other teammate:** Focused entirely on the player logic, specifically the computer opponent, writing the AI behavior using a Monte Carlo Tree Search (MCTS) algorithm.*
* **UI/UX sub-team (2 Members):**
  * **Teammates 3 & 4:** Created the visual layout, card rendering pipelines, screen menus, and audio events using Pygame.

---

## 🛠️ Repository structure

```bash
├── Logic/                      # Backend Rules & Core Engine
│   ├── GameLogic.py            # Main Game Loop & Move Workflows (My Focus)
│   ├── PlayerLogic.py          # Action Execution & Rules Checking (My Focus)
│   ├── Classes.py              # Card, Deck, and Hand Data Models
│   ├── ValidateCardLogic.py    # Card Combination (Meld) Checking Utilities
│   └── computerLogic/          # AI Decision Code
└── ui/                         # Visual Interface (Built by the UI Team)
├── screens.py              # Windows & Pygame Event Handlers
├── card_visual.py          # Card Rendering & UI Coordinates
└── sounds.py               # Audio Events


## 💻 Engineering highlights 

### 1. Game loop & turn management
I co-designed the system that manages how matches progress. In *Notty*, a player can perform multiple actions (drawing, stealing, or discarding card groups) in an arbitrary order during a single turn. I structured the flow so that the game loop accurately tracks the state after each intermediate action, ensuring variables update cleanly and turns transition only when all rules are satisfied.

### 2. Move constraint enforcement
I wrote the validation logic inside `GameLogic.py` to catch and block illegal moves. Key rules I enforced include:
* **Hand Capacity Limits:** Checking that a player does not exceed the 20-card hand maximum. If an action would push them over 20 cards, the backend sets drawing and stealing paths to invalid, blocking the UI action before it can corrupt the data state.
* **Action Limits:** Limiting specific moves (like stealing or draw-discard combinations) to once per turn, while allowing group discards to happen infinitely.

### 3. Integration & code debugging
I was heavily involved in the debugging phase when combining the backend logic with the UI. Because player hands are face-up and the AI continuously evaluates the deck, we had several data-sync bugs early on. Our Logic sub-team diagnosed and fixed race conditions between UI button clicks and backend state updates.

## 📋 Product Management highlights

### 1. Requirements translation & API design
* **Turning rules into code:** I took the text-heavy game rules document and translated it into clear, step-by-step logic requirements that our sub-team could easily convert into Python functions using LucidCharts.
* **Unblocking the UI team:** By designing the core functions and methods of `GameLogic.py` early, we established an 'API contract'. This allowed the UI team to build their buttons and layouts around our function signatures before our backend logic was fully finished.

### 2. Risk mitigation & quality control
* **Handling invalid actions:** I designed the error paths so that if a player tries to discard an invalid set of cards, the game cleanly rejects the move and resets the selection state without crashing the game loop.
* **Bug triage:** During the final week of integration, I organized our testing and sorted bugs into "UI presentation issues" versus "core data logic issues." This kept the team organized and helped us catch game-breaking bugs quickly before release.


## 🔧 Installation & quick start

### Prerequisites
* Python 3.10 or higher
* Pygame library

### Running the app
1. Clone this repository to your local computer.
2. Install the Pygame dependency:
   ```bash
   pip install pygame```
3. Run the main script:
   ```bash
   python main.py

