import Fastify from 'fastify'
const app = Fastify({ logger: true })
app.get('/health', async () => ({ status: 'ok', gateway: 'ok' }))
const port = process.env.PORT || 3000
app.listen({ port, host: '0.0.0.0' })
