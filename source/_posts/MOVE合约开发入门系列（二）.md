---
title: MOVE合约开发入门系列（二）
date: 2026-10-27 00:00:00 +0800
categories: [技术]
tags: [MOVE, 智能合约, Aptos, 区块链]
hidden: true
---

# MOVE合约开发入门系列（二）

提示：本文的 MOVE 是基于 APTOS 公链特性的 MOVE 语言学习。

## Lesson4-VECTOR(类似数组）向量核心特性(一)

### 基础概念

Vector（向量）类似其他语言中的数组，内部存储的是同一类型的数据。

|  |  |

| --- | --- |

|  |  |

|  |  |

### 查询功能

|  |  |

| --- | --- |

|  |  |

|  |  |

|  |  |

|  |  |

|  |  |

|  |  |

### 增删改1

|  |  |

| --- | --- |

|  |  |

|  |  |

|  |  |

|  |  |

|  |  |

|  |  |

|  |  |

|  |  |

|  |  |

### 增删改2

|  |  |

| --- | --- |

|  |  |

|  |  |

|  |  |

|  |  |

|  |  |

可以运行以下代码实习对一些功能的了解：

```

module 0x42::VectorDemo{
  use std::debug;
  use std::vector;
  #[test_only]
  use aptos_std::debug::print;

  const ARR:vector<u64> = vector[1,2,3,4,5,6,7,8,9,10];

  #[test]
  fun test_vector(){
    debug::print(&ARR);
  }

  #[test]
  fun test_empty_vector(){
    let bools:bool = vector::is_empty(&ARR);
    debug::print(&bools);
  }

  #[test]
  fun test_vector_length(){
    let len:u64 = vector::length(&ARR);
    debug::print(&len);
  }

  #[test]
  fun test_vector_borrow(){
    let val = vector::borrow(&ARR,3);
    debug::print(val);
  }

  #[test]
  fun test_vector_borrow_mut(){
    let arr:vector<u64> = vector[1,2,3,4,5,6,7,8,9,10];
    let val = vector::borrow_mut(&mut arr,3);
    *val=100;
    debug::print(&arr);
  }
}

```

## Lesson5-VECTOR向量核心特性(二)

剩余部分 Vector 功能实现。

## Lesson6-函数修饰符

### 核心概念

函数修饰符是用来赋予函数特殊能力的一组关键字。主要有以下几类：

#### 可见性

- 无 public，私有函数，仅限 module 内部调用

- friend public，模块内部函数，同包模块之间可以调用

- public，模块公开函数，所有模块都可以调用

#### 全局存储引用

- acquires，当需要使用 move_from、borrow_global、borrow_global_mut 访问地址下的资源的时候，需要用其修饰

#### 链下

- entry，修饰后，该方法可由链下脚本调用

具体可运行以下代码来理解以上概念：

```

address 0x42{
  module m {
    friend 0x42::m3;
    fun f1(): u64 {
      1
    }

    public fun f2(): u64 {
      2
    }

    public(friend) fun f3(): u64 {
      3
    }
  }
  module m2 {
    fun f1(): u64 {
      0x42::m::f2()
    }
  }
  module m3{
    fun f1():u64{
      0x42::m::f3()
    }
  }
}

```

```

module 0x42::Demo{
  use std::debug;
  use std::signer;
  use aptos_framework::coin;
  #[test_only]
  use std::signer::address_of;

  struct Coin has key{
    value:u64
  }

  public entry fun mint(account: &signer,value: u64){
    move_to(account,Coin{value});
  }

  #[test(account = @0x42)]
  public fun test_mint(account:&signer) acquires Coin{
    let addr = signer::address_of(account);
    mint(account,10);
    let coin = borrow_global<Coin>(addr).value;
    debug::print(&coin);
  }
}

```
