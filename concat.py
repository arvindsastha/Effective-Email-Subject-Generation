import pandas as pd
df1 = pd.read_csv("emails_and_subject.csv")
df2 = pd.read_csv("emails_and_subject_val.csv")

df1['Subject'].append(df2['Subject'])
df1['Email Body'].append(df2['Email Body'])

df1.to_csv("emails_and_subject.csv", index=False)
