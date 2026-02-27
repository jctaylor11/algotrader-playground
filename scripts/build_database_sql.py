from sqlalchemy import text

from src.data.database import get_engine


def main(): 
    engine = get_engine()

    with engine.connect() as conn:
        print("Connected")
        test = conn.execute(text("SELECT * FROM testing_table"))
        test_contents = test.fetchall()

        print(test_contents)


if __name__ == "__main__":
    main()