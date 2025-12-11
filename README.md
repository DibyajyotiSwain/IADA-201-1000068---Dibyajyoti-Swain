# IADA-201-1000068---Dibyajyoti-Swain

# **📘 Player Injury Impact Analysis & Streamlit Dashboard (Scenario 1)**

### Mathematics for AI – Summative Assessment

### CRS: Artificial Intelligence

This project examines how football player injuries affect performance before, during, and after recovery. The workflow covers data cleaning, feature creation, exploratory data analysis, and an interactive Streamlit dashboard designed for real-world use by coaches and analysts.

---

## **🎯 Project Objectives**

* Prepare and clean the injury dataset for analysis
* Compute key metrics such as **avg_rating_before**, **avg_rating_after**, and **performance_drop_index**
* Explore injury patterns across teams, months, and players
* Build five meaningful visualizations required for Scenario 1
* Deploy an interactive Streamlit dashboard for easy exploration

---

---

## **🧼 Data Cleaning Summary**

The cleaned CSV includes around 52 columns:

* **Player details:** player_name, team, position, age, season
* **Injury details:** injury, date_of_injury, date_of_return, injury_month, injury_year
* **Match ratings:** 3 matches before injury, 3 missed matches, 3 matches after injury
* **Derived metrics:** avg_rating_before, avg_rating_after, rating_change, team_gd_before, team_gd_missed, performance_drop_index

Key transformations:

* Normalized column names
* Converted date fields to datetime
* Converted rating fields to numeric
* Computed average ratings before/after injury
* Calculated performance_drop_index

---

## **📊 EDA (step3_eda_fixed.py)**

The EDA script produces the following outputs in **eda_outputs/**:

1. **Top 10 performance drops** (Bar chart)
2. **Before vs After Rating Comparison** for a default player
3. **Injury Heatmap** (Month × Team)
4. **Age vs Performance Drop** (Scatter + trendline)
5. **Comeback Leaderboard** (CSV + HTML)

All visuals are automatically exported as jpg files from html just for convinience.
![5_leaderboard_top_improvements](https://github.com/user-attachments/assets/c478b2f1-a810-4d98-8bae-187ff9665d59)

![2_before_after_Callum_Wilson](https://github.com/user-attachments/assets/72dc953c-4b81-4f1e-8c60-1399df9ccafd)

![3_heatmap_month_team](https://github.com/user-attachments/assets/1dc830f3-73a3-46a9-b513-65d870849cba)

![4_scatter_age_perf_drop](https://github.com/user-attachments/assets/606d3a2a-2957-476c-a532-fe1007be9961)

![1_top10_perf_drop](https://github.com/user-attachments/assets/26f308ab-1bf2-4f75-bbd7-5835a6dc34ca)

## **🖥️ Streamlit Dashboard (app.py)**

### **Dashboard Features**

* Filters: **Player**, **Team**, **Season**, **Injury Month**
* Automatically reacts to your selections
* Displays five required Scenario-1 visuals
* Uses only the columns present in your cleaned dataset

### **Generated Visuals**

1. Top players by performance drop
2. Injury counts by team
3. Month × Team injury heatmap
4. Age vs performance drop / Age vs rating
5. Comeback leaderboard (avg rating after − avg rating before)

Run locally: https://iada-201-1000068---dibyajyoti-swain-lwsnv92ojmhkwbvnfb52ki.streamlit.app/  

THANKYOU 

```

