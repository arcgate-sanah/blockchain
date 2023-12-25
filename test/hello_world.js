const HelloWorld = artifacts.require("HelloWorld");

contract("HelloWorld", accounts => {
  it("should return 'Hello World!'", async () => {
    const helloWorldInstance = await HelloWorld.deployed();
    const result = await helloWorldInstance.sayHello();

    assert.equal(result, "Hello World!");
  });
});
