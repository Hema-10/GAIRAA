cube(`Accounts`, {
  sql: `SELECT * FROM accounts`,

  joins: {
    Branches: {
      relationship: `many_to_one`,
      sql: `${CUBE}.branch_id = ${Branches}.branch_id`,
    },
  },

  measures: {
    count: { type: `count`, sql: `account_id` },
    totalBalance: { type: `sum`, sql: `current_balance`, format: `currency` },
    averageBalance: { type: `avg`, sql: `current_balance`, format: `currency` },
  },

  dimensions: {
    id: { sql: `account_id`, type: `number`, primaryKey: true },
    type: { sql: `account_type`, type: `string` },
    status: { sql: `status`, type: `string` },
    openedAt: { sql: `opened_at`, type: `time` },
  },
});
