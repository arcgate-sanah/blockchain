const TokenMaster = artifacts.require("TokenMaster");

contract("TokenMaster", (accounts) => {
  let tokenMaster;
  let owner = accounts[0];
  let buyer = accounts[1];
  

  beforeEach(async () => {
    tokenMaster = await TokenMaster.new("TokenMaster", "TN");
  });

  it("should list an occasion", async () => {
    await tokenMaster.list(
      "OccasionName",
      10, 
      100, 
      "2024-01-01", 
      "12:00 PM",
      "Event Location"
    );

    const occasion = await tokenMaster.getOccasion(1);
    assert.equal(occasion.name, "OccasionName", "Occasion name does not match");
    assert.equal(occasion.cost, 10, "Occasion cost does not match");
    assert.equal(occasion.tickets, 100, "Occasion tickets do not match");
  });

  it("should mint a token for a valid occasion and seat", async () => {
    await tokenMaster.list("TestEvent", 5, 10, "2024-01-01", "12:00 PM", "Location");

    const initialBalance = await web3.eth.getBalance(tokenMaster.address);
    const initialTokenSupply = await tokenMaster.totalSupply();

    await tokenMaster.mint(1, 1, { from: accounts[0], value: 5 });

    const finalBalance = await web3.eth.getBalance(tokenMaster.address);
    const finalTokenSupply = await tokenMaster.totalSupply();

    assert.equal(finalBalance - initialBalance, 5, "Incorrect ETH balance");
    assert.equal(finalTokenSupply - initialTokenSupply, 1, "Token not minted");
    
  });
  it("should return the correct seats taken", async () => {
    await tokenMaster.list(
      "TestEvent",
      5,
      10, 
      "2023-01-01", 
      "12:00 PM", 
      "Location"
    );

    const occasionId = 1;
    const seat = 1;
    
    await tokenMaster.mint(occasionId, seat, { from: accounts[0], value: 5 });

    const seatsTaken = await tokenMaster.getSeatsTaken(occasionId);

    assert.equal(seatsTaken.length, 1, "Incorrect number of seats taken");
    assert.equal(seatsTaken[0], seat, "Incorrect seat taken");
  });
  it("should return the correct occasion details", async () => {
    await tokenMaster.list(
      "OccasionName",
      10, 
      100, 
      "2023-01-01", 
      "12:00 PM", 
      "Event Location"
    );

    const occasionId = 1;
    const occasion = await tokenMaster.getOccasion(occasionId);

    assert.equal(occasion.id, occasionId, "Incorrect occasion ID");
    assert.equal(occasion.name, "OccasionName", "Incorrect occasion name");
    assert.equal(occasion.cost, 10, "Incorrect occasion cost");
    assert.equal(occasion.tickets, 100, "Incorrect occasion tickets");
    assert.equal(occasion.maxTickets, 100, "Incorrect occasion max tickets");
    
  });
  it("should withdraw funds", async () => {
    const owner = accounts[0];

    const initialBalance = await web3.eth.getBalance(owner);

    const tx = await tokenMaster.withdraw({ from: owner, gas: 2000000 });

    const finalBalance = await web3.eth.getBalance(owner);

    assert(
        finalBalance < initialBalance,
        "Owner balance not updated or decreased"
      );
     
  });
  
});
