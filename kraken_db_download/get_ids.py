my_ids = []
with open("seqid2taxid.map",'r') as myfile:
    for line in myfile:
        info = line.strip().split()
        if len(info[0]) > 0:
            id_part = info[0].split(":")
            if len(id_part) == 1:
                my_ids.append(id_part[0])
            else:
                id_str = id_part[1].split("|")[-1]
                my_ids.append(id_str)

with open("my_ids.txt",'w') as myout:
    myout.write("\n".join(my_ids))
