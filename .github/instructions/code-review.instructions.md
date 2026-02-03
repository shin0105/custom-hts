---
applyTo: "**/*"
description: "Code review standards and GitHub review guidelines for HTS application"
---

# Code Review Standards for HTS Application

Ensure high code quality and consistency through comprehensive code review practices.

## Code Review Process

### Review Requirements
- All code changes require peer review before merging
- Financial data processing code requires senior developer review
- Security-related changes require security team review
- Database schema changes require architecture review
- Performance-critical changes require performance testing

### Review Checklist
- Code follows established coding standards and conventions
- All tests pass and coverage requirements are met
- Security best practices are implemented
- Performance implications are considered
- Documentation is updated where necessary

### Review Priorities
- **Critical**: Security vulnerabilities, data integrity issues
- **High**: Performance problems, architectural concerns
- **Medium**: Code quality, maintainability improvements
- **Low**: Style issues, minor optimizations

## Code Quality Standards

### Functionality Review
- Verify code meets requirements and user stories
- Check edge cases and error handling
- Validate financial calculations and data processing
- Ensure proper integration with external APIs
- Test different market scenarios (Korean vs US)

### Security Review
- Check for security vulnerabilities and best practices
- Verify proper input validation and sanitization
- Review authentication and authorization implementations
- Check for sensitive data exposure
- Validate external API integration security

### Performance Review
- Assess performance impact of changes
- Review database query efficiency
- Check for potential memory leaks or bottlenecks
- Validate caching strategies and implementation
- Review real-time data processing efficiency

### Maintainability Review
- Check code readability and documentation
- Review function and component complexity
- Validate naming conventions and structure
- Assess code reusability and modularity
- Review error handling and logging

## Review Guidelines

### Frontend Review Focus
- React component design and reusability
- TypeScript type safety and proper typing
- State management patterns and efficiency
- User experience and accessibility compliance
- Performance optimization and bundle size

### Backend Review Focus
- API design and RESTful principles
- Database query optimization and data integrity
- External API integration patterns
- Error handling and logging implementation
- Security and data protection measures

### Financial Domain Review
- Accuracy of financial calculations and data processing
- Proper handling of different currencies and markets
- Compliance with financial data regulations
- Real-time data processing and synchronization
- Risk management and data validation

## GitHub Review Practices

### Pull Request Standards
- Use clear, descriptive PR titles and descriptions
- Include links to related issues or user stories
- Provide context and rationale for changes
- Include screenshots for UI changes
- List breaking changes and migration steps

### Review Comments
- Provide constructive and specific feedback
- Explain the reasoning behind suggestions
- Reference documentation or standards when applicable
- Use clear action items (must-fix vs suggestion)
- Acknowledge good practices and improvements

### Review Response
- Respond to review comments promptly
- Provide explanations for disagreements
- Update code based on feedback appropriately
- Request re-review when significant changes are made
- Thank reviewers for their time and feedback

## Automated Review Tools

### Static Analysis
- Use ESLint and Prettier for TypeScript/React code formatting
- Use Black and flake8 for Python code formatting
- Implement SonarQube or similar for code quality analysis
- Use security scanning tools for vulnerability detection
- Implement dependency vulnerability scanning

### Testing Requirements
- All new features must include appropriate tests
- Test coverage must meet minimum thresholds
- Integration tests required for API changes
- Performance tests required for critical paths
- Security tests required for authentication changes

### Documentation Requirements
- Public APIs must include proper documentation
- Complex algorithms must include explanatory comments
- Configuration changes must update relevant documentation
- Breaking changes must include migration guides
- New features must include user documentation

## Review Metrics and Improvement

### Review Quality Metrics
- Track review turnaround time and responsiveness
- Monitor defect discovery rate in reviews
- Measure post-review defect rates
- Track review coverage and participation
- Analyze review feedback quality and impact

### Continuous Improvement
- Regular retrospectives on review process effectiveness
- Training sessions on review best practices
- Knowledge sharing sessions on domain-specific issues
- Process refinement based on team feedback
- Tool evaluation and improvement initiatives

### Knowledge Sharing
- Rotate reviewers to spread knowledge
- Include junior developers in review process
- Share interesting findings and learnings
- Document common review patterns and issues
- Create guidelines for domain-specific reviews

## Special Considerations

### Financial Data Reviews
- Extra attention to data accuracy and precision
- Validation of regulatory compliance requirements
- Review of audit trails and logging
- Verification of data privacy and protection
- Assessment of financial risk implications

### Market-Specific Reviews
- Korean market data format validation
- US market timezone and trading hours handling
- Currency conversion accuracy and consistency
- Market holiday and schedule handling
- Cross-market data synchronization verification

### Integration Reviews
- External API error handling and resilience
- Data transformation and validation accuracy
- Rate limiting and quota management
- Caching strategies and cache invalidation
- Real-time data processing and display