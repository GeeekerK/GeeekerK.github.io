---
title: 如何编写基于零知识证明(Zero-Knowledge Proof)的Dapp
date: 2024-08-22 00:00:00 +0800
categories: [技术]
tags: [区块链, 智能合约, 零知识证明, Web3]
hidden: true
---

# 如何编写基于零知识证明(Zero-Knowledge Proof)的Dapp

过去几个月，零知识（ZK）加密技术风靡一时。随着新的 zkRollups 和 zkEVM 的发布，加密世界将注意力转向零知识证明为区块链上的隐私和可扩展性问题提供优雅解决方案的能力。该帖子假设您了解 Solidity 和 Typescript（react/next.js），并在此帮助下了解如何编写 ZK 电路（在 Circom 中）以及如何将其集成到 next.js 应用程序中。此外，关于有限域的基本知识也很有用。

这篇文章的主要目的不是解释如何在 Circom 中编写电路，而是概述从在 Circom 中编写代码到某人可以在他的 dApp 中将电路组连通合约和前端的一系列步骤。

## 我们将要构建的内容

我们将构建一个简单的 dApp，用于检查您提交的两个数字是否在 0 到 5 之间，以及它们是否不相等。您将在浏览器中生成 ZK 证明，并在交易中仅提交该证明，因此互联网上甚至合约本身都不会知道提交的两个数字，只会知道它们符合上述约束。

## 什么是 ZK 电路？

ZK 电路是一种程序，给定一组输入，输出一个证明，可以轻松验证电路内运行的每一步计算都是正确完成的。

## 如何编写 ZK 电路？

有多种方法可以创建 ZK 电路，使用一些更高级的领域特定语言（例如 Noir 和 Circom），您可以编写一个程序，该程序将被编译成电路。或者，还有像 Halo2 这样的低级包，您可以在其中精确指定值在代表电路的表中的位置。

今天，我们将使用 Circom 和 SnarkJS，因为它们都相对广泛使用，并且目前可用于在浏览器中生成证明。

## 值得了解的内容

使用 Circom 和大多数其他领域特定语言编写意味着我们需要熟悉处理字段元素（field elements）和编写约束。

### 字段元素

在 Circom 中，只有一种数据类型，即字段元素（field elements）。就本教程而言，您可以将字段元素视为任意数字基于所使用的椭圆曲线模大素数。Circom 中的默认椭圆曲线是 BN128。

### 约束

电路可以接受来自生成证明的实体的任意输入，因此这些输入必须在电路内受到约束，以便输入、输出和中间值落在某个可接受的值集内或与另一个变量保持某种关系。约束的两个例子是确保一个输入是另一个输入的平方，或者输入不等于输出。我们将在代码示例中讨论如何编写这些内容。

### 整体流程

总体流程分为三部分：Circuit（编写电路 → 编译为中间表示 → 基于 Powers of Tau 可信设置文件生成证明密钥）、Contract（编写利用或继承验证器的智能合约 → 导出智能合约验证器 → 部署合约 → 得到交易结果）、Frontend（用户输入 → 计算见证并生成证明 → 提交带证明的交易 → 交易结果反馈并更新前端）。

## Let's dive in

我将根据上面的一般流程图将其分为三个部分，以便更容易理解。电路部分讨论了在 Circom 中编写 ZK 电路的所有内容，然后我们将其导出到与前端部分交互的合约部分。

我们将使用的证明系统是 Plonk，它允许我们拥有一个通用的可信设置，而不必为每个电路生成额外的随机性。它比 Groth16 证明系统要慢，但足以满足我们现在的需求。

repo 的链接：https://github.com/ytham/zk_example_dapp

## 基本配置

在正式开始之前，我们需要安装以下内容：Node.js、Yarn、Foundry、Circom、SnarkJS、Metamask。

首先，让我们创建项目文件夹。我们将使用以下命令创建一个 next.js 应用程序：

```

yarn create next-app

```

配置新创立的 next.js 仓库（项目名、TypeScript、ESLint、src 目录、experimental app 目录、导入别名）。

完成所有操作后，进入文件夹，然后运行命令添加以下包：

```

yarn add circomlib snarkjs wagmi ethers@^5 axios @mantine/core @mantine/hooks @mantine/notifications @emotion/react

```

## Circuit(电路)

注：Powers of Tau 是一个旨在创建部分 zk-SNARK 参数的 MPC 仪式，适用于深度高达 2^21 的电路。它将所有 zk-SNARK MPC 共通的一个步骤整合到单一的仪式中，极大地降低了单次 MPC 的成本，并且允许其适应几乎无限数量的参与者。

### 配置

确保您位于项目文件夹中，并创建一个名为 circuits 的文件夹，然后在 circuits 内创建一个名为 build 的文件夹。我们将在本节中在 circuits 文件夹中工作。

### 编写电路

如上所述，我们今天要编写的电路需要两个输入，确保它们都在 0 到 5 之间，并且还确保它们彼此不相等。然后它将相乘并输出这两个值。我在下面为 circom 文件添加了内联注释：

注意：顶部显示 // file: 的行实际上不是文件的一部分，它只是告诉您文件相对于项目根目录的位置。

```

// file: /circuits/simple_multiplier.circom

pragma circom 2.1.3;

include "../node_modules/circomlib/circuits/comparators.circom";

template SimpleMultiplier() {
  // Private input signals
  signal input in[2];

  // Output signal (public)
  signal output out;

  // Create a constraint here saying that our two input signals cannot
  // equal each other.
  component isz = IsZero();
  isz.in <== in[0] - in[1];

  // The IsZero component returns 1 if the input is 0, or 0 otherwise.
  isz.out === 0;

  // Define the greater than and less than components that we'll define
  // inside the for loop below.
  component gte[2];
  component lte[2];

  // We loop through the two signals to compare them.
  for (var i = 0; i < 2; i++) {
    // Both the LessEqThan and GreaterEqThan components take number of
    // bits as an input. In this case, we want to ensure our inputs are
    // [0,5], which requires 3 bits (101).
    lte[i] = LessEqThan(3);

    // We put our circuit's input signal as the input signal to the
    // LessEqThan component and compare it against 5.
    lte[i].in[0] <== in[i];
    lte[i].in[1] <== 5;

    // The LessEqThan component outputs a 1 if the evaluation is true,
    // 0 otherwise, so we create this equality constraint.
    lte[i].out === 1;

    // We do the same with GreaterEqThan, and also require 3 bits since
    // the range of inputs is still [0,5].
    gte[i] = GreaterEqThan(3);

    // Compare our input with 0
    gte[i].in[0] <== in[i];
    gte[i].in[1] <== 0;

    // The GreaterEqThan component outputs a 1 if the evaluation is true,
    // 0 otherwise, so we create this equality constraint.
    gte[i].out === 1;
  }

  // Write a * b into c and then constrain c to be equal to a * b.
  out <== in[0] * in[1];
}

component main = SimpleMultiplier();

```

### 编译为中间表示(intermediate representation)

电路完成后，我们将把它编译为中间表示，称为 R1CS（等级 1 约束系统）。有关 R1CS 的更多信息，请参阅系列的其他文章。在电路文件夹中运行以下命令：

```

circom simple_multiplier.circom --r1cs --wasm --sym -o build

```

它将把 R1CS、WASM 和符号输出到 circuits/build 文件夹中，并显示电路数据，包括约束数量。

### Powers of Tau 可信设置文件

根据我们电路的大小（约束数量），我们可以使用许多 Powers of Tau 可信设置。为了减少证明时间，您需要使用最接近电路大小的 Powers of Tau。您可以在此存储库中找到可信设置文件：https://github.com/iden3/snarkjs#7-prepare-phase-2

让我们继续使用最小的一个（powersOfTau28_hez_final_08.ptau），它支持最多 256 个约束，因为我们的电路有 ~14 个约束。

### 生成证明密钥

现在，从电路目录中，我们将运行命令来生成证明密钥，我们将使用该密钥使用 R1CS 和 ptau 文件生成证明：

```

snarkjs plonk setup build/simple_multiplier.r1cs ptau/powersOfTau28_hez_final_08.ptau build/proving_key.zkey

```

## Contract(合约)

### 配置

在项目根目录中创建一个名为 contract 的新目录。cd contract，然后使用以下 Foundry 命令在 contract 文件夹中创建一个新项目：

```

forge init --no-commit

```

删除 script、src 和 test 文件夹中生成的启动文件。

在 contract 文件夹中添加一个 .env 文件，您将在其中添加要从中部署的钱包的私钥（确保此钱包有一些 GoerliETH，您可以从 Goerli PoW 水龙头获取）。您还需要拥有 Alchemy 帐户（或您选择的任何其他 RPC 提供商），并从 Alchemy 仪表板输入您的 RPC url：

```

// file: /contracts/.env

GOERLI_RPC_URL=https://eth-goerli.g.alchemy.com/v2/<YOUR_GOERLI_API_KEY>
PRIVATE_KEY=<YOUR_PRIVATE_KEY>

```

还将以下内容添加到您的 foundry.toml 文件中：

```

// file: /contracts/foundry.toml

[profile.default]
src = 'src'
out = 'out'
libs = ['lib']

# Add this
[rpc_endpoints]
goerli = "${GOERLI_RPC_URL}"

```

### 导出智能合约验证器

我们可以使用以下 SnarkJS 命令从项目根目录生成验证器智能合约：

```

snarkjs zkey export solidityverifier circuits/build/proving_key.zkey contracts/src/PlonkVerifier.sol

```

### 编写智能合约

我们将编写以下合约，该合约利用我们上面导出的 PlonkVerifier.sol 文件。合约仅根据 PlonkVerifier 的结果输出布尔值 true 或 false，但您可以想象编写一些可以铸造 NFT、转移代币、部署另一个合约或您能想到的任何其他东西。为简洁起见，我排除了测试。

```

// file: /contracts/src/SimpleMultiplier.sol

// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

// Interface to PlonkVerifier.sol
interface IPlonkVerifier {
  function verifyProof(bytes memory proof, uint[] memory pubSignals) external view returns (bool);
}

contract SimpleMultiplier {
  address public s_plonkVerifierAddress;

  event ProofResult(bool result);

  constructor(address plonkVerifierAddress) {
    s_plonkVerifierAddress = plonkVerifierAddress;
  }

  // ZK proof is generated in the browser and submitted as a transaction w/ the proof as bytes.
  function submitProof(bytes memory proof, uint256[] memory pubSignals) public returns (bool) {
    bool result = IPlonkVerifier(s_plonkVerifierAddress).verifyProof(proof, pubSignals);
    emit ProofResult(result);
    return result;
  }
}

```

通过在 contract 文件夹中运行以下命令来构建合约：

```

forge build

```

然后，返回到项目根目录，然后在 src/lib 文件夹中创建一个名为 abi 的文件夹，并将 json 输出复制到该文件夹中：

```

mkdir -p src/lib/abi

cp contract/out/SimpleMultiplier.sol/SimpleMultiplier.json src/lib/abi/。

```

### 部署合约

然后我们使用部署脚本部署合约：

```

// file: /contracts/scripts/SimpleMultiplier.s.sol

// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Script.sol";
import "../src/PlonkVerifier.sol";
import "../src/SimpleMultiplier.sol";

contract SimpleMultiplierScript is Script {
  function setUp() public {}

  function run() public {
    uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
    vm.startBroadcast(deployerPrivateKey);

    PlonkVerifier pv = new PlonkVerifier();
    SimpleMultiplier sm = new SimpleMultiplier(address(pv));

    vm.stopBroadcast();
  }
}

```

并使用以下命令运行部署脚本：

```

forge script script/SimpleMultiplier.s.sol SimpleMultiplierScript --broadcast --verify --rpc-url goerli

```

您将看到部署了两个合约。第一个是 PlonkVerifier 合约，第二个是 SimpleMultiplier 合约。我们只需要 SimpleMultiplier 合约的地址。让我们保存此地址以供稍后在前端使用：

```

// file: /src/shared/addresses.ts

export const Addresses = {
  SIMPLE_MULTIPLIER_ADDR: "<YOUR_DEPLOYED_CONTRACT_ADDR>" as `0x${string}`,
}

```

太棒了！现在我们已经部署了验证器和合约，并准备在浏览器中构建用户界面！

## 前端

### 配置

我们将通过 Github 将我们的 dApp 部署到 Vercel，因此请确保在继续之前在这两个地方都有一个帐户。

### 创建前端

我们将通过创建或修改以下文件来构建前端界面。为了简洁起见，我将多个项目放在不同的页面中，而不是为它们创建单独的组件。我也没有包括每个错误处理案例。这不是 next.js/react 教程，所以我假设读者已经粗略地了解了 next.js/react。

我们利用 Wagmi 包连接到区块链并将我们的整个应用程序包装在 WagmiConfig 中：

```

// file: /src/pages/_app.tsx

import '@/styles/globals.css'
import { WagmiConfig, createClient, configureChains, goerli } from 'wagmi'
import { publicProvider } from 'wagmi/providers/public'
import type { AppProps } from 'next/app'
import { MantineProvider } from '@mantine/core'
import { Notifications } from '@mantine/notifications';

// We'll just be using Goerli testnet for now
const { chains, provider, webSocketProvider } = configureChains(
  [goerli],
  [publicProvider()],
)

const client = createClient({
  autoConnect: true,
  provider,
  webSocketProvider,
})

export default function App({ Component, pageProps }: AppProps) {
  // We'll be using Wagmi sending our transaction and Mantine for CSS
  // and notifications
  return (
    <WagmiConfig client={client}>
      <MantineProvider withNormalizeCSS>
        <Notifications />
        <Component {...pageProps} />
      </MantineProvider>
    </WagmiConfig>
  )
}

```

我们的 index.tsx 文件包含一个 ConnectWalletButton 和两个输入字段，用户可以在其中输入数字 [0,5]。当用户按下两个输入字段的"提交"按钮时，它会向后端发送一个 POST 请求，其中包含输入以生成证明。生成证明后，它会获取该证明数据并将其作为交易提交到区块链上。

理想情况下，我们希望将其分成许多不同的组件文件，但为了简单起见，它们都放在一个文件中：

```

// file: /src/components/ConnectWalletButton.tsx

import { Button } from "@mantine/core"
import { disconnect } from "@wagmi/core";
import { useAccount, useConnect, useEnsName } from 'wagmi'
import { InjectedConnector } from 'wagmi/connectors/injected'

export const ConnectWalletButton = () => {
  const { address, isConnected } = useAccount();
  const { data: ensName } = useEnsName({ address });
  const { connect } = useConnect({
    connector: new InjectedConnector(),
  });

  const handleClick = () => {
    if (isConnected) {
      disconnect();
    } else {
      connect();
    }
  }

  const renderConnectText = () => {
    if (isConnected) {
      const start = address?.slice(0,6);
      const end = address?.slice(address.length-4, address.length);
      return `${start}...${end}`;
    } else {
      return "Connect Wallet";
    }
  }

  return (
    <Button onClick={handleClick}>
      { renderConnectText() }
    </Button>
  )
}

```

一旦我们从后端收到输入，我们就会解析输入，然后调用我们的 generateProof 库函数（我们将在下一节中实现）：

```

// file: /src/pages/api/generate_proof.ts

import { generateProof } from '@/lib/generateProof';
import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  const body = req?.body;
  if (body === undefined) {
    return res.status(403).json({error: "Request has no body"});
  }
  console.log(body);

  const input0 = parseInt(body.input0);
  const input1 = parseInt(body.input1);

  if (input0 === undefined || Number.isNaN(input0)
    || input1 === undefined || Number.isNaN(input1)) {
    return res.status(403).json({error: "Invalid inputs"});
  }
  const proof = await generateProof(input0, input1);

  if (proof.proof === "") {
    return res.status(403).json({error: "Proving failed"});
  }

  res.setHeader("Content-Type", "text/json");
  res.status(200).json(proof);
}

```

### 计算见证并生成证明

使用以下文件中的 snarkjs.plonk.fullProve 一步即可完成见证计算和证明生成。然后，数据被转换为 Solidity 调用数据 blob，该 blob 进一步分为 proof 和 publicSignals。

```

// file: /src/lib/generateProof.ts

import path from "path";
// @ts-ignore
import * as snarkjs from 'snarkjs';

export const generateProof = async (input0: number, input1: number): Promise<any> => {
  console.log(`Generating vote proof with inputs: ${input0}, ${input1}`);

  // We need to have the naming scheme and shape of the inputs match the .circom file
  const inputs = {
    in: [input0, input1],
  }

  // Paths to the .wasm file and proving key
  const wasmPath = path.join(process.cwd(), 'circuits/build/simple_multiplier_js/simple_multiplier.wasm');
  const provingKeyPath = path.join(process.cwd(), 'circuits/build/proving_key.zkey')

  try {
    // Generate a proof of the circuit and create a structure for the output signals
    const { proof, publicSignals } = await snarkjs.plonk.fullProve(inputs, wasmPath, provingKeyPath);

    // Convert the data into Solidity calldata that can be sent as a transaction
    const calldataBlob = await snarkjs.plonk.exportSolidityCallData(proof, publicSignals);
    const calldata = calldataBlob.split(',');

    console.log(calldata);

    return {
      proof: calldata[0],
      publicSignals: JSON.parse(calldata[1]),
    }
  } catch (err) {
    console.log(`Error:`, err)
    return {
      proof: "",
      publicSignals: [],
    }
  }
}

```

### 提交交易

交易在此文件中提交：

```

// file: /src/lib/executeTransaction.ts

import { Addresses } from '@/shared/addresses';
import { TransactionReceipt } from '@ethersproject/abstract-provider';
import { prepareWriteContract, writeContract } from '@wagmi/core';

export const executeTransaction = async (proof: any, publicSignals: Array<string>): Promise<TransactionReceipt> => {
  const abiPath = require('./abi/SimpleMultiplier.json');

  // Prepare the transaction data
  const config = await prepareWriteContract({
    address: Addresses.SIMPLE_MULTIPLIER_ADDR,
    abi: abiPath.abi,
    functionName: 'submitProof',
    args: [proof, publicSignals]
  });

  // Execute the transaction
  const writeResult = await writeContract(config);

  // Wait for the transaction block to be mined
  const txResult = await writeResult.wait();
  return txResult;
}

```

### 使用结果更新 UI

交易结果在 await txResult.wait() 的输出中提供给我们。在这里，我们刚刚向前端的用户发送了通知，但您可以按照自己认为最合适的方式使用信息更新 UI。

### 与您的应用交互

您可以通过在项目根目录中运行 `yarn dev` 来运行本地服务器以进行试用。

此外，您还可以部署到 Vercel，将您的 dApp 放在网络上供任何人使用。首先，创建一个新的 Github 存储库并提交所有更改并将文件推送到其中。转到 Vercel，然后添加一个新项目：选择 Add New... -> Project，选择您想要导入的 git 存储库（zk_example_dapp），确保框架预设是 Next.js，然后点击部署。等待几分钟让项目构建完成，然后你应该会得到一个可以使用或发送给朋友的链接。我的部署在这里：https://zk-example-dapp.vercel.app/

试试吧！导航到您在 Vercel 上部署的页面并尝试一下！

## 摘要

### 电路

1. 编写 circom 电路

1. 编译电路：`circom circuit.circom --r1cs --wasm --sym`

1. 下载 Powers of Tau 可信安装文件

1. 运行 Plonk setup 以获取证明密钥：`snarkjs plonk setup circuit.r1cs ptau_file.ptau proving_key.zkey`

### 合约

1. 导出验证者智能合约 `snarkjs zkey export solidityverifier proving_key.zkey verifier.sol`

1. 将验证器集成到您的 Solidity 项目中

### 前端

1. 接受用户输入

1. 一步计算见证并生成证明 `await snarkjs.plonk.fullProve({ inputs }, wasmPath, provingKeyPath);`

1. 向验证者合约提交带有证明的交易

## 结论

希望这篇文章对您的 zk dApp 开发之旅有所帮助。如果您有任何问题或需要任何澄清，请在评论中提出。

翻译自 [https://medium.com/@yujiangtham/writing-a-zero-knowledge-dapp-fd7f936e2d43](https://medium.com/@yujiangtham/writing-a-zero-knowledge-dapp-fd7f936e2d43)。本翻译目的主要用于 ZKP 技术学习。禁止非声明下商用。
