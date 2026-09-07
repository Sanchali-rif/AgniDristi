from app.services.firms.firms_runner_service import (
    run_firms_monitoring
)


def main():
    result = run_firms_monitoring(
        day_range=1,
        trigger_type="SCHEDULED"
    )

    print(result)


if __name__ == "__main__":
    main()