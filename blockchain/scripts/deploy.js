async function main() {
  const MediaRegistry = await ethers.getContractFactory("MediaRegistry");
  const registry = await MediaRegistry.deploy();
  await registry.waitForDeployment();
  console.log("MediaRegistry deployed to:", await registry.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
