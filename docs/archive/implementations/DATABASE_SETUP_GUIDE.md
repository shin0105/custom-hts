# Database Setup Instructions for Custom HTS

## Quick Setup (5 minutes)

Since the Python client cannot directly execute DDL statements, you need to run the SQL scripts manually in the Supabase UI. Follow these steps:

### Step 1: Access Supabase SQL Editor

1. Go to https://supabase.com/dashboard
2. Log in to your account
3. Select your project for Custom HTS
4. Click on **SQL Editor** in the left sidebar
5. Click **New Query** to open a blank SQL editor

### Step 2: Execute Base Tables Script

1. Open the file: `<repo-root>/database/init.sql`
2. Copy ALL the contents (Cmd+A, Cmd+C)
3. Paste into the Supabase SQL Editor
4. Click **Run** (or press Cmd+Enter)
5. Wait for completion (should see "Success" message)

**What this creates:**
- `korean_financials` table
- `us_financials` table  
- Indexes and triggers
- Update timestamp function

### Step 3: Execute Financial Statements Script

1. Open the file: `<repo-root>/database/financial_statements.sql`
2. Copy ALL the contents (Cmd+A, Cmd+C)
3. Paste into the Supabase SQL Editor (you can use the same query window)
4. Click **Run** (or press Cmd+Enter)
5. Wait for completion (should see "Success" message)

**What this creates:**
- `korean_balance_sheet` table
- `us_balance_sheet` table
- `korean_income_statement` table
- `us_income_statement` table
- `korean_cashflow_statement` table
- `us_cashflow_statement` table
- Indexes, triggers, and comments

### Step 4: Verify Tables Creation

Run the verification script to confirm all tables exist:

```bash
cd <repo-root>/backend
<repo-root>/backend/.venv/bin/python setup_database.py
```

**Expected output:**
```
================================================================================
  VERIFICATION RESULT: 8/8 tables found
================================================================================

✨ All tables exist! Database is ready for tests.
```

### Step 5: Run Tests

Once all tables are verified, proceed with running the API tests:

```bash
# Comprehensive API test
<repo-root>/backend/.venv/bin/python test_comprehensive_api.py

# Individual test scripts
<repo-root>/backend/.venv/bin/python test_workflow.py
<repo-root>/backend/.venv/bin/python test_financial_statements.py
<repo-root>/backend/.venv/bin/python test_api_raw_data.py
```

## Troubleshooting

### Issue: "relation already exists"

**This is normal!** The scripts use `CREATE TABLE IF NOT EXISTS` so they can be run multiple times safely. You can ignore these messages.

### Issue: "function update_updated_at_column() does not exist"

**Solution**: Make sure you ran `init.sql` first before `financial_statements.sql`. The function is defined in `init.sql`.

### Issue: Tables not showing in verification

**Solution**: 
1. Check Supabase SQL Editor for any error messages
2. Make sure you clicked "Run" after pasting the SQL
3. Try refreshing the Supabase dashboard
4. Check the "Table Editor" tab to see if tables appear there

### Issue: Permission denied

**Solution**: Make sure you're logged in as the project owner or have appropriate permissions to create tables.

## Quick Verification in Supabase UI

After running the SQL scripts, you can verify tables in the Supabase UI:

1. Go to **Table Editor** in the left sidebar
2. You should see 8 tables:
   - korean_financials
   - us_financials
   - korean_balance_sheet
   - us_balance_sheet
   - korean_income_statement
   - us_income_statement
   - korean_cashflow_statement
   - us_cashflow_statement

3. Click on any table to view its structure and columns

## What's Next?

After successful table creation:
1. ✅ Tables are ready
2. ✅ Run comprehensive API tests
3. ✅ Verify data insertion and retrieval
4. ✅ Check test results in `backend/test_results/` directory

---

**Time Required**: ~5 minutes  
**Difficulty**: Easy (copy-paste operations)  
**Prerequisites**: Supabase account with project access
