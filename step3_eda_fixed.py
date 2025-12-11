# step3_eda_fixed.py
"""
EDA adapted to the cleaned CSV's actual columns.
Run:
    python step3_eda_fixed.py
Outputs go to eda_outputs/ (HTML + CSV)
"""
import pandas as pd
import plotly.express as px
import plotly.io as pio
from pathlib import Path
import traceback
import sys
import os

CLEAN_CSV = r"E:\XII IBCP\AI\Maths\data\player_injuries_impact_cleaned.csv"
OUT_DIR = Path.cwd() / "eda_outputs"
OUT_DIR.mkdir(exist_ok=True)

def safe_read(csv_path):
    print("Checking file:", csv_path)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at: {csv_path}")
    try:
        df = pd.read_csv(csv_path, low_memory=False)
        print("Loaded OK — shape:", df.shape)
        return df
    except Exception as e:
        print("Error while reading CSV:")
        raise

def print_columns(df):
    print("\nColumns (exact):")
    for i, c in enumerate(df.columns):
        print(f"{i+1:02d}. '{c}'")
    print()

def has_cols(df, required):
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"[WARN] Missing columns: {missing}")
        return False
    return True

def safe_to_datetime(df, col):
    if col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            print(f"Converted column '{col}' to datetime (NaT count: {df[col].isna().sum()})")
        except Exception as e:
            print(f"[WARN] Failed to convert {col} to datetime:", e)

def main():
    try:
        df = safe_read(CLEAN_CSV)
        print_columns(df)

        # normalize column names to lowercase stripped for easier checks,
        orig_cols = list(df.columns)
        df.columns = [c.strip().lower() for c in df.columns]
        print("Normalized column names to lower-case/stripped.")
        print("\nNormalized columns:")
        print(df.columns.tolist())

        # convert known date-like columns if present
        # your file uses 'date of injury' / 'date of return'
        for date_col in ['date of injury','date_of_injury','date of return','date_of_return']:
            if date_col in df.columns:
                safe_to_datetime(df, date_col)

        # Ensure numeric rating column is available: use 'fifa_rating'
        if 'fifa_rating' in df.columns:
            df['fifa_rating'] = pd.to_numeric(df['fifa_rating'], errors='coerce')

        # You already have avg_rating_before/after in your file; ensure numeric
        for c in ['avg_rating_before','avg_rating_after','performance_drop_index','age']:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')

        # ----------------- 1) BAR: Top 10 performance drop injuries -----------------
        if 'performance_drop_index' in df.columns and df['performance_drop_index'].notna().any():
            top10 = df.sort_values('performance_drop_index', ascending=False).head(10)
            xcol = 'player_name' if 'player_name' in df.columns else ('player_name' if 'player_name' in orig_cols else 'player_name')
            # your file uses 'player_name' normalized to 'player_name' already
            # use 'player_name' (or 'player_name' fallback is same)
            # but original was 'player_name' -> present as 'player_name'
            # In your dataset it's 'player_name' (normalized). We'll use 'player_name' or 'name'.
            if 'player_name' not in df.columns and 'name' in df.columns:
                name_col = 'name'
            elif 'player_name' in df.columns:
                name_col = 'player_name'
            else:
                # try 'player_name' or 'name' from original columns
                name_col = None
                for alt in ['name','player_name','player_name']:
                    if alt in df.columns:
                        name_col = alt
                        break
            if name_col is None:
                # fallback to index
                fig1 = px.bar(top10.reset_index(), x=top10.reset_index().index, y='performance_drop_index',
                              title="Top 10 Injuries by Performance Drop Index")
            else:
                fig1 = px.bar(top10, x=name_col, y='performance_drop_index',
                              hover_data=[c for c in ['team','date of injury','date_of_injury'] if c in df.columns],
                              title="Top 10 Injuries by Performance Drop Index")
            out = OUT_DIR / "1_top10_perf_drop.html"
            pio.write_html(fig1, file=out, auto_open=False)
            print("Saved:", out)
        else:
            print("[SKIP] 1) performance_drop_index not available or all null.")

        # ----------------- 2) Alternative timeline: Before vs After per player -----------------
        # Original timeline required match_date; we don't have that in the file.
        # Instead create a before-vs-after bar chart for a chosen player using avg_rating_before / avg_rating_after
        if 'avg_rating_before' in df.columns and 'avg_rating_after' in df.columns:
            # choose default player
            name_col = 'player_name' if 'player_name' in df.columns else ('name' if 'name' in df.columns else None)
            if name_col is None:
                print("[SKIP] 2) timeline alternative - no player name column found.")
            else:
                # default choose the player with most records
                default_player = df[name_col].value_counts().idxmax() if df.shape[0] > 0 else None
                print("Default player for before/after bar:", default_player)
                # For script usage (non-interactive), we auto-select default_player
                sel = default_player
                if sel is not None:
                    p_df = df[df[name_col] == sel]
                    # compute mean before and after for that player (some rows may be duplicates across seasons)
                    before_val = p_df['avg_rating_before'].mean(skipna=True)
                    after_val = p_df['avg_rating_after'].mean(skipna=True)
                    bar_df = pd.DataFrame({
                        'phase': ['avg_before', 'avg_after'],
                        'rating': [before_val, after_val]
                    })
                    fig2 = px.bar(bar_df, x='phase', y='rating', title=f"Avg before vs after injury — {sel}", text='rating')
                    out2 = OUT_DIR / f"2_before_after_{str(sel).replace(' ','_')}.html"
                    pio.write_html(fig2, file=out2, auto_open=False)
                    print("Saved (before/after bar):", out2)
                else:
                    print("[SKIP] 2) timeline alternative - no default player found.")
        else:
            print("[SKIP] 2) timeline alternative - avg_rating_before/avg_rating_after missing.")

        # ----------------- 3) HEATMAP: Injury frequency by injury_month and team -----------------
        # Use your normalized columns: 'injury_month' and 'team'
        if 'injury_month' in df.columns and 'team' in df.columns:
            heat = df.groupby(['injury_month','team']).size().reset_index(name='count')
            pivot = heat.pivot(index='team', columns='injury_month', values='count').fillna(0)
            pivot_long = pivot.reset_index().melt(id_vars='team', var_name='injury_month', value_name='count')
            fig3 = px.density_heatmap(pivot_long, x='injury_month', y='team', z='count',
                                      title="Injury frequency by month and team (heatmap)")
            out = OUT_DIR / "3_heatmap_month_team.html"
            pio.write_html(fig3, file=out, auto_open=False)
            print("Saved:", out)
        else:
            print("[SKIP] 3) heatmap - 'injury_month' or 'team' missing")

        # ----------------- 4) SCATTER: Age vs Performance Drop -----------------
        if 'age' in df.columns and 'performance_drop_index' in df.columns:
            sc = df.dropna(subset=['age','performance_drop_index'])
            if sc.shape[0] > 0:
                fig4 = px.scatter(sc, x='age', y='performance_drop_index', hover_data=[c for c in ['player_name','team','name'] if c in df.columns],
                                  trendline='ols', title="Age vs Performance Drop Index")
                out = OUT_DIR / "4_scatter_age_perf_drop.html"
                pio.write_html(fig4, file=out, auto_open=False)
                print("Saved:", out)
            else:
                print("[SKIP] 4) scatter - not enough non-null age & performance_drop_index pairs")
        else:
            print("[SKIP] 4) scatter - 'age' or 'performance_drop_index' missing")

        # ----------------- 5) LEADERBOARD: Best comeback players using avg ratings -----------------
        # Use avg_rating_before / avg_rating_after to compute improvement
        if 'avg_rating_before' in df.columns and 'avg_rating_after' in df.columns:
            name_col = 'player_name' if 'player_name' in df.columns else ('name' if 'name' in df.columns else None)
            if name_col is None:
                print("[SKIP] 5) leaderboard - no name column found")
            else:
                summary = df.groupby(name_col).agg({
                    'avg_rating_before': 'mean',
                    'avg_rating_after': 'mean',
                    'performance_drop_index': 'mean'
                }).reset_index().rename(columns={name_col: 'player'})
                summary['rating_improvement'] = summary['avg_rating_after'] - summary['avg_rating_before']
                leaderboard = summary.sort_values('rating_improvement', ascending=False).head(20)
                out_csv = OUT_DIR / "5_leaderboard_top_improvements.csv"
                leaderboard.to_csv(out_csv, index=False)
                (OUT_DIR / "5_leaderboard_top_improvements.html").write_text(leaderboard.to_html(index=False))
                print("Saved leaderboard CSV and HTML:", out_csv)
        else:
            print("[SKIP] 5) leaderboard - avg_rating_before / avg_rating_after missing")

        print("\nEDA complete. Check the 'eda_outputs' folder for generated files:")
        for f in sorted(OUT_DIR.iterdir()):
            print(" -", f.name)

    except Exception as ex:
        print("\n=== ERROR ===")
        traceback.print_exc()
        print("\nPlease copy the above traceback and the printed column list and paste it here so I can fix it for your file.")
        sys.exit(1)

if __name__ == "__main__":
    main()
