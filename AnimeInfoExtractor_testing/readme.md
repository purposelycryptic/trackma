## Trackma AnimeInfoExtractor.py Tester

anime_extractor_test allows for testing a spreadsheet of filenames to see what information Trackma's AnimeInfoExtractor will pull from each one, and how it ends up with the information it does by showing the output of each function it runs. This information is written to the 'summary.xlsx' and 'output.xlsx' spreadsheets, respectively.

* For testing, comment out the last line of the "def __init__(self, filename):" function in your AnimeInfoExtractor.py before use (This has already been done in the included sample version)
* Also, be sure to set the path variable to match the location of your local files.

## How to Use

- Put filenames to be tested in the first column of 'files.xlsx' (The included version is pre-filled with random test names, just replace with your own).
- Run anime_extractor_test_v0.9.py.
- The two included blank Excel documents, 'output.xlsx' and 'summary.xlsx' should now be filled with the results:
- summary.xlsx shows only the final results provided by the AnimeInfoExtractor to Trackma for each filename.
- output.xlsx has a sheet for each filename, along with the values of each attribute after each function AnimeInfoExtractor calls is run, allowing you to see precisely where any issue in recognition is occuring.
   
   #### NOTE
   anime_extractor_test_v0.9.py will fail to run if the necessary Excel files do not exist, as it is unable to create new blank files. If you happen to delete one of the output files, just create a new blank one with the same filename.
