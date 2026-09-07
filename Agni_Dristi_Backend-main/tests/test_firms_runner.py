from app.services.firms.firms_runner_service import run_firms_monitoring


result = run_firms_monitoring(day_range=1)

print(result)