# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 14:57:33 2019
"""

from os import listdir
from os.path import join as os_join
from email.parser import Parser

employee_email_folder = '..\\Dataset\\maildir\\allen-p\\inbox\\'
print(listdir(employee_email_folder))

def parse_emails_in_folder(folder_path):
  
  parsed_emails_list = []
  parser = Parser()
  
  for email_file_name in listdir(folder_path):
    
    filename = os_join(folder_path, email_file_name)
    with open(filename, "r") as raw_email_file:
      raw_email_text = raw_email_file.read()
    
    parsed_email = parser.parsestr(raw_email_text)
    parsed_emails_list.append(parsed_email)
  
  return parsed_emails_list
  