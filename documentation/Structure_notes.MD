tasktracker/
├── core/
│   ├── domain/               # Pure business models
│   │   ├── task.py           # Task with progress logic
│   │   ├── task_list.py      # TaskList with completion %
│   │   └── user.py           # User domain model
│   │
│   ├── services/
│   │   ├── task_service.py   # Core progress logic
│   │   ├── analytics.py      # Progress calculations
│   │   └── notification.py   # Progress alerts
│   │
│   └── schemas/
│       └── shared/          # Pydantic Schemas
│           ├── task.py      # e.g., TaskBase, TaskProgress
│           └── user.py     # e.g., UserPublic
│
├── interfaces/
│   ├── telegram/
│   │   ├── handlers/
│   │   │   ├── tasks.py     # Task commands
│   │   │   └── progress.py  # Progress reports
│   │   ├── schemas/          # Bot-specific
│   │   │   ├── commands.py   # /addtask {task_name} {due_date}
│   │   │   └── replies.py    # Progress bars as MarkdownV2
│   │   └── bot.py
│   │
│   ├── api/
│   │   ├── schemas/          # FastAPI-specific
│   │   │   ├── tasks.py      # JSON request/response
│   │   │   └── progress.py   # % as float, nested tasks
│   │
│   └── web/                  # Future
│       └── schemas/          # Web-specific forms/UI models
│
├── db/
│   ├── sql/                 # SQL database
│   │   ├── models/          # SQLAlchemy models
│   │   └── repositories/
│   │
│   └── redis/               # Redis for caching
│       ├── models/          # Redis data structures
│       └── repositories/
│
└── infrastructure/
    ├── config.py
    ├── di.py                # Dependency injection
    └── logging.py