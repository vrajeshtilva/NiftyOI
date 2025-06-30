import requests
import pandas as pd

def fetch_nifty_option_chain():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Referer": "https://www.nseindia.com/option-chain"
    }

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)  # For cookies
    response = session.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        print(response.text)
        return None

    try:
        data = response.json()
    except Exception as e:
        print("Failed to parse JSON:", e)
        print("Response text:", response.text)
        return None

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

    atm_strike = min(df["Strike"], key=lambda x: abs(x - underlying_price))
    highest_call_oi = df.loc[df["Call OI"].idxmax()]
    highest_put_oi = df.loc[df["Put OI"].idxmax()]

    print(f"\n📍 NIFTY Spot Price: {underlying_price}")
    print(f"🎯 ATM Strike: {atm_strike}")
    print(f"🔺 Resistance (Highest Call OI): {highest_call_oi['Strike']} ({highest_call_oi['Call OI']})")
    print(f"🔻 Support (Highest Put OI): {highest_put_oi['Strike']} ({highest_put_oi['Put OI']})")

    return df

# Run
if __name__ == "__main__":
    df = fetch_nifty_option_chain()
    print("\n🔍 Top 10 Strikes by Call & Put OI:\n")
    print(df.sort_values("Call OI", ascending=False).head(5))
    print(df.sort_values("Put OI", ascending=False).head(5))
