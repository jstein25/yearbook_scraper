PDF scraper designed to access tables from statistical yearbooks.

Notes on use:
    - Search pdf or directory for the title of the desired table.
        This could be ascertained by manually viewing the table of contents for one
        of the documents, or by getting the Table of Contents via pdf_tools.get_pages_in_range().
    - Queries should be provided based on the full or shortened table name.
    Try not to include something which will yield > 2 results, otherwise the program may not include
    that result in the output. (Results of a search should contain one match from ToC and one from the body.)

    - Make sure to set the input and output directories via environment variables before using.
    - Title pages dividing each table can be set based on preference.

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
                search for query using ocr
        c. report page matches (p)
        d. if matches != 2 notify user and save to list in end report. (include doc name and error message)
            - if no matches can be found for a given text also note this.
        e. get page of second match in list
        f. export match to pdf (print)
    4. When finished, notify user and export match pdf to output directory.
    5. Print report.