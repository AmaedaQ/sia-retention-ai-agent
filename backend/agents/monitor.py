import pandas as pd
import os

def monitor_churn_risks(threshold=0.7):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, '..', 'data', 'jazz_users.csv')
    log_path = os.path.join(base_dir, '..', 'data', 'action_logs.csv')
    
    try:
        df = pd.read_csv(data_path)
        risky_users = df[df['churn_risk_score'] >= threshold].copy()

        # --- SMART MEMORY ---
        # Un logon ko nikaal do jinhe pehle hi action kiya ja chuka hai
        if os.path.exists(log_path):
            logs = pd.read_csv(log_path)
            processed_ids = logs['user_id'].unique()
            risky_users = risky_users[~risky_users['user_id'].isin(processed_ids)]
        # --------------------

        risky_users = risky_users.sort_values(by='churn_risk_score', ascending=False)
        return risky_users.to_dict(orient='records')
    except Exception as e:
        print(f"❌ Error in monitor: {e}")
        return []