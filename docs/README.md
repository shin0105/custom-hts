# Custom HTS Documentation

Welcome to the Custom HTS documentation! This directory contains comprehensive documentation for the Home Trading System application.

## Quick Links

### Getting Started
- [Setup Guide](SETUP.md) - Complete setup instructions for local development
- [GitHub Setup](GITHUB_SETUP.md) - GitHub Actions and Codespaces configuration
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project

### Project Overview
- [Project Summary](PROJECT_SUMMARY.md) - High-level project overview and architecture
- [API Documentation](API.md) - Complete REST API reference

### External APIs
- [KDevelopers API](KDEVELOPERS_API.md) - Korean Investment Securities API integration
- [OPENDART API](OPENDART_API.md) - Korean Financial Supervisory Service API
- [Supabase Integration](SUPABASE_INTEGRATION.md) - Database and storage integration

### Stock Market Data
- [Stock Master Files](STOCK_MASTER_FILES.md) - Stock listing and master data
- [Master File Guide](MASTERFILE_GUIDE.md) - Working with stock master files

### Testing
- [Running Tests Locally](RUNNING_TESTS_LOCALLY.md) - How to run API tests locally

## Documentation Structure

### Core Documentation (this directory)
Main documentation files covering setup, API reference, and guides for using external services.

### [Implementations](implementations/README.md)
Detailed implementation documentation for major features:
- API integrations (OPENDART, Yahoo Finance, KDevelopers)
- Financial statements system
- Database schema design
- Feature-specific implementation guides

### [Reports](reports/README.md)
Test reports and analysis documents:
- Test execution reports
- API integration test results
- Financial data analysis
- Test result data files in [test-results/](reports/test-results/)

## Documentation by Topic

### For New Users
1. Start with [Project Summary](PROJECT_SUMMARY.md)
2. Follow the [Setup Guide](SETUP.md)
3. Review [API Documentation](API.md)
4. Try [Running Tests Locally](RUNNING_TESTS_LOCALLY.md)

### For Developers
1. Review [Contributing Guide](CONTRIBUTING.md)
2. Check [Implementation Guides](implementations/README.md)
3. Study [API Documentation](API.md)
4. Review coding guidelines in `.github/instructions/`

### For API Integration
1. [OPENDART API Guide](OPENDART_API.md) - Korean financial data
2. [KDevelopers API Guide](KDEVELOPERS_API.md) - Korean market trading
3. [Supabase Integration](SUPABASE_INTEGRATION.md) - Database operations

### For Testing
1. [Running Tests Locally](RUNNING_TESTS_LOCALLY.md)
2. [Test Reports](reports/README.md)
3. [Test Results Data](reports/test-results/README.md)

## External Resources

- **Main Repository**: [github.com/shin0105/custom-hts](https://github.com/shin0105/custom-hts)
- **Korean Investment Securities**: [apiportal.koreainvestment.com](https://apiportal.koreainvestment.com/)
- **OPENDART**: [opendart.fss.or.kr](https://opendart.fss.or.kr/)
- **Supabase**: [supabase.com](https://supabase.com/)

## Documentation Guidelines

When contributing documentation, please follow these guidelines:

1. **File Location**:
   - Main guides: `docs/` (this directory)
   - Implementation docs: `docs/implementations/`
   - Test reports: `docs/reports/`
   - Test results: `docs/reports/test-results/`

2. **Naming Convention**:
   - Use descriptive, clear names (e.g., `OPENDART_API.md`)
   - Include issue number for issue-specific docs (e.g., `IMPL_1_*.md`)
   - Use UPPERCASE for main doc files

3. **Content**:
   - Include clear headings and table of contents
   - Provide code examples where applicable
   - Link to related documentation
   - Keep information up-to-date with code changes

4. **References**:
   - Use relative paths for internal links
   - Verify all links work correctly
   - Update references when files are moved/renamed

## Getting Help

- Check existing documentation first
- Review [Contributing Guide](CONTRIBUTING.md)
- Open an issue on GitHub for questions
- Review [Test Reports](reports/README.md) for common issues

---

**Last Updated**: 2026-02-05  
**Documentation Structure**: Reorganized and consolidated
