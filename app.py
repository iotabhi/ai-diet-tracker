import streamlit as st
import pandas as pd

from calorie_logic import (
    calculate_bmr,
    calculate_tdee,
    adjust_calories_for_goal,
    calculate_bmi,
    bmi_category
)

from daily_log import add_food, calculate_totals, daily_log,reset_day


# -------------------- PAGE SETUP --------------------
st.set_page_config(page_title="Indian Diet Tracker", layout="centered")
st.title("🥗 Indian Diet & Calorie Tracker")


# -------------------- LOAD FOOD DATA --------------------
food_df = pd.read_csv("clean_food_data.csv")
food_names = sorted(food_df["Dish Name"].unique())


# -------------------- USER DETAILS --------------------
st.header("👤 Your Details")

age = st.number_input("Age", min_value=10, max_value=100, step=1)
gender = st.selectbox("Gender", ["Male", "Female"])
weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, step=0.1)
height = st.number_input("Height (cm)", min_value=120.0, max_value=250.0, step=0.1)

activity = st.selectbox(
    "Activity Level",
    ["Sedentary", "Light", "Moderate", "Active"]
)

goal = st.selectbox(
    "Goal",
    ["Weight Loss", "Maintenance", "Muscle Gain"]
)


# -------------------- CALCULATE CALORIES --------------------
if st.button("Calculate My Daily Calories"):
    # BMI
    bmi = calculate_bmi(weight, height)
    category, message = bmi_category(bmi)

    st.subheader("📊 BMI Analysis")
    st.write(f"**Your BMI:** {round(bmi, 2)}")
    st.write(f"**Category:** {category}")
    st.info(message)

    # Calories
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity)

    st.session_state.final_calories = adjust_calories_for_goal(tdee, goal)

    st.subheader("🎯 Daily Calorie Target")
    st.write(f"**BMR:** {round(bmr, 2)} kcal")
    st.write(f"**TDEE:** {round(tdee, 2)} kcal")
    st.write(f"**Final Target:** {round(st.session_state.final_calories, 2)} kcal")


# -------------------- FOOD LOGGING --------------------
st.divider()
st.header("🍛 Log Your Food")

dish = st.selectbox("Select Dish", food_names)
quantity = st.number_input("Quantity (servings)", min_value=1, step=1)

if st.button("Add Food"):
    add_food(dish, quantity)
    st.success(f"Added {quantity} × {dish}")

st.divider()


# -------------------- DAILY LOG & TOTALS --------------------
if daily_log and "final_calories" in st.session_state:
    st.subheader("📋 Today's Food Log")
    log_df = pd.DataFrame(daily_log)
    st.dataframe(log_df)

    totals = calculate_totals()

    st.subheader("📊 Daily Totals")
    st.write(f"Calories Consumed: {round(totals['Calories'], 2)} kcal")
    st.write(f"Protein: {round(totals['Protein'], 2)} g")
    st.write(f"Carbs: {round(totals['Carbs'], 2)} g")
    st.write(f"Fats: {round(totals['Fats'], 2)} g")

    remaining = st.session_state.final_calories - totals["Calories"]

    st.subheader("🔥 Remaining Calories")
    if remaining > 0:
        st.success(f"You can still eat **{round(remaining, 2)} kcal** today 🎯")
    else:
        st.warning(f"You exceeded your limit by **{round(abs(remaining), 2)} kcal** ⚠️")


if st.button("🔁 Reset Day"):
    reset_day()
    st.success("New day started! Food log cleared ✅")
