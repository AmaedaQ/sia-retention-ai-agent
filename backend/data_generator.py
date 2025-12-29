import pandas as pd
import numpy as np
import os

def generate_jazz_data():
    np.random.seed(42) 
    n_users = 1000
    
    data = {
        'user_id': [f"JAZZ_{i:04d}" for i in range(n_users)],
        'avg_monthly_spend': np.random.uniform(200, 5000, n_users).round(2),
        'data_usage_gb': np.random.uniform(0, 50, n_users).round(2),
        'days_since_last_recharge': np.random.randint(0, 45, n_users),
        'signal_strength_score': np.random.uniform(0.1, 1.0, n_users).round(2),
        'active_plan': np.random.choice(['Weekly Mega', 'Monthly Super', 'Daily Social'], n_users),
        'support_tickets_open': np.random.randint(0, 3, n_users)
    }

    df = pd.DataFrame(data)
    df['churn_risk_score'] = ((df['days_since_last_recharge'] / 45) * 0.4 + (1 - df['signal_strength_score']) * 0.4 + (df['support_tickets_open'] * 0.2)).round(2)

    # --- THE FIX: PROFESSIONAL PATHING ---
    # This finds the folder where THIS script lives
    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    data_dir = os.path.join(base_dir, 'data')
    
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, 'jazz_users.csv')
    
    df.to_csv(file_path, index=False)
    print(f"✅ SUCCESS! Data saved at: {file_path}")

if __name__ == "__main__":
    generate_jazz_data()