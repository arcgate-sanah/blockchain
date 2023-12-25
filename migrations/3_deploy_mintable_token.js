const MintableToken = artifacts.require("MintableToken");

module.exports = function (deployer) {
  const name = "MyMintableToken";
  const symbol = "MTK";

  deployer.deploy(MintableToken, name, symbol);
};
