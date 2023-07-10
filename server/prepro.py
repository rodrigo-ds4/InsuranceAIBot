import pandas as pd
import pickle

# Open pickle file and load it into a variable
df = pickle.load(open('df.pickle', 'rb'))

# Show the resulting variable
print(df.columns)

prev_policy_title = None
prev_policy_code = None
text = ''

# Iterate thru the rows 
for index, row in df.iterrows():
    # set titles
    if row['Policy_Title'] != prev_policy_title or row['Policy_Code'] != prev_policy_code:
        text += 'Policy Title: ' + ' '.join(row['Policy_Title']) + '\n'
        text += 'Policy Code: ' + ' '.join(row['Policy_Code']) + '\n'

        prev_policy_title = row['Policy_Title']
        prev_policy_code = row['Policy_Code']

    # set article name and content
    text += 'Article Name: ' + ' '.join(row['Article_Name']) + '\n'
    text += 'Article Content: ' + ' '.join(row['Article_Content']) + '\n\n'

with open('policy_text.txt', 'w') as file:
    file.write(text)

# Split text into words
words = text.split()

# Count the amount of words
num_words = len(words)

print(f"the text contains {num_words} words.")
