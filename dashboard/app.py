from scipy import stats
import pandas as pd
import streamlit as st
import plotly.express as px

from database import (
    get_total_crimes,
    get_crime_types,
    get_yearly_trends,
    get_area_crime_counts
)

from hotspot_analysis import (
    load_hotspot_data,
    filter_hotspot_data,
    get_top_hotspots,
    create_hotspot_map,
    create_crime_count_map,
    get_neighborhood_crime_counts
)

@st.cache_data(ttl=60)
def get_cached_hotspot_data():
    return load_hotspot_data()

from prediction_model import (
    train_and_evaluate_model,
    forecast_next_weeks
)

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Crime Pattern Prediction System",
    page_icon="🕵🏻‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# PROFESSIONAL DARK NAVY THEME
# =========================================================

st.markdown("""
<style>

/* Remove the white Streamlit header and toolbar backgrounds */

[data-testid="stHeader"] {
    background: transparent !important;
    color: #F8FAFC !important;
}

[data-testid="stToolbar"] {
    background: transparent !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

/* Keep the main application background consistent */

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: linear-gradient(
        135deg,
        #06132F 0%,
        #081A3A 55%,
        #06142E 100%
    ) !important;
}

/* Prevent the main heading from being covered */

[data-testid="stMainBlockContainer"] {
    padding-top: 2rem !important;
}

/* Keep the sidebar and main content aligned */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0A1D42 0%,
        #071630 100%
    ) !important;
}

/* Main application background */

.stApp {
    background: linear-gradient(
        135deg,
        #06132F 0%,
        #081A3A 55%,
        #06142E 100%
    );
    color: #F8FAFC;
}

/* Main content spacing */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0A1D42 0%,
        #071630 100%
    );
    border-right: 1px solid #203B68;
}

[data-testid="stSidebar"] * {
    color: #F1F5F9;
}

/* General text visibility */

.stApp p,
.stApp label,
.stApp span {
    color: #E2EAF7;
}

/* Main heading */

.main-heading {
    color: #F8FAFC;
    font-size: 38px;
    font-weight: 800;
    line-height: 1.25;
    margin-bottom: 8px;
}

.main-subheading {
    color: #8EC5FF;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 30px;
}

/* Section headings */

.section-heading {
    color: #A8D2FF;
    font-size: 27px;
    font-weight: 750;
    margin-top: 24px;
    margin-bottom: 16px;
}

/* Statistics cards */

.metric-card {
    background: linear-gradient(
        145deg,
        #10284F,
        #0B1E40
    );
    border: 1px solid #244779;
    border-radius: 15px;
    padding: 23px 20px;
    min-height: 150px;
    box-shadow: 0 5px 18px rgba(0, 0, 0, 0.16);
}

.metric-icon {
    font-size: 29px;
    margin-bottom: 10px;
}

.metric-label {
    color: #C9DDF7;
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 10px;
}

.metric-value {
    color: #FFFFFF;
    font-size: 30px;
    font-weight: 800;
    overflow-wrap: anywhere;
}

/* Feature cards */

.feature-card {
    background: linear-gradient(
        145deg,
        #10284F,
        #0B1D3D
    );
    border: 1px solid #244779;
    border-radius: 14px;
    padding: 22px;
    min-height: 180px;
    margin-bottom: 15px;
}

.feature-icon {
    font-size: 30px;
    margin-bottom: 10px;
}

.feature-title {
    color: #B9DBFF;
    font-size: 19px;
    font-weight: 750;
    margin-bottom: 10px;
}

.feature-description {
    color: #E1EAF8;
    font-size: 15px;
    line-height: 1.7;
}

/* Welcome panel */

.welcome-panel {
    background: linear-gradient(
        120deg,
        #102950,
        #0C2042
    );
    border: 1px solid #244779;
    border-left: 5px solid #3B82F6;
    border-radius: 14px;
    padding: 25px;
    margin-top: 12px;
    margin-bottom: 25px;
}

.welcome-title {
    color: #FFFFFF;
    font-size: 23px;
    font-weight: 750;
    margin-bottom: 12px;
}

.welcome-description {
    color: #E2EAF7;
    font-size: 16px;
    line-height: 1.8;
}

/* Divider */

hr {
    border-color: #24416B !important;
}

/* Dataframe and table text */

[data-testid="stDataFrame"] {
    color: #FFFFFF;
}

/* Footer */

.footer-text {
    color: #C5D5EC;
    font-size: 13px;
    line-height: 1.7;
}

/* Buttons */

.stButton button {
    background-color: #174EA6;
    color: #FFFFFF;
    border: 1px solid #3B82F6;
    border-radius: 8px;
    font-weight: 600;
}

.stButton button:hover {
    background-color: #2563EB;
    color: #FFFFFF;
}

/* Improve navigation radio labels */

[data-testid="stSidebar"] [role="radiogroup"] label {
    background-color: transparent;
    padding: 8px;
    border-radius: 8px;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background-color: #173765;
}

/* Responsive heading */

@media (max-width: 768px) {
    .main-heading {
        font-size: 29px;
    }

    .section-heading {
        font-size: 23px;
    }

    .metric-value {
        font-size: 24px;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD REAL DATABASE DATA
# =========================================================

@st.cache_data(ttl=60)
def load_dashboard_data():
    total = get_total_crimes()
    crime_types = get_crime_types()
    yearly_trends = get_yearly_trends()
    area_crimes = get_area_crime_counts()

    return total, crime_types, yearly_trends, area_crimes


try:
    total_crimes, crime_types_df, yearly_df, areas_df = (
        load_dashboard_data()
    )

except Exception as error:
    st.error(
        "Unable to load the crime database. "
        "Check that crime_data.db exists in the main project folder."
    )
    st.code(str(error))
    st.stop()


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div style="padding: 12px 0 22px 0;">
            <div style="font-size: 34px;"></div>
            <div style="
                color: #FFFFFF;
                font-size: 22px;
                font-weight: 800;
                line-height: 1.3;">
                Crime Pattern<br>
                <span style="color: #60A5FA;">
                    Prediction System
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### Navigation")

    page = st.radio(
        "Choose a page",
        [
            "🏠 Home",
            "📊 Crime Analysis",
            "📈 Yearly Trends",
            "📍 Area Analysis",
            "⚠️ Risk Analysis",
            "🗺️ Crime Hotspot Analysis",
            "🔮 Future Crime Prediction",
            "🔎 Data Explorer"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown(
        """
        <div class="footer-text">
            <b>Data Source</b><br>
City of Chicago Open Data Portal<br>
Dataset: Crimes - 2001 to Present<br>
<a href="https://data.cityofchicago.org/"
   target="_blank"
   style="color: #7DD3FC;">
    View Official Dataset
</a>
<br><br>
<b>Technologies</b><br>
Java · Python · SQLite · Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div style="
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 8px;
    ">
        <div style="font-size: 55px;">🕵🏻‍♀️</div>
        <div>
            <div class="main-heading">
                Crime Pattern Prediction System
            </div>
            <div class="main-subheading">
                Smarter Analysis &nbsp; • &nbsp;
                Safer Communities &nbsp; • &nbsp;
                Data-Driven Decisions
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DATABASE OVERVIEW
# =========================================================

st.markdown(
    '<div class="section-heading">Crime Database Overview</div>',
    unsafe_allow_html=True
)

total_crime_types = len(crime_types_df)
total_community_areas = len(areas_df)

if not crime_types_df.empty:
    most_common_crime = str(
        crime_types_df.iloc[0]["crime_type"]
    )
else:
    most_common_crime = "No data"


metric_columns = st.columns(4)



# Custom styling for visible statistic cards

st.markdown("""
<style>


</style>
""", unsafe_allow_html=True)



stats = [
    ("Total Crime Records", f"{total_crimes:,}"),
    ("Crime Types", f"{total_crime_types:,}"),
    ("Community Areas", f"{total_community_areas:,}"),
    ("Most Common Crime", most_common_crime)
]

for column, (label, value) in zip(st.columns(4), stats):
    with column:
        with st.container(border=True):
            st.metric(
                label=label,
                value=value
            )


# =========================================================
# HOME PAGE
# =========================================================

if page == "🏠 Home":

    # Project introduction
    st.markdown(
        '<div class="section-heading">PROJECT OVERVIEW</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="welcome-panel">
            <div class="welcome-title">
                Crime Pattern Prediction System
            </div>
            <div class="welcome-description">
                An interactive crime analytics dashboard designed
                to explore historical crime data, discover geographic
                hotspots, analyze trends and understand crime patterns
                across particular community areas.
                <br><br>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # Key features
    st.markdown(
        '<div class="section-heading">EXPLORE THE PLATFORM</div>',
        unsafe_allow_html=True
    )

    features = [
        (
            "📊",
            "Crime Data Analysis",
            "Explore recorded crime categories, compare crime counts "
            "and understand patterns in the available dataset."
        ),
        (
            "📈",
            "Crime Trend Analysis",
            "Examine changes in recorded crime counts over time "
            "using interactive charts and statistical summaries."
        ),
        (
            "📍",
            "Crime Hotspot Analysis",
            "Explore geographic crime density and identify locations "
            "with higher recorded crime counts."
        ),
        (
            "🏙️",
            "Community Area Insights",
            "Compare historical crime counts across Chicago's "
            "community areas."
        ),
        (
            "🎯",
            "Future Crime Forecast",
            "Explore the project's available forecasting results "
            "and compare predicted counts with historical data."
        ),
        (
            "🔎",
            "Crime Data Explorer",
            "Filter and examine crime records by date, crime type "
            "and other available fields."
        )
    ]

    feature_columns = st.columns(3)

    for index, (icon, title, description) in enumerate(features):
        with feature_columns[index % 3]:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-description">
                        {description}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    # Project workflow
    st.markdown(
        '<div class="section-heading">HOW IT WORKS</div>',
        unsafe_allow_html=True
    )

    workflow_columns = st.columns(3)

    workflow = [
        (
            "01  |  EXPLORE",
            "Browse the available crime records and apply filters "
            "to focus on specific categories or dates."
        ),
        (
            "02  |  ANALYZE",
            "Use charts, statistical summaries and geographic maps "
            "to examine recorded crime patterns."
        ),
        (
            "03  |  DISCOVER",
            "Review hotspot locations, community-level comparisons "
            "and the available forecasting results."
        )
    ]

    for index, (heading, description) in enumerate(workflow):
        with workflow_columns[index]:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-title">{heading}</div>
                    <div class="feature-description">
                        {description}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# =========================================================
# CRIME ANALYSIS PAGE
# =========================================================

elif page == "📊 Crime Analysis":

    st.markdown(
        '<div class="section-heading">Top 10 Crime Types</div>',
        unsafe_allow_html=True
    )

    top_crimes = crime_types_df.head(10).sort_values(
        "total",
        ascending=True
    )

    if not top_crimes.empty:

        fig = px.bar(
            top_crimes,
            x="total",
            y="crime_type",
            orientation="h",
            labels={
                "total": "Recorded Crime Count",
                "crime_type": "Crime Type"
            },
            text="total",
            color="total",
            color_continuous_scale="Blues",
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="#081A3A",
            plot_bgcolor="#081A3A",
            font_color="#F8FAFC",
            height=550,
            coloraxis_showscale=False
        )

        fig.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
            cliponaxis=False
        )

        st.plotly_chart(fig, width="stretch")

        
        display_crimes = crime_types_df.head(10).rename(
            columns={
                "crime_type": "Crime Type",
                "total": "Recorded Crime Count"
            }
        )

        st.dataframe(
            display_crimes,
            width="stretch",
            hide_index=True
        )

    else:
        st.warning("No crime-type records are available.")



# =========================================================
# YEARLY TRENDS PAGE
# =========================================================

elif page == "📈 Yearly Trends":

    st.markdown(
        '<div class="section-heading">Yearly Crime Trends</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "Explore how recorded crime counts change across years "
        "using an interactive trend chart and year-by-year comparison."
    )

    st.divider()

    if not yearly_df.empty:

        yearly_display = yearly_df.copy()
        yearly_display["year"] = yearly_display["year"].astype(int)
        yearly_display = yearly_display.sort_values("year")

        yearly_display["total"] = pd.to_numeric(
            yearly_display["total"],
            errors="coerce"
        )

        yearly_display = yearly_display.dropna(
            subset=["year", "total"]
        )

        if not yearly_display.empty:

            # Calculate year-over-year change.
            yearly_display["Year-over-Year Change (%)"] = (
                yearly_display["total"]
                .pct_change()
                .mul(100)
            )

            # Interactive yearly trend chart.
            fig = px.line(
                yearly_display,
                x="year",
                y="total",
                markers=True,
                labels={
                    "year": "Year",
                    "total": "Recorded Crime Count"
                },
                template="plotly_dark",
                hover_data={
                    "year": True,
                    "total": ":,",
                    "Year-over-Year Change (%)": ":.2f"
                }
            )

            fig.update_traces(
                line=dict(color="#60A5FA", width=3),
                marker=dict(
                    size=9,
                    color="#93C5FD",
                    line=dict(color="#FFFFFF", width=1)
                ),
                hovertemplate=(
                    "<b>Year:</b> %{x}<br>"
                    "<b>Recorded Crimes:</b> %{y:,.0f}"
                    "<extra></extra>"
                )
            )

            fig.update_layout(
                title={
                    "text": "Recorded Crime Counts by Year",
                    "x": 0.02,
                    "xanchor": "left"
                },
                paper_bgcolor="#081A3A",
                plot_bgcolor="#081A3A",
                font=dict(color="#F8FAFC", size=12),
                height=500,
                margin=dict(l=20, r=25, t=75, b=30),
                hovermode="x unified",
                xaxis=dict(
                    title="Year",
                    tickmode="linear",
                    dtick=1,
                    showgrid=False
                ),
                yaxis=dict(
                    title="Recorded Crime Count",
                    tickformat=",",
                    gridcolor="rgba(148, 163, 184, 0.18)",
                    rangemode="tozero"
                )
            )

            st.plotly_chart(fig, width="stretch")

            st.markdown(
                '<div class="section-heading">'
                'Year-by-Year Comparison'
                '</div>',
                unsafe_allow_html=True
            )

            # Prepare readable table column names.
            display_table = yearly_display.rename(
                columns={
                    "year": "Year",
                    "total": "Recorded Crime Count"
                }
            ).copy()

            display_table["Recorded Crime Count"] = (
                display_table["Recorded Crime Count"].round().astype(int)
            )

            display_table["Year-over-Year Change (%)"] = (
                display_table["Year-over-Year Change (%)"].round(2)
            )

            display_table["Year-over-Year Change (%)"] = (
                display_table["Year-over-Year Change (%)"]
                .map(lambda value: f"{value:+.2f}%" if pd.notna(value)
                     else "N/A")
            )

            st.dataframe(
                display_table[
                    [
                        "Year",
                        "Recorded Crime Count",
                        "Year-over-Year Change (%)"
                    ]
                ],
                width="stretch",
                hide_index=True
            )

            st.caption(
                "Year-over-year change compares each year's recorded "
                "crime count with the previous available year. "
                "Positive values indicate an increase; negative values "
                "indicate a decrease. These are historical comparisons."
            )

        else:
            st.warning("No valid yearly trend records are available.")

    else:
        st.warning("No yearly trend data is available.")



# =========================================================
# AREA ANALYSIS PAGE
# =========================================================

elif page == "📍 Area Analysis":

    st.markdown(
        '<div class="section-heading">Community Area Analysis</div>',
        unsafe_allow_html=True
    )

    st.divider()

    if not areas_df.empty:

        # Prepare the top 10 community areas.
        top_areas = areas_df.head(10).copy()

        top_areas["total"] = pd.to_numeric(
            top_areas["total"],
            errors="coerce"
        )

        top_areas = top_areas.dropna(
            subset=["total", "community_area"]
        )

        top_areas["community_area"] = (
            top_areas["community_area"].astype(str)
        )

        # Sort in ascending order for a readable horizontal chart.
        top_areas = top_areas.sort_values(
            "total",
            ascending=True
        )

        if not top_areas.empty:

            fig = px.bar(
                top_areas,
                x="total",
                y="community_area",
                orientation="h",
                labels={
                    "total": "Recorded Crime Count",
                    "community_area": "Community Area"
                },
                text="total",
                color="total",
                color_continuous_scale="Teal",
                template="plotly_dark",
                hover_data={
                    "total": ":,",
                    "community_area": True
                }
            )

            fig.update_traces(
                texttemplate="%{text:,.0f}",
                textposition="outside",
                cliponaxis=False,
                marker_line_width=0,
                hovertemplate=(
                    "<b>Community Area:</b> %{y}<br>"
                    "<b>Recorded Crimes:</b> %{x:,.0f}"
                    "<extra></extra>"
                )
            )

            fig.update_layout(
                title={
                    "text": "Top 10 Community Areas by Recorded Crimes",
                    "x": 0.02,
                    "xanchor": "left"
                },
                paper_bgcolor="#081A3A",
                plot_bgcolor="#081A3A",
                font=dict(color="#F8FAFC", size=12),
                height=540,
                margin=dict(l=20, r=55, t=75, b=35),
                coloraxis_showscale=False,
                xaxis=dict(
                    title="Recorded Crime Count",
                    tickformat=",",
                    rangemode="tozero",
                    gridcolor="rgba(148, 163, 184, 0.18)"
                ),
                yaxis=dict(
                    title="Community Area",
                    showgrid=False
                ),
                hoverlabel=dict(
                    bgcolor="#102447",
                    font_color="#FFFFFF"
                )
            )

            st.plotly_chart(fig, width="stretch")

            st.markdown(
                '<div class="section-heading">'
                'Community Area Comparison'
                '</div>',
                unsafe_allow_html=True
            )

            # Use user-friendly names in the table.
            display_areas = top_areas.rename(
                columns={
                    "community_area": "Community Area",
                    "total": "Recorded Crime Count"
                }
            ).copy()

            display_areas["Recorded Crime Count"] = (
                display_areas["Recorded Crime Count"]
                .round()
                .astype(int)
            )

            st.dataframe(
                display_areas[
                    ["Community Area", "Recorded Crime Count"]
                ],
                width="stretch",
                hide_index=True
            )

            st.caption(
                "Areas are ranked by recorded crime counts in the "
                "available dataset. Higher counts do not necessarily "
                "indicate a higher individual risk of victimization."
            )

        else:
            st.warning(
                "No valid community-area records are available."
            )

    else:
        st.warning("No community-area data is available.")


# =========================================================
# RISK ANALYSIS PAGE
# =========================================================

elif page == "⚠️ Risk Analysis":

    st.markdown(
        '<div class="section-heading">Community Area Risk Analysis</div>',
        unsafe_allow_html=True
    )

    st.caption(
    "Risk scores reflect historical crime patterns and do not predict future crime probabilities."
    )

    if not areas_df.empty:

        risk_df = areas_df.copy()

        maximum_count = risk_df["total"].max()

        if maximum_count > 0:

            risk_df["risk_score"] = (
                risk_df["total"] * 100 / maximum_count
            ).round().astype(int)

            def classify_risk(score):
                if score >= 80:
                    return "Very High"
                elif score >= 60:
                    return "High"
                elif score >= 40:
                    return "Moderate"
                elif score >= 20:
                    return "Low"
                return "Very Low"

            risk_df["risk_level"] = (
                risk_df["risk_score"].apply(classify_risk)
            )

            risk_df = risk_df.rename(
                columns={
                    "community_area": "Community Area",
                    "total": "Recorded Crimes",
                    "risk_score": "Relative Risk Score",
                    "risk_level": "Risk Category"
                }
            )

            st.dataframe(
                risk_df,
                width="stretch",
                hide_index=True
            )

        else:
            st.warning("Risk scores cannot be calculated.")

    else:
        st.warning("No area data is available.")

# =========================================================
# CRIME HOTSPOT ANALYSIS PAGE
# =========================================================

elif page == "🗺️ Crime Hotspot Analysis":
    
    st.title("🗺️ Crime Hotspot Analysis")

    st.markdown(
        "Explore the geographic distribution of reported crimes "
        "and identify areas with higher recorded crime counts."
    )

    st.caption(
        "Hotspots reflect the selected historical data and filters. "
        "They do not predict that a crime will occur at a specific location."
    )

    st.divider()

    st.write(
        "Explore where recorded crimes are concentrated across Chicago. "
        "Use the filters to investigate different crime types and time periods."
    )

    try:
        # Load and cache the crime records
        hotspot_data = get_cached_hotspot_data()

        if hotspot_data.empty:
            st.warning("No crime records are available for hotspot analysis.")

        else:
            # Get the available date range
            valid_dates = hotspot_data["crime_date"].dropna()

            if valid_dates.empty:
                st.warning("No valid crime dates are available.")
            else:
                min_date = valid_dates.min().date()
                max_date = valid_dates.max().date()

                # Crime type filter
                crime_types = sorted(
                    hotspot_data["primary_type"]
                    .dropna()
                    .unique()
                    .tolist()
                )

                selected_crime = st.selectbox(
                    "Select Crime Type",
                    crime_types
                )

                # Date range filter styling
                st.markdown(
                    """
                    <style>
                    [data-testid="stDateInput"] input {
                        background-color: #FFFFFF !important;
                        color: #111111 !important;
                        -webkit-text-fill-color: #111111 !important;
                        opacity: 1 !important;
                    }

                    [data-testid="stDateInput"] input::placeholder {
                        color: #111111 !important;
                        -webkit-text-fill-color: #111111 !important;
                        opacity: 1 !important;
                    }

                    [data-testid="stDateInput"] [data-baseweb="input"] {
                        background-color: #FFFFFF !important;
                    }

                    [data-testid="stDateInput"] [data-baseweb="input"] input {
                        color: #111111 !important;
                        -webkit-text-fill-color: #111111 !important;
                        caret-color: #111111 !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                selected_dates = st.date_input(
                    "Select Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    format="DD/MM/YYYY",
                    key="hotspot_date_range"
                )

                if (
                    isinstance(selected_dates, (tuple, list))
                    and len(selected_dates) == 2
                ):
                    start_date, end_date = selected_dates

                    # Grid size controls hotspot grouping
                    grid_labels = {
                        0.0025: "Small areas",
                        0.005: "Medium areas",
                        0.01: "Large areas"
                    }

                    selected_grid_size = st.selectbox(
                        "Hotspot Area Size",
                        options=list(grid_labels.keys()),
                        index=1,
                        format_func=lambda value: grid_labels[value]
                    )

                    # Apply filters
                    filtered_data = filter_hotspot_data(
                        hotspot_data,
                        crime_type=selected_crime,
                        start_date=start_date,
                        end_date=end_date
                    )

                    st.info(
                        f"Showing {len(filtered_data):,} records for "
                        f"{selected_crime} from "
                        f"{start_date.strftime('%d %b %Y')} to "
                        f"{end_date.strftime('%d %b %Y')}."
                    )

                    if filtered_data.empty:
                        st.warning(
                            "No crime records match your selected filters."
                        )
                    else:
                        # Calculate hotspot locations
                        hotspots = get_top_hotspots(
                            filtered_data,
                            grid_size=selected_grid_size
                        )

                        # Summary metrics
                        col1, col2, col3 = st.columns(3)

                        col1.metric(
                            "Total Recorded Crimes",
                            f"{len(filtered_data):,}"
                        )

                        col2.metric(
                            "Hotspot Areas",
                            f"{len(hotspots):,}"
                        )

                        col3.metric(
                            "Highest Hotspot Count",
                            f"{int(hotspots.iloc[0]['crime_count']):,}"
                            if not hotspots.empty
                            else "0"
                        )

                        # Interactive crime density map
                        st.subheader("🌡️ Crime Hotspot Density Map")

                        st.caption(
                           "Highlights geographic areas with higher concentrations "
                           "of recorded crimes within the selected filters."
                        )

                        hotspot_map = create_hotspot_map(
                            filtered_data,
                            grid_size=selected_grid_size
                        )

                        if hotspot_map is not None:
                            st.plotly_chart(
                                hotspot_map,
                                width="stretch"
                            )
                        else:
                            st.info("A map could not be generated.")

                            
                        st.subheader("📍 Crime Count Map")

                        st.caption(
                            "Shows recorded crime counts across the geographic grid. "
                            "Use this view to compare areas with different crime volumes."
                        )

                        count_map = create_crime_count_map(
                            filtered_data,
                            grid_size=selected_grid_size
                        )

                        if count_map is not None:
                            st.plotly_chart(
                                count_map,
                                use_container_width=True
                            ) 
                        else:
                            st.info("No crime records found for the selected filters.")

                        # Top 10 hotspot areas
                        st.subheader("📍 Top 10 Crime Hotspot Areas")

                        if not hotspots.empty:
                            top_10 = hotspots.head(10).copy()

                            top_10 = top_10.rename(
                                columns={
                                    "latitude": "Latitude",
                                    "longitude": "Longitude",
                                    "crime_count": "Recorded Crimes"
                                }
                            )

                            top_10.insert(
                                0,
                                "Rank",
                                range(1, len(top_10) + 1)
                            )

                            top_10 = top_10[
                                [
                                    "Rank",
                                    "Latitude",
                                    "Longitude",
                                    "Recorded Crimes"
                                ]
                            ]

                            st.dataframe(
                                top_10,
                                width="stretch",
                                hide_index=True
                            )

                            csv_data = top_10.to_csv(
                                index=False
                            ).encode("utf-8")

                            st.download_button(
                                label="⬇️ Download Top 10 Hotspots (CSV)",
                                data=csv_data,
                                file_name="top_10_crime_hotspots.csv",
                                mime="text/csv"
                            )

                                                # Neighborhood crime analysis
                        st.divider()
                        st.subheader("🏘️ Neighborhood Crime Analysis")

                        st.write(
                            "Explore recorded crimes in Chicago's "
                            "community areas using the selected "
                            "crime type and date range."
                        )

                        neighborhood_counts = (
                            get_neighborhood_crime_counts(filtered_data)
                        )

                        if neighborhood_counts.empty:
                            st.info(
                                "No neighborhood crime data is available "
                                "for the selected filters."
                            )
                        else:
                            # Top 10 community areas
                            top_neighborhoods = (
                                neighborhood_counts.head(10).copy()
                            )

                            neighborhood_chart = px.bar(
                                top_neighborhoods,
                                x="crime_count",
                                y="community_area_name",
                                orientation="h",
                                labels={
                                    "crime_count": "Recorded Crimes",
                                    "community_area_name": (
                                        "Chicago Community Area"
                                    )
                                },
                                title=(
                                    "Top 10 Community Areas "
                                    "by Recorded Crime Count"
                                ),
                                text="crime_count"
                            )

                            neighborhood_chart.update_layout(
                                yaxis={
                                    "categoryorder": "total ascending"
                                },
                                height=500
                            )

                            st.plotly_chart(
                                neighborhood_chart,
                                width="stretch"
                            )

                            # Readable neighborhood table
                            neighborhood_table = (
                                neighborhood_counts[
                                    [
                                        "community_area",
                                        "community_area_name",
                                        "crime_count"
                                    ]
                                ]
                                .rename(
                                    columns={
                                        "community_area": (
                                            "Community Area ID"
                                        ),
                                        "community_area_name": (
                                            "Community Area Name"
                                        ),
                                        "crime_count": "Recorded Crimes"
                                    }
                                )
                            )

                            st.dataframe(
                                neighborhood_table,
                                width="stretch",
                                hide_index=True
                            )

                            # Download neighborhood counts
                            neighborhood_csv = (
                                neighborhood_table
                                .to_csv(index=False)
                                .encode("utf-8")
                            )

                            st.download_button(
                                label=(
                                    "⬇️ Download Neighborhood "
                                    "Crime Counts (CSV)"
                                ),
                                data=neighborhood_csv,
                                file_name="neighborhood_crime_counts.csv",
                                mime="text/csv",
                                key="download_neighborhood_crime_counts"
                            )

                else:
                    st.info(
                        "Please select both a start date and an end date."
                    )

    except Exception as error:
        st.error(
            f"Unable to load crime hotspot analysis: {error}"
        )

# =========================================================
# CRIME PREDICTION PAGE
# =========================================================

elif page == "🔮 Future Crime Prediction":
    st.title("🔮 Future Crime Prediction")

    st.markdown(
       "Explore historical crime patterns and view "
       "machine-learning-based estimates for the next four weeks."
    )

    st.caption(
       "Data-driven estimates based on historical Chicago crime records. "
       "Forecasts are uncertain and are not guaranteed outcomes."
    )

    st.divider()

    try:
        with st.spinner("Training the machine-learning model..."):
            results = train_and_evaluate_model()

        # Model evaluation metrics
        st.subheader("📊 Model Performance Comparison")

        st.markdown("#### Mean Absolute Error (MAE)")
        
        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Random Forest MAE",
            f"{results['mae']:.2f}"
        )

        col2.metric(
            "Previous-week MAE",
            f"{results['baseline_mae']:.2f}"
        )

        col3.metric(
            "Four-week-lag MAE",
            f"{results['seasonal_mae']:.2f}"
        )

        st.markdown("#### Root Mean Squared Error (RMSE)")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Random Forest RMSE",
            f"{results['rmse']:.2f}"
        )

        col2.metric(
            "Previous-week RMSE",
            f"{results['baseline_rmse']:.2f}"
        )

        col3.metric(
            "Four-week-lag RMSE",
            f"{results['seasonal_rmse']:.2f}"
        )

        st.metric(
            "Random Forest MAE Improvement vs Previous Week",
            f"{results['improvement_percent']:.2f}%"
        )

        st.caption(
            "MAE improvement compares Random Forest with the "
            "previous-week baseline only. Lower MAE and RMSE values "
            "indicate better prediction accuracy."
        )

        st.info(
            "MAE (Mean Absolute Error) measures the average absolute "
            "prediction error. RMSE (Root Mean Squared Error) gives "
            "more weight to larger errors. Lower values generally "
            "indicate better performance on historical test data."
        )

        # Actual vs predicted chart
        st.subheader("📊 Actual vs Predicted Crime Counts")

        test_results = results["test_results"]

        comparison = test_results.melt(
            id_vars="Week",
            value_vars=["Actual Crimes", "Predicted Crimes"],
            var_name="Type",
            value_name="Crime Count"
        )

        comparison_chart = px.line(
            comparison,
            x="Week",
            y="Crime Count",
            color="Type",
            markers=True,
            line_dash="Type",
            title="Actual vs Predicted Weekly Crime Counts",
            labels={
                "Week": "Week Starting",
                "Crime Count": "Number of Crimes",
                "Type": "Data Type"
            },
            template="plotly_white"
        )

        comparison_chart.update_layout(
            legend_title_text="",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0
            ),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=80, b=20)
        )

        comparison_chart.update_traces(
            line=dict(width=3),
            marker=dict(size=6)
        )

        st.plotly_chart(
            comparison_chart,
            width="stretch"
        )

        # Forecast next four weeks
        st.subheader("🔮 Forecast for the Next Four Weeks")

        forecast = forecast_next_weeks(
            results,
            number_of_weeks=4
        )

        
        forecast_chart = px.bar(
            forecast,
            x="Week",
            y="Predicted Crimes",
            text="Predicted Crimes",
            title="Crime Count Forecast — Next Four Weeks",
            labels={
                "Week": "Forecast Week Starting",
                "Predicted Crimes": "Estimated Number of Crimes"
            },
            template="plotly_white"
        )

        forecast_chart.update_traces(
            textposition="outside",
            cliponaxis=False
        )

        forecast_chart.update_layout(
            yaxis_title="Estimated Number of Crimes",
            xaxis_title="Forecast Week",
            showlegend=False,
            margin=dict(l=20, r=20, t=80, b=20),
            yaxis=dict(rangemode="tozero")
        )

        st.plotly_chart(
            forecast_chart,
            width="stretch"
        )

        
        st.subheader("📅 Weekly Forecast Details")

        forecast_display = forecast.copy()
        forecast_display["Week"] = pd.to_datetime(
            forecast_display["Week"]
        ).dt.strftime("%d %b %Y")

        forecast_display = forecast_display.rename(
            columns={
                "Week": "Week Starting",
                "Predicted Crimes": "Estimated Crime Count"
            }
        )

        st.dataframe(
            forecast_display,
            width="stretch",
            hide_index=True,
            column_config={
                "Week Starting": st.column_config.TextColumn(
                    "Week Starting"
                ),
                "Estimated Crime Count": st.column_config.NumberColumn(
                    "Estimated Crime Count",
                    format="%d"
                )
            }
        )

        # Download forecast
        csv_data = forecast_display.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇️ Download Forecast as CSV",
            data=csv_data,
            file_name="crime_forecast.csv",
            mime="text/csv",
            help="Download the four-week forecast as a CSV file."
        )


        st.caption(
            "Important: These are statistical estimates of aggregate "
            "weekly crime counts, not predictions of individual crimes. "
            "Forecasts are uncertain and should not be used alone to "
            "make public-safety decisions."
        )

    except Exception as error:
        st.error(
            f"Unable to generate the crime forecast: {error}"
        )

# =========================================================
# DATA EXPLORER PAGE
# =========================================================

elif page == "🔎 Data Explorer":

    st.markdown(
        '<div class="section-heading">Crime Data Explorer</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="welcome-panel">
            <div class="welcome-title">Explore Crime Data</div>
            <div class="welcome-description">
                Browse summarized crime records, compare historical trends,
                and download datasets for further analysis.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Choose a Dataset")

    dataset_choice = st.selectbox(
        "Select the dataset you want to explore",
        [
            "Crime Types",
            "Yearly Trends",
            "Community Areas"
        ],
        key="data_explorer_dataset"
    )

    if dataset_choice == "Crime Types":
        selected_df = crime_types_df
        dataset_description = (
            "Explore the distribution of reported crimes by crime type."
        )

    elif dataset_choice == "Yearly Trends":
        selected_df = yearly_df
        dataset_description = (
            "Review how reported crime counts change across years."
        )

    else:
        selected_df = areas_df
        dataset_description = (
            "Explore summarized crime information across community areas."
        )

    st.caption(dataset_description)

    # Dataset summary metrics
    total_rows = len(selected_df)
    total_columns = len(selected_df.columns)

    metric1, metric2 = st.columns(2)

    with metric1:
        st.metric("Total Records", f"{total_rows:,}")

    with metric2:
        st.metric("Total Columns", f"{total_columns:,}")

    st.markdown("---")

    # Dataset preview
    st.markdown("### Dataset Preview")

    st.caption(
        f"Showing {total_rows:,} records and "
        f"{total_columns:,} columns in the selected dataset."
    )

    if selected_df.empty:
        st.info(
            "No data is available for this dataset at the moment."
        )

    else:
        # Create a display copy with cleaner column labels
        display_df = selected_df.rename(columns={
    "crime_type": "Crime Type",
    "total": "Total Crimes",
    "year": "Year",
    "community_area": "Community Area",
    "crime_count": "Crime Count"
})

        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True
        )

        # CSV download
        csv_data = selected_df.to_csv(index=False).encode("utf-8")

        file_name = (
            dataset_choice.lower()
            .replace(" ", "_")
            + ".csv"
        )

        st.download_button(
            label="⬇️ Download Dataset as CSV",
            data=csv_data,
            file_name=file_name,
            mime="text/csv",
            use_container_width=True
        )

    st.caption(
        "Note: These are summarized datasets for exploration. "
        "The displayed record count refers to rows in the selected dataset."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
    <div class="footer-text">
        <b>Crime Pattern Prediction System</b><br>
        Built with Java, Python, SQLite, Streamlit and Plotly.<br>
        Data source: City of Chicago Open Data Portal — Crimes - 2001 to Present.
        <br><br>
    </div>
    """,
    unsafe_allow_html=True
)