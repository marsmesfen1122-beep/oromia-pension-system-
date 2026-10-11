# Oromia Bank Pension Payment System (Streamlit + Supabase)

Database: Supabase (PostgreSQL). If no DATABASE_URL is set, the app falls back to a local
SQLite file (pension.db) so it still runs on any computer without setup.
The five tables are created and filled with 60 sample pensioners automatically on first run.

## Demo logins
Pensioner: P0001 / 1234. Staff: officer, maker, checker, fraud, admin / 1234.
Demo flow: login as `maker` -> Payroll -> Prepare batch; sign out; login as `checker` -> Approve.

## 1. Create the Supabase database (free)
1. Go to supabase.com -> sign in -> New project. Choose a name, a strong database password
   (save it) and the region closest to you.
2. When the project is ready, click Connect (top of the page) and copy the
   **Session pooler** connection string. Use the pooler string, not "Direct connection":
   Streamlit Cloud only supports IPv4 and the direct connection is IPv6-only.
3. Replace [YOUR-PASSWORD] in the string with your password.

## 2. Run locally
    pip install -r requirements.txt
    copy .streamlit/secrets.toml.example to .streamlit/secrets.toml and paste your string
    streamlit run app.py

## 3. Deploy on Streamlit Community Cloud
1. Push this folder to GitHub (secrets.toml and pension.db are git-ignored on purpose).
2. share.streamlit.io -> New app -> choose repo, branch main, file app.py.
3. Before deploying open Advanced settings -> Secrets and paste:
       DATABASE_URL = "postgresql://postgres.xxxx:PASSWORD@aws-0-xxx.pooler.supabase.com:5432/postgres"
4. Deploy. Data is now stored in Supabase and survives restarts.
   (Check it in Supabase -> Table Editor.)

## Troubleshooting
- "connection refused / could not translate host": you used the Direct connection string. Use the Session pooler.
- "password authentication failed": wrong password, or special characters not URL-encoded.
- Supabase free projects pause after about 7 days without activity: open the dashboard and click Restore.
