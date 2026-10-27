---
title: MOVE合约开发入门系列（一）
date: 2024-04-08 00:00:00 +0800
categories: [技术]
tags: [MOVE, 智能合约, Aptos, 区块链]
hidden: true
---

# MOVE合约开发入门系列（一）

提示：本文的 MOVE 是基于 APTOS 公链特性的 MOVE 语言学习。

## 前言

智能合约是近十年来区块链领域的重要突破，它具有自动执行、不可篡改和去中心化等特性，为各行各业提供了无限的潜力和创新空间。然而，传统的智能合约开发过程中存在一些挑战和风险，包括安全漏洞、难以调试和可靠性等问题。

为了解决这些问题，并提供更安全、更高效、更易用的智能合约开发工具，MOVE 语言应运而生。MOVE 语言是一种新兴的智能合约语言，由世界知名的社交媒体公司 Meta（原 Facebook）所开发。它旨在为区块链开发者带来一种革命性的编程语言，以满足日益复杂的智能合约需求。

Move 是一种基于 Rust 的编程语言，它是为 Meta 的 Diem 区块链项目而开发的。该团队当时正在研究其他智能合约语言，但没有一种语言具有稀缺性、确定性和可验证性的特性，所以他们构建了 Move。

## Lesson1-HelloWorld

### 环境配置

1. rust 环境：https://www.rust-lang.org/

1. aptos move 环境：https://aptos.dev/tools/aptos-cli/use-cli/use-aptos-cli

### 创建项目

1. 初始化 move 项目

```

aptos move init --name lesson1

```

1. 初始化账户

```

aptos init

```

### 认识项目结构

```

Move.toml   //项目的配置，如项目名称，项目地址，第三方包

aptos       //模块所指向的账户及项目配置信息
  config.yaml

scripts     //脚本文件，用来调用模块（用的少）

sources     //模块文件夹，模块和测试可以放在这里面

tests       //测试文件，用来写测试用例（用的少）

```

### 打印 "Hello,world!"

```

module Lesson1::HelloWorld{
  use std::debug::print;
  use std::string::utf8;

  #[test]
  fun test_hello_world(){
    print( & utf8( b"Hello World"));// &var only reading &mut reading and writing
  }
}

```

## Lesson2-MVOE语言与变量

### 变量是什么？

变量：是有名字的对象；

对象：存储某个类型值的内存区域；

值：按照类型进行解释的 bytes 集合；

类型：定义可能值的操作；

### 值类型是如何存储的？

值类型，意为简单的类型，其主要特征是数量量较小，常见有以下类型：布尔类型、整数、浮点数、枚举、字符串、堆类型值的指向。

### 引用类型是如何存储的？

引用类型，意为复杂类型，通常存储的数据量较大，常见有以下类型：堆、对象、数组、类、函数。

### 值类型与引用类型的关系

通常我们定义一个变量为对象时，其对象的值存储在堆上，其堆内存的索引存储在栈上，用栈上的索引指向堆上存储的引用类型数据。（内存模型示意：栈上有 n = 1000、s = "hello world"、person = obj，堆上有一个对象 {name: "kaso", age: 25}，person 通过指针指向它。）

![值类型与引用类型的内存模型](https://pub-30d17fc7e72a4ebd980e1c0a6fcb7acc.r2.dev/csdn/move-1/memory.png)

### MOVE语言的核心差异

在值类型与引用类型关系上，不同于其他语言的索引方式，而是以"所有权"来作为引用类型的操作：

1. 所有权只能同时由 1"人"拥有；

1. 所有权以转移的形式流转给其他变量；

对比：Javascript 中 person2 = person 后两者指向同一对象，若 person2.age = 18 则 person.age = 18；C++ 中赋值会拷贝出新对象，若 person2.age = 18 则 person.age = 25 不变；Move 中 person2 = person 后，person 找不到对应值，意为转移所有权。

![Javascript / C++ / Move 赋值语义对比](https://pub-30d17fc7e72a4ebd980e1c0a6fcb7acc.r2.dev/csdn/move-1/semantics.png)

可通过运行以下代码体会 MOVE 的所有权转移，体会到 MOVE 语言作为面向资产的优势：

```

module 0x42::lesson2{
  use std::debug::print;

  struct Wallet has drop{
    balance:u64
  }

  #[test]
  fun test_wallet(){
    let wallet =Wallet{balance:1000};
    let wallet2 = wallet;
    // print(&wallet.balance);
    print(&wallet2.balance);
  }
}

```

### 这样做有什么好处？

1. 避免内存泄露，不同于其他语言，在编译阶段就可以告知什么时候可以回收内存

1. 提高内存使用效率，避免对引用类型的不必要拷贝

1. 更好的可读性和可维护性

## Lesson3-UINT/STRING/BOOL与及 ADDRESS 四大类型

通过运行以下代码可对比数据类型区别：

```

module 0x42::Types{
  use std::debug::print;
  use std::string;
  use std::string::{utf8,String};

  #[test]//some int types useing
  fun test_num(){
    let num_u8: u8=42;// u8:0-2**8-1
    let num_u8_2=42u8;
    let num_u8_3 = 0x2A;//hash
    print(&num_u8);
    print(&num_u8_2);
    print(&num_u8_3);
    let num_u256= 100_000u256;
    print(&num_u256);
    let num_sum = (num_u8_2 as u256) + num_u256;
    print(&num_sum);
  }

  #[test]
  fun test_bool(){
    let bool_true: bool=true ;
    let bool_false: bool=false ;
    print(&bool_true);
    print(&bool_false);
    print(&(bool_false != bool_true));
  }

  #[test]
  fun test_string(){
    let str:String = utf8(b"hello,world!");
    print(&str);
  }

  #[test]
  fun test_addr(){
    let addr:address = @0x2A;
    let add2:address = @0x00000000000000000000000000000000000000000A;
    print(&addr);
    print(&add2);
  }
}

```
