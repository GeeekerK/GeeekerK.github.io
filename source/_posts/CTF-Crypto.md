---
title: CTF Crypto
date: 2023-04-17 22:11:49
categories:
  - 技术
tags:
  - CTF
  - Crypto
---

# Rabbit

### 1.简介：

Rabbit 是一种**高速流密码**，于 2003 年在 FSE 研讨会上首次提出。 Rabbit 使用一个 128 位[密钥](https://so.csdn.net/so/search?q=密钥&spm=1001.2101.3001.7020)和一个 64 位初始化向量。 该加密算法的核心组件是一个位流生成器，该流生成器每次迭代都会加密 128 个消息位。

1.特点：

组成有26个大小写英文字母、=、+、/

Rabbit加密开头部分通常为U2FsdGVkX1
（AES、DES、RC4、Rabbit、Triple DES、3DES 这些算法都可以引入密钥，密文特征与Base64类似，明显区别是秘文里+比较多，并且经常有/）

可能以=结尾

2.实例：

    明文I Love You无密匙加密后密文为U2FsdGVkX1/ouFei55jKdzY1fWNS4jxHVNf/AfKWjnBrOGY=
    明文I Love You 521无密匙加密后密文为U2FsdGVkX19DvuEo5PvBA8TuLrM2t+EZBvUkzlAa
    明文I Love You 521密匙为666加密后密文为U2FsdGVkX18w6vxXxux/ivRVwo3xMzTxmUyk7cHz


# 栅栏密码

### 加密原理

①把将要传递的信息中的字母交替排成上下两行。
②再将下面一行字母排在上面一行的后边，从而形成一段密码。
③例如：
明文：THE LONGEST DAY MUST HAVE AN END

##### 加密：

1、把将要传递的信息中的字母交替排成上下两行。
T E O G S D Y U T A E N N
H L N E T A M S H V A E D
2、 密文：
将下面一行字母排在上面一行的后边。
TEOGSDYUTAENN HLNETAMSHVAED

##### 解密：

先将密文分为两行
T E O G S D Y U T A E N N
H L N E T A M S H V A E D
再按上下上下的顺序组合成一句话
明文：THE LONGEST DAY MUST HAVE AN END

# 栅栏密码变形--W型栅栏密码

##### 加密：

明文由上至下顺序写上，当到达最低部时，再回头向上，一直重复直至整篇明文写完为止。

!["E:\Blog\myblog\source\_posts\W型栅栏密码路径演示.png"](/images/W型栅栏密码路径演示.png)

##### 解密：

首先设栅栏数（阶数）为n，则第一行的数字相隔2(n-2)+1=2n-3位，第二行数字相隔2(n-1)-3=2n-5位，以此类推，根据此规律重新构造明文设计算法。



# 2023/2/16

## [GXYCTF2019]Ping Ping Ping

sep=' '



# 2023/2/20

## crypto

21 31 61 43 62 解密
九宫格对应
结果为admin

q&b解密
移位法
panda

# 2023/3/12

## crypto

**cryper: LYROR_AE_ARFVDEH_LUXWSIT**

提示:五连发夹弯

table:

THE_R

I_DAO

S_VER

ELF_Y

XURAL

**message: THE_ROAD_IS_VERY_FLEXURAL**

**cryper:Lqscqzogf_sotl_voziof**

对26字英语输入法键盘从左到右对应26字母顺序做单表替换

**message:Salvation_lies_within**



# 2023/3/21

## crypto

**cryper：**

987456321569874123
987412374123697415
98524568523745963

**Hint:**

九九成组七亦随
五三成群七并六

**message:**

Security

按照99775376个字符分割后在电脑
数字小键盘轨迹按下的轨迹即是单词security
987456321
569874123
9874123
7412369
74159
852
4568523
745963

# 2023/03/31

## crypto

**cryper:**

99 203 304 401 508

**message:**

(99)99+(104)203+(101)304+(97)401+(107)508

后面一个减去前面一个，得到中间差作为新密文的Ascll码

再将ASCLL码一一映射，即可得到密文creak

# 2023/04/14

## crypto

cryper:

​    Bnbwm   

hint:   异或表达图

key:12345

message:

Clash

感悟：先将密文转换为ASCll码再和密钥分别在对应位下作二进制形式的异或运算，相同则为False,不同则为True。最后将异或的二进制在转换为ASCll码对应的字符。

# 2023/04/17

## crypto

cryper:

​     43 32 11 42 44

hint:想不出来的话，可以尝试尝试tap(明文大小写均可)

message：

​      SMART

# 2023/04/20

Cryper:

​     已知明密文对：         Plaintext _attack→{GJBE_NS_tJ__JH@

​      hint:  yihuo 非常疑惑    （异或规则：相同为0，相异为1）                     

​                               01010000  01101100

​                               00101011  00101011

​                               01111011  01000111

由上述异或推导可得到key为‘+’

​                   求：？→{^QQGN

之后逆运算得到 Puzzle



# ROT13编码

ROT13（回转13位，rotate by 13 places，有时中间加了个连字符称作ROT-13）是一种简易的替换式密码。

ROT13被描述成“杂志字谜上下颠倒解答的Usenet点对点体”。ROT13 也是过去在古罗马开发的凯撒[加密](https://so.csdn.net/so/search?q=加密&spm=1001.2101.3001.7020)的一种变体

## 特点：

- 套用ROT13到一段文字上仅仅只需要检查字元字母顺序并取代它在13位之后的对应字母， 有需要超过时则重新绕回26英文字母开头即可。
- 只有这些出现在英文字母里头的字元受影响；数字、符号、空白字元以及所有其他字元都不变



## 小结：

1. 遇到synt{xx-xx-xx} 判定他为rot13；
2. 题目一般都是提示信息，“回旋踢”就暗示了rot13的特点，会重新绕回；

# 变异凯撒

左右移位时，移位数呈某种规律，如移位数依次递增1。具体需要结合ASCLL码来观察位移规律。一般前四位明文固定为flag，可以依据此来作为线索。

# PASSWORD

一般人的密码设置有以下几种常见的设置方式：

姓名首字母+生日（可能包括年份)

# Quoted-printable_ 引用可打印

### 简介：

Quoted-Printable编码可译为“可打印字符引用编码”，或者“使用可打印字符的编码”。通常我们接收电子邮件，查看电子邮件原始信息，经常会看到这种类型的编码，电子邮件信头显示：Content-Transfer-Encoding:quoted-printable。它是多用途互联网邮件扩展（MIME)
一种实现方式。其中MIME是一个互联网标准，它扩展了电子邮件标准，致力于使其能够支持非ASCII字符、二进制格式附件等多种格式的邮件消息。目前http协议中，很多采用MIME框架！quoted-printable就是说用一些可打印常用字符，表示一个字节（8位）中所有非打印字符方法。

### Quoted-Printable编码方法：

任何一个8位的字节值可编码为3个字符：一个等号“=”后跟随两个十六进制数字（0–9或A–F）表示该字节的数值。

例如：ASCII码换页符（十进制值为12）可以表示为”=0C”。

除了可打印ASCII字符与换行符以外，所有字符必须表示为这种格式。所有可打印ASCII字符（十进制值的范围为33到126）可用ASCII字符编码来直接表示，但是等号“=”（十进制值为61）不可以这样直接表示，等号”=”（十进制值为61）必须表示为”=3D”。ASCII的水平制表符（tab）与空格符（即：十进制为9和32），如果不出现在行尾则可以用其ASCII字符编码直接表示。如果这两个字符出现在行尾，必须QP编码表示为“=09”（tab）或“=20”（space）。

如果数据中包含有意义的行结束标志，必须转换为ASCII回车(CR)换行(LF)序列，既不能用原来的ASCII字符也不能用QP编码的“=”转义字符序列。 相反，如果字节值13与10有其它的不是行结束的含义，它们必须QP编码为=0D与=0A。

Quoted-Printable编码的数据的每行长度不能超过76个字符。为满足此要求又不改变被编码文本，在QP编码结果的每行末尾加上软换行(soft line break)。 即在每行末尾加上一个”=”， 但并不会出现在解码得到的文本中。

很多时候，我们用些常见字符表示所有8位其它非打印字符，这种通过Quoted-Printable编码，只是对该字节转为16进制后，做简单增加前缀！然后做些特殊字符处理即可！ 它的简单，及编码高效，也让该编码在邮件格式里面，得到了广泛使用。

敲黑板：**Quoted-Printable编码适合所传输数据中只有少量的非ASCII编码**，来表示一个非ASCII码字符！！！
