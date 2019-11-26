# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 14:57:33 2019
"""

from os import listdir
from os import walk
from os.path import isdir
from os.path import exists as os_exists
from os.path import join as os_join
from email.parser import Parser
from collections import defaultdict
import glob
import re
import pandas as pd
import pickle as pk

employee_email_folder1 = '..\\Dataset\\maildir\\allen-p\\sent\\'
employee_email_folder2 = '..\\Dataset\\maildir\\allen-p\\inbox\\'

employee_email_folder3 = '..\\Dataset\\maildir\\campbell-l\\sent\\'
employee_email_folder4 = '..\\Dataset\\maildir\\campbell-l\\inbox\\'

employee_email_folder5 = '..\\Dataset\\maildir\\heard-m\\sent\\'
employee_email_folder6 = '..\\Dataset\\maildir\\heard-m\\inbox\\'

employee_email_folder7 = '..\\Dataset\\maildir\\townsend-j\\sent\\'
employee_email_folder8 = '..\\Dataset\\maildir\\townsend-j\\inbox\\'

email_test_folder = '..\\Dataset\\Test\\'
email_dataset_folder = '..\\Dataset\\maildir\\'

#processed_data_folder = '..\\Source Code\\Processed Data\\'

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
        parsed_email = parser.parsestr(raw_email_text)
        parsed_emails_list.append(parsed_email)      
  return parsed_emails_list


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


def format_name(name):
  names = []
  if "@" in name:
    if "'" in name:
      split_names = name.split("\',")
    elif '"' in name:
      split_names = name.split('\",')
    else:
      split_names = name.split(",")

    #print("***************************")
    #print(name + ":" + str(split_names))

    for i in range(len(split_names)):
      formatted_name = ""
      #print("++++++++++++++++++++++++++++++")
      if "," in split_names[i]:
        split_names_subset = split_names[i].split("\',")
        #print(split_names[i] + ":" + str(split_names_subset))
        for j in range(len(split_names_subset)):
          formatted_name = ""
          #print(split_names_subset[j])
          if "," in split_names_subset[j]:
            #print("@@@@@@@@@@@@@@@@@@")
            formatted_name = format_name_as_fname_mname_lname(split_names_subset[j])
            #print(formatted_name)
            names.append(formatted_name.strip())
          else:
            formatted_name = split_names_subset[j].replace("'", "")
            formatted_name = formatted_name.replace('"', '')
            names.append(formatted_name.strip())
      else:
        formatted_name = split_names[i].replace("'", "")
        formatted_name = formatted_name.replace('"', '')
        names.append(formatted_name.strip())

      #print(names)
      #print("+++++++++++++++++++++++++++++++++++")
    #print("***************************")
    
  elif "," in name:
    name = name.replace("'", "")
    name = name.replace('"', '')
    name = format_name_as_fname_mname_lname(name)
    names.append(name.strip())
  else:
    name = name.replace("'", "")
    name = name.replace('"', '')
    names.append(name.strip())
  return names


def identify_employees_from_header(folder_path):
  email_list = parse_emails_in_folder(folder_path)
  senders_in_folder = defaultdict(set)
  #senders_in_folder_count = defaultdict(int)
  for email in email_list:  
    from_header_field = email['from'].lower().strip()
    x_from_header_field = re.sub("<.*>","",email['x-from'].lower()).strip()
    x_from_header_field = re.sub("\(.*\)","",x_from_header_field).strip()
    x_from_header_field = re.sub("\{.*\}","",x_from_header_field).strip()  
    x_from_header_field = format_name_as_fname_mname_lname(x_from_header_field)  
    if "@" in from_header_field:
      senders_in_folder[x_from_header_field].add(from_header_field)
    elif "@" in x_from_header_field:
      senders_in_folder[from_header_field].add(x_from_header_field)
    else:
      print("Skipping.. " + "\n" + email)
    
  #  senders_in_folder_count[email['from']] += 1
  #  senders_in_folder_count[email['x-from']] += 1
    
  #print(senders_in_folder_count)
  return senders_in_folder


def flatten_list(list_to_flatten):
  flat_list = []
  for sublist in list_to_flatten:
    for item in sublist:
        flat_list.append(item)
  return flat_list


def identify_employees_using_to_cc_bcc(folder_path, entity_list, main_list):
  email_list = parse_emails_in_folder(folder_path)  
  other_names = defaultdict(set)
  #senders_in_folder_count = defaultdict(int)  
  for email in email_list:    
    x_to_field = []
    x_cc_field = []   

    if email['x-to']:
      x_to_field = email['x-to'].split(">,")     
      for i in range(len(x_to_field)):
        x_to_field[i] = re.sub("<.*>","",x_to_field[i].lower()).strip()
        x_to_field[i] = re.sub("<.*$","",x_to_field[i].lower()).strip()
        x_to_field[i] = re.sub("\(.*\)","",x_to_field[i]).strip()
        x_to_field[i] = re.sub("\{.*\}","",x_to_field[i]).strip()

    if email['x-cc']:
      x_cc_field = email['x-cc'].split(">,")
      for i in range(len(x_cc_field)):
        x_cc_field[i] = re.sub("<.*>","",x_cc_field[i].lower()).strip()
        x_cc_field[i] = re.sub("<.*$","",x_cc_field[i].lower()).strip()
        x_cc_field[i] = re.sub("\(.*\)","",x_cc_field[i]).strip()
        x_cc_field[i] = re.sub("\{.*\}","",x_cc_field[i]).strip()

      #print("============================================")    
      #print(x_to_field)
      #print(x_cc_field)
      
    processed_x_to_field = []
    processed_x_cc_field = []
    
    for i in range(len(x_cc_field)):
      formatted_names = format_name(x_cc_field[i])
      processed_x_cc_field.append(formatted_names)
    
    for i in range(len(x_to_field)):  
      formatted_names = format_name(x_to_field[i])
      processed_x_to_field.append(formatted_names)
    
    processed_x_to_field = flatten_list(processed_x_to_field)
    processed_x_cc_field = flatten_list(processed_x_cc_field)
    
    #print(processed_x_to_field)
    #print(processed_x_cc_field)
    #print("============================================")    

    for key, id_list in entity_list.items():
      key_split = key.split(" ")
      fname = key_split[0]
      
      match1 = ""
      match2 = ""
      match3 = ""
      match4 = ""
      
      if len(key_split) == 3:
        mname = key_split[1]
        lname = key_split[2]
        match1 = fname + "." + mname + "." + lname
        match2 = fname + " " + lname
        match4 = fname + "." + lname
        match3 = fname[0] + lname
      elif len(key_split) == 2:
        lname = key_split[1]
        match1 = fname + "." + lname
        match2 = fname + " " + lname
        match3 = fname[0] + lname
        match4 = match2
      else:
        match1 = fname
        match2 = fname
        match3 = fname
        match4 = fname

      for i in range(len(processed_x_to_field)):
        if key in processed_x_to_field[i] or match1 in processed_x_to_field[i] or match2 in processed_x_to_field[i] or match3 in processed_x_to_field[i] or match4 in processed_x_to_field[i]:
          other_names[key].add(processed_x_to_field[i])
          break
        else:
          for identifier in id_list:
            if identifier in processed_x_to_field[i]:
              other_names[key].add(processed_x_to_field[i])
      
      for i in range(len(processed_x_cc_field)):
        if key in processed_x_cc_field[i] or match1 in processed_x_cc_field[i] or match2 in processed_x_cc_field[i] or match3 in processed_x_cc_field[i] or match4 in processed_x_cc_field[i]:
          other_names[key].add(processed_x_cc_field[i])
          break
        else:
          for identifier in id_list:
            if identifier in processed_x_cc_field[i]:
              other_names[key].add(processed_x_cc_field[i])

    #senders_in_folder_count[email['from']] += 1
    #senders_in_folder_count[email['x-from']] += 1
    
  #print(senders_in_folder_count)
  
  for key, value in entity_list.items():
    existing_names = entity_list.get(key)
    optional_names = other_names.get(key)
    if optional_names:
      for name in optional_names:
        existing_names.add(name)
    main_list[key] = existing_names
      
  return main_list


def retrieve_inbox_folders(folder_path):
  inbox_folder_paths = []
  for x in walk(folder_path):
    for y in glob.glob(os_join(x[0], 'inbox')):
      inbox_folder_paths.append(y)  
  return inbox_folder_paths


def retrieve_employee_folders(folder_path):
  inbox_folder_paths = glob.glob(folder_path + "/*/")
  
  '''for x in walk(folder_path):
    for y in glob.glob(os_join(x[0], 'inbox')):
      inbox_folder_paths.append(y)  
  '''
  return inbox_folder_paths


def retrieve_send_folders(folder_path):
  sent_folder_paths = []
  for x in walk(folder_path):
    for y in glob.glob(os_join(x[0], 'sent')):
      sent_folder_paths.append(y)  
  return sent_folder_paths


entity_dict = {} 

def extract_email_addresses_and_optional_names(folder_path):
  employee_folders = retrieve_employee_folders(folder_path)
  
  for employee_folder in employee_folders:
    print(employee_folder)
    send_folder_list = retrieve_send_folders(employee_folder)  
    inbox_folder_list = retrieve_inbox_folders(employee_folder)
    if send_folder_list:
      entities_from_sent = identify_employees_from_header(send_folder_list[0])
      
      if inbox_folder_list:
        identify_employees_using_to_cc_bcc(inbox_folder_list[0], entities_from_sent, entity_dict)
      else:
        print(entities_from_sent)
      
    for key, value in entities_from_sent.items():
      entity_dict[key] = value
  #print(len(send_folder_list), " ", len(inbox_folder_list), " ", len(employee_folders))
  
  #print(entity_dict)
  save_entity_list(entity_dict)
  #for folder in folder_list:
  #  entities_from_sent = identify_employees_from_header(folder) 
  #  entity_dict.update()
  #  entity_dict = identify_employees_using_to_cc_bcc(, r1, r)
    


def extract_optional_names_and_email_addresses(folder_path, entity_list):
  folder_list = retrieve_inbox_folders(folder_path)  
  for folder in folder_list:
    entity_dict.update(identify_employees_using_to_cc_bcc(folder, entity_list))
    


def save_entity_list(entity_list):  
  data_frame = pd.DataFrame(list(entity_list.items()),columns=['Name','Alias'])
  data_frame.to_csv("entities.csv", index=False) 
  data_frame.to_pickle("entities.pickle")
  data_frame = pk.load(open("entities.pickle", "rb"))
  print(data_frame)

#print(entity_extraction(email_dataset_folder))

#r=identify_employees_from_header(employee_email_folder1)
#print(r)
#print("========================")
#r = identify_employees_using_to_cc_bcc(employee_email_folder2, r, r)
#print(r)
#print(r)
#print("+++++++++++++++++++++++++++++++++")

#r1=identify_employees_from_header(employee_email_folder3)
#print(r1)
#print("========================")
#r=identify_employees_using_to_cc_bcc(employee_email_folder4, r1, r)
#print(r)
#print("+++++++++++++++++++++++++++++++++")

#r1=identify_employees_from_header(employee_email_folder5)
#print(r1)
#print("========================")
#r=identify_employees_using_to_cc_bcc(employee_email_folder6, r1, r)
#print(r)
#print("+++++++++++++++++++++++++++++++++")

#r1=identify_employees_from_header(employee_email_folder7)
#print(r1)
#print("========================")
#r=identify_employees_using_to_cc_bcc(employee_email_folder8, r1, r)
#print(r)
#print("+++++++++++++++++++++++++++++++++")

#save_entity_list(r)
extract_email_addresses_and_optional_names(email_dataset_folder)
#r = retrieve_for_send_inbox_folders(email_dataset_folder) 
#print(str(identify_employees_using_from_header(r[0])))