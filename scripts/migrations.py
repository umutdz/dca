import inspect
import os
import sys


def initial_migration():
    """
    Make an initial migration
    command: python scripts/migrations.py initial
    """
    os.system("docker compose run --rm chat_assistant_app alembic -c /app/alembic.ini revision --autogenerate -m 'initial migration'")


def make_migration(message):
    """
    Make a new migration
    command: python scripts/migrations.py make <message>
    """
    os.system(f"docker compose run --rm chat_assistant_app alembic -c /app/alembic.ini revision --autogenerate -m '{message}'")


def upgrade_migrations():
    """
    Upgrade the migrations
    command: python scripts/migrations.py upgrade
    """
    os.system("docker compose run --rm chat_assistant_app alembic -c /app/alembic.ini upgrade head")


def downgrade_migrations():
    """
    Downgrade the migrations
    command: python scripts/migrations.py downgrade
    """
    os.system("docker compose run --rm chat_assistant_app alembic -c /app/alembic.ini downgrade -1")


def downgrade_zero():
    """
    Downgrade the migrations to the base
    command: python scripts/migrations.py downgrade-zero
    """
    os.system("docker compose run --rm chat_assistant_app alembic -c /app/alembic.ini downgrade base")


def show_migrations():
    """
    Show the migrations
    command: python scripts/migrations.py show
    """
    os.system("docker compose run --rm chat_assistant_app alembic -c /app/alembic.ini history")


def current_migrations():
    """
    Show the current migrations
    command: python scripts/migrations.py current
    """
    os.system("docker compose run --rm chat_assistant_app alembic -c /app/alembic.ini current")


def back_migration(migration_id):
    """
    Downgrade the migrations to a specific migration
    command: python scripts/migrations.py back <migration_id>
    """
    os.system(f"docker compose run --rm chat_assistant_app alembic -c /app/alembic.ini downgrade {migration_id}")


def forward_migration(migration_id):
    """
    Upgrade the migrations to a specific migration
    command: python scripts/migrations.py forward <migration_id>
    """
    os.system(f"docker compose run --rm chat_assistant_app alembic -c /app/alembic.ini upgrade {migration_id}")


def print_help():
    """
    Print help message with docstrings
    """
    print("Available commands:")
    print()

    # Get all functions in the current module
    functions = [f for f in globals().values() if inspect.isfunction(f) and f.__module__ == __name__]

    # Sort functions by name
    functions.sort(key=lambda x: x.__name__)

    # Print each function's name and docstring
    for func in functions:
        if func.__name__ != "print_help":
            if func.__doc__:
                print(func.__doc__.strip())
            print()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_help()
        sys.exit(1)
    command = sys.argv[1]

    match command:
        case "initial":
            initial_migration()
        case "make":
            make_migration(sys.argv[2])
        case "upgrade":
            upgrade_migrations()
        case "downgrade":
            downgrade_migrations()
        case "downgrade-zero":
            downgrade_zero()
        case "show":
            show_migrations()
        case "current":
            current_migrations()
        case "back":
            back_migration(sys.argv[2])
        case "forward":
            forward_migration(sys.argv[2])
        case _:
            print("Invalid command")
