import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Map;
import java.util.Scanner;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

public class Main {

    private static final String CSV_FILE = "data/chicago_crimes.csv";
    private static final String DATABASE_URL = "jdbc:sqlite:crime_data.db";

    public static void main(String[] args) {

    System.out.println("==============================================");
    System.out.println("       CRIME PATTERN PREDICTION SYSTEM");
    System.out.println("==============================================");

    try {
        createDatabase();

if (isDatabaseEmpty()) {
    System.out.println("\nDatabase is empty. Importing crime dataset...");
    importCrimeData();
} else {
    System.out.println("\nExisting database found.");
    System.out.println("Skipping CSV import.");
}

showDatabaseSummary();

        Scanner scanner = new Scanner(System.in);
        int choice;

        do {
            System.out.println("\n========== MAIN MENU ==========");
            System.out.println("1. View Top 10 Crime Types");
            System.out.println("2. View High-Crime Areas");
            System.out.println("3. View Yearly Crime Trends");
            System.out.println("4. View Community Area Risk Scores");
            System.out.println("5. Exit");
            System.out.print("Enter your choice: ");

            while (!scanner.hasNextInt()) {
                System.out.print("Please enter a number from 1 to 5: ");
                scanner.next();
            }

            choice = scanner.nextInt();

            try {
                switch (choice) {
                    case 1:
                        analyzeCrimeTypes();
                        break;

                    case 2:
                        analyzeHighRiskAreas();
                        break;

                    case 3:
                        analyzeYearlyTrends();
                        break;

                    case 4:
                        calculateCrimeRiskScores();
                        break;

                    case 5:
                        System.out.println("Thank you for using the system!");
                        break;

                    default:
                        System.out.println("Invalid choice. Please select 1 to 5.");
                }
            } catch (SQLException e) {
                System.out.println("Could not complete the selected analysis: "
                        + e.getMessage());
            }

        } while (choice != 5);

        scanner.close();

    } catch (Exception e) {
        System.out.println("\nAn error occurred:");
        System.out.println(e.getMessage());
    }
}

    private static Connection connect() throws SQLException {
        return DriverManager.getConnection(DATABASE_URL);
    }

    private static void createDatabase() throws SQLException {

        System.out.println("\nStep 1: Creating the database...");

        String sql = """
                CREATE TABLE IF NOT EXISTS crimes (
                    id TEXT PRIMARY KEY,
                    crime_date TEXT,
                    primary_type TEXT,
                    description TEXT,
                    location_description TEXT,
                    community_area TEXT,
                    year INTEGER,
                    latitude REAL,
                    longitude REAL
                )
                """;

        try (Connection connection = connect();
             Statement statement = connection.createStatement()) {

            statement.execute(sql);
        }

        System.out.println("Database created successfully.");
    }

    private static void importCrimeData()
            throws IOException, SQLException {

        Path csvPath = Path.of(CSV_FILE);

        if (!Files.exists(csvPath)) {
            throw new IOException(
                    "Dataset not found: " + csvPath.toAbsolutePath()
                    + "\nMake sure chicago_crimes.csv is inside the data folder."
            );
        }

        System.out.println("\nStep 2: Reading the Chicago dataset...");

        CSVFormat format = CSVFormat.DEFAULT.builder()
                .setHeader()
                .setSkipHeaderRecord(true)
                .setIgnoreEmptyLines(true)
                .get();

        long imported = 0;
        long skipped = 0;

        String sql = """
                INSERT OR IGNORE INTO crimes
                (id, crime_date, primary_type, description,
                 location_description, community_area, year,
                 latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """;

        try (BufferedReader reader = Files.newBufferedReader(
                    csvPath, StandardCharsets.UTF_8);
             CSVParser parser = format.parse(reader);
             Connection connection = connect();
             PreparedStatement statement = connection.prepareStatement(sql)) {

            connection.setAutoCommit(false);

            Map<String, Integer> headers = parser.getHeaderMap();

            String idColumn = findHeader(headers, "ID");
            String dateColumn = findHeader(headers, "Date");
            String typeColumn = findHeader(headers, "Primary Type");

            if (idColumn == null || dateColumn == null || typeColumn == null) {
                throw new IOException(
                        "Required CSV columns were not found.\n"
                        + "Available columns: " + headers.keySet()
                );
            }

            String descriptionColumn =
                    findHeader(headers, "Description");

            String locationColumn =
                    findHeader(headers, "Location Description");

            String areaColumn =
                    findHeader(headers, "Community Area");

            String yearColumn =
                    findHeader(headers, "Year");

            String latitudeColumn =
                    findHeader(headers, "Latitude");

            String longitudeColumn =
                    findHeader(headers, "Longitude");

            for (CSVRecord record : parser) {

                try {
                    String id = getValue(record, idColumn);
                    String date = getValue(record, dateColumn);
                    String type = getValue(record, typeColumn);

                    if (id.isBlank() || date.isBlank() || type.isBlank()) {
                        skipped++;
                        continue;
                    }

                    statement.setString(1, id);
                    statement.setString(2, date);
                    statement.setString(3, type);

                    statement.setString(
                            4, getValue(record, descriptionColumn));

                    statement.setString(
                            5, getValue(record, locationColumn));

                    statement.setString(
                            6, getValue(record, areaColumn));

                    statement.setInt(
                            7, parseInteger(getValue(record, yearColumn)));

                    statement.setDouble(
                            8, parseDouble(getValue(record, latitudeColumn)));

                    statement.setDouble(
                            9, parseDouble(getValue(record, longitudeColumn)));

                    int affectedRows = statement.executeUpdate();

                    if (affectedRows == 1) {
                        imported++;
                    } else {
                        skipped++;
                    }

                    if ((imported + skipped) % 10000 == 0 && (imported + skipped) > 0) {
                        connection.commit();
                        System.out.println(
                                "Processed " + (imported + skipped) + " records...");
                    }

                } catch (Exception e) {
                    skipped++;
                }
            }

            connection.commit();
        }

        System.out.println("\nDataset processing completed.");
        System.out.println("New records processed: " + imported);
        System.out.println("Skipped records: " + skipped);
    }

    private static String findHeader(
        Map<String, Integer> headers, String target) {

    String normalizedTarget = target
            .replace("_", "")
            .replace(" ", "")
            .trim();

    for (String header : headers.keySet()) {

        String normalizedHeader = header
                .replace("_", "")
                .replace(" ", "")
                .trim();

        if (normalizedHeader.equalsIgnoreCase(normalizedTarget)) {
            return header;
        }
    }

    return null;
}

    private static String getValue(
            CSVRecord record, String column) {

        if (column == null) {
            return "";
        }

        try {
            String value = record.get(column);
            return value == null ? "" : value.trim();
        } catch (Exception e) {
            return "";
        }
    }

    private static int parseInteger(String value) {
        try {
            return Integer.parseInt(value.trim());
        } catch (Exception e) {
            return 0;
        }
    }

    private static double parseDouble(String value) {
        try {
            return Double.parseDouble(value.trim());
        } catch (Exception e) {
            return 0.0;
        }
    }

    private static void showDatabaseSummary() throws SQLException {

        System.out.println("\nStep 3: Database summary");

        try (Connection connection = connect();
             Statement statement = connection.createStatement();
             ResultSet result = statement.executeQuery(
                     "SELECT COUNT(*) FROM crimes")) {

            if (result.next()) {
                System.out.println(
                        "Total records stored: " + result.getLong(1));
            }
        }

        System.out.println("\nDatabase location: " +
                Path.of("crime_data.db").toAbsolutePath());

        System.out.println("\nDatabase setup completed!");
    }
        private static void analyzeCrimeTypes() throws SQLException {

        System.out.println("\n========== TOP 10 CRIME TYPES ==========");

        String sql = """
                SELECT primary_type, COUNT(*) AS total
                FROM crimes
                GROUP BY primary_type
                ORDER BY total DESC
                LIMIT 10
                """;

        try (Connection connection = connect();
             Statement statement = connection.createStatement();
             ResultSet result = statement.executeQuery(sql)) {

            while (result.next()) {
                System.out.printf(
                        "%-30s : %d%n",
                        result.getString("primary_type"),
                        result.getLong("total")
                );
            }
        }
    }
        private static void analyzeHighRiskAreas() throws SQLException {

        System.out.println("\n========== TOP 10 HIGH-CRIME AREAS ==========");

        String sql = """
                SELECT community_area, COUNT(*) AS total
                FROM crimes
                WHERE community_area IS NOT NULL
                  AND TRIM(community_area) != ''
                GROUP BY community_area
                ORDER BY total DESC
                LIMIT 10
                """;

        try (Connection connection = connect();
             Statement statement = connection.createStatement();
             ResultSet result = statement.executeQuery(sql)) {

            while (result.next()) {
                System.out.printf(
                        "Community Area %-8s : %d crimes%n",
                        result.getString("community_area"),
                        result.getLong("total")
                );
            }
        }
    }
        private static void analyzeYearlyTrends() throws SQLException {

        System.out.println("\n========== YEARLY CRIME TRENDS ==========");

        String sql = """
                SELECT year, COUNT(*) AS total
                FROM crimes
                WHERE year > 0
                GROUP BY year
                ORDER BY year
                """;

        try (Connection connection = connect();
             Statement statement = connection.createStatement();
             ResultSet result = statement.executeQuery(sql)) {

            while (result.next()) {
                System.out.printf(
                        "Year %d : %d crimes%n",
                        result.getInt("year"),
                        result.getLong("total")
                );
            }
        }
    }
        private static void calculateCrimeRiskScores() throws SQLException {

        System.out.println("\n========== COMMUNITY AREA RISK SCORES ==========");

        String sql = """
                SELECT community_area, COUNT(*) AS total
                FROM crimes
                WHERE community_area IS NOT NULL
                  AND TRIM(community_area) != ''
                GROUP BY community_area
                ORDER BY total DESC
                """;

        Map<String, Long> areaCounts = new java.util.LinkedHashMap<>();
        long maxCount = 0;

        try (Connection connection = connect();
             Statement statement = connection.createStatement();
             ResultSet result = statement.executeQuery(sql)) {

            while (result.next()) {
                String area = result.getString("community_area");
                long count = result.getLong("total");

                areaCounts.put(area, count);

                if (count > maxCount) {
                    maxCount = count;
                }
            }
        }

        if (maxCount == 0) {
            System.out.println("No community area data is available.");
            return;
        }

        for (Map.Entry<String, Long> entry : areaCounts.entrySet()) {

            int score = (int) Math.round(
                    entry.getValue() * 100.0 / maxCount
            );

            String riskLevel;

            if (score >= 80) {
                riskLevel = "Very High";
            } else if (score >= 60) {
                riskLevel = "High";
            } else if (score >= 40) {
                riskLevel = "Moderate";
            } else if (score >= 20) {
                riskLevel = "Low";
            } else {
                riskLevel = "Very Low";
            }

            System.out.printf(
                    "Area %-5s | Crimes: %-7d | Score: %3d/100 | Risk: %s%n",
                    entry.getKey(),
                    entry.getValue(),
                    score,
                    riskLevel
            );
        }
    }
    private static boolean isDatabaseEmpty() throws SQLException {

    String sql = "SELECT COUNT(*) FROM crimes";

    try (Connection connection = connect();
         Statement statement = connection.createStatement();
         ResultSet result = statement.executeQuery(sql)) {

        if (result.next()) {
            return result.getLong(1) == 0;
        }
    }

    return true;
}
}