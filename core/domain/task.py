from interfaces.shared.schemas import Task


class Task:
    def __init__(
            self,
            id: int,
            workspace: type[Workspace],
            name: str,
            parent_task: type[Task],
    ):
        self.id = id
        self.workspace = workspace
        self.name = name
        self.parent_task = task

    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"))
    workspace: Mapped["Workspace"] = relationship(back_populates="child_tasks")

    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    parent_task: Mapped[Optional["Task"]] = relationship(
        "Task", back_populates="child_tasks", remote_side=id
    )

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    weight: Mapped[float] = mapped_column(Float, default=1)
    owner_name: Mapped[str] = mapped_column(ForeignKey("users.username"))

    child_tasks: Mapped[List["Task"]] = relationship(back_populates="parent_task", cascade="all, delete-orphan")