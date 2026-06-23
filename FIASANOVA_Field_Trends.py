from pytrends.request import TrendReq
import pandas as pd
import time
from datetime import datetime, timezone
import os

# Node categories per your Boolean logic
NODES = {
    "Bloodline": ["Rothschild", "Rockefeller", "Orsini"],
    "Freemasons": ["Freemason", "Masonic Lodge"],
    "CIA": ["CIA covert", "CIA operation"],
    "Israel": ["Israel policy", "Mossad"]
}

# Control baseline for normalization
CONTROL = ["climate change", "global economy"]

def fetch_trends(node_name, keywords, timeframe="today 3-m"):
    """Fetch weekly interest for a node and calculate sentiment volatility."""
    pytrend = TrendReq(hl='en-US', tz=360)
    try:
        kw_list = keywords + CONTROL
        pytrend.build_payload(kw_list=kw_list, cat=0, timeframe=timeframe, geo='US')
        data = pytrend.interest_over_time()
        if data.empty:
            return None
        # Drop the 'isPartial' column and fill NAs
        if 'isPartial' in data.columns:
            data = data.drop(columns=['isPartial']).fillna(0)
        else:
            data = data.fillna(0)

        node_avg = data[keywords].mean(axis=1).mean()
        control_avg = data[CONTROL].mean(axis=1).mean()
        volatility = data[keywords].std(axis=1).mean() / (node_avg + 0.01)
        return {
            "node_avg": float(node_avg),
            "control_avg": float(control_avg),
            "volatility": float(volatility)
        }
    except Exception as e:
        return {"error": str(e)}

def append_report_row(path, row):
    df = pd.DataFrame([row])
    header = not os.path.exists(path)
    df.to_csv(path, mode='a', index=False, header=header)

def main(out_csv='fiasanova_trends_report.csv'):
    report = []
    for name, kw in NODES.items():
        res = fetch_trends(name, kw)
        ts = datetime.now(timezone.utc).isoformat()
        row = {
            'node': name,
            'node_avg': None,
            'control_avg': None,
            'volatility': None,
            'timestamp_utc': ts
        }
        if res is None:
            row.update({'error': 'no-data'})
        elif 'error' in res:
            row.update({'error': res['error']})
        else:
            row.update(res)

        append_report_row(out_csv, row)
        report.append(row)
        time.sleep(3)  # Respect rate limits

    print(report)

if __name__ == '__main__':
    main()
