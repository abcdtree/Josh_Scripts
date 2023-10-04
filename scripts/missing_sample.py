import os

path = "/home/mdu/reads"
db = "/home/mdu/reads/qc.tab"

db_id = []
with open(db, 'r') as mydb:
    count = 0
    for line in mydb:
        if count == 0:
            count =1
            continue
        info = line.strip().split("\t")
        mid = info[0]
        db_id.append(mid)

reads_id = []
reads_path_dict = {}
for rid in os.listdir(path):
    if os.path.isdir(os.path.join(path,rid)) and "test" not in rid:
        for mid in os.listdir(os.path.join(path, rid)):
            if os.path.isdir(os.path.join(path, rid, mid)):
                reads_id.append(mid)
                reads_path_dict[mid] = [str(os.path.join(path, rid, mid)), rid]

print("In reads but not in db:")
my_set = set(reads_id) - set(db_id)
print(len(list(my_set)))

rid_dict = {}

with open("/home/jianszhang/missing_check.txt", 'w') as myout:
    for mid in sorted(list(my_set)):
        mpath, rid = reads_path_dict[mid]
        #myout.write(f"{mid}\t{reads_path_dict[mid]}\n")
        mid_list = rid_dict.get(rid, [])
        mid_list.append(mid)
        rid_dict[rid] = mid_list
    for rid in rid_dict:
        run_path = f"/home/mdu/data/{rid}"
        id_line = ",".join(rid_dict[rid])
        myout.write(f"{rid}\t{run_path}\t{len(rid_dict[rid])}\n")
