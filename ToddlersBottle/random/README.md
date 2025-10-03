# random — pwnable.kr

## Goal

get the flag

---

## Files Provided

* `random`
* `random.c` — `random`s source
* `flag` — the goal

---

## Walkthrough

```shell
random@ubuntu:~$ ls -l
total 24
-r--r----- 1 root random_pwn    34 Apr  5 09:45 flag
-r-xr-sr-x 1 root random_pwn 16232 Apr  5 09:49 random
-rw-r--r-- 1 root root         335 Apr  5 09:49 random.c
random@ubuntu:~$ cat random.c
#include <stdio.h>

int main(){
	unsigned int random;
	random = rand();	// random value!

	unsigned int key=0;
	scanf("%d", &key);

	if( (key ^ random) == 0xcafebabe ){
		printf("Good!\n");
		setregid(getegid(), getegid());
		system("/bin/cat flag");
		return 0;
	}

	printf("Wrong, maybe you should try 2^32 cases.\n");
	return 0;
}
```

Here we can see that to get the flag -> the input from scanf ^ random should result 0xcafebabe.
To get the key requirements we need to XOR by random both sides of the equation:
```shell
key ^ random = 0xcafebabe
key ^ random ^ random = 0xcafebabe ^ random # random ^ random = 0
key = 0xcafebabe ^ random
```

So if we find random we will be able to find key.
`rand()` with a fixed seed will always result in the same sequence of numbers.
No one here calls `srand(seed)` so the seed defaults to 1.
Hence, by checking once what is the value, we can calculate the key needed.

I decided to run in `gdb` with a break at main to see the value,
```shell
# breakpoint after call to rand@plt
pwndbg> print/d $eax
$1 = 1804289383
```
```shell
In [0]: 0xcafebabe ^ 1804289383
Out[0]: 2708864985
```

Since the scanf takes the input as %d I type the input as digit:
```shell
random@ubuntu:~$ ./random
2708864985
Good!
m0mmy_I_can_predict_rand0m_v4lue!
```
