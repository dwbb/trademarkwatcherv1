import re
import os
import json
import csv
import tess_scraper_functions as selenium

min_confidence_score = 15

def trademark_formatter(mark_registry):
### Checks if the registry is a file or is a string. Opens and assigns to variable if file and assigns to variable if string.
### Accepts file or string of trademark record as argument
  if os.path.exists(mark_registry):
    mark_content = open(mark_registry).read()
  else:
    mark_content = mark_registry

  return mark_content

def mark_category_check(mark_registry):
### Checks if trademark is filed under one of the trademark classes relevant to surveillance.
### 009 (electrical and scientific apparatuses); 042 (computer and analytic); 045(personal and legal services)
### Accepts file or string of trademark record as argument
    mark_content = trademark_formatter(mark_registry)
    match = re.search(r'IC 009', mark_content) or re.search(r'IC 035', mark_content) or re.search(r'IC 042', mark_content) or re.search(r'IC 045', mark_content)
    ### Returns false if match not found and true is one is found
    if match is not None:
        return True
    else:
        return False

def trademark_serial(mark_registry):
### Uses Regex to pull trademark registration serial number
### Accepts file or string of trademark record as argument
    mark_content = trademark_formatter(mark_registry)

    serial_num = re.search(r'Serial Number\s+(\d{8})', mark_content)

    if serial_num is None:
        serial_num = re.search(r'(\d{8})', mark_content)

    try:
        serial_num = serial_num.group(1)
    except:
        serial_num = "Serial Number Not Found"

    return serial_num

def trademark_date(mark_registry):
### Uses Regex to pull trademark registration serial number
### Accepts file or string of trademark record as argument
    mark_content = trademark_formatter(mark_registry)

    mark_date = re.search(r'Filing Date\s+(\w+\s\d+\,\s\d+$)', mark_content)
    #serial_num = re.search(r'(\d{8})', mark_content)
    mark_date = mark_date.group(1)

    return mark_date

def trademark_name(mark_registry):
### Uses Regex to pull trademark registration mark name
### Accepts file or string of trademark record as argument
    mark_content = trademark_formatter(mark_registry)

    mark_name = re.search(r'Word Mark\s?(.+)', mark_content)

    # Checks for entries without Mark Name
    if mark_name is not None:
        mark_name = mark_name.group(1)
    else:
        mark_name = "Unnamed Mark"

    return mark_name

def trademark_owner(mark_registry):
### Uses Regex to pull trademark registration mark owner
### Accepts file or string of trademark record as argument
    mark_content = trademark_formatter(mark_registry)

    # Gets owner name
    mark_owner = re.search(r'Owner\s?[\(REGISTRANT\)|\(APPLICANT\)]\s(.+)\s+[\non-profit|\(s\/a\)|LIMITED|PRIVATE|LLP|congress|corporation|JOINT|Limited|INDIVIDUAL|Inc\.|\(gmbh\)|\(S|\(A|\(a|CORPORATION|private|\(ltd\.\)|\(b\.v\.\)]', mark_content)

    if mark_owner is None:
        mark_owner = re.search(r'Owner\s(\(REGISTRANT\)|\(APPLICANT\))\s?(.+)', mark_content)
        mark_owner = mark_owner.group(2)
    else:
        mark_owner = mark_owner.group(2)

    return mark_owner

def trademark_classes(mark_registry):
### Uses Regex to pull relevant  trademark class(es)
### Accepts file or string of trademark record as argument
    mark_content = trademark_formatter(mark_registry)
    mark_class_list = re.findall(r'IC\s009|IC\s035|IC\s042|IC\s045', mark_content)
    mark_class = ', '.join(mark_class_list)

    return mark_class

def trademark_description(mark_registry):
### Uses Regex to pull trademark registration relevant class mark description
### Accepts file or string of trademark record as argument
    mark_content = trademark_formatter(mark_registry)

    mark_description = ''

    ### Checks for each relevant class and creates a string of each present in a given record
    mark_descrip = re.search(r'(IC 009\. ).+ G & S: (.+)', mark_content)
    if mark_descrip is not None:
      mark_descrip009 = mark_descrip.group(1) + mark_descrip.group(2)
      mark_description += mark_descrip009 + '\n'

    mark_descrip = re.search(r'(IC 035\. ).+ G & S: (.+)', mark_content)
    if mark_descrip is not None:
        mark_descrip035 = mark_descrip.group(1) + mark_descrip.group(2)
        mark_description += mark_descrip035 + '\n'

    mark_descrip = re.search(r'(IC 042\. ).+ G & S: (.+)', mark_content)
    if mark_descrip is not None:
        mark_descrip042 = mark_descrip.group(1) + mark_descrip.group(2)
        mark_description += mark_descrip042 + '\n'

    mark_descrip = re.search(r'(IC 045\. ).+ G & S: (.+)', mark_content)
    if mark_descrip is not None:
        mark_descrip045 = mark_descrip.group(1) + mark_descrip.group(2)
        mark_description += mark_descrip045 + '\n'

    return mark_description

def mark_csv(mark_registry, trademarks = "trademarks.csv"):
### Creates and updates a .csv file containing the serial numbers and mark name from the first argument
### mark_registry = feil/string of trademark record; trademarks = .csv file to store trademark information
    mark_content = trademark_formatter(mark_registry)

    serial_num = trademark_serial(mark_registry)
    mark_name = trademark_name(mark_registry)
    mark_descrip = trademark_description(mark_registry)
    surveillance_related = ''

    # Retrieves confidence score
    score = keyword_check(mark_registry)

    # Checks if surveillance related best on confidence score
    if score >= min_confidence_score:
        surveillance_related = "Yes"
    else:
        surveillance_related = "No"
        mark_descrip = ''

    # Opens and writes csv file with serial number, mark name, description, whether or not surveillance related, confidence score
    with open(trademarks, mode = 'a') as csv_file:
        fieldnames = ['Serial Number', 'Mark Name', 'Surveillance Related', 'Confidence Score', 'Trademark Description']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writerow({'Serial Number': serial_num, 'Mark Name': mark_name, 'Surveillance Related': surveillance_related, 'Confidence Score': score, 'Trademark Description': mark_descrip})

    return None

def mark_csv_checker(mark_registry, trademarks = "trademarks.csv"):
### Checks if current trademark record is in the csv file and has therefore been checked already
### mark_registry = feil/string of trademark record; trademarks = .csv file where trademark information is stored
    mark_content = trademark_formatter(mark_registry)

    serial_num = trademark_serial(mark_content)

    # Checks if file exists and opens/appends
    if os.path.isfile(trademarks) == False:
      with open(trademarks, 'a') as new_csv_file:
          pass

    # Checks for serial number in each row
    with open(trademarks) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if serial_num == row[0]:
              return True

    return False

def keyword_check(mark_registry):
### Uses regex to look for keywords that suggest entry may be pertaining to some surveillance technology.
### Considering creating a confidence metrics to try to avoid false positives and false negatives -- need to talk to Levendowski
    mark_content = trademark_formatter(mark_registry)

    # Confidence score to track likelihood that entry is actually surveillance related
    confidence_score = 0

# Words commonly found in surveillance related tradmark entries
# (monitor)ing, surveillance, anti-intrusion, anti-theft, security, theft-prevention, crime prevention, law enforcement
# scanner, sensor, tracking, crime
# Need to decide on values for each in terms of confidence that entry is surveillance related - 10 as holder value

    if re.search(r'surveillance', mark_content):
        confidence_score += 10
    if re.search(r'anti-intrusion', mark_content):
        confidence_score += 10
    if re.search(r'anti-theft', mark_content):
        confidence_score += 10
    if re.search(r'security', mark_content):
        confidence_score += 10
    if re.search(r'theft[-|\s]prevention', mark_content):
        confidence_score += 10
    if re.search(r'crime[-|\s]prevention', mark_content):
        confidence_score += 10
    if re.search(r'law enforcement', mark_content):
        confidence_score += 10
    if re.search(r'scanner', mark_content):
        confidence_score += 10
    if re.search(r'sensor', mark_content):
        confidence_score += 10
    if re.search(r'tracking', mark_content):
        confidence_score += 10
    if re.search(r'crime', mark_content):
        confidence_score += 10

    return confidence_score

def keyword_counter(mark_registry):
    # Creates a list of the keywords found in a given entry to be user to display the int
    mark_content = trademark_formatter(mark_registry)

    keyword_list = []

    if re.search(r'surveillance', mark_content):
        keyword_list.append('surveillance')
    if re.search(r'anti-intrusion', mark_content):
        keyword_list.append('anti-intrusion')
    if re.search(r'anti-theft', mark_content):
        keyword_list.append('anti-theft')
    if re.search(r'security', mark_content):
        keyword_list.append('security')
    if re.search(r'theft-prevention', mark_content):
        keyword_list.append('theft-prevention')
    if re.search(r'theft prevention', mark_content):
        keyword_list.append('theft prevention')
    if re.search(r'crime prevention', mark_content):
        keyword_list.append('crime prevention')
    if re.search(r'crime-prevention', mark_content):
        keyword_list.append('crime-prevention')
    if re.search(r'law enforcement', mark_content):
        keyword_list.append('law enforcement')
    if re.search(r'scanner', mark_content):
        keyword_list.append('scanner')
    if re.search(r'sensor', mark_content):
        keyword_list.append('sensor')
    if re.search(r'tracking', mark_content):
        keyword_list.append('tracking')
    if re.search(r'crime', mark_content):
        keyword_list.append('crime')

    return keyword_list

def retrieve_url(browser, entry_counter):
    # retrieves url using selenium
    if selenium.get_url(browser, entry_counter):
        mark_url = selenium.get_url(browser, entry_counter)
    else:
        mark_url = 'URL not found'

    return mark_url

def tweet_mark_info(mark_registry, browser, url):
### Function formats trademark information for display
    mark_content = trademark_formatter(mark_registry)

    # Use other functions to get information to output
    mark_name = trademark_name(mark_content)
    serial_num = trademark_serial(mark_content)
    mark_owner = trademark_owner(mark_content)
    #Shorten long owner names and signify abbreviation with ...
    if len(mark_owner) > 30:
        mark_owner = mark_owner[:30] + '...'

    mark_class = trademark_classes(mark_content)
    mark_url = url
    url_length = len(mark_url)

    keyword_list = keyword_counter(mark_registry)
    mark_flags = ', '.join(keyword_list)

    # Concatenate and format information
    partial_mark_info = mark_name + '\n' + serial_num + '\n' + mark_owner + '\n' + mark_class + '\n' + mark_flags

    #Makes sure there is enough room for full url -- Unlikely to be an issue s
    #Consider using bitly or some other url shortening api to further preserve space
    partial_mark_info = partial_mark_info[:250 - url_length]

    mark_info = partial_mark_info + '\n' + mark_url

    return mark_info


def full_display_mark_info(mark_registry, browser, url):
### Function formats trademark information for display
    mark_content = trademark_formatter(mark_registry)

    # Use other functions to get information to output
    serial_num = 'Serial Number: ' + trademark_serial(mark_content)
    mark_name = 'Mark Name: ' + trademark_name(mark_content)
    mark_owner = 'Owner: ' + trademark_owner(mark_content)
    if len(mark_owner) > 55:
        mark_owner = mark_owner[:55] + '...'

    mark_class = 'Mark Class(es): ' +trademark_classes(mark_content)
    mark_url = url

    mark_flags = keyword_counter(mark_registry)
    mark_flags = ', '.join(mark_flags)

    keyword_list = 'Flagged Words: ' + mark_flags

    mark_descrip = 'Mark Description: ' + trademark_description(mark_content)
    if len(mark_descrip) > 333:
        mark_descrip = mark_descrip[:333] + '...'

    # Concatenate and format information
    full_mark_info = mark_name + '\n' + serial_num + '\n' + mark_owner + '\n' + mark_class + '\n' + keyword_list + '\n' + mark_descrip + '\n' + mark_url

    return full_mark_info


def trademark_watcher(mark_registry, browser, url, trademarks = "trademarks.csv"):
### Top Level Function
    if mark_csv_checker(mark_registry) == False:
        mark_csv(mark_registry)

        if mark_category_check(mark_registry) == True:
            if keyword_check(mark_registry) >= min_confidence_score:
                # Gets the search date and either creates or appends a file with the following format "Tess_Log(YYYYMMDD).txt"
                date = selenium.tess_search_date()
                filename = "Tess_Log(" + date + ").txt"

                full_content = full_display_mark_info(mark_registry, browser, url)
                tweet_content = tweet_mark_info(mark_registry, browser, url)

                #Create and save a .txt file of each mark that passes
                mark_name = trademark_name(mark_registry)
                mark_name = mark_name.replace('/','').strip()
                serial_num = trademark_serial(mark_registry)

                mark_file = mark_name + ' (' + serial_num + ')' +".txt"

                #Get curent directory, make a folder and store txt files in it (use to gather examples for qualatative analysis)
                path = os.getcwd()
                dir = "Tess txt Files"
                dir_path = os.path.join(path, dir)

                if os.path.exists(dir_path):
                    pass
                else:
                    os.mkdir(dir)

                mark_path = os.path.join(dir_path, mark_file)

                if os.path.exists(mark_path):
                    pass
                else:
                    mf = open(mark_path, "a")
                    mf.write(mark_registry)
                    mf.close()

                return tweet_content, full_content
    # Passes if any of the conditions not fulfilled
            else:
                pass
        else:
            pass
    else:
        pass

    return None, None
