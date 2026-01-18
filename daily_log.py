import pandas as pd

# load cleaned food data
df = pd.read_csv("clean_food_data.csv")

daily_log = []

def add_food(dish_name, quantity):
    food = df[df["Dish Name"].str.lower() == dish_name.lower()]

    if food.empty:
        print("Food not found")
        return

    food = food.iloc[0]

    entry = {
        "Dish Name": dish_name,
        "Quantity": quantity,
        "Calories": food["Calories (kcal)"] * quantity,
        "Protein": food["Protein (g)"] * quantity,
        "Carbs": food["Carbohydrates (g)"] * quantity,
        "Fats": food["Fats (g)"] * quantity
    }

    daily_log.append(entry)


def calculate_totals():
    totals = {
        "Calories": 0,
        "Protein": 0,
        "Carbs": 0,
        "Fats": 0
    }

    for item in daily_log:
        totals["Calories"] += item["Calories"]
        totals["Protein"] += item["Protein"]
        totals["Carbs"] += item["Carbs"]
        totals["Fats"] += item["Fats"]

    return totals


# test
if __name__ == "__main__":
    add_food("Plain Dosa", 2)
    add_food("Chapati", 3)

    totals = calculate_totals()

    print("Daily Log:")
    for item in daily_log:
        print(item)

    print("\nTotals:")
    print(totals)
    
def reset_day():
    daily_log.clear()
