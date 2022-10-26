def StarRating(rating):
    # find nearest half
    # count fulls
    print(round(0.36))

    #return strParam


#print(StarRating(input()

result = []
rating='0.26'

full = rating.split('.')[0]
rest = rating.split('.')[1]

for star in range(int(full)):
    result.append('full')

if 75 > int(rest) > 25:
    result.append('half')
elif int(rest) >= 75:
    result.append('full')

while len(result) < 5:
    result.append('empty')


print(' '.join(result))

arr = [1, 2, 3, 4, 5]
arr.pop(1)
print(arr)