word=input("Enter the word: ")
i=0
answer=""
current=""
while(i<len(word)):
    if word[i] in current:
        if len(answer)<len(current):
            answer=current
        current=current[1:]
    else:
        current+=word[i]
        i+=1
if len(current)>len(answer):
    answer=current
print(answer)