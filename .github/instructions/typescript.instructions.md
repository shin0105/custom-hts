---
applyTo: "**/*.ts,**/*.tsx"
description: "TypeScript and React development guidelines for HTS frontend"
---

# TypeScript and React Development Guidelines for HTS Frontend

Apply the [general coding guidelines](../copilot-instructions.md) to all TypeScript and React code.

## TypeScript Guidelines

### Type Safety
- Use TypeScript strict mode for maximum type safety
- Define explicit types for all function parameters and return values
- Use interfaces for data structures and API response types
- Prefer type-only imports when importing types
- Avoid using `any` type - use proper type definitions instead

### Type Definitions
- Create dedicated type files in `/src/types/` directory
- Define separate interfaces for Korean and US market data
- Use union types for market-specific variations
- Define proper types for API responses and errors
- Use generic types for reusable components

### Modern TypeScript Features
- Use optional chaining (`?.`) and nullish coalescing (`??`) operators
- Leverage type guards for runtime type checking
- Use mapped types and conditional types for complex scenarios
- Implement discriminated unions for different market types
- Use const assertions where appropriate

## React Development Guidelines

### Component Architecture
- Use functional components with hooks exclusively
- Keep components small, focused, and single-responsibility
- Separate presentational and container components
- Use compound component patterns for complex UI components
- Implement proper component composition

### Performance Optimization
- Use React.memo for pure components
- Implement useMemo for expensive calculations
- Use useCallback for event handlers passed to child components
- Optimize re-renders with proper dependency arrays
- Implement virtual scrolling for large data lists

### State Management
- Use useState for local component state
- Implement useReducer for complex state logic
- Consider React Query for server state management
- Use Context API for theme and user preferences
- Avoid prop drilling with proper state placement

### Custom Hooks
- Extract reusable logic into custom hooks
- Create hooks for API data fetching
- Implement hooks for Korean and US market data
- Use hooks for form handling and validation
- Create hooks for real-time data updates

### Error Handling
- Implement Error Boundaries for component error handling
- Use proper error states in components
- Handle loading states gracefully
- Implement retry mechanisms for failed requests
- Display user-friendly error messages

## HTS-Specific Guidelines

### Market Data Handling
- Separate Korean and US market components clearly
- Handle different data formats and currencies
- Implement real-time data updates with WebSockets
- Use proper number formatting for financial data
- Handle timezone differences between markets

### UI/UX Patterns
- Implement responsive design for mobile and desktop
- Use consistent color schemes for gains/losses
- Implement data tables with sorting and filtering
- Create reusable chart components for financial data
- Use proper loading skeletons for data fetching

### Data Visualization
- Use appropriate charting libraries (Chart.js, Recharts)
- Implement interactive charts with zoom and pan
- Display candlestick charts for price data
- Create volume charts and technical indicators
- Implement real-time chart updates

### Routing and Navigation
- Use React Router for client-side routing
- Implement separate routes for Korean and US markets
- Create nested routes for detailed views
- Handle 404 errors gracefully
- Implement navigation guards for authenticated routes

## Code Organization

### File Structure
- Group components by feature/market type
- Use index files for clean imports
- Separate utility functions into dedicated files
- Create shared components in common directory
- Organize types by domain (market, user, api)

### Naming Conventions
- Use PascalCase for component names
- Use camelCase for variables and functions
- Use UPPER_CASE for constants
- Use descriptive names for props and state
- Prefix custom hooks with "use"

### Import Organization
- Group imports by type (React, third-party, local)
- Use absolute imports for common utilities
- Sort imports alphabetically within groups
- Use named imports where possible
- Avoid default exports for utilities

## Styling Guidelines

### CSS-in-JS or CSS Modules
- Use consistent styling approach throughout the app
- Create design system variables for colors and spacing
- Implement responsive breakpoints
- Use semantic class names
- Avoid inline styles except for dynamic values

### Accessibility
- Use semantic HTML elements
- Implement proper ARIA labels
- Ensure keyboard navigation support
- Provide alt text for images
- Test with screen readers

## Testing Guidelines

### Component Testing
- Write tests for all public component interfaces
- Test component behavior, not implementation details
- Use React Testing Library for component tests
- Mock external dependencies and APIs
- Test error states and edge cases

### Integration Testing
- Test component interactions and data flow
- Test routing and navigation
- Test form submissions and validations
- Test real-time data updates
- Mock API responses consistently