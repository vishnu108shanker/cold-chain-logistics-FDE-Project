# Phase 0

## Connecting to PostgreSQL

Start PostgreSQL and the Adminer database UI from the project directory:

```
docker compose up -d postgres adminer
```

Open http://localhost:8080 and sign in with:

| Field | Value |
| --- | --- |
| System | PostgreSQL |
| Server | `postgres` |
| Username | `me` |
| Password | The `POSTGRES_PASSWORD` value from your `.env` file |
| Database | `cold-chain-postgres` |

Adminer runs in the same Compose network as PostgreSQL, so use the service name
`postgres` and the container port `5432` in Adminer. For a database client
running directly on your computer, connect to `localhost:5433` instead.
Adminer is bound to localhost and is not exposed to other machines on your network.

## Ingesting data

- Download the dataset from 'data\source\data.txt'
- Create an EC2 instance > docker container > mcr.microsoft.com/mssql/server:2022-latest
- Spin up the Legacy MSSQL Server
```
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=FdeEnterprisePass123!" -p 1433:1433 --name legacy-mssql -d mcr.microsoft.com/mssql/server:2022-latest

# or multi-line in windows 
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=FdeEnterprisePass123!" ^
   -p 1433:1433 --name legacy-mssql ^
   -d mcr.microsoft.com/mssql/server:2022-latest

# or multi-line unix
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=FdeEnterprisePass123!" \
   -p 1433:1433 --name legacy-mssql \
   -d mcr.microsoft.com/mssql/server:2022-latest

# or multi-line with volume inside EC2
docker run -v mssql_data:/var/opt/mssql \
  -e "ACCEPT_EULA=Y" \
  -e "MSSQL_SA_PASSWORD=FdeEnterprisePass123!" \
  -p 1433:1433 \
  --name legacy-mssql \
  -d mcr.microsoft.com/mssql/server:2022-latest

```
- install the req > pip install -r requirements.txt

- python scripts\ingest_legacy_data.py

## Connecting to the data 

We need to query the database
- Download : https://github.com/microsoft/azuredatastudio
   - https://learn.microsoft.com/en-us/previous-versions/azure-data-studio/download-azure-data-studio?tabs=win-install%2Cwin-user-install%2Credhat-install%2Cwindows-uninstall%2Credhat-uninstall
- The recommendation is to use VS code extension : "SQL Server (mssql)" by microsoft
   - Click on icon that looks like server or refrigarator, not the one with cylinder 
   - Add connection
   - Fill the below :
   ```
   Profile Name: legacy-mssql
   Server name*: localhost
   Port: 1433
   Trust server certificate: 🟩 Check this box / turn it ON (Crucial for Docker)
   Authentication type*: SQL Login
   User name*: sa
   Password*: FdeEnterprisePass123!
   Save Password: 🟩 Check this box
   Database name: Type master (or leave it on "Select a database")
   Encrypt: ⚠️ Change this from Mandatory to Optional (or False)
   ```

- CTRL + N
- SQL
- SELECT COUNT(*) AS total_rows FROM dbo.TBL_SC_FLEET_HIST_RAW;

## PostgreSQL on an EC2 instance

This uses the project's `docker-compose.yml` to run PostgreSQL 17 with a
persistent Docker volume. The database port is bound to the EC2 instance's
loopback interface, so it is not directly exposed to the internet. Use an SSH
tunnel when connecting from your computer.

1. Create an Ubuntu EC2 instance and allow inbound SSH (TCP 22) only from your
   current public IP in its security group. Do not add an inbound rule for
   PostgreSQL (TCP 5433).
2. From PowerShell on your computer, SSH into the instance (replace the key
   path and public IP):

   ```
   ssh -i "C:\path\to\your-key.pem" ubuntu@EC2_PUBLIC_IP
   ```

3. On the EC2 instance, install Docker and Compose, then clone this repository:

   ```
   sudo apt update
   sudo apt install -y docker.io docker-compose-v2 git openssl
   sudo systemctl enable --now docker
   cd ~
   git clone https://github.com/vishnu108shanker/cold-chain-logistics-FDE-Project.git
   cd cold-chain-logistics-FDE-Project
   ```

   If you already cloned the repository, `cd` into that checkout and pull the
   version containing `docker-compose.yml` instead.

4. Create a private `.env` file with a new, randomly generated database password,
   then start the services:

   ```
   umask 077
   printf 'POSTGRES_PASSWORD=%s\n' "$(openssl rand -hex 32)" > .env
   sudo docker compose up -d postgres adminer
   sudo docker compose ps
   sudo docker compose exec postgres pg_isready -U me -d cold-chain-postgres
   ```

   Keep this `.env` file and password private. PostgreSQL data persists in the
   `postgres_data_new` Docker volume when containers are restarted or recreated.
   This password-generation step is for a fresh database volume: changing
   `POSTGRES_PASSWORD` in `.env` later does not change the password of a database
   that PostgreSQL has already initialized. Do not run `docker compose down -v`
   unless you intend to delete the database data.

5. To connect from your computer, keep the SSH session open and open a second
   PowerShell window. Forward the database and (optionally) Adminer ports:

   ```
   ssh -i "C:\path\to\your-key.pem" -N `
     -L 5433:127.0.0.1:5433 `
     -L 8080:127.0.0.1:8080 `
     ubuntu@EC2_PUBLIC_IP
   ```

   In your PostgreSQL client, use host `localhost`, port `5433`, database
   `cold-chain-postgres`, username `me`, and the password from the EC2 `.env`.
   To use Adminer, open http://localhost:8080 and connect with server `postgres`,
   username `me`, the same password, and database `cold-chain-postgres`.

   If the application runs in another container on this Compose network, connect
   it to host `postgres`, port `5432` instead of using the SSH tunnel.

This provisions an empty PostgreSQL database; it does not convert the existing
MSSQL ingestion scripts or MSSQL-specific SQL into PostgreSQL automatically.

# Phase 1

## SOP Ingestion

- https://app.pinecone.io/ > get api key
- Use it in .env
- run python scripts\ingest_sop_pinecone.py

# Phase 2

## Data Security

- Click on file : scripts\setup_security_and_view.sql
- VS-code will show you Start button directly on top else run like we were running the commands previously.
- Once done, create a new connection now with Agent-Profile
```
* Profile Name: agent-fde-ro
* Connection Group: Leave it on <Default>
* Input type: Select Parameters (Do not click "Load from Connection String", "Browse Azure", or "Browse Fabric")
* Server name*: localhost
* Port: 1433
* Trust server certificate: 🟩 Check this box / Turn it ON
* Authentication type*: SQL Login
* User name*: USR_FDE_RO
* Password*: AgentPassword2026!
* Save Password: 🟩 Check this box / Turn it ON
* Database name: Type master (or click "Select a database" and select master)
* Encrypt: Change this from Mandatory to Optional (or False)
```

Connect and test below commands :
```
-- TEST 1: This SHOULD work perfectly (Access to clean view)
SELECT TOP 5 * FROM FDE_VIEWS.VW_ACTIVE_FLEET;

-- TEST 2: This SHOULD fail instantly (Access to raw legacy table is DENIED)
SELECT TOP 5 * FROM dbo.TBL_SC_FLEET_HIST_RAW;
```

## Phase 3

run src\agent_tools.py
run src\orchestrator.py

Step-1 : Pass below in the dispatcher >
- Question-1 (The "Domino Effect" Test)
```
Find any active shipments near Los Angeles (Latitude ~33.8, Longitude ~-118.1). Check the local weather there, and tell me if the current cargo temperature violates the SOP for fresh perishables.
```

- Question-2 (The "Restraint" Test (No-Tool Routing))
```
I'm a new dispatcher on the night shift. Can you quickly explain the difference between a Tier 1 and Tier 2 escalation?
```


## Phase 4
Go to VS-code > CTRL + N > 'click on plain-text' and use 'sql'

Select the su user and write below :

CREATE TABLE FDE_VIEWS.AgentAuditLog (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    Timestamp DATETIME DEFAULT GETDATE(),
    SessionID VARCHAR(50),
    NodeExecuted VARCHAR(50),
    ToolName VARCHAR(100),
    Content NVARCHAR(MAX) -- NVARCHAR to safely handle JSON strings and large LLM outputs
);

-- Grant the agent user permission to write only to this specific table
```
GRANT INSERT ON FDE_VIEWS.AgentAuditLog TO USR_FDE_RO;
```

## Phase 5
streamlit run src\ui.py

## Phase 6
- Deployment
```
sudo apt update && sudo apt install -y python3-pip python3-venv git
cd /home/ubuntu
git clone https://github.com/nimowhyca/cold-chain-logistics-FDE-Project.git
cd cold-chain-logistics-FDE-Project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run src/ui.py
```

1. Add the Microsoft GPG repository key
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

2. Add the Microsoft SQL Server Ubuntu repository
curl -fsSL https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

3. Update apt and install the driver (Accepting the EULA)
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18

4. Install the unixODBC development headers
sudo apt-get install -y unixodbc-dev

5. Create the systemd service file
```
sudo nano /etc/systemd/system/streamlit.service
```

6. Paste the configuration
```
[Unit]
Description=Streamlit Cold-Chain Dispatch Console
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/cold-chain-logistics-FDE-Project
ExecStart=/home/ubuntu/cold-chain-logistics-FDE-Project/venv/bin/streamlit run src/ui.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

7. Register and start the service
```
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit
```