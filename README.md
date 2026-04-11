# AI Battle Simulator

A fully programmable real-time strategy (RTS) battle simulator inspired by Age of Empires II, designed to experiment with AI-controlled generals, tactical decision-making.

This project focuses on AI behavior, combat mechanics, and experimental evaluation rather than game design or graphical polish.

---

## 🎯 Overview

The simulator models medieval-style online battles between many armies composed of units such as Knights, Pikemen, and Crossbowmen.  
Each army is commanded by a general implementing a specific AI strategy, which fully controls unit movement, target selection, formations, and engagements.

The system is designed as an experimental platform to compare AI behaviors under controlled scenarios.

---

## 🛠 Requirements

- Python 3.12
- Pygame

---

## 🚀 How to Run

Make sure you are in the `src` directory and use one of the following commands:

### Test a multi battle
```bash
python3 Main.py multi <AI1> 
python3 Main.py multi Smart

```

### Run a single battle
```bash
python3 Main.py run <AI1> <AI2> [-t]
python3 Main.py run Smart Daft

```

### Run a 4 IA battle
```bash
python3 Main.py run4 <AI1> <AI2> <AI3> <AI4> [-t]
python3 Main.py run4 Smart Daft Daft Smart

```

### Access rights
```bash
If you get this error : PermissionError: [Errno 13] Permission denied: './network/comm_c_c'
You must type in the terminal : chmod +x ./network/comm_c_c

```
