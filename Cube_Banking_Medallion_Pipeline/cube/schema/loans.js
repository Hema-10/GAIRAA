cube(`Loans`, {
  sql: `SELECT * FROM loans`,

  joins: {
    Customers: {
      relationship: `many_to_one`,
      sql: `${CUBE}.customer_id = ${Customers}.customer_id`,
    },
    Branches: {
      relationship: `many_to_one`,
      sql: `${CUBE}.branch_id = ${Branches}.branch_id`,
    },
    LoanPayments: {
      relationship: `one_to_many`,
      sql: `${CUBE}.loan_id = ${LoanPayments}.loan_id`,
    },
  },

  measures: {
    count: { type: `count`, sql: `loan_id` },
    principalAmount: { type: `sum`, sql: `principal_amount`, format: `currency` },
    averageInterestRate: { type: `avg`, sql: `interest_rate` },
  },

  dimensions: {
    id: { sql: `loan_id`, type: `number`, primaryKey: true },
    status: { sql: `loan_status`, type: `string` },
    issuedDate: { sql: `issued_date`, type: `time` },
    dueDate: { sql: `due_date`, type: `time` },
  },
});
