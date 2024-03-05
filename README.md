# timecode

Requirement:  a method for measuring the time it takes for specific tasks as you might need if you were tracking time for billing purposes or tracking counts and time for tasks if you were attempting to calculate before-automation state of an activity in order to compare to the after-automation state. 

A small python script with a Tk gui to allow a user to track time coding for multiple projects and tasks.  Scripts were first generated and re-generated with whole chatgpt from .specs file input.  Final testing and iteration was done by generating smaller pieces of code and fixes and integrating them into the code.

This system has 3 parts:
1.  timecode_ui.py - the tiny interface used to generate timed records.  This generates a .csv file for each start and stop toggle in a destination folder.
2.  timecode_watcher.py.  A long-running script that waits for new files to be generated and dropped into the destination folder.  These files are read, uploaded to an SQLITE database, then moved to an ARCHIVE sub-folder.
3. timecode_report.py - a simple example of reporting from the SQLITE database with SQL statements to a .csv test file to demonstrate the possibilities for output.

All the code was generated and tested on macos.  In this configuration, files are delivered to the current logged-in user's Documents folder.  Small tweaks to folders will be needed to make this work on Windows.
