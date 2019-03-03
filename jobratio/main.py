
import re

with open("input.txt") as f:
    content = f.readlines()

result = []


for line in content:
    line = line.replace(chr(10), "").replace("\r", "")
    if not line.strip().startswith("JOB_RATIO"):
        result.append(line)
    else:
        newline = []
        
        for i in range(len(line)):
            jobp = re.search('JOBP_.*,', line)
            if jobp:
                jobp = jobp.group(0)
                newline = line[0:line.find(jobp)] + line[line.find(jobp) + len(jobp):]
            else:
                newline = line
           
        
        result.append(newline)
        
f = open("output.txt", "w+")
for line in result:
    f.write(line + "\n")
f.close()