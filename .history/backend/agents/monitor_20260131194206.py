import pandas as pd
import os

def monitor_churn_risks(threshold=0.7):
    """Scan users and filter those above the churn risk threshold."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'jazz_users.csv')
    log_path = os.path.join(base_dir, 'data', 'action_logs.csv')
    
    try:
        if not os.path.exists(data_path):
            print(f"File not found: {data_path}")
            return []
            
        df = pd.read_csv(data_path)
        # Filter users above threshold
        risky_users = df[df['churn_risk_score'] >= threshold].copy()

        # SMART MEMORY: Exclude users who already received an offer
        if os.path.exists(log_path):
            logs = pd.read_csv(log_path)
            processed_ids = logs['user_id'].unique()
            risky_users = risky_users[~risky_users['user_id'].isin(processed_ids)]

        return risky_users.sort_values(by='churn_risk_score', ascending=False).to_dict(orient='records')
    except Exception as e:
        print(f"Monitor Agent Error: {e}")
        return []
