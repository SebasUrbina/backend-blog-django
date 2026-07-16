# Backend/DevOps Engineer Interview

A small content service: users, posts, comments, tags. Django + Ninja + Postgres.

---

## 🚀 Getting Started & Local Setup

We support two ways to run this application locally. **Option A** is the recommended way for a fresh laptop (requires only Docker), while **Option B** is optimized for local development and debugging (requires Python/Mise/UV).

---

### 🐳 Option A: Zero-Install Quick Start (Docker Compose)
This is the easiest way to get the application up and running with a single command.

#### Prereqs
* [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

#### Steps
1. **Create your environment file:**
   Copy the example file to `.env`:
   ```sh
   cp .env.example .env
   ```

2. **Build and start the services:**
   This command pulls the database and builds the API container:
   ```sh
   docker-compose up -d --build
   ```

3. **Run database migrations:**
   ```sh
   docker-compose exec api python manage.py migrate
   ```

4. **Seed the database:**
   ```sh
   docker-compose exec api python manage.py seed
   ```

Your backend service will be up at **http://localhost:8000**!
* **API Interactive Documentation:** [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
* **To stop services:** `docker-compose down`

---

### 💻 Option B: Local Native Setup (For Development)
If you are actively developing and want rapid-rebuilds or native toolchain support.

#### Prereqs
* [mise](https://mise.jdx.dev/) — manages the Python toolchain and uv.
* A running PostgreSQL 16 instance on `localhost:5432` with a database called `backend_devops_interview` accessible to `postgres`/`postgres`.

#### Steps
1. **Install Python & toolchain via mise:**
   ```sh
   mise install
   ```

2. **Install project dependencies:**
   We use `uv` for lightning-fast package management:
   ```sh
   uv sync
   ```

3. **Create the PostgreSQL database:**
   *(Ensure your Postgres server is running)*
   ```sh
   createdb backend_devops_interview
   ```

4. **Run migrations and seed the database:**
   ```sh
   uv run python manage.py migrate
   uv run python manage.py seed
   ```

5. **Start the development server:**
   ```sh
   uv run python manage.py runserver
   ```
   *Alternative high-performance ASGI server:*
   ```sh
   uv run uvicorn core.asgi:application --host 0.0.0.0 --port 8000 --reload
   ```

---

## 🧪 Testing and Code Quality

### Running Unit & Integration Tests
To run the test suite and verify everything is working:
```sh
uv run pytest
```

### Pre-commit Hooks (Formatting & Linting)
We use `ruff` and `black` to keep code clean and standardized. Install pre-commit hooks locally:
```sh
uv run pre-commit install
```
To run the hooks manually across all files:
```sh
uv run pre-commit run --all-files
```

---

## ⚡ Performance Testing with Locust
We include a Locust-based performance test script (`locustfile.py`) to measure API endpoints' latencies under concurrent user load.

### 1. Web UI Mode (Recommended)
1. Ensure the API service is running.
2. Start Locust:
   ```sh
   uv run locust -f locustfile.py
   ```
3. Open your browser at [http://localhost:8089](http://localhost:8089).
4. Enter target host `http://localhost:8000`, the number of concurrent users, spawn rate, and click **Start swarming**.

### 2. Headless Mode (Terminal-only)
To run an automated performance test directly in the terminal for a specific duration:
```sh
uv run locust --headless -u 100 -r 10 --run-time 1m --host http://localhost:8000
```


## What the API does

| Method | Path | Description |
| ------ | ---- | ----------- |
| GET    | `/api/posts` | Published posts, newest first |
| GET    | `/api/posts/search?q=` | Full-text-ish search across title and body |
| GET    | `/api/posts/by-tag/{slug}` | Posts carrying a given tag |
| GET    | `/api/posts/{id}` | Post detail with comments |
| POST   | `/api/posts` | Create a post |
| POST   | `/api/posts/{id}/comments` | Add a comment to a post |
| GET    | `/api/users/{id}` | User profile with post and comment counts |
| GET    | `/api/users/find?email=` | Look up a user by email |

## The assignment

We want to see how you take a working prototype and turn it into something a team can develop on and operate. Pick the changes that give the strongest signal about how you'd improve this codebase if you owned it. There are three areas we care about:

1. **Developer experience.** Getting this running on a fresh laptop is harder than it should be. Make it easier.
2. **Performance.** Once the database is seeded, exercise the endpoints. Some of them are slow. Find out why and fix what you can.
3. **Production readiness.** This service is a long way from something you'd put behind a load balancer. Move it closer — pick whichever deployment target you'd reach for at work (Helm chart, ECS task def, K8s manifests, Fly, Render, plain Docker + systemd — your call).

**Depth beats breadth.** Pick 2–3 things and go deep rather than touching ten things shallowly. Write a short `NOTES.md` covering:

- What you did and why.
- What you deliberately *didn't* do.
- What you'd do next if you had another day.

## Non-goals

- **Authentication / authorization** is intentionally absent. If you want to suggest a direction in `NOTES.md`, great — but no need to implement anything.
- **Test coverage** is not what we're grading. The smoke tests are there so you have something to wire into CI.
- **Reshaping the domain model** isn't expected. Adjust it if a perf fix needs it; otherwise leave it.

## Time

Soft cap of 2–6 hours, depending on your experience and what tooling you have available (AI agents are fine — say so in `NOTES.md` and include chat transcripts). We're looking at signal, not hours.

## Deliverable

Whatever's easy for you to share: a GitHub link, a [gitfront](https://gitfront.io) link, a git bundle, even `git format-patch`. Please don't open a PR against this repo.
