const { ApolloServer } = require('@apollo/server');
const { ApolloGateway } = require('@apollo/gateway');
const { startStandaloneServer } = require('@apollo/server/standalone');

async function startGateway() {
  // Initialize the gateway
  const gateway = new ApolloGateway({
    serviceList: [
      // Add your federated services here
      // { name: 'users', url: 'http://localhost:4001' },
      // { name: 'products', url: 'http://localhost:4002' },
    ],
  });

  // Create Apollo Server with the gateway
  const server = new ApolloServer({
    gateway,
  });

  // Start the server
  const { url } = await startStandaloneServer(server, {
    listen: { port: 4000 },
  });

  console.log(`🚀 Gateway ready at ${url}`);
}

startGateway().catch(err => {
  console.error('Error starting gateway:', err);
  process.exit(1);
});