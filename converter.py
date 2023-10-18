import csv
import datetime
import os
import pytz
import sys
from icalendar import Calendar


def convert(filename):
    with open(filename + '.csv', 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['DTSTART', 'DTEND', 'SUMMARY', 'ATTENDEES', 'DESCRIPTION']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        with open(filename + '.ics', 'rb') as f:
            cal = Calendar.from_ical(f.read())
            for component in cal.walk():
                if component.name == 'VCALENDAR':
                    CAL_NAME = component['X-WR-CALNAME']
                    TIMEZONE = pytz.timezone(component['X-WR-TIMEZONE'])
                if component.name == 'VEVENT':
                    dic = {}
                    
                    # reset start and end time with the timezone
                    for time in ['DTSTART', 'DTEND']:
                        dic[time] = component[time].dt
                        if type(dic[time]) is datetime.date:
                            dic[time] = datetime.datetime.combine(dic[time], datetime.time())
                        dic[time] = dic[time].astimezone(TIMEZONE)

                    # Check if SUMMARY is present in component before accessing it
                    if 'SUMMARY' in component:
                        dic['SUMMARY'] = component['SUMMARY'].to_ical().decode()
                    else:
                        dic['SUMMARY'] = ''

                    # Check if DESCRIPTION is present in component before accessing it
                    if 'DESCRIPTION' in component:
                        dic['DESCRIPTION'] = component['DESCRIPTION'].to_ical().decode().replace(r'\n', ' ')
                    else:
                        dic['DESCRIPTION'] = ''

                    # Gather all ATTENDEE email addresses
                    attendees = []
                    for attendee in component.get('ATTENDEE', []):
                        # Extract email address from the attendee field
                        email = str(attendee).split(":")[-1]
                        attendees.append(email)
                    dic['ATTENDEES'] = ', '.join(attendees)
                    
                    writer.writerow(dic)
                
                
if __name__ == '__main__':
    args = sys.argv
    
    if len(args) == 1:
        print('Please input file names after this python file')
    else:
        args.pop(0)
        for arg in args:
            if os.path.isfile(arg):
                convert(arg.split('.')[0])
            else:
                print('{} is not found'.format(arg))
