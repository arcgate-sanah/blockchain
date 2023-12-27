const MintableToken = artifacts.require('MintableToken');

contract('MintableToken', (accounts) => {
  let mintableToken;

  // Deploy the contract before each test
  beforeEach(async () => {
    mintableToken = await MintableToken.new('MyMintableToken', 'MTK');
  });

  it('should have the correct name and symbol', async () => {
    const name = await mintableToken.name();
    const symbol = await mintableToken.symbol();

    assert.equal(name, 'MyMintableToken', 'Incorrect name');
    assert.equal(symbol, 'MTK', 'Incorrect symbol');
  });

  it('should mint new tokens to the specified address', async () => {
    const recipient = accounts[1];
    const amountToMint = 1000;

    await mintableToken.mint(recipient, amountToMint);

    const balance = await mintableToken.balanceOf(recipient);
    assert.equal(balance.toNumber(), amountToMint, 'Incorrect balance after minting');
  });

  it('should only allow the owner to mint new tokens', async () => {
    const nonOwner = accounts[1];
    const recipient = accounts[2];
    const amountToMint = 1000;

    // Attempt to mint from a non-owner account
    try {
      await mintableToken.mint(recipient, amountToMint, { from: nonOwner });
      assert.fail('Minting should only be allowed by the owner');
    } catch (error) {
      assert.include(error.message, 'revert', 'Expected "revert" but got ' + error.message);
    }
  });
  it("should mint new tokens", async () => {
    const recipient = accounts[1];
    const amountToMint = 10000;

    const balanceBefore = await mintableToken.balanceOf(recipient);

    await mintableToken.mint(recipient, amountToMint);

    const balanceAfter = await mintableToken.balanceOf(recipient);

    assert.equal(
      balanceAfter.toNumber(),
      balanceBefore.toNumber() + amountToMint,
      "New tokens were not minted successfully"
    );
  });
});
