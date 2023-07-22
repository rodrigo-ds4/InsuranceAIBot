import pandas as pd
import pickle

df = pickle.load(open('df.pickle', 'rb'))

print(df.columns)

prev_policy_title = None
prev_policy_code = None
text = ''

for index, row in df.iterrows():
    if row['Policy_Title'] != prev_policy_title or row['Policy_Code'] != prev_policy_code:
        text += 'Policy Title: ' + ' '.join(row['Policy_Title']) + '\n'
        text += 'Policy Code: ' + ' '.join(row['Policy_Code']) + '\n'

        prev_policy_title = row['Policy_Title']
        prev_policy_code = row['Policy_Code']

    text += 'Article Name: ' + ' '.join(row['Article_Name']) + '\n'
    text += 'Article Content: ' + ' '.join(row['Article_Content']) + '\n\n'

with open('policy_text.txt', 'w') as file:
    file.write(text)

words = text.split()

num_words = len(words)

print(f"the text contains {num_words} words.")
