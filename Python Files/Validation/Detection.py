abc=list(map(int, input("Enter elements:").split()))
visit=set()
duplicate=set()
for num in abc: 
    if num in visit:
         duplicate.add(num)
    else:
        visit.add(num)

print("Duplicate Elements:", duplicate)
    

