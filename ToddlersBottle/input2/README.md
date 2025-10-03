# input2 — pwnable.kr

## Goal

get the flag

---

## Files Provided

* `input2`
* `input2.c` — `input2`s source
* `flag` — the goal

---

## Walkthrough

```shell
input2@ubuntu:~$ ls -l
total 28
-r--r----- 1 root input2_pwn    45 Apr  2  2025 flag
-r-xr-sr-x 1 root input2_pwn 16720 Apr  1  2025 input2
-rw-r--r-- 1 root root        1787 Apr  1  2025 input2.c
input2@ubuntu:~$ cat input2.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int main(int argc, char* argv[], char* envp[]){
	printf("Welcome to pwnable.kr\n");
	printf("Let's see if you know how to give input to program\n");
	printf("Just give me correct inputs then you will get the flag :)\n");

	// argv
	if(argc != 100) return 0;
	if(strcmp(argv['A'],"\x00")) return 0;
	if(strcmp(argv['B'],"\x20\x0a\x0d")) return 0;
	printf("Stage 1 clear!\n");	

	// stdio
	char buf[4];
	read(0, buf, 4);
	if(memcmp(buf, "\x00\x0a\x00\xff", 4)) return 0;
	read(2, buf, 4);
        if(memcmp(buf, "\x00\x0a\x02\xff", 4)) return 0;
	printf("Stage 2 clear!\n");
	
	// env
	if(strcmp("\xca\xfe\xba\xbe", getenv("\xde\xad\xbe\xef"))) return 0;
	printf("Stage 3 clear!\n");

	// file
	FILE* fp = fopen("\x0a", "r");
	if(!fp) return 0;
	if( fread(buf, 4, 1, fp)!=1 ) return 0;
	if( memcmp(buf, "\x00\x00\x00\x00", 4) ) return 0;
	fclose(fp);
	printf("Stage 4 clear!\n");	

	// network
	int sd, cd;
	struct sockaddr_in saddr, caddr;
	sd = socket(AF_INET, SOCK_STREAM, 0);
	if(sd == -1){
		printf("socket error, tell admin\n");
		return 0;
	}
	saddr.sin_family = AF_INET;
	saddr.sin_addr.s_addr = INADDR_ANY;
	saddr.sin_port = htons( atoi(argv['C']) );
	if(bind(sd, (struct sockaddr*)&saddr, sizeof(saddr)) < 0){
		printf("bind error, use another port\n");
    		return 1;
	}
	listen(sd, 1);
	int c = sizeof(struct sockaddr_in);
	cd = accept(sd, (struct sockaddr *)&caddr, (socklen_t*)&c);
	if(cd < 0){
		printf("accept error, tell admin\n");
		return 0;
	}
	if( recv(cd, buf, 4, 0) != 4 ) return 0;
	if(memcmp(buf, "\xde\xad\xbe\xef", 4)) return 0;
	printf("Stage 5 clear!\n");

	// here's your flag
	setregid(getegid(), getegid());
	system("/bin/cat flag");	
	return 0;
}
```

This stage has 5 inner stages.
Starting with the first stage:

```shell
// argv
if(argc != 100) return 0;
if(strcmp(argv['A'],"\x00")) return 0;
if(strcmp(argv['B'],"\x20\x0a\x0d")) return 0;
printf("Stage 1 clear!\n");	
```

It requires 100 args to continue (argc -> args count),
Having the arguments at 'A' (65) 'B' (66) be "\x00" and "\x20\x0a\x0d"
The first arg of a program is always the command ran.
so lets pass 99 args with the correct values in them

I copied the source code to my computer to adjust it and add prints (I didn't change no functionality -> only added
prints)

[./input2_adjusted.c](runnables/input2_adjusted.c)
[./run_input2.py](runnables/run_input2.py)

Note that "\x00" is NULL byte signaling end of string
so an empty string should do the trick

```python
import os

binary_path = "runnables/input2_adjusted"
arguments = (
        [binary_path.encode()] +
        [b"ph"] * 64 +
        [b""] +
        [b" \n\r"] +
        [b"ph"] * 33
)
os.execv(binary_path, arguments)
```

```shell
input2@ubuntu:~$ python /tmp/run_input2.py 
Total number of arguments being sent: 100
[b'./input2', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'', b' \n\r', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph']
Welcome to pwnable.kr
Let's see if you know how to give input to program
Just give me correct inputs then you will get the flag :)
Stage 1 clear!

```

Stage 2 requires us to pipe into stdin and stderr specific bytes.

```shell
// stdio
char buf[4];
read(0, buf, 4);
if(memcmp(buf, "\x00\x0a\x00\xff", 4)) return 0;
read(2, buf, 4);
    if(memcmp(buf, "\x00\x0a\x02\xff", 4)) return 0;
printf("Stage 2 clear!\n");
```

fd 0 - stdin
fd 2 - stdout
in order to pipe those bytes I've constructed the following programs:
[/tmp/with_stdin.py](./runnables/with_stdin.py)
[/tmp/with_stderr.py](./runnables/with_stderr.py)
That just write bytes to stdout buffer

Then I Piped their output to files:

```shell
input2@ubuntu:~$ python3 /tmp/with_stdin.py > /tmp/file_in
input2@ubuntu:~$ python3 /tmp/with_stderr.py > /tmp/file_err
```

And piped them accordingly to the program input

```shell
input2@ubuntu:~$ python3 /tmp/run_input2.py < /tmp/file_in 2< /tmp/file_err
Total number of arguments being sent: 100
[b'./input2', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'', b' \n\r', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph', b'ph']
Welcome to pwnable.kr
Let's see if you know how to give input to program
Just give me correct inputs then you will get the flag :)
Stage 1 clear!
Stage 2 clear!
```
