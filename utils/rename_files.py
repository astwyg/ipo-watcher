import os

dir_path = "..\\data\\"
files = os.listdir(dir_path)

cnt = 0
for file in files:
    if cnt == 0:
        pass
    else:
        old_name = dir_path + files[cnt]
        new_name = dir_path + old_name.split("公司")[0]+"公司"+old_name[-4:]
        os.rename(old_name, new_name)

    cnt = cnt+1