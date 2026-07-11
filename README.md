[README.md](https://github.com/user-attachments/files/29926509/README.md)
# EduPro-Instructor-Performance-Course-Quality-Evaluation
Streamlit dashboard evaluating instructor performance and course quality on the EduPro learning platform — leaderboards, experience-vs-rating analysis, and quality heatmaps.
# EduPro — Instructor Performance & Course Quality Evaluation

A Streamlit dashboard prototype for evaluating instructor performance and course
quality on the EduPro online learning platform. Built for the Unified Mentor
project.

## Features

- **Instructor Performance Leaderboard** — ranked instructors by rating, with enrollment counts
- **Experience vs Rating** — scatter plots (with trendlines) of years of experience against teacher and course ratings
- **Course Quality Heatmap** — average course rating by category × level, and by level × instructor gender
- **Expertise-wise Performance Comparison** — teacher/course rating and enrollment volume by expertise area

Filterable by instructor expertise, course category, course level, and rating range.

## Data

The app loads `EduPro_Online_Platform.xlsx` (Teachers / Courses / Transactions sheets)
if present in the project root. If that file is missing, it looks for
`data/teachers.csv`, `data/courses.csv`, `data/transactions.csv`. If none of those
are found, it falls back to synthetic demo data generated on the fly.

## Setup

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python -m streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Project structure

```
.
├── app.py                          # Streamlit application
├── requirements.txt                 # Python dependencies
├── EduPro_Online_Platform.xlsx      # Source dataset
└── README.md
```

## Tech stack

- [Streamlit](https://streamlit.io/) — dashboard framework
- [Pandas](https://pandas.pydata.org/) — data wrangling
- [Plotly Express](https://plotly.com/python/plotly-express/) — interactive charts

## License

For educational/portfolio use as part of the Unified Mentor program.
