from app.models.search import Search, Condition
from app.services.database import (
    save_search,
    get_saved_searches,
    delete_search,
    search_exists,
)


def show_searches():
    searches = get_saved_searches()

    if not searches:
        print("\nNo saved searches yet. ♡")
        return

    print("\n♡ Saved Searches\n")

    for search in searches:
        max_price = (
            f"${search.max_price:,.2f}"
            if search.max_price is not None
            else "No limit"
        )

        print(
            f"{search.id}. "
            f"{search.query} • "
            f"{max_price} • "
            f"{search.condition.value.upper()}"
        )


def add_search():
    print("\n♡ Add Search\n")

    query = input("Query: ").strip()

    if not query:
        print("✕ Query cannot be empty.")
        return

    max_price_input = input(
        "Max price (leave blank for no limit): "
    ).strip()

    if max_price_input:
        try:
            max_price = float(max_price_input)

            if max_price < 0:
                print("✕ Max price cannot be negative.")
                return

        except ValueError:
            print("✕ Please enter a valid price.")
            return
    else:
        max_price = None

    print("\nCondition:")
    print("1. Any")
    print("2. New")
    print("3. Used")

    condition_choice = input("Choose: ").strip()

    conditions = {
        "1": Condition.ANY,
        "2": Condition.NEW,
        "3": Condition.USED,
    }

    condition = conditions.get(condition_choice)

    if condition is None:
        print("✕ Invalid condition.")
        return

    search = Search(
        id=None,
        query=query,
        max_price=max_price,
        condition=condition,
    )

    if search_exists(search):
        print("\n✕ That search already exists.")
        return

    save_search(search)

    print("\n♡ Search saved!")


def remove_search():
    searches = get_saved_searches()

    if not searches:
        print("\nNo saved searches to delete. ♡")
        return

    show_searches()

    search_id = input(
        "\nEnter the search ID to delete: "
    ).strip()

    try:
        search_id = int(search_id)
    except ValueError:
        print("✕ Please enter a valid ID.")
        return

    if not any(search.id == search_id for search in searches):
        print("✕ Search not found.")
        return

    delete_search(search_id)

    print("\n♡ Search deleted.")


def main():
    while True:
        print(
            """
♡ Vintage Hunter

1. Add search
2. View searches
3. Delete search
4. Exit
"""
        )

        choice = input("Choose: ").strip()

        if choice == "1":
            add_search()

        elif choice == "2":
            show_searches()

        elif choice == "3":
            remove_search()

        elif choice == "4":
            print("\n♡ Goodbye!")
            break

        else:
            print("\n✕ Invalid option.")


if __name__ == "__main__":
    main()