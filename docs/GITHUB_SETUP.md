# GitHub Actions Secrets Configuration Guide

This guide explains how to set up the required secrets for the GitHub Actions workflow to test the financial statements API.

## Required Secrets

The workflow needs the following secrets to be configured in your GitHub repository:

### 1. DART_API_KEY
- **Description**: API key for OPENDART (Korean Financial Supervisory Service)
- **Get it from**: https://opendart.fss.or.kr/
- **Used for**: Fetching Korean financial statements for companies like Samsung (005930)

### 2. SUPABASE_URL
- **Description**: Your Supabase project URL
- **Format**: `https://your-project-id.supabase.co`
- **Get it from**: Supabase Dashboard → Settings → API → Project URL
- **Used for**: Connecting to the Supabase database

### 3. SUPABASE_KEY
- **Description**: Your Supabase anon/service key
- **Get it from**: Supabase Dashboard → Settings → API → Project API keys → `anon` `public` key
- **Used for**: Authenticating with Supabase database
- **Note**: Use the `anon` public key for read/write operations, or `service_role` key for admin operations

### 4. HANTU_API_KEY (Optional)
- **Description**: Korean Investment Securities API key
- **Get it from**: https://apiportal.koreainvestment.com/
- **Used for**: Real-time Korean stock trading (optional for financial statements)

### 5. HANTU_API_SECRET (Optional)
- **Description**: Korean Investment Securities API secret
- **Get it from**: https://apiportal.koreainvestment.com/
- **Used for**: Real-time Korean stock trading (optional for financial statements)

## How to Add Secrets to GitHub

### Step 1: Navigate to Repository Settings
1. Go to your GitHub repository: https://github.com/shin0105/custom-hts
2. Click on **Settings** (in the repository menu)

### Step 2: Access Secrets Configuration
1. In the left sidebar, click **Secrets and variables**
2. Click **Actions**

### Step 3: Add Each Secret
1. Click **New repository secret**
2. Enter the **Name** (exactly as shown above, e.g., `DART_API_KEY`)
3. Enter the **Secret** (paste your actual API key/URL)
4. Click **Add secret**
5. Repeat for all required secrets

## Configuration in Different Environments

### Local Development (.env file)
```bash
# Create .env file in project root
DART_API_KEY=your_dart_api_key_here
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
HANTU_API_KEY=your_hantu_api_key_here
HANTU_API_SECRET=your_hantu_api_secret_here
```

### GitHub Codespaces
Codespaces uses **Codespaces secrets** which are different from Actions secrets:
1. Go to GitHub → Settings → Codespaces → Secrets
2. Add the same secrets there for use in Codespaces
3. These are automatically available as environment variables in Codespaces

### GitHub Actions
Uses **Actions secrets** (as described in the steps above):
1. Go to Repository → Settings → Secrets and variables → Actions
2. Add secrets there for use in workflows
3. The workflow file already references these secrets correctly

## How the Workflow Uses Secrets

In `.github/workflows/test-financial-api.yml`, secrets are passed as environment variables:

```yaml
jobs:
  test-financial-api:
    runs-on: ubuntu-latest
    
    env:
      DART_API_KEY: ${{ secrets.DART_API_KEY }}
      SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
      SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
      HANTU_API_KEY: ${{ secrets.HANTU_API_KEY }}
      HANTU_API_SECRET: ${{ secrets.HANTU_API_SECRET }}
```

## How the Code Uses Environment Variables

In `backend/src/utils/config.py`:

```python
class Settings:
    # OPENDART API
    DART_API_KEY: str = os.getenv("DART_API_KEY", "")
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
```

**All three are configured identically:**
- Read from environment variables using `os.getenv()`
- Work the same way in all environments (local, Codespaces, GitHub Actions)
- Default to empty string if not set

## Verifying Configuration

### Check if Secrets are Set
After adding secrets, trigger the workflow manually:
1. Go to **Actions** tab
2. Select **Test Financial Statements API** workflow
3. Click **Run workflow**
4. Check the "Verify environment variables" step to see which are configured

### Expected Output (All Configured)
```
✅ DART_API_KEY is set
✅ SUPABASE_URL is set
✅ SUPABASE_KEY is set
```

### If Secrets are Missing
```
⚠️  DART_API_KEY not set
⚠️  SUPABASE_URL not set
⚠️  SUPABASE_KEY not set
```

## Troubleshooting

### Workflow fails with "Supabase client not initialized"
**Solution**: Add `SUPABASE_URL` and `SUPABASE_KEY` to GitHub Actions secrets

### Workflow fails with "DART API key not configured"
**Solution**: Add `DART_API_KEY` to GitHub Actions secrets

### Configuration works in Codespaces but not in Actions
**Cause**: Codespaces secrets and Actions secrets are separate
**Solution**: Add secrets to both locations if you use both environments

### How to test locally
```bash
# 1. Create .env file with your secrets
cp .env.example .env
# Edit .env and add your actual keys

# 2. Run tests
cd backend
python test_workflow.py
python test_financial_statements.py
```

## Security Best Practices

1. **Never commit secrets to git** - Use .env files locally (already in .gitignore)
2. **Use separate keys for development and production**
3. **Rotate keys periodically**
4. **Use minimum required permissions** - Use Supabase `anon` key, not `service_role` unless needed
5. **Monitor secret usage** - Check Actions logs for unusual activity

## Summary

Both DART_API_KEY and SUPABASE credentials are configured **identically**:
- ✅ Defined in `.env.example` as templates
- ✅ Read from environment variables in `config.py`
- ✅ Passed from GitHub secrets in workflow
- ✅ Work the same way in all environments

The configuration is already correct. You just need to add the actual secret values to GitHub repository settings.
