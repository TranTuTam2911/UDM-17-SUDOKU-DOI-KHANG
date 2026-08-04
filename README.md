# Multiplayer Sudoku Game

A real-time competitive multiplayer Sudoku game system based on Client-Server architecture using Python TCP Sockets (asyncio / selectors). The application supports real-time matchmaking, 1v1 challenges, live Spectator Mode, and concurrent management of multiple game rooms.

---

## Repository

| | |
|---|---|
| **Repository** | https://github.com/TranTuTam2911/UDM-17-SUDOKU-DOI-KHANG |
| **Course** | Network Programming |
| **Group** | UDM17 — Group 9 |
| **Target Runtime** |  |
| **Video** | |

---

## Team Members

| No. | Name | Role |
|-----|------|------|
| 1 |  | Team Leader |
| 2 |  | Developer |
| 3 |  | Developer |
| 4 |  | Developer |
| 5 |  | Developer |
| 6 | Nguyễn Hoài Vũ | Developer |

---

## Architecture

```
NP_NetGroup11_UDM12/
├── Code/
│   ├── sudoku_shared/            # Shared protocols, Sudoku generator, and constants
│   ├── sudoku_server/            # Socket TCP server & matchmaker engine
│   ├── sudoku_client/            # Game GUI client (Pygame / Tkinter)
│   └── sudoku_stress_test/       # Automated bot clients & concurrency test scripts
├── Extra/
│   ├── Documentation/            # Deployment and server setup guides
│   └── Test report/              # Concurrency & latency test reports
├── DOCX/                         # Project documentation (Word)
├── PPTX/                         # Presentation slides
└── README.md
```

---
