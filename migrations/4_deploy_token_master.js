const TokenMaster = artifacts.require("TokenMaster");

module.exports = function (deployer) {
  deployer.deploy(TokenMaster, "TokenMaster", "TN");
};
