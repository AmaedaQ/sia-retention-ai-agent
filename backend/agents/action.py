import datetime
import os
import pandas as pd

def execute_retention_action(report):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(base_dir, '..', 'data')
    log_file = os.path.join(log_dir, 'action_logs.csv')
    
    # Create directory if not exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": report['user_id'],
        "offer_sent": report['offer'],
        "status": "SUCCESS_SENT"
    }
    
    df_log = pd.DataFrame([log_entry])
    
    try:
        if not os.path.isfile(log_file):
            df_log.to_csv(log_file, index=False)
        else:
            df_log.to_csv(log_file, mode='a', header=False, index=False)
        return True
    except Exception as e:
        print(f"❌ Critical Error in action.py: {e}")
        return False