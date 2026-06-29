import { Hono } from 'hono'
import { sha256 } from 'hono/utils/crypto'

const app = new Hono()

app.post('/complex-transform', async (c) => {
  const start = performance.now()
  const body = await c.req.json()
  const items = Array.isArray(body.items) ? body.items : []

  const total = items.reduce((sum, item) => sum + Number(item.numeric_value || 0), 0)
  const avg = items.length ? total / items.length : 0
  const concat = items.map((item) => String(item.string_data || '')).join('')
  const hash = await sha256(concat)
  const base = concat.length / 2

  const transformed = items.map((item) => {
    const numeric = Number(item.numeric_value || 0)
    const score = (numeric * 1.5) + base
    return { ...item, computed_score: score }
  }).sort((a, b) => b.computed_score - a.computed_score)

  const end = performance.now()
  return c.json({
    average_numeric_value: avg,
    concatenated_hash: hash,
    transformed_and_sorted_items: transformed,
    server_processing_time_ms: end - start,
  })
})

export default {
  port: 8894,
  fetch: app.fetch,
}
