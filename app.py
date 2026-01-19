import streamlit as st
import pandas as pd
from datetime import date
import os

from calorie_logic import (
    calculate_bmr,
    calculate_tdee,
    adjust_calories_for_goal,
    calculate_bmi,
    bmi_category
)

from daily_log import add_food, calculate_totals, daily_log, reset_day


# -------------------- PAGE SETUP --------------------
st.set_page_config(page_title="Indian Diet Tracker", layout="centered")
st.title("🥗 Indian Diet & Calorie Tracker")


# -------------------- LOAD FOOD DATA --------------------
# -------------------- LOAD FOOD DATA --------------------
try:
    food_df = pd.read_csv("clean_food_data.csv")

    if "Dish Name" not in food_df.columns:
        st.error("❌ 'Dish Name' column not found in clean_food_data.csv")
        st.stop()

    food_names = sorted(food_df["Dish Name"].dropna().unique())

except FileNotFoundError:
    st.error("❌ clean_food_data.csv not found. Keep it in the same folder as app.py")
    st.stop()

except pd.errors.EmptyDataError:
    st.error("❌ clean_food_data.csv is empty")
    st.stop()

except Exception as e:
    st.error("❌ Error loading clean_food_data.csv")
    st.code(str(e))
    st.stop()

# -------------------- SESSION STATE INIT --------------------
if "page" not in st.session_state:
    st.session_state.page = 1

for key in [
    "name", "age", "gender", "weight", "height",
    "activity", "goal",
    "bmi", "bmr", "tdee", "final_calories"
]:
    if key not in st.session_state:
        st.session_state[key] = None


# -------------------- SAVE HISTORY --------------------
def save_day_to_history(totals, final_calories):
    today = date.today().isoformat()
    status = "Within Calories" if totals["Calories"] <= final_calories else "Exceeded Calories"

    row = {
        "Date": today,
        "Name": st.session_state.name,
        "Calories": round(totals["Calories"], 2),
        "Protein": round(totals["Protein"], 2),
        "Carbs": round(totals["Carbs"], 2),
        "Fats": round(totals["Fats"], 2),
        "Status": status
    }

    df = pd.DataFrame([row])
    df.to_csv("history.csv", mode="a", header=not os.path.exists("history.csv"), index=False)


# ======================================================
# PAGE 1 — USER DETAILS
# ======================================================
if st.session_state.page == 1:
    st.header("👤 Step 1: Your Details")

    st.session_state.name = st.text_input("Your Name")
    st.session_state.age = st.number_input("Age", min_value=10, max_value=100, step=1)
    st.session_state.gender = st.selectbox("Gender", ["Male", "Female"])
    st.session_state.weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, step=0.1)
    st.session_state.height = st.number_input("Height (cm)", min_value=120.0, max_value=250.0, step=0.1)

    st.session_state.activity = st.selectbox(
        "Activity Level",
        ["Sedentary", "Light", "Moderate", "Active"]
    )

    st.session_state.goal = st.selectbox(
        "Goal",
        ["Weight Loss", "Maintenance", "Muscle Gain"]
    )

    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("➡️ Continue", use_container_width=True):
            st.session_state.page = 2
            st.rerun()


# ======================================================
# PAGE 2 — CALCULATE + FOOD LOGGING
# ======================================================
elif st.session_state.page == 2:
    st.header(f"📊 Welcome, {st.session_state.name}")

    if st.button("🧮 Calculate Health Metrics"):
        st.session_state.bmi = calculate_bmi(
            st.session_state.weight,
            st.session_state.height
        )

        st.session_state.bmr = calculate_bmr(
            st.session_state.weight,
            st.session_state.height,
            st.session_state.age,
            st.session_state.gender
        )

        st.session_state.tdee = calculate_tdee(
            st.session_state.bmr,
            st.session_state.activity
        )

        st.session_state.final_calories = adjust_calories_for_goal(
            st.session_state.tdee,
            st.session_state.goal
        )

    if st.session_state.final_calories is not None:
        st.subheader("📌 Health Summary")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**BMI:** {round(st.session_state.bmi, 2)}")
            st.write(f"**BMR:** {round(st.session_state.bmr, 2)} kcal")
        with col2:
            st.write(f"**TDEE:** {round(st.session_state.tdee, 2)} kcal")
            st.success(f"🎯 Daily Target: {round(st.session_state.final_calories, 2)} kcal")

        category, message = bmi_category(st.session_state.bmi)
        st.info(message)

        st.divider()

        # -------- FOOD LOGGING --------
        st.subheader("🍛 Log Your Food")

        dish = st.selectbox("Select Dish", food_names)
        quantity = st.number_input("Quantity (servings)", min_value=1, step=1)

        if st.button("Add Food"):
            add_food(dish, quantity)
            st.success(f"Added {quantity} × {dish}")

        # -------- CUSTOM FOOD --------
        st.markdown("**Can't find your food?**")
        add_custom = st.checkbox("➕ Add custom food")

        if add_custom:
            cname = st.text_input("Food name")
            ccal = st.number_input("Calories per serving", min_value=0.0, step=10.0)
            cpro = st.number_input("Protein (g)", min_value=0.0, step=1.0)
            ccarb = st.number_input("Carbs (g)", min_value=0.0, step=1.0)
            cfat = st.number_input("Fats (g)", min_value=0.0, step=1.0)
            cqty = st.number_input("Quantity", min_value=1, step=1)

            if st.button("Add Custom Food"):
                daily_log.append({
                    "Dish Name": f"{cname} (Custom)",
                    "Quantity": cqty,
                    "Calories": ccal * cqty,
                    "Protein": cpro * cqty,
                    "Carbs": ccarb * cqty,
                    "Fats": cfat * cqty
                })
                st.success(f"Added custom food: {cname}")

        # -------- FEEDBACK & LOG --------
        if daily_log:
            totals = calculate_totals()
            protein_need = 0.8 * st.session_state.weight
            percent_used = (totals["Calories"] / st.session_state.final_calories) * 100
        st.markdown(
    f"### 🔥 Total Calories Consumed Today: **{round(totals['Calories'], 2)} kcal**"
)

            st.subheader("🍽️ Meal Feedback")

            if percent_used < 50:
                st.info("🌱 Plenty of calories left today.")
            elif percent_used < 80:
                st.info("🙂 You're doing well so far.")
            else:
                st.warning("⚠️ Near daily calorie limit.")

            if totals["Calories"] > st.session_state.final_calories:
                if totals["Protein"] >= protein_need * 0.8:
                    st.info("🥚 Protein was good, calories exceeded.")
                else:
                    st.warning("⚠️ Calories exceeded and protein was low.")
            else:
                if totals["Protein"] < protein_need * 0.5:
                    st.info("🥚 Protein intake is low.")
                else:
                    st.success("💪 Calories & protein are balanced.")

            st.divider()
            st.subheader("📋 Today's Food Log")

            log_df = pd.DataFrame(daily_log)
            log_df.insert(0, "S.No", range(1, len(log_df) + 1))
            st.dataframe(log_df, hide_index=True, use_container_width=True)

        st.divider()
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("⬅️ Back"):
                st.session_state.page = 1
                st.rerun()

        with col2:
            if st.button("📅 View History"):
                st.session_state.page = 3
                st.rerun()

        with col3:
            if st.button("🔁 Reset Day"):
                reset_day()          # ONLY clears today's log
                st.success("Today's log cleared. Start fresh ✨")
                st.rerun()

    else:
        st.warning("Please calculate health metrics first.")


# ======================================================
# PAGE 3 — HISTORY
# ======================================================
elif st.session_state.page == 3:
    st.header("📅 Step 3: Previous Day Records")

    try:
        if os.path.exists("history.csv"):
            history_df = pd.read_csv("history.csv",engine="python",on_bad_lines="skip")


            if not history_df.empty:
                # Safe serial number (no duplicate column error)
                history_df = history_df.reset_index(drop=True)
                history_df.insert(0, "S.No", history_df.index + 1)

                st.dataframe(
                    history_df,
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No history found yet.")
        else:
            st.info("No history available yet.")

    except Exception as e:
        st.error("Error loading history file.")
        st.caption(str(e))

    st.divider()

    if st.button("⬅️ Back to Food Log"):
        st.session_state.page = 2
        st.rerun()

    st.caption(
        "Disclaimer: This project is for educational purposes only and is not a medical application."
    )

