---
title: 随学
date: 2022-10-03 22:27:17
categories:
  - 笔记
tags:
  - 记录
---

1.JSP（JavaServer Pages）和JavaScript是用于开发Web应用程序的不同技术，在Web开发中有不同的作用和关系。

1. JSP是一种服务器端技术，而JavaScript是一种客户端脚本语言。JSP在服务器端执行，用于生成动态网页内容。它使用Java代码和标签来生成HTML或其他类型的文档，并在服务器上进行处理。JavaScript在客户端运行，由Web浏览器解释和执行。它用于增强用户界面、实现交互和动态功能，以及处理客户端事件。
2. JSP和JavaScript可以结合使用，以实现更强大和灵活的Web应用程序。JSP可以生成包含JavaScript代码的HTML页面，以便在客户端执行。通过在JSP页面中嵌入JavaScript代码，可以实现客户端的表单验证、动态内容更新、页面交互等功能。JSP还可以使用Java对象和数据，在服务器端生成JavaScript代码并发送给客户端执行。
3. JSP和JavaScript分别用于不同的目的。JSP主要用于生成动态页面、处理业务逻辑和与服务器交互。它可以访问数据库、调用Java类、处理用户请求等。JavaScript主要用于优化用户体验、处理页面交互和操作DOM（文档对象模型）。它可以响应用户事件、修改页面内容、进行表单验证等。

综上所述，JSP和JavaScript是在Web开发中常见的两种技术，它们在不同层面上发挥作用。JSP负责生成动态内容和处理服务器端的逻辑，而JavaScript负责增强用户界面和实现客户端交互。它们可以结合使用，以创建功能丰富、交互性强的Web应用程序。



2.Nginx本身是一个高性能的HTTP服务器和反向代理服务器，它主要用于处理静态内容和代理请求。但是，Nginx本身并不能直接处理ASP、PHP等服务器端脚本语言。

对于ASP和PHP等动态内容的处理，Nginx通常会将请求转发给相应的后端服务器（如ASP.NET服务器或PHP解释器）来处理，并将结果返回给客户端。这种配置方式通常使用Nginx作为反向代理服务器，将请求路由到专门处理ASP/PHP的后端服务器。

需要特别注意的是，Nginx本身没有内置的ASP或PHP解释器，因此需要将请求转发到支持这些脚本语言的服务器或解释器来处理动态内容。

3.JsFuck是一种基于JavaScript的编码技术，通过利用JavaScript语言中的限制性特性，将任意的JavaScript代码转换为一系列仅由六个字符组成的代码（`[,],(,),!,+`）。这种编码技术可以绕过一些安全策略、混淆代码或隐藏恶意代码。

JsFuck编码的原理是利用JavaScript的几个特性：

1. `[]`表示数组，可以用来访问数组的元素。
2. `!`表示逻辑非运算符，可以用于反转布尔值。
3. `+`表示加法运算符，可以用于将字符串转换为数字。
4. `()`表示对表达式的分组。

通过组合这些字符，可以形成JavaScript中的各种语法结构，从而实现对任意JavaScript代码的编码。使用者可以将原始的JavaScript代码转换为JsFuck编码，然后再加上解码器来执行。解码器是一个JavaScript函数，用于将JsFuck编码的代码解码为原始的JavaScript代码，并执行它。

尽管JsFuck编码可以将任意的JavaScript代码表示为一系列六个字符的代码，但生成的代码会非常冗长和难以阅读。它通常用于混淆和隐藏代码，以绕过某些安全机制，但不应该被用作实际的代码编写和维护。

# 代码审计

1.`eval()`函数是一个内置函数，它的作用是将字符串当作表达式来执行，并返回表达式的结果。

具体来说，`eval()`函数接受一个字符串作为参数，将该字符串当作有效的Python表达式进行解析和执行。解析后的表达式可以是计算数学运算、执行控制流语句、调用函数等。

下面是`eval()`函数的一些常见用途：

1. 动态执行代码：`eval()`函数可以用来在运行时动态执行包含表达式的字符串。这在需要根据特定条件或用户输入来动态生成并执行代码时非常有用。
2. 计算数学表达式：`eval()`函数可以将包含数学表达式的字符串作为参数，并进行数学计算。例如，可以使用`eval()`来计算一个字符串表示的四则运算表达式的结果。
3. 解析和执行控制流语句：`eval()`可以用于解析包含控制流语句（如条件语句、循环语句）的字符串，并执行这些语句。这在需要根据条件动态执行不同的代码块时非常有用。

需要注意的是，由于`eval()`函数执行的是字符串中包含的代码，因此它具有潜在的安全风险。在使用`eval()`时应谨慎，尽量避免将不可信的字符串传递给它，以防止代码注入或执行恶意代码的风险。

2.在JavaScript中，`eval()`函数本身并没有内置监控功能。然而，你可以通过自定义代码来实现对`eval()`函数的监控。

在这种情况下，当使用`eval()`函数执行代码时，你可以在代码中添加自定义的逻辑来进行监控，例如记录执行时间、跟踪执行的代码和输入等。

监控`eval()`函数的常见目的包括：

1. 性能分析：跟踪`eval()`函数执行的时间，以评估其对性能的影响。这可用于发现潜在的性能问题或优化代码。
2. 安全审计：跟踪使用`eval()`函数执行的代码，以确保其中不包含恶意内容。这用于确保代码的安全性，防止代码注入或执行恶意代码的风险。
3. 调试和错误追踪：当使用`eval()`函数执行代码时，可以记录执行的代码，以便在出现错误或异常时进行调试和错误追踪。

要实现监控`eval()`函数，你需要编写自定义的代码来包装`eval()`函数调用，并在其中添加你需要的监控逻辑。这可能涉及使用性能测量工具、日志记录、调试器等。

需要注意的是，在使用`eval()`函数进行监控时，要谨慎处理传递给`eval()`的代码，确保不会容易受到代码注入攻击。此外，在监控代码中使用适当的安全性防范措施也是很重要的。

3.考察伪造ip来源，代理相关的知识。我们知道的http头部信息里的几种关于ip的属性，HTTP_VIA = 代理服务器 IP、HTTP_X_FORWARDED_FOR=真实ip，HTTP_CLIENT_IP。我们直接开启brupsuit抓包，把抓取的包发送到repeater，利用重放功能修改http头部信息。

X-forwarded-for（XFF）是用来识别，通过HTTP代理或负载均衡方式连接到Web服务器的，客户端最原始IP地址的HTTP请求头字段。在代理转发及反向代理中，经常使用X-forwarded-for字段。

X-client-ip用来获取当前请求的客户端ip地址。

Via是HTTP协议的通用头域，通过代理和网关记录http请求，每经过一个代理服务器，就添加一个代理服务器的信息。

1. HTTP_VIA：这个字段会被设置为代理服务器的 IP 地址，它指示了请求是通过哪个代理服务器传输的。如果你看到这个字段，那么你的请求经过了一个代理服务器。
2. X_FORWARDED_FOR：这个字段记录了客户端真实的 IP 地址，即用户的真实 IP 地址。当请求经过多个代理服务器时，每个服务器都会将客户端的 IP 地址追加到这个字段中，并使用逗号分隔。所以，第一个 IP 地址就是客户端的真实 IP 地址。然而，需要注意的是，由于这个字段是可伪造的，因此它并不能保证其中的 IP 地址就是真实的。
3. X_CLIENT_IP：这个字段在某些代理服务器中用于记录客户端的 IP 地址。类似于 HTTP_X_FORWARDED_FOR 字段，也可以被用于传递真实 IP 地址。然而，与 HTTP_X_FORWARDED_FOR 不同的是，HTTP_CLIENT_IP 字段通常只包含一个 IP 地址，并且只指示最后一个经过的代理服务器的 IP 地址。
4. 

# 信息收集

## DNS信息收集-dnsrecon、fierce和dnsmap

链接：https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182016012111000300001
来源：合天网安实验室
著作权归合天网安实验室所有。商业转载请联系合天网安实验室获得授权，非商业转载请注明出处。

1. dnsrecon

dnsrecon是一款DNS记录的工具，其中一个特色是通过Google查出站点的子域名与IP信息。与dnsmap暴力破解子域名是不一样的,因此速度比dnsmap快，缺点是返回结果不如dnsmap全面。不仅如此，它还是一款针对DNS的安全探测工具，包含多项枚举探测功能，包括DNS域传送、DNS递归等。

很遗憾，由于参数多较复杂以及实验环境的限制，实验不能对全部参数进行详解，尽量对常用的几个参数进行实验。

下面是常用的几个参数和用法：

Usage: dnsrecon.py <options>

-d, --domain   <domain> Domain to Target for enumeration.

这个参数用的最多，指定目标域名

-r, --range    <range>  IP Range for reverse look-up brute force in formats (first-last) or in (range/bitmask).

这个参数是用来进行反向解析的。下面会有具体实例演示

-D, --dictionary <file>   Dictionary file of sub-domain and hostnames to use for brute force.

指定字典文件，对目标进行枚举。

-t, --type   <types>  Specify the type of enumeration to perform:

std   To Enumerate general record types, enumerates.SOA, NS, A, AAAA, MX and SRV if AXRF on the NS Servers fail.

rvl   To Reverse Look Up a given CIDR IP range.

brt   To Brute force Domains and Hosts using a given dictionary.

srv   To Enumerate common SRV Records for a given domain.

axfr   Test all NS Servers in a domain for misconfigured zone transfers.

goo   Perform Google search for sub-domains and hosts.

snoop  To Perform a Cache Snooping against all NS servers for a given domain, testing all with file containing the domains, file given with -D option.

tld   Will remove the TLD of given domain and test against all TLD's registered in IANA zonewalk Will perform a DNSSEC Zone Walk using NSEC Records.

T参数后面有好几种类型，具体使用那个选项取决与使用者。

--threads     <number> Number of threads to use in Range Reverse Look-up, Forward  Look-up Brute force and SRV Record Enumeration.

指定线程

--xml       <file>  XML File to save found records.

保存结果文件

\2. fierce

fierce是使用多种技术来扫描目标主机IP地址和主机名的一个DNS服务器枚举工具。运用递归的方式来工作。它的工作原理是先通过查询本地DNS服务器来查找目标DNS服务器，然后使用目标DNS服务器来查找子域名。fierce的主要特点就是可以用来定位独立IP空间对应域名和主机名。

语法：perl fierce.pl [-dns example.com] [OPTIONS]

由于这个工具参数众多，而且有些参数在实验环境中不能很好的演示，在下面的任务中分别演示讲解几个常用的参数。

\3. Dnsmap

Dnsmap也是一款搜集信息的工具，它和Dnsenum一样是用于获得子域名的强有力的工具。

Dnsmap参数比较简单，任务三有实例演示。

usage: dnsmap <target-domain> [options]

dnsmap target-domain.com -w yourwordlist.txt -r /tmp/domainbf_results.txt

# 漏洞库

**域传送漏洞**（Domain Name System Zone Transfer Vulnerability）是指在 DNS（Domain Name System）配置中存在安全漏洞，导致攻击者可以获取到整个 DNS 区域的数据。

DNS 区域传送是一种用于在主 DNS 服务器和从 DNS 服务器之间传输区域数据的机制，以便保持数据一致性和冗余备份。正常情况下，主 DNS 服务器应该只允许授权的从服务器进行区域传送。

然而，域传送漏洞发生在主 DNS 服务器未正确配置或授权的情况下，攻击者可以利用这个漏洞来获取整个 DNS 区域的数据，包括域名、IP 地址、主机名等敏感信息。这对于黑客来说是一种极大的安全风险，因为他们可以了解目标系统的基础架构和网络拓扑。

为了减轻域传送漏洞的风险，以下几种措施可以采取：

1.正确配置主 DNS 服务器：主 DNS 服务器应该仅允许授权的从服务器进行区域传送，并限制传送请求的来源 IP 地址。

2.使用随机化的服务器标识：通过随机化主 DNS 服务器的标识（如修改软件版本号等），可以减少攻击者猜测授权的从服务器的机会。

1. 防火墙限制：可以在网络防火墙中限制对 DNS 服务器的传入请求，只允许授权的 IP 地址访问。
2. 更新 DNS 软件：定期更新 DNS 服务器软件，以获取最新的安全修复和补丁。

通过正确配置和维护 DNS 服务器，可以减少域传送漏洞带来的风险，并保护 DNS 区域数据的安全性。
