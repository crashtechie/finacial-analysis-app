# Dev Container Guide

This project includes a fully configured [dev container](https://containers.dev/) that provides a consistent, reproducible development environment with Python 3.14, Node.js 20.x, and all required tooling pre-installed.

## What's Included

- Python 3.14 with `uv` package manager
- Node.js 20.x LTS
- SQLite3, Git, and build tools
- Automatic dependency installation (Python via `uv sync`, frontend via `npm install`)
- Django migrations and fixture loading
- Forwarded ports: `8000` (Django API), `5173` (Vite frontend)

---

## Using the Dev Container with VS Code

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [VS Code](https://code.visualstudio.com/) installed
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) installed (`ms-vscode-remote.remote-containers`)

### Steps

1. Open the project folder in VS Code.
2. VS Code should detect the `.devcontainer/` folder and show a prompt:
   > "Folder contains a Dev Container configuration file. Reopen folder to develop in a container?"

   Click **Reopen in Container**.

   If the prompt doesn't appear, open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) and run:
   ```
   Dev Containers: Reopen in Container
   ```
3. VS Code will build the Docker image (first time takes a few minutes) and run the `postCreateCommand` script, which:
   - Installs Python dependencies via `uv sync --extra dev`
   - Runs Django migrations and loads fixtures
   - Installs frontend npm packages
4. Once the container is ready, you'll have a fully configured workspace with all extensions, linters, and formatters pre-installed.

### Running the App (inside the container terminal)

**Backend:**
```bash
source .venv/bin/activate
cd app/backend
python manage.py runserver
# API at http://127.0.0.1:8000/api/
```

**Frontend:**
```bash
cd app/frontend
npm run dev
# App at http://localhost:5173
```

Ports 8000 and 5173 are automatically forwarded to your host machine.

---

## Using the Dev Container Without VS Code

You can use the dev container with any editor or workflow using the [Dev Container CLI](https://github.com/devcontainers/cli) or plain Docker.

### Option 1: Dev Container CLI

The Dev Container CLI lets you build and run dev containers from any terminal.

#### Install the CLI

```bash
npm install -g @devcontainers/cli
```

#### Build and start the container

From the project root:

```bash
devcontainer up --workspace-folder .
```

#### Open a shell inside the container

```bash
devcontainer exec --workspace-folder . bash
```

From there you can run the backend and frontend as described above.

### Option 2: Docker / Docker Compose (manual)

If you prefer not to install the Dev Container CLI, you can build and run the container directly with Docker.

#### Build the image

```bash
docker build -t financial-analysis-devcontainer -f .devcontainer/Dockerfile .
```

#### Run the container

```bash
docker run -it --rm \
  -v "$(pwd)":/workspace \
  -p 8000:8000 \
  -p 5173:5173 \
  -w /workspace \
  -u vscode \
  financial-analysis-devcontainer \
  bash
```

#### Run the post-create setup manually

Once inside the container:

```bash
bash .devcontainer/postCreateCommand.sh
```

This installs all dependencies, runs migrations, and loads fixtures — the same setup that happens automatically in VS Code.

#### Start developing

```bash
# Backend
source .venv/bin/activate
cd app/backend && python manage.py runserver 0.0.0.0:8000

# Frontend (in a second terminal / tmux pane)
cd app/frontend && npm run dev -- --host
```

> **Note:** When running manually with Docker, use `0.0.0.0` as the bind address so the forwarded ports are accessible from your host machine.

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Container build fails | Make sure Docker Desktop is running and has enough resources (4 GB+ RAM recommended) |
| `uv` not found | The `postCreateCommand.sh` script adds `$HOME/.cargo/bin` to PATH. If running manually, run `export PATH="$HOME/.cargo/bin:$PATH"` first |
| Ports not accessible from host | When using plain Docker, bind to `0.0.0.0` instead of `127.0.0.1` |
| Slow first build | The initial image build downloads Python 3.14, Node.js, and system packages. Subsequent starts reuse the cached image |
| Migrations fail | This is expected if the Django app hasn't been fully set up yet. The script handles this gracefully and continues |
