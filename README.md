# Crime Pattern Prediction System

### Analyzing Crime Data to Identify Patterns, Trends, and High-Risk Areas

## 📌 Project Overview

The **Crime Pattern Prediction System** is a data-driven application developed to analyze historical crime records, identify crime patterns, understand crime trends, and highlight areas with a higher concentration of reported criminal incidents.

The system uses crime data from Chicago to explore crime distribution across different time periods and geographical locations. By organizing and analyzing historical records, it helps users understand crime patterns and supports data-informed decision-making.

Developed using **Java and Maven**, this project demonstrates how software development, database management, and crime data analysis can be combined to build a practical crime analytics application.

## 🎯 Objectives

- Analyze historical crime records to identify recurring crime patterns.
- Understand crime trends across different years and time periods.
- Identify geographical areas with high concentrations of reported crimes.
- Analyze crime distribution by crime type and location.
- Explore crime records using relevant filters.
- Present crime-related information in an organized and understandable format.
- Explore historical data to support crime trend analysis and prediction.

## ✨ Key Features

### 1. Crime Data Management
- Store and manage historical crime records.
- Retrieve crime information from the project's database.
- Process structured crime data for further analysis.

### 2. Crime Pattern Analysis
- Examine the distribution of different crime types.
- Identify frequently reported crimes.
- Explore patterns within historical crime records.

### 3. Yearly Crime Trend Analysis
- Analyze crime records across different years.
- Compare crime counts between available time periods.
- Identify changes in reported crime patterns over time.

### 4. Geographical Crime Analysis
- Examine crime distribution across geographical locations.
- Identify areas with higher concentrations of reported incidents.
- Analyze location-based crime patterns using available geographical coordinates.

### 5. Crime Hotspot Identification
- Group geographical coordinates into grid-based areas.
- Calculate the number of reported crimes within each grid cell.
- Identify locations with relatively high crime concentrations.
- Display hotspot information, including crime counts and commonly reported crime types, where available.

### 6. Crime Data Exploration
- Access stored crime records.
- Examine relevant crime attributes.
- Support further investigation through structured data exploration.

### 7. Crime Pattern Prediction
- Use historical crime patterns as the basis for exploring potential future trends.
- Support the analysis of crime behavior over time.
- Provide a foundation for data-driven crime trend forecasting.

*Note: The availability of individual features depends on their implementation in the current project version.*

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Java | Core programming language |
| Apache Maven | Project build and dependency management |
| SQLite | Local database for storing crime records |
| SQL | Database queries and data retrieval |
| CSV | Structured crime dataset format |
| Git | Version control (if configured) |
| GitHub | Source code hosting and project sharing |

## 📂 Dataset Information

This project uses historical crime records from Chicago.

**Dataset source:** Chicago Data Portal — City of Chicago.

The dataset contains information about reported crime incidents, including crime classification, dates, geographical coordinates, and location details.

### Dataset Attributes

The available dataset includes the following fields:

- `id` — Unique identifier for a crime record.
- `case_number` — Police case number.
- `date` — Date and time of the reported incident.
- `block` — Block-level location information.
- `iucr` — Illinois Uniform Crime Reporting code.
- `primary_type` — Primary classification of the crime.
- `description` — Description of the reported incident.
- `location_description` — Description of the incident location.
- `arrest` — Indicates whether an arrest was recorded.
- `domestic` — Indicates whether the incident was classified as domestic.
- `beat` — Police beat identifier.
- `district` — Police district identifier.
- `ward` — Ward identifier.
- `community_area` — Community area identifier.
- `fbi_code` — FBI crime classification code.
- `x_coordinate` — X-coordinate of the location.
- `y_coordinate` — Y-coordinate of the location.
- `year` — Year associated with the record.
- `updated_on` — Date the record was last updated.
- `latitude` — Latitude of the incident location.
- `longitude` — Longitude of the incident location.
- `location` — Geographic location information, where available.

### Dataset Summary

| Attribute | Details |
|---|---|
| Dataset location | Chicago, Illinois, USA |
| Data format | CSV |
| Database | SQLite |
| Records imported | 404,179 |
| Date range in imported data | January 2025 – September 2026 |
| Main analytical dimensions | Crime type, time, and geographical location |

The record count and date range above describe the imported dataset used during development. They may differ if the database is updated.

**Official dataset source:** [Chicago Data Portal — Crimes](https://data.cityofchicago.org/browse?tags=crime)

The dataset contains reported crime records. Its contents should not be interpreted as a complete representation of all crimes or as proof that a particular person or location is dangerous.

## 🏗️ Project Architecture

The system follows a structured application workflow:

```text
              Chicago Crime Dataset
                       |
                       v
              Data Import Process
                       |
                       v
                SQLite Database
                  crime_data.db
                       |
                       v
              Java Application
                       |
                       v
             Crime Data Processing
                       |
                       v
             Crime Pattern Analysis
                       |
          +------------+------------+
          |            |            |
          v            v            v
       Temporal    Geographical   Crime Type
       Analysis      Analysis      Analysis
          |            |            |
          +------------+------------+
                       |
                       v
              Analysis Results
                       |
                       v
          Crime Insights and Trends
```

This diagram represents the overall analytical workflow. Adapt it if the implemented application uses a different execution flow.

## 📋 Prerequisites

Before running the project, ensure that the following software is installed:

- **Java Development Kit (JDK):** A version compatible with the project's Maven configuration.
- **Apache Maven:** For compiling, testing, and packaging the application.
- **Git:** Optional, for cloning the repository.
- **Visual Studio Code** or another Java-compatible IDE.
- **SQLite database file:** Required if the application uses the pre-populated local database.

Verify your Java installation:

```bash
java -version
```

Verify the Java compiler:

```bash
javac -version
```

Verify Maven:

```bash
mvn -version
```

## 🚀 Installation and Setup

### Step 1: Clone the Repository

Replace `<your-github-username>` with your actual GitHub username.

```bash
git clone https://github.com/<your-github-username>/Crime_Pattern_Prediction_System.git
```

Navigate to the project directory:

```bash
cd Crime_Pattern_Prediction_System
```

Alternatively, download the project as a ZIP file from GitHub and extract it.

### Step 2: Verify the Project Structure

A typical Maven project uses the following structure:

```text
Crime_Pattern_Prediction_System/
│
├── src/
│   ├── main/
│   │   └── java/
│   │       └── ...
│   │
│   └── test/
│       └── java/
│           └── ...
│
├── data/
│   └── ...
│
├── crime_data.db
├── pom.xml
├── README.md
└── .gitignore
```

This is an illustrative structure. The actual folders and files may differ depending on your implementation.

### Step 3: Build the Project

Run the following command from the project root directory:

```bash
mvn clean package
```

Maven will clean previous build outputs, compile the application, run configured tests, and package the project if the build succeeds.

### Step 4: Run the Application

The correct command depends on how the Java application is configured.

If your Maven project is configured with the Maven Exec Plugin and the appropriate main class, run:

```bash
mvn exec:java
```

Alternatively, if the project includes a suitable executable JAR, run:

```bash
java -jar target/<application-name>.jar
```

Replace `<application-name>.jar` with the actual generated JAR filename.

If the project uses a menu-driven Java application, follow the instructions displayed in the terminal after starting the program.

**Important:** The application entry point and Maven plugins must be configured correctly for these commands to work. Use the actual main class and build configuration from your project.

## 🗄️ Database Information

The project uses SQLite to store and retrieve crime records.

**Database file:** `crime_data.db`

The database allows the application to access structured crime information without requiring a separate database server.

Typical database operations include:

- Reading stored crime records.
- Filtering records by relevant attributes.
- Retrieving records for a particular time period.
- Aggregating crime counts.
- Supporting geographical and temporal analysis.

If the database is not included in the repository, create or obtain it using the project's data-import procedure.

Do not commit sensitive credentials or unnecessary generated files to version control.

## 📊 Analysis Methodology

The project analyzes crime records using several dimensions.

### Temporal Analysis

Crime records are examined according to their recorded dates and years. Aggregating records over time makes it possible to compare crime counts and explore changes in reported crime patterns.

### Crime Type Analysis

Records are grouped by their primary crime classifications to identify frequently reported crime categories.

### Geographical Analysis

Available latitude and longitude coordinates are used to examine the spatial distribution of reported crime incidents.

### Hotspot Analysis

Geographical coordinates can be grouped into grid cells. The number of crime records within each cell is calculated to identify locations with relatively high incident concentrations.

A grid-based approach helps summarize spatial patterns, although results depend on the selected grid size and data quality.

### Prediction and Forecasting

Historical crime data can be used to explore potential future trends. The reliability of any forecast depends on the implemented prediction method, the quality of the input data, and evaluation against previously unseen records.

The presence of historical patterns does not guarantee that future incidents will follow the same patterns.

## 🧪 Testing

The project should be tested to verify that its components work correctly.

Suggested testing areas include:

| Test Area | Expected Result |
|---|---|
| Application startup | Application starts without unexpected errors |
| Database connection | Application connects to the configured SQLite database |
| Data retrieval | Crime records can be retrieved successfully |
| Crime classification | Records are grouped using the correct crime categories |
| Date filtering | Records outside the selected period are excluded |
| Yearly analysis | Crime counts are calculated for the selected years |
| Geographical analysis | Valid coordinates are processed correctly |
| Hotspot analysis | Crime counts are aggregated by geographical grid cells |
| Empty dataset handling | The application handles missing results gracefully |
| Invalid input handling | Invalid inputs do not cause unhandled application failures |
| Maven build | The project compiles and packages successfully |

Run the project's configured tests with:

```bash
mvn test
```

Run the complete Maven build with:

```bash
mvn clean package
```

Record the actual results of these tests before publishing your final project report.

## 🔒 Limitations

- The analysis depends on the accuracy and completeness of the available crime records.
- Reported crime data may not represent every incident that occurred.
- Missing or invalid geographical coordinates can affect hotspot analysis.
- Results may change when the dataset is updated.
- Geographical hotspots indicate concentrations of recorded incidents, not certainty about future crimes.
- Forecasts, when implemented, are estimates and should not be treated as guaranteed outcomes.
- Historical associations do not establish causation.
- The system should support analysis and decision-making rather than replace professional judgment.

## 🔮 Future Enhancements

Possible improvements include:

- Integrating regularly updated crime datasets.
- Developing more advanced time-series forecasting models.
- Comparing forecasting methods using appropriate evaluation metrics.
- Improving interactive geographical visualizations.
- Adding additional geographical and temporal filters.
- Improving dashboard accessibility and usability.
- Introducing automated data-import workflows.
- Adding more comprehensive automated tests.
- Deploying the application for online access, where technically appropriate.

These are potential enhancements and should not be interpreted as features that are already implemented.

## 👩‍💻 Author

**Jothi Cherina K**

B.Tech CSE — Artificial Intelligence and Machine Learning

GitHub: [jothicherina](https://github.com/jothicherina)

## 📄 License

This project is licensed under the [MIT License](LICENSE).

The MIT License allows others to use, copy, modify, merge, publish, distribute, sublicense, and sell copies of the project's licensed code, subject to the license terms.

See the [LICENSE](LICENSE) file for the complete license text.

**Note:** The license applies to the project materials you own. The Chicago crime dataset and third-party dependencies may be subject to separate licensing terms.

## 🙏 Acknowledgements

- City of Chicago for providing publicly accessible crime data.
- The open-source community for the tools and technologies used in software development.
- Academic guidance and project support received during development.

---

⭐ **If you find this project interesting, consider starring the repository on GitHub.**
