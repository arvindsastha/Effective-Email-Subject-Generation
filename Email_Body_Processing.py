# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 20:28:37 2019

@author: arvin
"""
import re
import string
from os.path import join as os_join
import pandas as pd
import pickle as pk
from email.parser import Parser
from datetime import date
from collections import defaultdict
from os import listdir
from os import walk
from os.path import isdir
from os.path import exists as os_exists
import glob

'''
class Error(Exception):
   """Base class for other exceptions"""
   pass

class EmailParseException(Error):
   """Raised when the input value is too large"""
   pass
'''
#from babel.dates import format_date

employee_email_folder1 = '..\\Dataset\\maildir\\allen-p\\sent\\'
employee_email_folder2 = '..\\Dataset\\maildir\\allen-p\\inbox\\'

email_test_folder = '..\\Dataset\\Test\\'
email_dataset_folder = '..\\Dataset\\maildir\\'

entity_list_dir = "..\\Processed Data\\"
entity_list_data_frame = pd.read_csv(os_join(entity_list_dir, "entities.csv"))
entity_list = dict(zip(entity_list_data_frame.Name, entity_list_data_frame.Alias))

email_set = set()
pair_mail = defaultdict(set)
unique_body = []
unique_subject = []

data_frame = pd.DataFrame()
data_frame_1 = pd.DataFrame()

From = []
To = []
Date = []
Subject = []
Body = []
  
def format_name_as_fname_mname_lname(name):
  if "," not in name:
    return name
  name = name.strip()
  name = name.replace(",", "")
  name = name.replace("'", "")
  name = name.replace('"', "")
  split_names = name.split(" ")
  name = ""
  for i in range(1, len(split_names)):
    name += split_names[i]
    name += " "
  name += split_names[0]
  name = re.sub("\. ", " ", name)
  return name.strip()


def format_email(email):
  #form "abc@neron.com [abc@enron.com]"
  if "@" in email:
    info_inside_bracket = re.findall("\[.*\]", email)
    #print(info_inside_bracket)
    
    if info_inside_bracket:
      email = info_inside_bracket[0]
      email = email.replace("[", "")
      email = email.replace("]", "")
      email = email.replace("mailto:", "").strip()
      if "_" in email and "@" in email:
        name = email.split("@")
        name = name[0].split("_")
        name = ' '.join([x for x in name])
        #entity_list[name].append(email)
      elif "." in email and "@" in email:
        name = email.split("@")
        name = name[0].split(".")
        name = ' '.join([x for x in name])
        #entity_list[name].append(email)
        return email
        
    info_inside_bracket = re.findall("<.*>", email)
    #print(info_inside_bracket)
    
    if info_inside_bracket:
      email = info_inside_bracket[0]
      email = email.replace("<", "")
      email = email.replace(">", "")
      email = email.replace("mailto:", "").strip()
      if "_" in email and "@" in email:
        name = email.split("@")
        name = name[0].split("_")
        name = ' '.join([x for x in name])
        #entity_list[name].append(email)
      elif "." in email and "@" in email:
        name = email.split("@")
        name = name[0].split(".")
        name = ' '.join([x for x in name])
        #entity_list[name].append(email)
        return email
    
    #print(info_inside_bracket)
    #if info_inside_bracket:
    #  info = info_inside_bracket
    if "@" in email:
      return email  
    #form "abc [mail to: abc@enron.com]"
    else:
      return format_name_as_fname_mname_lname(email)
  else:
    return format_name_as_fname_mname_lname(email)

def removing_special_words(email_body):
  email_body = email_body.lower()
  #date_filter = "([1-9]|1[0-9]|2[0-9]|3[0-1])(\.|\/|-)([1-9]|1[0-2])(\.|\/|-)20[0-9][0-9]$"
  #email_body = re.sub(date_filter, "", email_body).lower().strip()
  
  #remove bullets of type 1., 1), a., a)
  bullet_filter = "(\\n\(*[1-9]+\))|(\\n\(*[a-z]\))|(\\n\(*[1-9]\.)|(\\n\(*[a-z]\.)"
  email_body = re.sub(bullet_filter, ".\\n", email_body).lower().strip()
  
  extension_filter = "(\.[a-z]+ )"
  email_body = re.sub(extension_filter, ".", email_body).lower().strip()
  
  percentage_filter = "[1-9][0-9]*%"
  email_body = re.sub(percentage_filter, "", email_body).lower().strip()
   
  non_acsii_filter = set(string.printable)
  email_body = ''.join(filter(lambda x: x in non_acsii_filter, email_body))
  
  #new_line_filter = 
  return email_body


def convert_long_month_to_short_month(long_month):

  return{
        'january' : 'Jan',
        'february' : 'Feb',
        'march' : 'Mar',
        'april' : 'Apr',
        'may' : 'May',
        'june' : 'Jun',
        'july' : 'Jul',
        'august' : 'Aug',
        'september' : 'Sep', 
        'october' : 'Oct',
        'novomber' : 'Nov',
        'december' : 'Dec'
        }[long_month]
  
def get_author_name(email):
  name = email.split("@")
  if "_" in name:
    name = name[0].split("_")
    name = ' '.join([x for x in name if len(x) > 1])
  else:
    name = name[0].split(".")
    name = ' '.join([x for x in name if len(x) > 1])
  
  return name.strip()


def format_date_in_forward_reply_header(input_string):
  #print(input_string)
  input_string_split = input_string.split(",")
  #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
  #print(input_string_split)
  #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
  input_date_split = input_string_split[1].split(" ")
  
  if len(input_date_split[1]) == 3:
    output_date = input_date_split[1].strip() + " " 
  else:
    output_date = convert_long_month_to_short_month(input_date_split[1]).strip() + " " 
  output_date += str(int(input_date_split[2])).strip() + " " 
  
  input_date_split = input_string_split[2].split(" ")
  output_date += input_date_split[1].strip() + " "
  output_date += input_date_split[2].strip() + input_date_split[3].strip()
  return output_date
  
def segrating_reply_email(email_body, inbox_identifier):
  global data_frame
  global data_frame_1
  global From
  global To
  global Date
  global Subject
  global Body
  
  message_body = email_body.get_payload()
  message_body = re.sub("\\n>>" , "", message_body).strip()
  message_body = re.sub("\\n>" , "\n", message_body).strip()
  message_body = re.sub("<< file: ", "", message_body).strip()

  original_email_filter = ".*\-+original message\-+"
  original_emails = re.compile(original_email_filter).split(message_body)
  
  #From = []
  #To = []
  #Date = []
  #Subject = []
  #Body = []

  for email in original_emails:
    
    forward_indicator = 0
    header_filter = "\\n(.*):(.*)\\t"
    headers = re.compile(header_filter).split(email)
    #print("\n\n")
    #print(headers)
    #print("\n\n")
    
    if not "forwarded by" in headers[0] and "from:" in headers[0]:
      header_filter = "\\n(.*): (.*)"
      headers = re.compile(header_filter).split(email)
      forward_indicator = 1
      #print(len(headers))
      #print(headers)
    
    if len(headers) == 1:
      if "forwarded by" in headers[0]:
        #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        #print(headers)
        #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        forward_indicator = 1
        forward_email_filter = "(\\n)*\-+ forwarded by.*"
        forward_emails = re.compile(forward_email_filter).split(headers[0])
        #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        #print(forward_emails)
        #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        #print("*******************************************")
        
        forward_emails = list(filter(None.__ne__, forward_emails))
          
        for f_mail in forward_emails:
          
          find_forward_header = re.search("[0-9][0-9]:[0-9][0-9] (am|pm) \-+", f_mail)
          #print(find_forward_header)
          if not find_forward_header and f_mail:
            date_split = email_body['date'].split(" ")
            f_date = date_split[0] + " " + date_split[2].capitalize() + " " + date_split[1] + ", " + date_split[3] + " " + date_split[4][:5] + " pm"
            subj = email_body['subject'].strip()
            subj = re.sub(".*:", "", subj).strip()
            new_email = "\nfrom: " + email_body['x-from'] + "\nsent: " + f_date + "\nto: " + email_body['x-to'] + "\ncc: " + email_body['x-cc'] + "\nsubject: " + subj + "\n" + f_mail 
            original_emails.append(new_email)
            continue
          elif not f_mail:
            continue
          
          f_mail = re.sub("([0-9][0-9]:[0-9][0-9] (am|pm) )*\-+", "", f_mail).strip()
          f_mail = f_mail.replace('"', '')
          #print("*******************************************")
          #print(f_mail)
          #print("*******************************************")
          
          f_mail = "\nfrom: " + f_mail
          f_mail_copy = re.split("\\nfrom: (.*)on(.*)", f_mail)
          f_mail = re.sub(" on [0-9][0-9].*", "", f_mail)
          #print("#########################################")
          #print(f_mail)
          #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
          #print(f_mail_copy)
          #print("#########################################")

          #print(f_mail_copy)
          f_mail_copy[2] = f_mail_copy[2].strip()
          date_time_split = f_mail_copy[2].split(" ")
          split_date = date_time_split[0].split("/")
          d = date(day=int(split_date[1]), month=int(split_date[0]), year=int(split_date[2])).strftime('%A %d %B %Y')
          d_split = d.split(" ")
          d = d_split[0].strip() + ", " + d_split[2].strip() + " " + d_split[1].strip() + ", " + d_split[3] 
          formatted_time = date_time_split[1][:5].strip() + " " + date_time_split[2]
          #format_date(d, locale='en')
          
          forward_date = d + " " + formatted_time
          #print("====" + forward_date + "======")
          f_mail = f_mail[:f_mail.index('to:')] + "sent: " + forward_date.strip().lower() + "\n" + f_mail[f_mail.index('to:'):]
          #print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
          #print(f_mail)
          original_emails.append(f_mail)
          #d = date(2007, 4, 1)
          #format_date(d, locale='en')
          #u'Apr 1, 2007'
          #print("#########################################")
      else:
        if headers[0]:
          #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
          #print(headers[0])
          #print(email_body['date'])
          #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
          o_date_split = email_body['date'].split(" ")
          o_date = o_date_split[0] + " " + o_date_split[2].capitalize() + " " + o_date_split[1] + ", " + o_date_split[3] + " " + o_date_split[4][:5] + " pm"
          o_subj = email_body['subject'].strip()
          o_subj = re.sub(".*:", "", o_subj).strip()
          new_email = "\nfrom: " + email_body['x-from'] + "\nsent: " + o_date + "\nto: " + email_body['x-to'] + "\ncc: " + email_body['x-cc'] + "\nsubject: " + o_subj + "\n" + headers[0] 
          original_emails.append(new_email)
            
      #body = headers[0]
      #print(body)
      #print("**********************************************")
      continue
    
    
    if forward_indicator == 1:
      print("Forward")
      #print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
      #print(headers)
      #print(email)
      #print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
      
      from_header = headers[2]
      to_header = headers[8]
      header_date = headers[5]
    
      if "cc" in headers[10]:
        cc = headers[11].strip()
        subject = headers[14]
        body = headers[15]
      else:
        cc = ""
        subject = headers[11]
        body = headers[12]
      
    else:
      print("Reply")
      from_header = headers[3]
      to_header = headers[9]
      header_date = headers[6]
    
      if "cc" in headers[10]:
        cc = headers[12]
        body = headers[15]
      else:
        cc = ""
        body = headers[12]
      subject_filter = "([a-z]*:)*(.*)\\n"
      subject = re.search(subject_filter, body)
    
    from_header = format_email(from_header)
    to_header = to_header.split(";")
    
    recipient_list = []
    
    #print(headers)
    header_date = format_date_in_forward_reply_header(header_date)
    cc = cc.split(";")
    
    for recipient in cc:
      if recipient:
        recipient_list.append(format_email(recipient))  
    
    if subject and forward_indicator == 0:
      subject = re.sub(".*:", "", subject.group()).strip()
      
    body = body.replace(subject, "").strip()
    body = body.replace("\n", "")
    body = re.sub("[^a-z0-9\.]+", " ", body)
    
    sender_split = from_header.split(" ")
    for sender in sender_split:
      body = body.replace(sender, "")
    
    body = re.sub("re", "", body)
    body = re.sub("fw", "", body)
    body = re.sub("thanks(.*)", "", body)
    body = re.sub("\.(.*)regards(.*)", "", body)
    body = re.sub("sincerely(.*)\.", "", body)
    body = re.sub("good luck(.*)\.", "", body).strip()
    
    if "@" in from_header:
      format_name = get_author_name(from_header)
      body = body.replace(format_name, "").strip()
      body = re.sub("good luck(.*)\.", "", body)
    
    for recipient in to_header:
      recipient = recipient.strip()
      formatted_recipient = format_email(recipient)
      formatted_recipient_split = formatted_recipient.split(" ")
      
      for name in formatted_recipient_split:
        if len(name) == 1:
          continue
        body = body.replace(name, "")
        
      if "@" in formatted_recipient:
        format_name = get_author_name(formatted_recipient)
        format_name = format_name.split(" ")
        for name in format_name:
          if len(name) == 1:
            continue
          body = body.replace(name, "").strip()
      
      if inbox_identifier == 1:
        key = from_header + ";" + formatted_recipient
      else:
        key = formatted_recipient + ";" + from_header
        
      body = body.strip()
      
      if not body:
        continue
      
      if body not in email_set:
        From.append(from_header)
        To.append(formatted_recipient)
        Date.append(header_date)
        Body.append(body)
        Subject.append(subject)
        email_set.add(body)
        unique_body.append(body)
        unique_subject.append(subject)
        pair_mail[key].add(len(unique_body) - 1)
      else:
        index = unique_body.index(body)
        if key not in pair_mail:
          From.append(from_header)
          To.append(formatted_recipient)
          Date.append(header_date)
          Body.append(body)
          Subject.append(subject)
          pair_mail[key].add(index)
        elif key in pair_mail and index not in pair_mail[key]:
          From.append(from_header)
          To.append(formatted_recipient)
          Date.append(header_date)
          Body.append(body)
          Subject.append(subject)
          pair_mail[key].add(index)
      
    for recipient in recipient_list:
      recipient = recipient.strip()
      recipient_split = recipient.split(" ")
      for name in recipient_split:
        if len(name) == 1:
          continue
        body = body.replace(name, "")

      if "@" in recipient:
        format_name = get_author_name(recipient)
        format_name = format_name.split(" ")
        for name in format_name:
          if len(name) == 1:
            continue
          body = body.replace(name, "").strip()
          
      if inbox_identifier == 1:
        key = from_header + ";" + formatted_recipient
      else:
        key = formatted_recipient + ";" + from_header
      
      body = body.strip()

      if not body:
        continue
      
      if body not in email_set:
        From.append(from_header)
        To.append(formatted_recipient)
        Date.append(header_date)
        Body.append(body)
        Subject.append(subject)
        email_set.add(body)
        unique_body.append(body)
        unique_subject.append(subject)
        pair_mail[key].add(len(unique_body) - 1)
      else:
        index = unique_body.index(body)
        if key not in pair_mail:
          From.append(from_header)
          To.append(formatted_recipient)
          Date.append(header_date)
          Body.append(body)
          Subject.append(subject)
          pair_mail[key].add(index)
        elif key in pair_mail and index not in pair_mail[key]:
          From.append(from_header)
          To.append(formatted_recipient)
          Date.append(header_date)
          Body.append(body)
          Subject.append(subject)
          pair_mail[key].add(index)
    #subject_filter = "([a-z]*:)*(.*)\\n"
    #body = re.sub(subject_filter, "", body)
    
    print("From: " + from_header)
    print("To: ", to_header)
    print("Date: " + header_date)
    print("Cc: ", cc)
    print("Recipients: ", To)
    if subject:
      print("Subject: " + subject)

    print("Body: " + body)
    
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    # \\n(.*):(.*)\\t
    # [a-z]*: [a-z]* [a-z]*\\n
    #email = email.split(header_filter)
    #email_list.append(email)
    
  #data_frame = pd.DataFrame()
  '''
  data_frame['From'].append(From)
  data_frame['To'].append(To)
  data_frame['Date'].append(Date)
  data_frame['Subject'].append(Subject)
  data_frame['Body'].append(Body)
  
  
  data_frame.to_csv("conversation.csv", index=False) 
  data_frame.to_pickle("conversation.pickle")
  data_frame = pk.load(open("conversation.pickle", "rb"))
  print(data_frame)
  '''

  #data_frame_1 = pd.DataFrame()
  '''
  data_frame_1['Subject'].append(unique_subject)
  data_frame_1['Email Body'].append(unique_body)
  
  print("Appended")
  
  data_frame_1.to_csv("emails_and_subject.csv", index=False) 
  data_frame_1.to_pickle("emails_and_subject.pickle")
  data_frame_1 = pk.load(open("emails_and_subject.pickle", "rb"))
  print(data_frame_1)
  '''
  '''
  data_frame_2 = pd.DataFrame(list(pair_mail.items()),columns=['Pair','Email Set'])
  
  data_frame_2.to_csv("pair_and_email_list.csv", index=False) 
  data_frame_2.to_pickle("pair_and_email_list.pickle")
  data_frame_2 = pk.load(open("pair_and_email_list.pickle", "rb"))
  print(data_frame_2) 
  '''
  #print(email_list)
  
def retrieve_inbox_folders(folder_path):
  inbox_folder_paths = []
  for x in walk(folder_path):
    for y in glob.glob(os_join(x[0], 'inbox')):
      inbox_folder_paths.append(y)  
  return inbox_folder_paths

def retrieve_send_folders(folder_path):
  sent_folder_paths = []
  for x in walk(folder_path):
    for y in glob.glob(os_join(x[0], 'sent')):
      sent_folder_paths.append(y)  
  return sent_folder_paths

def parse_emails_in_folder(folder_path):
  parsed_emails_list = []
  parser = Parser()
  if os_exists(folder_path):
    for email_file_name in listdir(folder_path):    
      filename = os_join(folder_path, email_file_name)    
      if isdir(filename):
        continue      
      with open(filename, "r") as raw_email_file:
        raw_email_text = raw_email_file.read()
        raw_email_text = removing_special_words(raw_email_text)
        parsed_email = parser.parsestr(raw_email_text)
        parsed_emails_list.append(parsed_email)      
  return parsed_emails_list

def retrieve_employee_folders(folder_path):
  inbox_folder_paths = glob.glob(folder_path + "/*/")
  return inbox_folder_paths

def extract_conversations(folder_path):
  employee_folders = retrieve_employee_folders(folder_path)
  global data_frame
  global data_frame_1
  
  for employee_folder in employee_folders:
    print(employee_folder)
    sent_folder_list = retrieve_send_folders(employee_folder)  
    inbox_folder_list = retrieve_inbox_folders(employee_folder)
    
    for sent_folder in sent_folder_list:
      print(sent_folder)
      email_list = parse_emails_in_folder(sent_folder)
      i = 0
      for sent_email in email_list:
        print(i)
        i = i + 1
        #sent_email = removing_special_words(sent_email)
        #parser = Parser()
        #sent_email = parser.parsestr(sent_email)
        #print("----------------------------------------------")
        #print(sent_email)
        try:
          segrating_reply_email(sent_email, 0)
        except:
          print("Exception occured")
          pass
      
    for inbox_folder in inbox_folder_list:
      print(inbox_folder)
      email_list = parse_emails_in_folder(inbox_folder)
      i = 0
      for inbox_email in email_list:
        print(i)
        i = i + 1
        #inbox_email = removing_special_words(inbox_email)
        #parser = Parser()
        #inbox_email = parser.parsestr(inbox_email)
        #print("----------------------------------------------")
        #print(inbox_email)
        try:
          segrating_reply_email(sent_email, 1)
        except:
          print("Exception occured")
          pass
        
  data_frame['From'] = From
  data_frame['To'] = To
  data_frame['Date'] = Date
  data_frame['Subject'] = Subject
  data_frame['Body'] = Body
  
  data_frame.to_csv("conversation.csv", index=False) 
  data_frame.to_pickle("conversation.pickle")
  data_frame = pk.load(open("conversation.pickle", "rb"))
  print(data_frame)
  
  data_frame_1['Subject'] = unique_subject
  data_frame_1['Email Body'] = unique_body
  
  data_frame_1.to_csv("emails_and_subject.csv", index=False) 
  data_frame_1.to_pickle("emails_and_subject.pickle")
  data_frame_1 = pk.load(open("emails_and_subject.pickle", "rb"))
  print(data_frame_1)
  
  data_frame_2 = pd.DataFrame(list(pair_mail.items()),columns=['Pair','Email Set'])
  
  data_frame_2.to_csv("pair_and_email_list.csv", index=False) 
  data_frame_2.to_pickle("pair_and_email_list.pickle")
  data_frame_2 = pk.load(open("pair_and_email_list.pickle", "rb"))
  print(data_frame_2)

extract_conversations(email_dataset_folder)
        
'''  
#filename = os_join("..\\Dataset\\Test\\", "test_email_body.txt")    
filename = os_join("..\\Dataset\\Test\\", "test_forward_email.txt")    

with open(filename, "r") as raw_email_file:
  email_body = raw_email_file.read()

#entity_list.set_index('Name')['Alias'].to_dict()
#entity_list = entity_list.to_dict('set')
  
email_body = removing_special_words(email_body)
parser = Parser()
email_body = parser.parsestr(email_body)
print(email_body)
print("----------------------------------------------")
print(str(entity_list_data_frame))
print("----------------------------------------------")
segrating_reply_email(email_body.get_payload())
entity_list_data_frame = pd.DataFrame(list(entity_list.items()),columns=['Name','Alias'])
#entity_list.get('ina rangel').add("ina.rangel@enron.com")
print(str(entity_list_data_frame))
'''