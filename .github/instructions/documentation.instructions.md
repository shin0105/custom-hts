---
applyTo: "**/*.md,**/*.rst,**/*.txt"
description: "Documentation requirements and standards for HTS application"
---

# Documentation Standards for HTS Application

Maintain comprehensive, clear, and up-to-date documentation for all aspects of the HTS application.

## Documentation Types

### API Documentation
- Document all REST API endpoints with OpenAPI/Swagger
- Include request/response examples for each endpoint
- Document authentication requirements and rate limits
- Provide error codes and troubleshooting information
- Include examples for both Korean and US market data

### Code Documentation
- Write docstrings for all Python functions and classes
- Document React component props and usage patterns
- Include JSDoc comments for TypeScript functions
- Document complex business logic and algorithms
- Explain financial calculations and data transformations

### User Documentation
- Create user guides for HTS interface navigation
- Document market-specific features and differences
- Provide troubleshooting guides for common issues
- Include screenshots and visual guides
- Document data interpretation and analysis features

### Developer Documentation
- Maintain setup and installation instructions
- Document development environment configuration
- Provide debugging guides and common issues
- Document deployment procedures and environments
- Include architecture decisions and design rationale

## Documentation Format Standards

### Markdown Guidelines
- Use consistent heading hierarchy (h1 for main titles)
- Include table of contents for long documents
- Use code blocks with proper language syntax highlighting
- Include links to related documentation sections
- Use bullet points and numbered lists for clarity

### Code Comments
- Write clear, concise comments explaining "why" not "what"
- Use consistent comment formatting and style
- Document complex financial calculations step-by-step
- Include links to external API documentation
- Document assumptions and limitations

### API Documentation Format
- Use OpenAPI 3.0 specification format
- Include comprehensive parameter descriptions
- Provide realistic example requests and responses
- Document all possible error responses
- Include authentication and authorization details

## Content Guidelines

### Clarity and Accessibility
- Write in clear, simple language
- Avoid jargon and explain technical terms
- Use active voice and present tense
- Include examples and use cases
- Structure information logically

### Accuracy and Completeness
- Keep documentation synchronized with code changes
- Review and update documentation during code reviews
- Include version information and change logs
- Document known limitations and workarounds
- Provide contact information for questions

### Financial Domain Specificity
- Explain Korean and US market differences
- Document currency handling and conversions
- Explain financial terminology and calculations
- Include market hours and trading calendars
- Document regulatory compliance requirements

## Documentation Organization

### File Structure
- Organize documentation by feature and audience
- Use consistent naming conventions
- Create index files for navigation
- Separate user and developer documentation
- Maintain separate docs for Korean and US markets

### Cross-References
- Link related documentation sections
- Reference external API documentation
- Include links to code repositories
- Cross-reference between user and developer docs
- Maintain consistent link formatting

## Maintenance Guidelines

### Regular Reviews
- Review documentation during code reviews
- Update documentation for feature changes
- Validate links and references regularly
- Check for outdated information monthly
- Update screenshots and examples as needed

### Version Control
- Commit documentation changes with related code
- Tag documentation versions with releases
- Maintain change logs for major documentation updates
- Archive old versions for reference
- Track documentation coverage metrics

## Documentation Tools and Standards

### Required Documentation
- README files for all major components
- API reference documentation
- Installation and setup guides
- Troubleshooting and FAQ sections
- Architecture and design documentation

### Tool Usage
- Use appropriate tools for different documentation types
- Generate API docs automatically from code annotations
- Use diagrams and flowcharts for complex processes
- Include interactive examples where possible
- Maintain documentation in version control

### Quality Standards
- Proofread all documentation for grammar and spelling
- Validate technical accuracy of all examples
- Test all installation and setup procedures
- Verify all links and references work correctly
- Ensure documentation is accessible and inclusive