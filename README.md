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

All visuals are automatically exported as HTML files.
[Uploading 1_top10_perf_drop.html…]()
[Uploading 2_before_after _Callum_Wilson.html…]()
[Uploading  3_heatmap_month_team.html…]()
[Uploading 4_scatter_age_perf_drop.html…]()
[Uploading 5_leaderboard_top_improvements.html…]()
Run with:
```
python step3_eda_fixed.py
```
---

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
```
## **👤 Student Details**

```
Student Name: Dibyajyoti Swain
CRS: Artificial Intelligence
Assessment: Mathematics for AI-II Summative Assessment
Scenario: Scenario 1 — Injury Impact Analysis
```
