---
title: CTF每日收获
date: 2023-02-21 18:27:24
categories:
  - 笔记
tags:
  - CTF
  - Crypto
---

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

