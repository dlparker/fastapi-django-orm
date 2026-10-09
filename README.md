# FastAPI + Django ORM Template

A GitHub template to quickly get a FastAPI project
that needs an awesome ORM up and running.

If you only need the Django ORM to write scripts,
feel free to simply use https://github.com/Andrew-Chen-Wang/django-orm-template
which does not include FastAPI.

Includes support for:
- Either SQLite or PostgreSQL
- Pre-commit

## About this fork

This is a fork of
[Andrew-Chen-Wang/fastapi-django-orm](https://github.com/Andrew-Chen-Wang/fastapi-django-orm),
which has had no updates since January 2023. This fork brings it up to date
and fills in the gaps that matter when building a real project on it.

### What has changed

- **Startup bug fixed.** `python main.py run` failed with
  `AppRegistryNotReady` because `app/main.py` imported the models before
  calling `django.setup()`. The tests never caught it because pytest-django
  sets Django up first.
- **Dependencies updated** to current releases: Django 6.1, FastAPI 0.143
  (Pydantic 2), uvicorn 0.54, httpx 0.28, pytest 9, pytest-asyncio 1.4, and
  so on. The optional Postgres driver is now psycopg 3 instead of psycopg2.
- **Test client updated** for httpx 0.28, which removed `AsyncClient(app=...)`
  in favor of `AsyncClient(transport=ASGITransport(app=...))`.

### Improvements

- **Database connection management** ([`app/db.py`](./app/db.py)).
  FastAPI routes don't go through Django's request handling, so in the
  original template:
  - every async ORM call in the whole process ran on one shared thread, one
    query at a time, over one connection;
  - connections were never closed or health-checked, so a database restart
    or dropped connection broke the app until it was restarted.

  `DjangoDBMiddleware` now does for each FastAPI request what Django's own
  ASGI handler does: the request gets its own ORM thread, and Django's
  `request_started`/`request_finished` signals run around it, which closes
  stale connections. Measured against PostgreSQL: 10 concurrent requests now
  use 10 ORM threads instead of 1, and after a burst of 200 concurrent
  requests no connections are left open.
- **Environment-driven settings** ([`config/settings/`](./config/settings)).
  `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` and `DATABASE_URL` come from the
  environment or a `.env` file, using `django-environ` (installed but unused
  before). `production` settings refuse to start without `SECRET_KEY` and
  `ALLOWED_HOSTS`. `manage.py` now uses the `local` settings, matching the
  server.
- **Working Django mount and admin.** The Django app mounted at `/d` crashed
  on every request because there was no URLconf. It now serves the Django
  admin at `/d/admin/` (sessions, CSRF and login all work under the `/d`
  prefix), with the admin's static files served by FastAPI. The sample
  `User` model is registered in the admin.
- **Pydantic schema example.** A `/users` API
  ([`app/core/api/users.py`](./app/core/api/users.py),
  [`app/core/schemas.py`](./app/core/schemas.py)) shows the glue most
  projects need: validating input with a Pydantic model and returning Django
  model instances through a `from_attributes` response model.
- **Tests.** 12 tests (up from 2) covering the middleware's threading and
  cleanup, the `/users` API and an admin login. They pass on both SQLite and
  PostgreSQL.
- **Tooling.**
  - `--settings` only offers `local` and `production` (`staging` was
    accepted but didn't exist), and uvicorn no longer warns about reload
    options when `--reload` is off.
  - mypy runs clean with the django-stubs plugin configured.
  - Pre-commit hooks updated to current versions. `lines_after_imports` was
    removed from the isort config because it fought with current black.
  - CI uses Python 3.12 and current actions, runs the tests against
    PostgreSQL 17 (it previously started Postgres and Redis containers it
    never used) and runs mypy.

### Usage

To get started, run:

```bash
pip install -r requirements/local.txt
python manage.py migrate
```

To run tests, run `pytest tests/`

To run the application:

```bash
python main.py run --reload --settings=local --log-level=debug
```

You can test FastAPI with our default view by going to http://127.0.0.1:5000/hello.
The API docs are at http://127.0.0.1:5000/docs.

To use the Django admin, create a user with `python manage.py createsuperuser`
and go to http://127.0.0.1:5000/d/admin/

To run management commands such as `makemigrations` and `migrate`:

```bash
python manage.py makemigrations core && python manage.py migrate
```

You can still run a script by adding a click command in [`main.py`](./main.py)

#### Configuration

Settings are read from environment variables, or from a `.env` file in the
project root:

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite:///db.sqlite3` | e.g. `postgres://user:password@localhost:5432/dbname` (needs `pip install "psycopg[binary]"`) |
| `SECRET_KEY` | insecure placeholder | Required with `--settings=production` |
| `DEBUG` | `True` locally, `False` in production | |
| `ALLOWED_HOSTS` | empty | Comma-separated. Required with `--settings=production` |

#### Using the ORM from FastAPI routes

- In `async def` routes, use the async ORM API: `acreate`, `aget`,
  `acount`, `async for` over querysets, and so on. Calling the sync API
  (`create`, `get`, ...) there raises `SynchronousOnlyOperation`.
- For sync code that can't easily be made async (e.g. a function making
  several ORM calls or using `transaction.atomic`), wrap it with
  `asgiref.sync.sync_to_async` and await it from an `async def` route. It
  then runs on the request's ORM thread and gets the same connection cleanup.
- Avoid ORM calls in plain `def` routes. FastAPI runs those on its own
  threadpool, outside the middleware's per-request thread, so their
  connections are never cleaned up.

### Credit and License

This repository is based on the repository
by [@dancaron](https://github.com/dancaron/Django-ORM)
and reuses much of the code from https://github.com/Andrew-Chen-Wang/django-orm-template.

This repository is a quick template repository that I personally use.

This repository is licensed under the Apache 2.0 license
which can be found in the [LICENSE](./LICENSE) file.
