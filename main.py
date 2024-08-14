import random

no_after = [9,18,27,36,45,54,63,72,81]
no_before = [1,10,19,28,37,46,55,64,73]

def chunk(table):
    rows = []
    i = 1
    for n in no_after:
        row = table[n - 9:n]
        rows.append(row)
        i += 1
    return(rows)

bomb_blocks = random.sample(range(1, 82), 10)

table = []
i = 1
while i < 82:
    if i in bomb_blocks:
        table.append("*")
    else:
        b = 0
        if i not in no_after and i not in no_before:
            if i + 1 in bomb_blocks:
                b += 1            
            if i - 1 in bomb_blocks:
                b += 1
            for num in [8,9,10]:
                if i - num > 0 :
                    if i - num in bomb_blocks:
                        b += 1
                if i + num < 82 :
                    if i + num in bomb_blocks:
                        b += 1
        elif i in no_after:
            if i - 1 in bomb_blocks:
                b += 1            
            if i - 9 > 0 :
                if i - 9 in bomb_blocks:
                    b += 1
            if i + 9 < 82 :
                if i + 9 in bomb_blocks:
                    b += 1            
            if i - 10 > 0 :
                if i - 10 in bomb_blocks:
                    b += 1
            if i + 8 < 82 :
                if i + 8 in bomb_blocks:
                    b += 1
        elif i in no_before:
            if i + 1 in bomb_blocks:
                b += 1            
            if i - 9 > 0 :
                if i - 9 in bomb_blocks:
                    b += 1
            if i + 9 < 82 :
                if i + 9 in bomb_blocks:
                    b += 1            
            if i - 8 > 0 :
                if i - 8 in bomb_blocks:
                    b += 1
            if i + 10 < 82 :
                if i + 10 in bomb_blocks:
                    b += 1
        table.append(b)
    i += 1
    continue

shit = chunk(table)
for i in range(9):
    print(shit[i])
