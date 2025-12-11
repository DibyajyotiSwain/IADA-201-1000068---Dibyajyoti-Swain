# app.py
"""
Streamlit dashboard tailored to your cleaned CSV columns.
Path used (update if needed):
E:\XII IBCP\AI\Maths\data\player_injuries_impact_cleaned.csv

Run:
    streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import traceback

st.set_page_config(page_title="Player Injuries & Team Performance", layout="wide")

# ---------- CONFIG: single fixed csv path ----------
CSV_PATH = r"E:\XII IBCP\AI\Maths\data\player_injuries_impact_cleaned.csv"

# ---------- helpers ----------
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

def to_numeric_safe(df: pd.DataFrame, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def parse_dates_safe(df: pd.DataFrame, cols):
    for c in cols:
        if c in df.columns:
            try:
                df[c] = pd.to_datetime(df[c], errors="coerce")
            except Exception:
                pass
    return df

def mean_of_cols(df, col_list, new_col):
    present = [c for c in col_list if c in df.columns]
    if not present:
        df[new_col] = pd.NA
        return df
    df[new_col] = df[present].astype(float).mean(axis=1, skipna=True)
    return df

def has_cols(df, cols):
    return all(c in df.columns for c in cols)

# ---------- UI ----------
st.title("Player Injuries & Team Performance")
st.write("Loading cleaned CSV from fixed path. If you want to use a different file, replace the CSV at the path above and restart the app.")

# ---------- load ----------
p = Path(CSV_PATH)
try:
    if not p.exists():
        raise FileNotFoundError(f"File not found: {CSV_PATH}")
    raw = pd.read_csv(p, low_memory=False)
    source = CSV_PATH
except Exception as e:
    st.error("Could not load the cleaned CSV from the fixed path.")
    with st.expander("Error details"):
        st.text(traceback.format_exc())
    st.stop()

# ---------- normalize & parse ----------
df = normalize_columns(raw)
df = parse_dates_safe(df, ['date_of_injury', 'date_of_return', 'date_of_injury', 'date_of_return'])
# numeric conversions
df = to_numeric_safe(df, ['fifa_rating', 'age', 'avg_rating_before', 'avg_rating_after', 'performance_drop_index',
                          'team_gd_before', 'team_gd_missed'])

# compute derived if needed
# If avg_rating_before/after don't exist but individual match ratings do, compute them
before_cols = ['match1_before_injury_player_rating', 'match2_before_injury_player_rating', 'match3_before_injury_player_rating']
after_cols = ['match1_after_injury_player_rating', 'match2_after_injury_player_rating', 'match3_after_injury_player_rating']
df = mean_of_cols(df, before_cols, 'rating_before_avg')
df = mean_of_cols(df, after_cols, 'rating_after_avg')
# unify names: prefer avg_rating_before/after if present, else fallback to computed
if 'avg_rating_before' not in df.columns and 'rating_before_avg' in df.columns:
    df['avg_rating_before'] = df['rating_before_avg']
if 'avg_rating_after' not in df.columns and 'rating_after_avg' in df.columns:
    df['avg_rating_after'] = df['rating_after_avg']
# performance_drop_index fallback
if 'performance_drop_index' not in df.columns:
    if 'avg_rating_before' in df.columns and 'avg_rating_after' in df.columns:
        df['performance_drop_index'] = df['avg_rating_before'] - df['avg_rating_after']

# injury month extraction
if 'date_of_injury' in df.columns:
    df['injury_month'] = df['date_of_injury'].dt.to_period('M').astype(str)
elif 'injury_month' not in df.columns:
    df['injury_month'] = pd.NA

# ---------- show debug info ----------
st.markdown(f"**Data source:** `{source}` — rows: **{len(df)}**, cols: **{len(df.columns)}**")
with st.expander("Column list (normalized) — check these names"):
    st.write(list(df.columns))

# ---------- sidebar filters ----------
st.sidebar.header("Filters")
players = sorted(df['player_name'].dropna().unique().tolist()) if 'player_name' in df.columns else (sorted(df['name'].dropna().unique().tolist()) if 'name' in df.columns else [])
teams = sorted(df['team'].dropna().unique().tolist()) if 'team' in df.columns else (sorted(df['team_name'].dropna().unique().tolist()) if 'team_name' in df.columns else [])
seasons = sorted(df['season'].dropna().unique().tolist()) if 'season' in df.columns else []

player_choice = st.sidebar.selectbox("Player", options=["All"] + players)
team_choice = st.sidebar.selectbox("Team", options=["All"] + teams)
season_choice = st.sidebar.selectbox("Season", options=["All"] + seasons)
month_choice = st.sidebar.selectbox("Injury month", options=["All"] + (sorted(df['injury_month'].dropna().unique().tolist()) if 'injury_month' in df.columns else ["All"]))

# apply filters
view = df.copy()
name_col = 'player_name' if 'player_name' in view.columns else ('name' if 'name' in view.columns else None)
team_col = 'team' if 'team' in view.columns else ('team_name' if 'team_name' in view.columns else None)

if player_choice != "All" and name_col:
    view = view[view[name_col] == player_choice]
if team_choice != "All" and team_col:
    view = view[view[team_col] == team_choice]
if season_choice != "All" and 'season' in view.columns:
    view = view[view['season'] == season_choice]
if month_choice != "All" and 'injury_month' in view.columns:
    view = view[view['injury_month'] == month_choice]

st.sidebar.write(f"Rows after filters: {view.shape[0]}")

# ---------- metrics ----------
c1, c2, c3 = st.columns(3)
c1.metric("Records (filtered)", int(view.shape[0]))
if 'fifa_rating' in view.columns:
    c2.metric("Avg rating", round(view['fifa_rating'].mean(skipna=True), 3))
else:
    c2.metric("Avg rating", "N/A")
c3.metric("Unique players", int(view[name_col].nunique()) if name_col else 0)

st.markdown("---")

# ---------- VISUAL 1: Top performance drops ----------
st.subheader("Top players by performance drop")
if 'performance_drop_index' in view.columns and view['performance_drop_index'].notna().any():
    name_for_plot = name_col if name_col else (team_col if team_col else view.index.name)
    bar_df = view[[name_for_plot, 'performance_drop_index']].dropna(subset=['performance_drop_index']).groupby(name_for_plot).mean().reset_index().sort_values('performance_drop_index', ascending=False).head(15)
    fig1 = px.bar(bar_df, x=name_for_plot, y='performance_drop_index', title="Top performance drops (higher = bigger drop)", labels={'performance_drop_index':'Performance drop'})
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("performance_drop_index not available. Ensure avg_rating_before & avg_rating_after or performance_drop_index are present.")

# ---------- VISUAL 2: Injury counts by team ----------
st.subheader("Injury counts by team")
if team_col and team_col in view.columns:
    counts = view[team_col].value_counts().reset_index()
    counts.columns = [team_col, 'injury_count']
    fig2 = px.bar(counts, x=team_col, y='injury_count', title="Injury counts by team")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Team column not found (team/team_name).")

# ---------- VISUAL 3: Heatmap month × team ----------
st.subheader("Injury frequency — Month × Team (heatmap)")
if 'injury_month' in view.columns and team_col:
    heat = view.groupby(['injury_month', team_col]).size().reset_index(name='count')
    pivot = heat.pivot(index=team_col, columns='injury_month', values='count').fillna(0)
    pivot_long = pivot.reset_index().melt(id_vars=team_col, var_name='injury_month', value_name='count')
    if pivot_long['count'].sum() > 0:
        fig3 = px.density_heatmap(pivot_long, x='injury_month', y=team_col, z='count', title="Injury frequency by month & team")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No injury counts to show in heatmap (filtered data).")
else:
    st.info("To show heatmap, need 'injury_month' and team column present.")

# ---------- VISUAL 4: Age vs Performance Drop or Age vs Rating ----------
st.subheader("Age vs performance drop / rating")
if 'age' in view.columns and 'performance_drop_index' in view.columns and view.dropna(subset=['age','performance_drop_index']).shape[0] > 0:
    sc = view.dropna(subset=['age','performance_drop_index'])
    fig4 = px.scatter(sc, x='age', y='performance_drop_index', hover_data=[c for c in [name_col, team_col] if c in sc.columns], trendline='ols', title="Age vs performance drop")
    st.plotly_chart(fig4, use_container_width=True)
elif 'age' in view.columns and 'fifa_rating' in view.columns and view.dropna(subset=['age','fifa_rating']).shape[0] > 0:
    sc = view.dropna(subset=['age','fifa_rating'])
    fig4b = px.scatter(sc, x='age', y='fifa_rating', hover_data=[c for c in [name_col, team_col] if c in sc.columns], trendline='ols', title="Age vs FIFA rating")
    st.plotly_chart(fig4b, use_container_width=True)
else:
    st.info("No valid data for age comparison (need 'age' plus 'performance_drop_index' or 'fifa_rating').")

# ---------- VISUAL 5: Leaderboard (improvement) ----------
st.subheader("Leaderboard — Best comebacks (avg_after − avg_before)")
if 'avg_rating_before' in view.columns and 'avg_rating_after' in view.columns and name_col:
    summary = view.groupby(name_col).agg({'avg_rating_before':'mean','avg_rating_after':'mean'}).reset_index()
    summary['improvement'] = summary['avg_rating_after'] - summary['avg_rating_before']
    top_improve = summary.sort_values('improvement', ascending=False).head(20)
    st.dataframe(top_improve.round(3))
else:
    st.info("Comeback leaderboard requires 'avg_rating_before' and 'avg_rating_after' columns and a player name column.")

st.markdown("---")
st.caption("If a chart is empty, check the 'Column list (normalized)' above and the CSV content. Ask me to map any different column name if needed.")
