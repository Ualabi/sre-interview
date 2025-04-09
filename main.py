# jhinojoza: Moved sys to the top part of the file where all imports are done
#            and added the enum class
import datetime
import csv
import requests
import sys
import time
import yaml
from collections import defaultdict
from enum import Enum, verify, UNIQUE
from concurrent.futures import ThreadPoolExecutor

# jhinojoza: Fix the response codes
@verify(UNIQUE)
class ResponseCode(Enum):
    UP = "UP"
    DOWN = "DOWN"

# Function to load configuration from the YAML file
def load_config(file_path) -> list[dict[str: any]]:
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Function to perform health checks
def check_health(endpoint) -> ResponseCode:
    url = endpoint['url']
    # jhinojoza: Added default cases
    method = endpoint.get('method', 'GET')
    headers = endpoint.get('headers', None)
    body = endpoint.get('body', None)

    # jhinojoza: added timeout of 0.5 seconds and timeout exception
    try:
        response = requests.request(method, url, headers=headers, json=body, timeout=0.5)
        if 200 <= response.status_code < 300:
            return ResponseCode.UP
        else:
            return ResponseCode.DOWN
    except requests.exceptions.Timeout:
        return ResponseCode.DOWN
    except requests.RequestException:
        return ResponseCode.DOWN

# Main function to monitor endpoints
def monitor_endpoints(file_path):
    config = load_config(file_path)
    domain_stats = defaultdict(
        lambda: {ResponseCode.UP: 0, ResponseCode.DOWN: 0, "TOTAL": 0}
    )

    # A list where the response codes for each url will be stored on each iteration
    number_of_urls = len(config)
    response_codes = [None for _ in range(number_of_urls)]

    # jhinojoza: We can improve the code by mapping the urls to the domains just once
    urls_to_domains, sorted_domains = extract_domains(config)
    size_longest_domain = max([len(domain) for domain in sorted_domains])
    availabilities = {domain: None for domain in sorted_domains}
    iteration = 0

    # Printing the start time of the code
    start_time = time.time()
    print("Starting the monitoring at {}\n".format(time.ctime(start_time)))
    
    # Write CSV file
    file_name = create_csv_file(sorted_domains)

    # Loop to monitor the endpoints
    while True:
        iteration += 1

        # Time when we start checking the health of the endpoints
        monitoring_time = datetime.datetime.now()

        # Using ThreadPoolExecutor to manage threads
        with ThreadPoolExecutor(max_workers=min(1000,number_of_urls)) as executor:
            # Submit tasks and keep track of the futures
            futures = [executor.submit(check_health, config[i]) for i in range(number_of_urls)]
    
            for i, future in enumerate(futures):
                result = future.result()  # Blocking call to get the result of each task
                response_codes[i] = result
        
        # This part executes once we already have the results of checking all endpoints
        for i, endpoint in enumerate(config):
            result = response_codes[i]
            domain = urls_to_domains[endpoint["url"]]
            domain_stats[domain][result] += 1
            domain_stats[domain]["TOTAL"] += 1

        # Calculate the availabity per domain
        for domain, stats in domain_stats.items():
            availability = round(100 * stats[ResponseCode.UP] / stats["TOTAL"])
            availabilities[domain] = availability
        
        # We want to make sure that we print the dashboard every 15 seconds
        curr_time = time.time()
        waiting_time = 15*iteration + start_time - curr_time
        # Removing possible negative times
        time.sleep(max(waiting_time, 0))

        # Print the availability table on the terminal
        print_table(iteration, monitoring_time, size_longest_domain, availabilities, sorted_domains)
        # Write the next line in the csv report-file
        write_line_csv_file(file_name, iteration, monitoring_time, availabilities, sorted_domains)

# jhinojoza: Funtion to extract the map of urls_to_domains and the list of sorted
def extract_domains(config) -> tuple[dict[str: str], list[str]]:
    # domain = Second-Level-Domain + Top-Level-Domain
    domains_set = set()
    urls_to_domains = {}
    for endpoint in config:
        raw_url = endpoint["url"]
        # Obtain the hostname without the port
        hostname = raw_url.split("//")[-1].split("/")[0].split(":")[0]
        # Keep just Second-Level-Domain + Top-Level-Domain
        domain = ".".join(hostname.split(".")[-2:])
        # Add the map from the raw_url to the domain
        urls_to_domains[raw_url] = domain
        # Add the domain
        domains_set.add(domain)
    # We sort the domains
    domains = sorted(domains_set)

    return urls_to_domains, domains

# jhinojoza: Function that prints the table
def print_table(iteration, monitoring_time, size_longest_domain, availabilities, sorted_domains):
    # Log cumulative availability percentages
    print("Iteration: {}".format(iteration))
    print("Monitor endpoints Local Time: {}".format(monitoring_time.isoformat()))
    print("Print avail table Local Time: {}\n".format(datetime.datetime.now().isoformat()))

    # Print the header of the availability table
    header_spaces = " "*max(0, size_longest_domain-6)
    print("Domain{} | Availability".format(header_spaces))

    # Print the division line
    print("-"*size_longest_domain+"-|-------------")

    # Print a line in the availability table
    for domain in sorted_domains:
        availability = availabilities[domain]
        domain_spaces = " "*(size_longest_domain-len(domain))
        percentage_spaces = " "*(3-len(str(availability)))
        print("{}{} |         {}{}%".format(
            domain, domain_spaces, percentage_spaces, availability))
    
    # Division line between tables
    print("\n---\n")

# jhinojoza: Function that writes the csv file
def create_csv_file(sorted_domains) -> str:
    curr_time = datetime.datetime.now()
    file_time = curr_time.strftime("%Y-%m-%d_%H-%M-%S")
    file_name = 'logs_{}.csv'.format(file_time)
    with open(file_name, 'w+', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['item', 'time'] + sorted_domains)
    return file_name

# jhinojoza: Function that appends a new line to the csv file
def write_line_csv_file(file_name, iteration, monitoring_time, availabilities, sorted_domains):
    next_line = [iteration, monitoring_time.isoformat()]
    for domain in sorted_domains:
        next_line.append('{}%'.format(availabilities[domain]))
    with open(file_name, 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(next_line)

# Entry point of the program
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python monitor.py <config_file_path>")
        sys.exit(1)

    config_file = sys.argv[1]
    try:
        monitor_endpoints(config_file)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
