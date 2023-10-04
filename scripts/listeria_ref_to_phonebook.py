import json

listeria_ref = "/home/jianszhang/analysis/listeria/Listeria_ref.json"

json_file = open(listeria_ref, 'r')
ref_dict = json.load(json_file)
json_file.close()

phonebook_list = []
sp = "Listeria monocytogenes"
for key in ref_dict:
    rpath = ref_dict[key]["genome"]
    phonebook_list.append(f"{rpath}\t{sp}\tST{key} using for survillance report")

with open("listeria_ref_book.txt", 'w') as myout:
    for line in phonebook_list:
        myout.write(line + "\n")
