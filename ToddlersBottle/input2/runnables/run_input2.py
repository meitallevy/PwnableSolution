import os

binary_path = "input2_adjusted"

# Construct the argument list with the null byte
# The total number of arguments must be 100
# argv[0]: binary_path
# argv[1] - argv[64]: 'ph' - placeholder
# argv[65] (for argv['A']): null byte - empty string
# argv[66] (for argv['B']): \x20\x0a\x0d - " \n\r"
# argv[67] - argv[99]: 'ph' - placeholder
arguments = (
    [binary_path.encode()] +
    [b"ph"] * 64 +
    [b""] +
    [b" \n\r"] +
    [b"ph"] * 33
)

print(f"Total number of arguments being sent: {len(arguments)}")
print(arguments)

print(f"Setting env var for stage 3")
env = {b"\xde\xad\xbe\xef": b"\xca\xfe\xba\xbe"}

print(f"Creating file for stage 4")
fd = os.open("\x0a", flags=os.O_RDWR)
os.write(fd,b"\x00\x00\x00\x00")
os.close(fd)
# The os.execve call replaces the current process with the target binary,
# so code after this will not run.
# All arguments must be byte strings.
try:
    os.execve(binary_path, arguments, env)
except Exception as e:
    print(f"An error occurred during os.execve: {e}")


