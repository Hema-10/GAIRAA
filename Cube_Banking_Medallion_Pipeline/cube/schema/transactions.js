cube(`Transactions`, {
  sql: `SELECT * FROM bank_transactions`,

  joins: {
    Accounts: {
      relationship: `many_to_one`,
      sql: `${CUBE}.account_id = ${Accounts}.account_id`,
    },
  },

  measures: {
    count: { type: `count`, sql: `transaction_id` },
    successfulCount: {
      type: `count`,
      sql: `transaction_id`,
      filters: [{ sql: `${CUBE}.status = 'SUCCESS'` }],
    },
    failedCount: {
      type: `count`,
      sql: `transaction_id`,
      filters: [{ sql: `${CUBE}.status = 'FAILED'` }],
    },
    totalAmount: { type: `sum`, sql: `amount`, format: `currency` },
    successfulAmount: {
      type: `sum`,
      sql: `amount`,
      format: `currency`,
      filters: [{ sql: `${CUBE}.status = 'SUCCESS'` }],
    },
    averageAmount: { type: `avg`, sql: `amount`, format: `currency` },
  },

  dimensions: {
    id: { sql: `transaction_id`, type: `number`, primaryKey: true },
    type: { sql: `transaction_type`, type: `string` },
    status: { sql: `status`, type: `string` },
    channel: { sql: `channel`, type: `string` },
    merchantCategory: { sql: `merchant_category`, type: `string` },
    currency: { sql: `currency`, type: `string` },
    transactionTime: { sql: `transaction_time`, type: `time` },
  },
});
