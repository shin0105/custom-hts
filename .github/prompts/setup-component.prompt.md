---
agent: 'component-generator'
model: GPT-5.1-Codex-Max (copilot)
tools: ['semantic_search', 'file_search', 'read_file']
description: 'Generate new React components for HTS trading interface'
---

# HTS Component Generator

Your goal is to generate a new React component for the HTS trading interface based on the project's established patterns and requirements.

## Component Requirements

Ask for the following information if not provided:
- **Component name**: What should this component be called?
- **Market type**: Is this for Korean market, US market, or shared?
- **Component purpose**: What functionality should this component provide?
- **Data requirements**: What data does this component need to display or handle?

## Component Template

Create components following these patterns:

### Functional Component Structure
- Use TypeScript with proper interface definitions
- Implement functional components with hooks
- Include proper error boundaries and loading states
- Use React.memo for performance optimization where appropriate

### Props Interface
- Define clear TypeScript interfaces for component props
- Include optional props with default values
- Document prop purposes and expected data formats
- Use generic types for reusable components

### Styling Approach
- Follow the established styling system (CSS modules or styled-components)
- Use consistent spacing and color variables
- Implement responsive design principles
- Include proper hover and focus states

### Financial Data Handling
- Format currency values according to market (KRW vs USD)
- Display percentage changes with appropriate color coding (green/red)
- Handle large numbers with proper formatting and abbreviations
- Include proper loading skeletons for async data

## Market-Specific Requirements

### Korean Market Components
- Handle Korean Won (KRW) currency formatting
- Support Korean company names and symbols
- Integrate with Korean Investment Securities API data
- Handle Korean market hours and holidays

### US Market Components
- Handle USD currency formatting with cents
- Support US ticker symbols and company names
- Integrate with Yahoo Finance data structures
- Handle US market hours and timezones

### Shared Components
- Support both market types with configuration props
- Use generic interfaces that work for both markets
- Include market type indicators in the UI
- Handle currency conversion if needed

## Required Features

### Data Display Components
- Include proper loading and error states
- Implement data refresh capabilities
- Use consistent number formatting
- Include tooltips for complex financial terms

### Interactive Components
- Include proper form validation for financial inputs
- Implement keyboard navigation support
- Add accessibility labels and ARIA attributes
- Include confirmation dialogs for important actions

### Chart Components
- Use established charting library (Chart.js/Recharts)
- Include interactive features (zoom, pan, hover)
- Support real-time data updates
- Handle different chart types (line, candlestick, volume)

## Testing Requirements

Generate corresponding test files:
- Unit tests for component rendering
- Tests for user interactions and event handling
- Tests for different data states (loading, error, success)
- Tests for accessibility and keyboard navigation
- Mock external dependencies and API calls

## File Generation

Create the following files:
1. **Component file**: `src/components/[Market]/[ComponentName].tsx`
2. **Types file**: `src/types/[ComponentName].types.ts` (if complex)
3. **Test file**: `src/components/[Market]/[ComponentName].test.tsx`
4. **Styles file**: `src/components/[Market]/[ComponentName].module.css` (if using CSS modules)

## Example Component Structure

```typescript
// Component Props Interface
interface ComponentProps {
  // Define props here
}

// Main Component
export const ComponentName: React.FC<ComponentProps> = React.memo(({ 
  // props 
}) => {
  // Hooks and state management
  
  // Event handlers
  
  // Render logic
  return (
    <div className={styles.container}>
      {/* Component JSX */}
    </div>
  );
});

ComponentName.displayName = 'ComponentName';
```

## Documentation Requirements

Include JSDoc comments with:
- Component purpose and usage examples
- Prop descriptions and expected values
- Performance considerations
- Accessibility features
- Integration requirements with external APIs

Follow the [TypeScript development guidelines](./.github/instructions/typescript.instructions.md) and [testing standards](./.github/instructions/testing.instructions.md) for all generated code.