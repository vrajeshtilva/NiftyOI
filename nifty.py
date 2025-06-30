import requests
import pandas as pd
import time

def fetch_nifty_option_chain():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/option-chain",
        "Connection": "keep-alive"
    }

    session = requests.Session()

    # Step 1: Fetch cookies by accessing home page
    try:
        home = session.get("https://www.nseindia.com", headers=headers, timeout=5)
        time.sleep(1.5)  # Delay to mimic real user
    except Exception as e:
        raise Exception(f"Failed to fetch NSE homepage: {e}")

    # Step 2: Make the API call
    try:
        response = session.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "json" not in content_type.lower():
            raise ValueError("NSE did not return JSON. You might be blocked.")
        data = response.json()
    except Exception as e:
        print("🔴 NSE API returned unexpected response.")
        print("🔍 First 300 characters:\n", response.text[:300])
        raise e

    # Step 3: Parse the Option Chain
    records = data['records']['data']
    underlying_price = data['records']['underlyingValue']

    rows = []
    for item in records:
        strike = item['strikePrice']
        ce_oi = item.get('CE', {}).get('openInterest', 0)
        pe_oi = item.get('PE', {}).get('openInterest', 0)
        rows.append([strike, ce_oi, pe_oi])

    df = pd.DataFrame(rows, columns=["Strike", "Call OI", "Put OI"])
    df = df.sort_values("Strike").reset_index(drop=True)

    return df, underlying_price

if __name__ == "__main__":
    df, spot = fetch_nifty_option_chain()
    print(f"\n📍 Spot Price: {spot}")
    print(df.head())
