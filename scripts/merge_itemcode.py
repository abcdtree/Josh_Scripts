import os

output_info = []
with open("info.tab", 'r') as myinput:
    count = 0
    for line in myinput:
        if count == 0:
            count +=1
            continue
        mduid,itemcode,ausid = line.strip().split("\t")
        if len(itemcode) == 0:
            output_info.append([mduid, ausid])
        else:
            output_info.append([mduid+"-"+itemcode, ausid])

with open("ids.tab", 'w') as myout:
    for out in output_info:
        myout.write("\t".join(out) + "\n")
