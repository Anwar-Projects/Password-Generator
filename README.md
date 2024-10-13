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
