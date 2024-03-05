# timecode_watcher.py - Script to watch a specified folder and load new records in new time coding files to a database.
#
# CHANGELOG:
# Version 1.0 - Initial version.
#   - Implemented watcher functionality to monitor for new .csv files and process them into the SQLite database.
#   - Added functionality to create the database and table if they do not exist.
#   - Files are moved to ARCHIVE folder after processing.

import glob
import time
import os
import getpass
import sqlite3
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def get_current_user_id():
    """Retrieve the currently logged-in user, cross-platform."""
    return getpass.getuser()

userid = get_current_user_id()
print(userid)

# Constants
INPUT_FOLDER = os.path.join("/Users", userid, "Documents")
print(INPUT_FOLDER)
ARCHIVE_FOLDER = os.path.join(INPUT_FOLDER, "ARCHIVE")
print(ARCHIVE_FOLDER)
DB_PATH = "timecode.sqlite"
TABLE_NAME = "timecode"

# Ensure archive directory exists
if not os.path.exists(ARCHIVE_FOLDER):
    os.makedirs(ARCHIVE_FOLDER)
    print("Created ARCHIVE Folder: ", ARCHIVE_FOLDER)

# Function to check and create the database and table if they do not exist
def check_or_create_db():
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        userid TEXT,
        datetime_start TEXT,
        datetime_end TEXT,
        project TEXT,
        user_entered_identifier TEXT,
        task TEXT,
        Code TEXT
    )
    ''')
    
    # Close connection
    conn.commit()
    conn.close()


def process_existing_files(prefix):
    """
    Process all existing files in the INPUT_FOLDER that match the pattern 'prefix.*.csv'
    """
    # Construct the pattern to match files.  Example timecode.12a556c2234123a5.cav
    pattern = os.path.join(INPUT_FOLDER, prefix, ".*.csv")
    
    # Find all files in INPUT_FOLDER matching the pattern
    for filename in glob.glob(pattern):
        print(f"Processing existing file: {filename}")
        try:
            # Process each file
            process_and_move_file(os.path.basename(filename))
        except FileNotFoundError as e:
            print(f"Error processing file {filename}: {e}")
        except Exception as e:
            print(f"Unexpected error processing file {filename}: {e}")
        time.sleep(1)  # Optional: sleep for a bit between processing files

# Function to process and move the file
def process_and_move_file(filename):
    
    # Construct the full path for the file
    file_path = os.path.join(INPUT_FOLDER, filename)
    
    # Retry mechanism with a delay
    for attempt in range(5):  # Try up to 5 times
        try:
            # Try to read the CSV file into a DataFrame
            df = pd.read_csv(file_path)
            break  # Success, exit the loop
        except FileNotFoundError:
            print(f"Attempt {attempt + 1}: File not found, retrying in 2 seconds...")
            time.sleep(2)  # Wait for 2 seconds before retrying
    else:
        # If all attempts fail, raise an error
        raise FileNotFoundError(f"Failed to find the file after several attempts: {file_path}")
       
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_PATH)
    
    # Insert data into the database.  We are assuming the data is in a perfect order matching the db setup.  TODO:  be more specific
    df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
    
    # Close connection
    conn.close()
    
    # Move file to ARCHIVE folder
    os.rename(os.path.join(INPUT_FOLDER, filename), os.path.join(ARCHIVE_FOLDER, filename))

# Watcher event handler
class WatcherEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Check if the created file is a CSV
        if event.is_directory or not event.src_path.endswith('.csv'):
            return
        
        # Process and move the file
        filename = os.path.basename(event.src_path)
        print("Found file:", filename)
        process_and_move_file(filename)
        print("File moved.")

# Main function to start the watcher
def start_watcher():
    print("Starting watcher on folder:",INPUT_FOLDER)
    check_or_create_db()
    event_handler = WatcherEventHandler()
    observer = Observer()
    observer.schedule(event_handler, INPUT_FOLDER, recursive=False)
    observer.start()
    try:
        while True:
            # Run indefinitely
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":

    # Helper function to process any existing files manually.  Specify the file prefix.  Our naming convention has "timecode" as the prefix
    prefix = "timecode"
    process_existing_files(prefix)

    # Start the regular watcher for any new files
    start_watcher()
