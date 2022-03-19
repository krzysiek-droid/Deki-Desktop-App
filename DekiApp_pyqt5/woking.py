
sample = []
harness = []
with open(r'C:\Users\Młody\Desktop\[Srv] Doktorat\PUBLIKACJE\Twardosci\1_2-20x2.txt', 'r') as fop:
    data = fop.readlines()


    for row in data:
        nr = row.split('  ')
        sample.append(nr)



new_r = sample[2]

for row in sample:
    harness.append(row[4][:6])

print(harness)
with open(r'C:\Users\Młody\Desktop\[Srv] Doktorat\PUBLIKACJE\Twardosci\1_2-20x2-measurements.txt', 'w') as fwr:
    fwr.write('\n'.join(m for m in harness))