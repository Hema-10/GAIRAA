cube(`Customers`, {
  sql: `SELECT * FROM customers`,

  measures: {
    count: { type: `count`, sql: `customer_id` },
  },

  dimensions: {
    id: { sql: `customer_id`, type: `number`, primaryKey: true },
    name: { sql: `full_name`, type: `string` },
    segment: { sql: `customer_segment`, type: `string` },
    createdAt: { sql: `created_at`, type: `time` },
  },
});
