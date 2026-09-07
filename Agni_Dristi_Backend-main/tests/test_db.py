from sqlalchemy import text
from app.core.database import engine


try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        print(result.scalar())
        print("NeonDB connected successfully")

except Exception as e:
    print("Database connection failed")
    print(e)