cube(`LoanPayments`, {
  sql: `SELECT * FROM loan_payments`,

  joins: {
    Loans: {
      relationship: `many_to_one`,
      sql: `${CUBE}.loan_id = ${Loans}.loan_id`,
    },
  },

  measures: {
    count: { type: `count`, sql: `payment_id` },
    amountPaid: { type: `sum`, sql: `amount_paid`, format: `currency` },
    successfulAmount: {
      type: `sum`,
      sql: `amount_paid`,
      format: `currency`,
      filters: [{ sql: `${CUBE}.payment_status = 'SUCCESS'` }],
    },
  },

  dimensions: {
    id: { sql: `payment_id`, type: `number`, primaryKey: true },
    status: { sql: `payment_status`, type: `string` },
    paymentDate: { sql: `payment_date`, type: `time` },
  },
});
