def calculate_bmr(weight, height, age, gender):
    """
    weight in kg
    height in cm
    age in years
    """
    if gender == "Male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    return bmr

def calculate_tdee(bmr, activity_level):
    activity_multiplier = {
        "Sedentary": 1.2,
        "Light": 1.375,
        "Moderate": 1.55,
        "Active": 1.725
    }

    return bmr * activity_multiplier[activity_level]

def adjust_calories_for_goal(tdee, goal):
    if goal == "Weight Loss":
        return tdee - 500
    elif goal == "Muscle Gain":
        return tdee + 300
    else:  # Maintenance
        return tdee


# test the function
if __name__ == "__main__":
    bmr = calculate_bmr(
        weight=53,
        height=160,
        age=20,
        gender="Female"
    )

    tdee = calculate_tdee(bmr, "Light")

    final_calories = adjust_calories_for_goal(tdee, "Weight Loss")

    print("BMR:", round(bmr, 2))
    print("TDEE:", round(tdee, 2))
    print("Final Daily Calories:", round(final_calories, 2))
    
def calculate_bmi(weight, height):
    """
    weight in kg
    height in cm
    """
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return bmi


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight", "You may benefit from healthy weight gain."
    elif bmi < 25:
        return "Normal", "You seem fit. Maintenance is a good option."
    elif bmi < 30:
        return "Overweight", "Weight loss could be beneficial."
    else:
        return "Obese", "Consulting a professional is recommended."

