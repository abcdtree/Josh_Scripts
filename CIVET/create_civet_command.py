my_ids = []

with open("ids.txt", 'r') as myids:
    for line in myids:
        my_ids.append(line.strip())

print("civet -c config.yaml -ids " + ",".join(my_ids))
