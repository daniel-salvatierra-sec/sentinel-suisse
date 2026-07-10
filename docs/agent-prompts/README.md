# Agent security prompts

One file per phase with **explicit** security instructions for the AI coding agent.

| Phase | File | Status |
|-------|------|--------|
| 0 | Secure environment | Done |
| 1 | [phase-1-data-model.md](phase-1-data-model.md) | Active |
| 2 | CRUD internal API | Pending |
| 3 | Ingestion pipeline | Pending |
| 4 | Search + preferences | Pending |
| 5 | WhatsApp alerts | Pending |

**Rule:** the agent never sees real credentials. Use `os.getenv()` and `.env.example` as reference only.
