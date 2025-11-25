# Local Development Setup Guide

Since you are running the project locally without Docker, you need to set up the database services (Neo4j and Redis) manually.

## 1. Neo4j Graph Database Setup

The easiest way to run Neo4j on Windows is using **Neo4j Desktop**.

1.  **Download & Install**:
    *   Go to [Neo4j Download Center](https://neo4j.com/download-center/#desktop).
    *   Download **Neo4j Desktop** and install it.

2.  **Create a Database**:
    *   Open Neo4j Desktop.
    *   Click **"New Project"**.
    *   Click **"Add"** -> **"Local DBMS"**.
    *   Set the password to `password` (to match your `.env` file).
    *   Click **"Create"**.

3.  **Start the Database**:
    *   Hover over your new DBMS and click **"Start"**.
    *   Wait for it to show "Active".
    *   It should be running at `bolt://localhost:7687`.

4.  **Verify**:
    *   Click **"Open"** to open the Neo4j Browser.
    *   You should be able to log in with username `neo4j` and password `password`.

## 2. Redis Setup

Redis does not officially support Windows, but there are good alternatives.

### Option A: Memurai (Recommended for Native Windows)
Memurai is a Redis-compatible cache and datastore for Windows.

1.  **Download**:
    *   Go to [Memurai Developer Edition](https://www.memurai.com/get-memurai).
    *   Download and install the Developer Edition (free for development).

2.  **Run**:
    *   It usually runs automatically as a Windows Service after installation.
    *   You can verify it by opening a command prompt and typing `memurai-cli`.

### Option B: Redis on WSL2 (Windows Subsystem for Linux)
If you have WSL2 installed (Ubuntu on Windows):

1.  Open your Ubuntu terminal.
2.  Run:
    ```bash
    sudo apt-get update
    sudo apt-get install redis-server
    sudo service redis-server start
    ```

## 3. Update Configuration (If needed)

If you chose different passwords or ports, update the `backend/.env` file:

```dotenv
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_new_password
REDIS_URL=redis://localhost:6379
```
