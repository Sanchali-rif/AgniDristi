from app.services.firms.firms_api_service import fetch_latest_firms


df = fetch_latest_firms(day_range=1)

print("Rows:", len(df))

print(df.head())

print("\nColumns:")
print(df.columns.tolist())