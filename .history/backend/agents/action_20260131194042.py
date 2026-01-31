import datetime
import os
import pandas as pd

def execute_retention_action(report):
    """Log the approved retention offer into a CSV for tracking."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_file = os.path.join(base_dir, 'data', 'action_logs.csv')
    
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": report['user_id'],
        "offer_sent": report['offer'],
        "status": "SUCCESS_SENT"
    }
    
    try:
        df_log = pd.DataFrame([log_entry])
        # Create file with header if it doesn't exist, else append
        if not os.path.isfile(log_file):
            df_log.to_csv(log_file, index=False)
        else:
            df_log.to_csv(log_file, mode='a', header=False, index=False)
        return True
    except Exception as e:
        print(f"Action Agent Error: {e}")
        return False
