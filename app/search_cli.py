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
        min_price = (
            f"${search.min_price:,.2f}"
            if search.min_price is not None
            else "No min"
        )

        max_price = (
            f"${search.max_price:,.2f}"
            if search.max_price is not None
            else "No max"
        )

        color = search.color if search.color is not None else "Any color"

        print(
            f"{search.id}. "
            f"{search.query} • "
            f"{min_price}–{max_price} • "
            f"{search.condition.value.upper()} • "
            f"{color}"
        )


def add_search():
    print("\n♡ Add Search\n")

    query = input("Query: ").strip()

    if not query:
        print("✕ Query cannot be empty.")
        return

    min_price_input = input(
        "Min price (leave blank for no minimum): "
    ).strip()

    if min_price_input:
        try:
            min_price = float(min_price_input)

            if min_price < 0:
                print("✕ Min price cannot be negative.")
                return

        except ValueError:
            print("✕ Please enter a valid price.")
            return
    else:
        min_price = None

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

    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        print("✕ Min price cannot be greater than max price.")
        return

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

    color = choose_color()

    search = Search(
        id=None,
        user_id=1,
        query=query,
        condition=condition,
        min_price=min_price,
        max_price=max_price,
        color=color,
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

def choose_color() -> str | None:
    print(
        """
Color:
1. Any
2. Black
3. White
4. Brown
5. Beige
6. Red
7. Blue
8. Pink
9. Green
10. Gray
11. Other
"""
    )

    choice = input("Choose: ")

    colors = {
        "1": None,
        "2": "Black",
        "3": "White",
        "4": "Brown",
        "5": "Beige",
        "6": "Red",
        "7": "Blue",
        "8": "Pink",
        "9": "Green",
        "10": "Gray",
    }

    if choice in colors:
        return colors[choice]

    if choice == "11":
        color = input("Enter color: ").strip()

        if color:
            return color

    print("✕ Invalid color.")
    return None


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