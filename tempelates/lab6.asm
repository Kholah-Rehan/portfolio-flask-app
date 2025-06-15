.data
msg1: .asciiz "enter some value of x:"
msg2:.asciiz "enter some value for y:"
msg3: .asciiz "enter some value for z:"
.text
.globl main
.ent main
main:
li $v0,4
la $a0 , msg1
syscall
li $v0, 5
syscall
move $t1,$v0  
li $v0, 4
la $a0,msg2
syscall
li $v0,5
syscall
move $t2,$v0
li $v0,4
la $a0,msg5
syscall
li $v0,5
syscall
move $t3,$v0
sub $t2,$t1,$t2
add $t3,$t2,$t3
addi $t3,$t3,-24
li $v0,1
move $a0,$t3
syscall
jr $ra
li $v0,10
syscall
.end main

