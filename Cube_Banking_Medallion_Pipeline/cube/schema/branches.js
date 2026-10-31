cube(`Branches`, {
  sql: `SELECT * FROM branches`,

  measures: {
    count: { type: `count`, sql: `branch_id` },
  },

  dimensions: {
    id: { sql: `branch_id`, type: `number`, primaryKey: true },
    name: { sql: `branch_name`, type: `string` },
    city: { sql: `city`, type: `string` },
  },
});
