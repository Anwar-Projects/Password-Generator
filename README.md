# Password-Generator
Password Generation Script with CPU/GPU Management, Error Handling, and Terminal Output

Real-time Terminal Output: Passwords are printed as they are generated, which helps you monitor progress.
Error Handling: Wrapped critical sections of the code in try-except blocks, printing detailed error messages if any exceptions occur.
CPU Monitoring: Introduced a background thread that continuously monitors CPU usage using the psutil library. If the CPU usage exceeds 60%, the script temporarily pauses to reduce the load.
GPU Management: Since Python doesn't have direct control over GPU usage without specific libraries (like TensorFlow or PyTorch), the GPU handling in this script is a placeholder (MAX_GPU_USAGE). If you are running this in an environment that supports GPU monitoring, you can integrate a GPU management library for advanced control.
Efficient Resource Usage: Implemented throttling on CPU overuse, sleeping the process if CPU consumption goes above the defined threshold.

Prerequisites:
Install the psutil library for CPU monitoring:
pip install psutil

Running the Script:
Save the script to a Python file (password_generator.py).
Run the script:
python password_generator.py

How to Run the Script:
Save the script to a file named passgen.py.
Open your terminal.
Navigate to the directory where the script is located.
Run the script using the command:

You’ll be able to see the passwords as they are generated in real-time, along with detailed error messages if anything goes wrong, and the script will automatically adjust for CPU usage to stay within the defined limits.

Troubleshooting:
If you continue facing issues, consider breaking down the script into smaller functions and testing them individually to identify the bottleneck. Adjusting how and when results are written to the output file can also help in managing memory usage effectively. If you have a specific line of code or a section causing issues, feel free to share it for more targeted suggestions!

Password Requirements:

This Python script generates the following types of passwords and store them in a single file called passwords.txt as an output to all the below mentioned instructions:

1. Write all the words from the dictionary in lowercase with only first alphabet of the word should be Capital letter. Example: Animal, Beautiful, Dog
2. Write all the words from the dictionary words with all letters in lowercase. example dog, hospital.
3. Write all the permutation and combination of the 26 characters from the alphabets list wherein the total alphabet count should not be less than 4 alphabets and not more than 12 and if the given word is already in step#1, then ignore the word. The first alphabet of the word should be a capital letter.
4. Replace the characters such as: a with @, o with 0, i with 1, s with 5, for all the words found in step#1, 2 & 3 and get a complete list, example: @pple
5. Replace the characters such as: o with 0 for all the words found in step#1, 2 & 3 and get a complete list irrespective of the case sensitivity, for example, both o & O should be replaced with 0, example: 0range
6. Replace the characters such as: i with 1 for all the words found in step#1, 2 & 3 and get a complete list irrespective of the case sensitivity, example, for example, both i & I should be replaced with 1; 1nd1a for India
7. Replace the characters such as: i with ! for all the words found in step#1, 2 & 3 and get a complete list irrespective of the case sensitivity, example, for example, both i & I should be replaced with !; !nd!a for India
8. Replace the characters such as: s with 5, for all the words found in step#1, 2 & 3 and get a complete list irrespective of the case sensitivity of the letter, example: For example, both s & S should be replaced with 5; 5even for Seven
9. For all the words found in step 1, 2 & 3 replace a with @, s with 5, o with 0, I wish I wherever found in the given word irrespective of the case sensitivity of the letter. For example, both i & I should be replaced with 1.
10. For all the words found in step#1, 2, 3, 4, 5 & 6 add in front of all these words with 4-digit numbers in such a way that all permutation and combinations of the 4-digit numbers are taken from 0 to 9 and between the alphabets and the digits the following characters must be inserted !@#$%^&*()_+-=[]{}|;:'",.<>/?. Not all these characters in a single word but one by one for each and every word found in step 1, 2, 3, 4, 5 & 6.  Example dictionary@1234, dictionary +4321, dictionary =0123
11. For all the words found in step#1, 2, 3, 4, 5 & 6 add in front of all these words with 3-digit numbers in such a way that all permutation and combinations of the 3-digit numbers are taken from 0 to 9 and between the alphabets and the digits the following characters must be inserted !@#$%^&*()_+-=[]{}|;:'",.<>/?. Not all these characters in a single word but one by one for each and every word found in step 1, 2, 3, 4, 5 & 6.  Example dictionary@123, dictionary +432, dictionary =012
12. For all the words found in step#1, 2, 3, 4, 5 & 6 add in front of all these words with 2-digit numbers in such a way that all permutation and combinations of the 2-digit numbers are taken from 0 to 9 and between the alphabets and the digits the following characters must be inserted !@#$%^&*()_+-=[]{}|;:'",.<>/?. Not all these characters in a single word but one by one for each and every word found in step 1, 2, 3, 4, 5 & 6.  Example dictionary@14, @pple+41, b0y=03
13. For all the words found in step#1, 2, 3, 4, 5 & 6 add in front of all these words with 1-digit numbers in such a way that all permutation and combinations of the 1-digit numbers are taken from 0 to 9 and between the alphabets and before the digits the following characters must be inserted !@#$%^&*()_+-=[]{}|;:'",.<>/?. Not all these characters in a single word but one by one for each and every word found in step 1, 2, 3, 4, 5 & 6.  Example dictionary@1, dictionary#2, dictionary!3
14. Write all the dictionary words found in step 1, 2, 3, 4, 5 & 6 with '@' symbol in front of the dictionary word and then 1-digit numbers after the word in such a way that all permutation and combinations of the 3-digit numbers from 0 to 9 are met. Example d1ct10n@ry@1, apple@2, boy@3
15. Write all the dictionary words found in step 1, 2, 3, 4, 5 & 6 and add 1-digit number after these words in such a way that all permutation and combinations of the 0 to 9 are taken. Example d1ct10n@ry3, apple2, boy1 
16. Write all the dictionary words found in step 1, 2, 3, 4, 5 & 6 and add 2-digit number after these words in such a way that all permutation and combinations of the 0 to 9 are taken. Example d1ct10n@ry13, apple@2, boy@1 
17. Write all the dictionary words found in step 1, 2, 3, 4, 5 & 6 and add 3-digit number after these words in such a way that all permutation and combinations of the 0 to 9 are taken. Example d1ct10n@ry130, apple@279, boy@134
18. For the words found as an output from step 14, 15 and 16, add the following characters in the end one by one and generate the list of new words: !@#$%^&*()_+-=[]{}|;:'",.<>/?
19. Write all the dictionary words found in step 1, 2, 3, 4, 5 & 6 and add 4-digit number after these words in such a way that all permutation and combinations of the 0 to 9 are taken. Example d1ct10n@ry1302, apple@2791, boy@1340
