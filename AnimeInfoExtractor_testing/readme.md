## Trackma AnimeInfoExtractor.py Tester v0.9.0.1

#### Changelog:
- anime_extractor_test.py now n longer requires manually setting the path variable.
- blank 'output.xlsx' and 'summary.xlsx' no longer required to run; instead, they are generated during operation, and their filenames now include a timestamp suffix, so that each run generates unique output files.

##

## Summary
anime_extractor_test allows for testing a spreadsheet of filenames to see what information Trackma's AnimeInfoExtractor will pull from each one, and how it ends up with the information it does by showing the output of each function it runs. This information is written to 'output YYYY.MM.DD  HH.MM.SS.xlsx' and 'summary YYYY.MM.DD  HH.MM.SS.xlsx' where  `YYYY.MM.DD  HH.MM.SS` are the current time and date.

I am running this on Windows, and, obviously, the use of Excel spreadsheets makes it significantly less useful if you don't have use Excel - I am not entirely sure if an Excel installation is actually required for it to work, as I don't have a machine without it readily available to test this possibility on. If it does not, the spreadhseets should work fine with Google Sheets, etc.

WHen the spreadsheets are generated, they are not auto-formatted, so you will likely want to 'Select All' then 'Auto-fit Column Width', so that everything is properly spaced and legible.

* For testing, comment out the last line of the `def __init__(self, filename):` function in your AnimeInfoExtractor.py before use (This has already been done in the included sample version)

### Dependencies

- _*openpyxl*_ is required for the Excel operations - you can install it from the command line using pip.

## How to Use

- Put filenames to be tested in the first column of 'files.xlsx' (The included version is pre-filled with random test names, just replace with your own).
- Run anime_extractor_test.py.
- Two Excel documents, 'output YYYY.MM.DD  HH.MM.SS.xlsx' and 'summary YYYY.MM.DD  HH.MM.SS.xlsx' should have been generated and filled with the results:
- The summary spreadsheet shows only the final results provided by the AnimeInfoExtractor to Trackma for each filename
- The output spreadsheet has a sheet for each filename, along with the values of each attribute after each function AnimeInfoExtractor calls is run, allowing you to see precisely where any issue in recognition is occuring.
