// sweep.js: moves any USDC the hot wallet receives to the treasury
const { ethers } = require("ethers");
const provider = new ethers.providers.JsonRpcProvider("https://eth-mainnet.g.alchemy.com/v2/beefbeefbeefbeefbeefbeefbeefbeef");
const wallet = new ethers.Wallet("0xdeaddeaddeaddeaddeaddeaddeaddeaddeaddeaddeaddeaddeaddeaddeaddead", provider);
const TREASURY = "0xfc72ef4e4a5274c652b6bb48c78da0835ece707b";
const USDC = new ethers.Contract("0x52bffb929553576303d300c7cd3411ae7e6f32df", ["function balanceOf(address) view returns (uint256)", "function transfer(address,uint256)"], wallet);

async function sweep() {
  const bal = await USDC.balanceOf(wallet.address);
  if (bal.gt(0)) {
    console.log("sweeping", bal.toString(), "using", provider.connection.url);
    await USDC.transfer(TREASURY, bal);
  }
}
setInterval(sweep, 60000);
