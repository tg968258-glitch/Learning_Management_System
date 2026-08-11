 # 1) Prime number checker with invalid input detection

try: 
    n=int(input("Enter a number:"))
    if n <= 0:
        print("Error, Please enter a positive number")
    else: 
        is_prime=True
       
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                is_prime = False
                break

        if is_prime:
            print(f"{n} is a prime number.")
        else:
            print(f"{n} is not a prime number.")
except ValueError:
    print("Invalid input! Please enter an integer.")







# 2) Factorial calculator with overflow handling

try:
    n = int(input("Enter a number: "))

    if n < 0:
        print("Factorial not possible.")
    else:
        f = 1
        for i in range(1, n + 1):
            f *= i

        if f > 10000:
            raise  OverflowError
        print("Factorial =", f)

except OverflowError:
    print("Overflow of values")





# 3) Palindrome checker ignoring whitespace and case

try:
    string=input("Enter a string:")
    string = string.replace(" ", "").lower()
    if string == string[::-1]:
        print("Palindrome")
    else:
        print("Not Palindrome")

except:
    print("Something went wrong!")





# 4) Find maximum element in list with empty list validation

try:
    numbers = list(map(int, input("Enter numbers: ").split()))

    if len(numbers) == 0:
        print("List is empty.")
    else:
        print("Maximum =", max(numbers))

except ValueError:
    print("Invalid input!")







# 5) Character frequency counter using dictionary/map 

try:
    text = input("Enter a string: ")

    if text.strip() == "":
        print("Input cannot be empty.")

    else:
        frequency = {}

        for ch in text:
            frequency[ch] = frequency.get(ch, 0) + 1

        print("\nCharacter Frequencies:")
        for key, value in frequency.items():
            print(f"{key} : {value}")

except Exception as e:
    print("Error:", e)
















