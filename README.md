PDF scraper designed to access tables from statistical yearbooks.

Notes on use:
    - Search pdf or directory for the title of the desired table.
        This could be ascertained by manually viewing the table of contents for one
        of the documents
    - Queries should be provided based on the full or shortened table name.

    - **Make sure to set the input and output directories via environment variables before using.**
    TO RUN: run directory_scraper.py or file_scraper.py as module

Operation flow is as follows:
    1. User enters command/runs program.
    Print statement.
    2. Program begins scraping pdfs.
    Print statement.
    3. For each pdf:
        a. program tries to extract text. (print)
        b.  if text doc:
                search for query using text
            else if scanned:
                search table of contents to get page number of query.
                search range of pages around page number for query.
        c. report page matches (p)
        d. if matches != 2 notify user and save to list in end report. (include doc name and error message)
            - if no matches can be found for a given text also note this.
        f. export matches to pdf (print)
    4. When finished, notify user and export match pdf to output directory.
    5. Print report.