# Oromia Bank Pension Payment System (Streamlit)

Run locally:
    pip install -r requirements.txt
    streamlit run app.py

Demo logins: Pensioner P0001 / 1234. Staff: officer, maker, checker, fraud, admin / 1234.
Flow to demo: login as `maker` -> Payroll -> Prepare batch; sign out; login as `checker` -> Approve.

Deploy (Streamlit Community Cloud, free):
1. Create a GitHub repo and push this folder (app.py, requirements.txt, assets/, .streamlit/).
2. Go to share.streamlit.io -> sign in with GitHub -> New app.
3. Choose repo, branch main, main file app.py -> Deploy.
Note: SQLite data resets when the app restarts. Use PostgreSQL for permanent storage.
