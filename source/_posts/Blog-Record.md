---
title: Markdown文本BLOG记录方法
date: 2022-11-10 11:48:49
categories:
  - 笔记
tags:
  - blog
  - Markdown
---

Markdown插图片有三种方法，各种Markdown编辑器的插图方式也都包含在这三种方法之内。
插图最基础的格式就是：

```
![Alt text](图片链接 "optional title")
```

插入本地图片
只需要在基础语法的括号中填入图片的位置路径即可，支持绝对路径和相对路径。 
例如： 

```
![avatar](/home/picture/1.png)
```

插入网络图片
只需要在基础语法的括号中填入图片的网络链接即可，现在已经有很多免费/收费图床和方便传图的小工具可选。 
例如： 

```
![avatar](http://baidu.com/pic/doge.png)
```


把图片存入markdown文件
用base64转码工具把图片转成一段字符串，然后把字符串填到基础格式中链接的那个位置。 
基础用法： 

![avatar](data:image/png;base64,iVBORw0......) 
这个时候会发现插入的这一长串字符串会把整个文章分割开，非常影响编写文章时的体验。如果能够把大段的base64字符串放在文章末尾，然后在文章中通过一个id来调用，文章就不会被分割的这么乱了。 
比如： 

![avatar][doge] 
[doge]:data:image/png;base64,iVBORw0......
然后，base64的图片编码如何得来？

图片转化为base64字符串


base64字符串转化为图片























