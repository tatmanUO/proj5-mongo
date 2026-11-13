# Project 5 – Brevet Calculator with AJAX and MongoDB

**Author:** Andy Tatman  
**Repository:** https://github.com/tatmanUO/proj5-mongo

## Overview

This project builds on the Project 4 brevet calculator. The original application calculates opening and closing times for ACP brevet controls using Flask and JavaScript. Project 5 adds MongoDB so the calculated control times can be saved and viewed later.

You pick a brevet distance, set the start date and time, and enter control distances in miles or kilometers. The times update through AJAX without reloading the page. Once the controls have been calculated, **Submit** saves them to MongoDB and **Display** opens a separate page showing saved controls.

## ACP control-time rules

The calculations follow the RUSA explanation of the ACP rules: https://rusa.org/octime_alg.html.

Opening times use maximum speeds and closing times use minimum speeds. The speed limits change as the distance increases:

| Distance interval | Minimum speed (km/h) | Maximum speed (km/h) |
| --- | ---: | ---: |
| 0–200 km | 15 | 34 |
| 200–400 km | 15 | 32 |
| 400–600 km | 15 | 30 |
| 600–1000 km | 11.428 | 28 |
| 1000–1300 km | 13.333 | 26 |

These are **piecewise calculations**. For example, a control at 350 km uses 200 km at 34 km/h and another 150 km at 32 km/h when calculating the opening time. You cannot divide the whole distance by one speed.

There are also some special cases:

- The start control closes one hour after the start.
- Controls in the first 60 km use the special closing-time rule: one hour plus the control distance divided by 20 km/h.
- Finish controls use fixed time limits: **13.5 hours** for 200 km, **20 hours** for 300 km, **27 hours** for 400 km, **40 hours** for 600 km, and **75 hours** for 1000 km.
- If a control is beyond the official brevet distance, the calculation uses the brevet distance instead.
- Distances entered in miles are converted to kilometers and truncated; calculated times are rounded to the nearest minute.

The implementation is in `acp_times.py`, with boundary and special-case tests in `test_acp_times.py`.

## How it works

When you enter a control distance, JavaScript converts miles to kilometers if needed and sends an AJAX request to Flask. Flask calls the functions in `acp_times.py`, returns opening and closing times as JSON, and JavaScript fills in the appropriate row. Changing the start time or brevet distance recalculates the control times.

Project 5 adds two buttons:

- **Submit:** Sends the calculated control entries to Flask, which validates the request and inserts the controls into MongoDB. Submitting no controls returns an error instead of saving an empty list.
- **Display:** Opens a new page where Flask retrieves saved controls from MongoDB and displays them in a table.

The application also handles invalid requests and database errors. MongoDB runs in a separate Docker container, and a named Docker volume preserves saved data across normal container restarts.

## Running the project

Install Docker and Docker Compose. From the `DockerMongo2` directory, build and start the application:

```bash
docker compose up -d --build
```

Then open **http://localhost:5001**. Docker maps port 5001 on the computer to port 5000 in the Flask container.

To see application logs:

```bash
docker compose logs -f web
```

To stop the application:

```bash
docker compose down
```

The MongoDB volume remains intact with `docker compose down`. Using `docker compose down -v` also removes the database volume and deletes saved data.

### Configuration

The assignment requires a `credentials.ini` file containing the author's name and repository URL in the `[DEFAULT]` section. The Flask application also reads its port and development secret key from this file:

```ini
[DEFAULT]
author = Andy Tatman
repo = https://github.com/tatmanUO/proj5-mongo
PORT = 5000
SECRET_KEY = cs322-project5
```

The example secret key is for local coursework only, not a public deployment. **Include `credentials.ini` in the submission**, as required by the Project 5 instructions.

## Testing

Project 4 included 15 tests for the ACP calculations, including speed boundaries, the first-60-km rule, finish limits, and controls beyond the brevet distance. Project 5 adds 12 tests covering Flask routes, valid and invalid submissions, database error handling, and displaying saved controls. The database operations in these tests are mocked so the tests do not alter saved controls.

Run all tests inside the web container:

```bash
docker compose exec web python -m pytest -v test_acp_times.py test_mongodb.py
```

**Latest test result (November 13, 2026): 27 passed, 0 failed.**

I also manually checked that controls could be submitted, displayed, and retained after restarting Docker.

## Main files

| File | Purpose |
| --- | --- |
| `acp_times.py` | ACP opening and closing time calculations |
| `flask_brevets.py` | Flask routes for AJAX, Submit, and Display |
| `config.py` | Application configuration |
| `templates/calc.html` | Calculator page and frontend AJAX |
| `templates/display.html` | Page showing saved MongoDB controls |
| `test_acp_times.py` | 15 calculation tests |
| `test_mongodb.py` | 12 Flask and MongoDB tests |
| `Dockerfile` | Builds the Flask application container |
| `docker-compose.yml` | Runs Flask and MongoDB together |
| `requirements.txt` | Python dependencies, including pytest |
| `credentials.ini` | Required author/repository metadata and local configuration |

