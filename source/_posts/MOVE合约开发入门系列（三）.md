---
title: MOVE合约开发入门系列（三）
date: 2024-04-09 00:00:00 +0800
categories: [技术]
tags: [MOVE, 智能合约, Aptos, 区块链]
hidden: true
---

# MOVE合约开发入门系列（三）

提示：本文的 MOVE 是基于 APTOS 公链特性的 MOVE 语言学习。

## Lesson7-STRUCT(类似结构体)特性解读

### 核心概念

Struct 结构体，用来存储具有结构化的数据。struct 可以相互嵌套，可存储地址下作为资源。

1. 命名必须以大写字母开头

1. 可以通过 has 关键词赋与能力

```

struct Person{
  age: u8,
  birthday: u32,
}

struct People{
  people: vector<Person>,
}

```

### 修饰符

- Copy：值能够被复制。

- Drop：值可以在作用域结束时删除。

- Key：值可以用作全局存储操作的 key。

- Store：值可以被全局存储。

除 struct 类型外，其他的类型默认具备 store、drop、copy 的能力，struct 最终是存储在用户的地址上（或者被销毁），不存在 aptos 合约里，aptos 合约是一个全纯的函数。

#### drop

值能够在使用结束后被销毁。

```

// drop
struct Coin{
  b: bool
}

#[test]
fun test6(){
  let c = Coin{b: true};
}
// 会报错

```

```

// drop
struct Coin has drop{
  b: bool
}

#[test]
fun test6(){
  let c = Coin{b: true};
}

```

#### copy

值能够在使用结束后被复制。

```

// copy
struct CanCopy has drop{
  b: bool
}

#[test]
fun test5(){
  let c = CanCopy{b: true};
  let c2 = c;
  let CanCopy{b} = &mut c2;
  *b = false;
  debug::print(&c2.b);
}

```

```

// copy
struct CanCopy has copy, drop{
  b: bool
}

#[test]
fun test5(){
  let c = CanCopy{b: true};
  let c2 = c;
  let CanCopy{b} = &mut c2;
  *b = false;
  debug::print(&c2.b);
  debug::print(&c.b);
}

```

#### key

值可以用作全局存储操作的 key。

```

struct Coin has key {
  value:u64
}

public entry fun mint(account: &signer, value: u64) {
  move_to(account, Coin{value});
}

#[test(account = @0x42)]
public fun test_mint(account: &signer) acquires Coin{
  let addr = signer::address_of(account);
  mint(account, 10);
  let coin = borrow_global<Coin>(addr).value;
  debug::print(&coin);
}

```

#### store

值可以被全局存储，通常配合 key 使用。

```

// store
struct Key has key,drop {
  a: Store
}

struct Store has store, drop {
  b: bool
}

#[test]
fun test10() {
  let k = Key {
    a: Store {
      b: false
    }
  };
  debug::print(&k.a.b)
}

```

通过运行以下代码可以更好理解以上概念：

```

module 0x42::Demo{
  use std::debug;
  use std::signer;

  struct Foo has drop{
    u: u64,
    b: bool
  }

  #[test]
  fun test(){
    let f = Foo{u: 42, b:true};
    debug::print(&f.u);
    debug::print(&f.b);
  }

  #[test]
  fun test2(){
    let f = Foo{u: 42,b: true};
    let Foo{u,b} = &mut f;
    *u = 43;
    debug::print(&f.u);
    debug::print(&f.b);
  }

  //copy
  struct Cancopy has drop, copy{
    x: u64,
    y: u64
  }

  #[test]
  fun test3(){
    let c = Cancopy{x: 42, y: 43};
    let c2 = copy c;
    let Cancopy{x,y} = &mut c2;
    *x = 44;
    debug::print(&c.x);
    debug::print(&c2.x);
  }

  //store
  struct Key has key,drop{
    s: Struct
  }
  struct Struct has store,drop{
    x: u64
  }

  #[test]
  fun test4(){
    let s = Struct{x: 42};
    let k = Key{s: s };
    debug::print(&k.s.x);
  }
}

```

## Lesson8-函数控制流 if while loop

```

module 0x42::Demo{
  use std::debug;

  #[test]
  fun test_if(){
    let x=5 ;
    let x2 = 10;
    if (x == 6){
      debug::print(&x);
    }else {
      debug::print(&x2)
    }
  }

  #[test]
  fun test_while(){
    let x =5 ;
    while ( x > 0 ) {
      x = x-1;
      if (x == 3){
        continue ;
      };
      debug::print(&x);
    }
  }

  #[test]
  fun test_loop(){
    let x=5;
    loop{
      x = x-1;
      if (x == 3 ){
        continue;
      };
      if (x == 0){
        break ;
      };
      debug::print(&x);
    }
  }
}

```

## Lesson9-模块的特性

### 引用

可以通过以下三种方式导入模块，用来更好的进行管理。注意命名不能重复。一般是 库::模块::方法：

```

use std::debug;
use std::debug::print;
use std::debug::{print as P, native_print, print};

fun main(){
  debug::print(&v);
  print(&v);
  P(&v)
}

```

### 作用域

可以再全局定义，也可以定义在函数内部，只在所在的作用域内有效。

```

fun main(){
  use std::debug::print;
  print(&v);
}

```

### Public(friend)

声明当前模块信任用模块，受信任模块可以调用当前模块中具有 public(friend) 的可见性函数。

### Public

声明当前模块对外可供其他接口调用的方法。

### Entry

声明可被链下调用的模块方法。

ma.move

```

module MyPackage::ma{
  friend MyPackage::mc;
  public fun num():u64{
    66
  }
  public(friend) fun num2():u64{
    88
  }
}

```

mb.move

```

module MyPackage::mb{
  #[test]
  fun test(){
    use std::debug::print;
    use MyPackage::ma::num;
    let n = num();
    print(&n);
  }
  // #[test]
  // fun test2(){
  //   use std::debug::print;
  //   use MyPackage::ma::num2;
  //
  //   let n =num2();
  //   print(&n);
  // }
}

```

mc.move

```

module MyPackage::mc{
  #[test_only]
  use MyPackage::ma::num;

  #[test]
  fun test(){
    use std::debug::print;
    use MyPackage::ma::num;

    let n = num();
    print(&n);
  }

  #[test]
  fun test2(){
    use std::debug::print;
    use MyPackage::ma::num2;

    let n =num2();
    print(&n);
  }
}

```
