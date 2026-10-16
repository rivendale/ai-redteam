// Excerpt (lines 1-60) of lib/common.js from github.com/revert-finance/liquidator-js, commit 6a94b77c7f4cc30da67c6680258922559a12587e.
// MIT License, Copyright (c) 2024 Revert Labs Inc. Unmodified except for this header and the cut after line 60.
const axios = require('axios');
const ethers = require("ethers");
const univ3prices = require('@thanpolas/univ3prices')
const Mutex = require('async-mutex').Mutex
const mutex = new Mutex()
const fs = require('fs')

const { AlphaRouter, SwapType } = require('@uniswap/smart-order-router')
const { Token, CurrencyAmount, TradeType, Percent, ChainId } = require('@uniswap/sdk-core')

const mode = "LIQUIDATOR"
const network = process.env.NETWORK
const exchange = process.env.EXCHANGE || "uniswap-v3"

function isAerodromeVault() {
    return exchange === "aerodrome" && network === "base"
}

const IERC20_ABI = require("../contracts/IERC20.json")
const POOL_ABI = require("../contracts/IUniswapV3Pool.json")
const FACTORY_RAW = require("../contracts/IUniswapV3Factory.json")
const NPM_RAW = require("../contracts/INonfungiblePositionManager.json")
const AERODROME_NPM_ABI = require("../contracts/IAerodromeNPM.json")

const BigNumber = ethers.BigNumber

const Q32 = BigNumber.from(2).pow(32)
const Q64 = BigNumber.from(2).pow(64)
const Q96 = BigNumber.from(2).pow(96)

const genericPoolContract = new ethers.Contract(ethers.constants.AddressZero, POOL_ABI)

// cache for price pools used to estimate token value in ETH
const pricePoolCache = {}

const observationCardinalityIncreases = {}

// current prices are stored here
const prices = {}

const provider = new ethers.providers.JsonRpcProvider(process.env["RPC_URL_" + network.toUpperCase()])
const privateProvider = process.env["PRIVATE_RPC_URL_" + network.toUpperCase()] ? new ethers.providers.JsonRpcProvider(process.env["PRIVATE_RPC_URL_" + network.toUpperCase()]) : provider

// Support separate private key for Aerodrome liquidator, falls back to default
const privateKey = isAerodromeVault()
    ? (process.env["PRIVATE_KEY_LIQUIDATOR_AERODROME"] || process.env["PRIVATE_KEY_" + mode])
    : process.env["PRIVATE_KEY_" + mode]
const signer = new ethers.Wallet(privateKey, provider)
const privateSigner = new ethers.Wallet(privateKey, privateProvider)

const npmAbi = isAerodromeVault() ? AERODROME_NPM_ABI : NPM_RAW.abi
const npmContract = new ethers.Contract(getNPMAddress(), npmAbi, provider)

// current ws provider, is replaced on disconnect
let wsProvider;

// last nonce
let lastNonce;
const pendingTxs = {};

