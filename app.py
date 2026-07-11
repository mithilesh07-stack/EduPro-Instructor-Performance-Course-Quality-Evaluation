

import os
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="EduPro | Instructor & Course Quality",
    page_icon="🎓",
    layout="wide",
)

# --------------------------------------------------------------------------
# Data loading (real CSVs if present, otherwise synthetic demo data)
# --------------------------------------------------------------------------

DATA_DIR = "data"
EXCEL_FILENAMES = ["EduPro_Online_Platform.xlsx", os.path.join("data", "EduPro_Online_Platform.xlsx")]
EXPERTISE_AREAS = [
    "Data Science", "Web Development", "Cloud Computing", "Cybersecurity",
    "Design", "Business", "Marketing", "AI & ML",
]
CATEGORIES = [
    "Data Science", "Web Development", "Cloud Computing", "Cybersecurity",
    "Design", "Business", "Marketing", "AI & ML",
]
LEVELS = ["Beginner", "Intermediate", "Advanced"]


@st.cache_data
def load_or_generate_data(seed: int = 42):
    # 1) Real EduPro workbook (Users / Teachers / Courses / Transactions sheets)
    for excel_path in EXCEL_FILENAMES:
        if os.path.exists(excel_path):
            sheets = pd.read_excel(excel_path, sheet_name=None)
            return sheets["Teachers"], sheets["Courses"], sheets["Transactions"]

    # 2) Plain CSVs dropped into ./data
    teachers_path = os.path.join(DATA_DIR, "teachers.csv")
    courses_path = os.path.join(DATA_DIR, "courses.csv")
    transactions_path = os.path.join(DATA_DIR, "transactions.csv")

    if all(os.path.exists(p) for p in [teachers_path, courses_path, transactions_path]):
        teachers = pd.read_csv(teachers_path)
        courses = pd.read_csv(courses_path)
        transactions = pd.read_csv(transactions_path)
        return teachers, courses, transactions

    rng = np.random.default_rng(seed)
    n_teachers = 60
    n_courses = 150
    n_transactions = 4000

    teachers = pd.DataFrame({
        "TeacherID": range(1, n_teachers + 1),
        "TeacherName": [f"Instructor {i}" for i in range(1, n_teachers + 1)],
        "Age": rng.integers(24, 65, n_teachers),
        "Gender": rng.choice(["Male", "Female"], n_teachers, p=[0.55, 0.45]),
        "Expertise": rng.choice(EXPERTISE_AREAS, n_teachers),
        "YearsOfExperience": rng.integers(1, 25, n_teachers),
    })

    # Rating tends to rise with experience, then plateau, plus noise
    exp_effect = np.clip(teachers["YearsOfExperience"] / 12, 0, 1.6)
    noise = rng.normal(0, 0.45, n_teachers)
    teachers["TeacherRating"] = np.clip(3.0 + exp_effect + noise, 1.0, 5.0).round(2)

    courses = pd.DataFrame({
        "CourseID": range(1, n_courses + 1),
        "CourseName": [f"Course {i}" for i in range(1, n_courses + 1)],
        "CourseCategory": rng.choice(CATEGORIES, n_courses),
        "CourseLevel": rng.choice(LEVELS, n_courses, p=[0.4, 0.4, 0.2]),
    })

    course_teacher_map = rng.choice(teachers["TeacherID"], n_courses)
    teacher_rating_lookup = teachers.set_index("TeacherID")["TeacherRating"]
    base_course_rating = teacher_rating_lookup.loc[course_teacher_map].values
    course_noise = rng.normal(0, 0.35, n_courses)
    courses["CourseRating"] = np.clip(base_course_rating * 0.8 + course_noise + 0.8, 1.0, 5.0).round(2)
    courses["_TeacherID_temp"] = course_teacher_map  # used to build transactions realistically

    transactions = pd.DataFrame({
        "TransactionID": range(1, n_transactions + 1),
        "CourseID": rng.choice(courses["CourseID"], n_transactions),
    })
    transactions = transactions.merge(
        courses[["CourseID", "_TeacherID_temp"]], on="CourseID", how="left"
    ).rename(columns={"_TeacherID_temp": "TeacherID"})
    courses = courses.drop(columns=["_TeacherID_temp"])

    return teachers, courses, transactions


teachers_df, courses_df, transactions_df = load_or_generate_data()

# --------------------------------------------------------------------------
# Merge into an analysis-ready table
# --------------------------------------------------------------------------

merged = (
    transactions_df
    .merge(teachers_df, on="TeacherID", how="left")
    .merge(courses_df, on="CourseID", how="left")
)

# --------------------------------------------------------------------------
# Sidebar — User Capabilities: filters
# --------------------------------------------------------------------------

st.sidebar.title("🎓 EduPro Filters")

expertise_options = sorted(teachers_df["Expertise"].unique())
selected_expertise = st.sidebar.multiselect(
    "Instructor Expertise", expertise_options, default=expertise_options
)

category_options = sorted(courses_df["CourseCategory"].unique())
selected_categories = st.sidebar.multiselect(
    "Course Category", category_options, default=category_options
)

level_options = sorted(courses_df["CourseLevel"].unique())
selected_levels = st.sidebar.multiselect(
    "Course Level", level_options, default=level_options
)

rating_range = st.sidebar.slider(
    "Rating Range (Teacher & Course)", 1.0, 5.0, (1.0, 5.0), step=0.1
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data source: place EduPro_Online_Platform.xlsx (or a ./data copy of it) "
    "next to app.py to use the real dataset. Falls back to teachers.csv / "
    "courses.csv / transactions.csv in ./data, then to synthetic demo data."
)

# Apply filters
f_teachers = teachers_df[
    teachers_df["Expertise"].isin(selected_expertise)
    & teachers_df["TeacherRating"].between(*rating_range)
]
f_courses = courses_df[
    courses_df["CourseCategory"].isin(selected_categories)
    & courses_df["CourseLevel"].isin(selected_levels)
    & courses_df["CourseRating"].between(*rating_range)
]
f_merged = merged[
    merged["Expertise"].isin(selected_expertise)
    & merged["CourseCategory"].isin(selected_categories)
    & merged["CourseLevel"].isin(selected_levels)
    & merged["TeacherRating"].between(*rating_range)
    & merged["CourseRating"].between(*rating_range)
]

# --------------------------------------------------------------------------
# Header + top-line KPIs
# --------------------------------------------------------------------------

st.title("🎓 EduPro — Instructor Performance & Course Quality Evaluation")
st.caption("Prototype dashboard · Unified Mentor project")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Instructors (filtered)", f"{f_teachers['TeacherID'].nunique():,}")
k2.metric("Courses (filtered)", f"{f_courses['CourseID'].nunique():,}")
k3.metric("Avg Teacher Rating", f"{f_teachers['TeacherRating'].mean():.2f}" if len(f_teachers) else "—")
k4.metric("Avg Course Rating", f"{f_courses['CourseRating'].mean():.2f}" if len(f_courses) else "—")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Instructor Leaderboard",
    "📈 Experience vs Rating",
    "🔥 Course Quality Heatmap",
    "🧭 Expertise Comparison",
])

# --------------------------------------------------------------------------
# Module 1: Instructor performance leaderboard
# --------------------------------------------------------------------------

with tab1:
    st.subheader("Instructor Performance Leaderboard")

    enrollment_counts = (
        f_merged.groupby("TeacherID")["TransactionID"].count().rename("Enrollments")
    )
    leaderboard = (
        f_teachers.set_index("TeacherID")
        .join(enrollment_counts, how="left")
        .fillna({"Enrollments": 0})
        .reset_index()
        .sort_values("TeacherRating", ascending=False)
    )
    leaderboard["Enrollments"] = leaderboard["Enrollments"].astype(int)
    leaderboard.insert(0, "Rank", range(1, len(leaderboard) + 1))

    display_cols = [
        "Rank", "TeacherName", "Expertise", "YearsOfExperience",
        "TeacherRating", "Enrollments", "Gender", "Age",
    ]
    st.dataframe(
        leaderboard[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "TeacherRating": st.column_config.ProgressColumn(
                "TeacherRating", min_value=1, max_value=5, format="%.2f"
            ),
        },
    )

    top_n = st.slider("Show top N instructors in chart", 5, 30, 10)
    top_chart = leaderboard.head(top_n)
    fig = px.bar(
        top_chart, x="TeacherRating", y="TeacherName", color="Expertise",
        orientation="h", title=f"Top {top_n} Instructors by Rating",
        hover_data=["YearsOfExperience", "Enrollments"],
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------------------------------
# Module 2: Experience vs rating scatter plots
# --------------------------------------------------------------------------

with tab2:
    st.subheader("Experience vs Rating")

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.scatter(
            f_teachers, x="YearsOfExperience", y="TeacherRating",
            color="Expertise", size="YearsOfExperience", trendline="ols",
            title="Years of Experience vs Teacher Rating",
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        exp_course = f_merged.groupby("TeacherID").agg(
            YearsOfExperience=("YearsOfExperience", "first"),
            AvgCourseRating=("CourseRating", "mean"),
            Expertise=("Expertise", "first"),
        ).reset_index()
        fig2 = px.scatter(
            exp_course, x="YearsOfExperience", y="AvgCourseRating",
            color="Expertise", trendline="ols",
            title="Years of Experience vs Avg Course Rating",
        )
        st.plotly_chart(fig2, use_container_width=True)

    corr1 = f_teachers[["YearsOfExperience", "TeacherRating"]].corr().iloc[0, 1]
    corr2 = exp_course[["YearsOfExperience", "AvgCourseRating"]].corr().iloc[0, 1]
    c1, c2 = st.columns(2)
    c1.metric("Correlation: Experience ↔ Teacher Rating", f"{corr1:.2f}")
    c2.metric("Correlation: Experience ↔ Course Rating", f"{corr2:.2f}")

# --------------------------------------------------------------------------
# Module 3: Course quality heatmaps
# --------------------------------------------------------------------------

with tab3:
    st.subheader("Course Quality Heatmap")

    pivot = f_courses.pivot_table(
        index="CourseCategory", columns="CourseLevel", values="CourseRating", aggfunc="mean"
    )
    fig3 = px.imshow(
        pivot, text_auto=".2f", color_continuous_scale="RdYlGn",
        aspect="auto", title="Avg Course Rating: Category vs Level",
        labels=dict(color="Avg Rating"),
    )
    st.plotly_chart(fig3, use_container_width=True)

    gender_level = f_merged.pivot_table(
        index="CourseLevel", columns="Gender", values="CourseRating", aggfunc="mean"
    )
    fig4 = px.imshow(
        gender_level, text_auto=".2f", color_continuous_scale="Blues",
        aspect="auto", title="Avg Course Rating: Course Level vs Instructor Gender",
        labels=dict(color="Avg Rating"),
    )
    st.plotly_chart(fig4, use_container_width=True)

# --------------------------------------------------------------------------
# Module 4: Expertise-wise performance comparisons
# --------------------------------------------------------------------------

with tab4:
    st.subheader("Expertise-wise Performance Comparison")

    expertise_summary = f_merged.groupby("Expertise").agg(
        AvgTeacherRating=("TeacherRating", "mean"),
        AvgCourseRating=("CourseRating", "mean"),
        Enrollments=("TransactionID", "count"),
    ).reset_index().sort_values("AvgTeacherRating", ascending=False)

    fig5 = px.bar(
        expertise_summary.melt(
            id_vars="Expertise", value_vars=["AvgTeacherRating", "AvgCourseRating"],
            var_name="Metric", value_name="Rating"
        ),
        x="Expertise", y="Rating", color="Metric", barmode="group",
        title="Avg Teacher Rating vs Avg Course Rating by Expertise",
    )
    st.plotly_chart(fig5, use_container_width=True)

    fig6 = px.bar(
        expertise_summary, x="Expertise", y="Enrollments",
        title="Enrollment Volume by Expertise Area", color="Expertise",
    )
    st.plotly_chart(fig6, use_container_width=True)

    st.dataframe(expertise_summary, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("EduPro Instructor Performance and Course Quality Evaluation · Unified Mentor Project · Prototype build")
