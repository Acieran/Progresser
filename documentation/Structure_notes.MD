tasktracker/
├── core/                   # Strictly business logic - NO framework/db dependencies
│   ├── domain/             # Pure business entities (no ORM, no serialization)
│   │   ├── task.py         # Task entity with progress calculation methods
│   │   ├── workspace.py    # Workspace entity with validation rules
│   │   ├── user.py         # User management logic
│   │   └── user_state.py   # State transition logic (business rules)
│   │
│   └── application/        # Business use cases
│       ├── tasks/          # Task management flows
│       ├── analytics/      # Progress calculation services
│       └── ports/          # Abstract interfaces (Repository, StateStore, Notifier)
│
├── interfaces/             # Delivery mechanisms (adapters)
│   ├── telegram/           # Telegram-specific implementation
│   │   ├── handlers/       # Command handlers
│   │   ├── presenters/     # Markdown formatting
│   │   └── schemas/        # Telegram-specific DTOs
│   │
│   └── api/                # Future FastAPI
│       ├── routes/         # API endpoints
│       └── schemas/        # OpenAPI schemas
│
├── infrastructure/         # Implementation details
│   ├── persistence/        # DB implementations
│   │   ├── sqlalchemy/     # SQL models/repos
│   │   └── redis/          # Redis state store
│   │
│   ├── services/           # External service integrations
│   └── config/             # Environment configuration
│
└── shared/                 # Cross-cutting concerns
    ├── schemas/            # Common DTOs (base classes)
    └── utils/              # Shared utilities