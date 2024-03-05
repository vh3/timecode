# timecode_report.py - A script to produce a simple SQL summary report from an SQLite database.
#
# CHANGELOG:
# Version 1.1 - Modifications to include rounding of duration minutes to 1 decimal place,
#               addition of average time per unit (TPU) calculation for each task,
#               and appending the total duration at the end of the report.
#
# This script reads data from an SQLite database and generates a summary report
# grouped by project and task. It calculates the duration in minutes for each task,
# rounded to 1 decimal place, and calculates the average time per unit for each task.
# The final row of the output file lists the total number of minutes recorded.

import getpass
import os
import sqlite3
import pandas as pd

def get_current_user_id():
    """Retrieve the currently logged-in user, cross-platform."""
    return getpass.getuser()

# Constants
USERID = get_current_user_id()
print("userid=:", USERID)
DB_PATH = os.path.join("/Users", USERID, "Documents", "timecode.sqlite")
OUTPUT_FILENAME = os.path.join("/Users", USERID, "Documents", "timecode_report.csv")
TABLE_NAME = "timecode"

def generate_report(db_path, table_name, output_filename):
    """
    Generate a summary report from an SQLite database, including average time per unit and total minutes.
    
    Parameters:
    - db_path: Path to the SQLite database file.
    - table_name: Name of the table to query data from.
    - output_filename: Path to the output CSV file for the summary report.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    # SQL query to extract data, calculate duration, round to 1 decimal place, and group by project and task
    query = f"""
    SELECT project, Code, task, 
           COUNT(*) AS task_count,
           ROUND(SUM(strftime('%s', datetime_end) - strftime('%s', datetime_start)) / 60.0, 1) AS duration_minutes,
           ROUND(AVG((strftime('%s', datetime_end) - strftime('%s', datetime_start)) / 60.0), 1) AS avg_tpu
    FROM {table_name}
    GROUP BY project, task
    """
    
    # Execute the query and load results into a DataFrame
    df = pd.read_sql_query(query, conn)
     
    # Calculate the total minutes recorded and task count
    total_minutes = df['duration_minutes'].sum().round(1)
    total_tasks = df['task_count'].sum()
    avg_tpu = df['avg_tpu'].mean().round(1)  # Assuming TPU count means averaging TPU across tasks
    
    # Append a row with total minutes, task count, and TPU count to the DataFrame
    total_row = pd.DataFrame([["Total", "", "All Tasks", total_tasks, total_minutes, avg_tpu]], columns=df.columns)
    df = pd.concat([df, total_row], ignore_index=True)
    
    # Close the database connection
    conn.close()
    
    # Save the summary table to a CSV file
    df.to_csv(output_filename, index=False)
    print(f"Summary report generated: {output_filename}")

if __name__ == "__main__":
    generate_report(DB_PATH, TABLE_NAME, OUTPUT_FILENAME)
