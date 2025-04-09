Fetch Take Home Exercise -  jhinojoza
-----------------------------------------
jhiojoza improvements of https://github.com/fetch-rewards/sre-take-home-exercise-python/blob/main/main.py

How to install the code
=======================

- Make sure you have the requests and yaml libraries
    - `$ pip install pyyaml`
    - `$ pip install requests`

- Clone the repo
    - `$ git clone <url>`

How to run the code
===================

- Run in the terminal the following code

::

    $ python <python_file_path> <yaml_file_path>

- The code will print in the terminal something similar to:
    - ::

        $ python c:/Users/jhino/Documents/sre-interview/main.py C:\Users\jhino\Documents\sre-interview\endpoints.yaml
        Starting the monitoring at Tue Apr  8 17:42:00 2025
    
        Iteration: 1
        Monitor endpoints Local Time: 2025-04-08T17:42:00.855524
        Print avail table Local Time: 2025-04-08T17:42:15.855460
    
        Domain           | Availability
        -----------------|-------------
        facebook.com     |         100%
        fetchrewards.com |          25%
        google.com       |         100%
        nopage.com       |           0%
        typicode.com     |         100%
    
        ---
    
        Iteration: 2
        Monitor endpoints Local Time: 2025-04-08T17:42:15.856469
        Print avail table Local Time: 2025-04-08T17:42:30.855621
    
        Domain           | Availability
        -----------------|-------------
        facebook.com     |         100%
        fetchrewards.com |          25%
        google.com       |         100%
        nopage.com       |           0%
        typicode.com     |         100%
    
        ---

- The program will also write csv-log-report with the name format as `logs_YYYY-MM-DD_HH-MM-SS.csv`
    - ::

        item,time,facebook.com,fetchrewards.com,google.com,nopage.com,typicode.com
        1,2025-04-08T17:42:00.855524,100%,25%,100%,0%,100%
        2,2025-04-08T17:42:15.856469,100%,25%,100%,0%,100%

Problems identified
===================

- `check_health()` returns a `str`
    - This is consider a bad practice, since the code might change in the future.
    - I fixed it declaring an Enum class at the beginning of the code.

- Importing `sys` inside the `__main__` function
    - Moved the import to the top part of the file.

- Extracting method, headers and body from the dict without defining the default value
    - Add the default value for each option

- The request don't have the requested timeout
    - Added the 0.5 timeout

- The domain is cosider to be the second-level-domain + top-level-domain
    - Added the part that removes the port from the URL and only considers the
      second-level-domain + top-level-domain

- Domains are being extracted from the URL on every run of the code
    - Created a new function that obtaines the domains and mapped to the urls

- Prints are being done inside the while-loop without a structure
    - Created a new funtion to print the table

- We are priting the dashboard every 15 seconds + time of checking urls
    - Now we calculate the time to sleep to be exactly what we are missing to be 15 seconds
    - Given that we can consider that each print-table and csv-append happen in constant time,
      the monitoring is also happening exactly every 15 seconds
    - ::

                           Monitoring-1  Waiting-1  Printing-1  Monitoring-2  Waiting-2  Printing-2 ...
        Time consumption: [------------][---------][----------][------------][---------][----------]...
                          [ 15 seconds            ]
                          [ 30 seconds                                                 ]
                          ...

- Logs are not being stored for future analysis
    - Create new functions to create csv file and write a new line to it on each iteration

Current problems
================

- `max_workers` in `ThreadPoolExecutor` has an actual real limit
    - Though there is no maximum number of worker threads in the ThreadPoolExecutor,
      the system will have an upper limit of the number of threads that can be created
      based on how much main memory (RAM) is available.
- `urls_to_domains` dict can be optimized in memory if we normalize the domains
    - This part I leave as a TODO, since it would increase the readability difficulty
