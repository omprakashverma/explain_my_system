# CodeAtlas Light Theme Design System
## Professional AI Developer Platform Redesign

---

## 1. Design Philosophy

CodeAtlas is an AI-powered collaborative intelligence platform for developers. The light theme should embody:

- **Clarity**: Clean information hierarchy with generous whitespace
- **Precision**: Technical accuracy reflected in UI refinement
- **Collaboration**: Warm but professional aesthetic
- **Performance**: Visual feedback without clutter
- **Accessibility**: High contrast, readable typography

This design should feel like tools developers trust: Linear, GitHub, Vercel, Stripe Dashboard, Notion.

---

## 2. Color System

### Primary Palette

```css
/* Neutral Foundation */
--color-bg-primary: #F8FAFC;           /* Primary background */
--color-bg-secondary: #FFFFFF;         /* Card/surface background */
--color-bg-tertiary: #F3F4F6;          /* Hover states, disabled */

/* Text */
--color-text-primary: #111827;         /* Main text - #1F2937 acceptable */
--color-text-secondary: #6B7280;       /* Supporting text */
--color-text-tertiary: #9CA3AF;        /* Placeholder, helper text */
--color-text-inverse: #FFFFFF;         /* On dark backgrounds */

/* Borders & Dividers */
--color-border-primary: #E5E7EB;       /* Default borders */
--color-border-secondary: #D1D5DB;     /* Stronger borders */
--color-border-focus: #BFDBFE;         /* Focus states */

/* Accent Colors */
--color-accent-primary: #3B82F6;       /* Primary action - Blue */
--color-accent-secondary: #10B981;     /* Secondary action - Green */
--color-accent-tertiary: #F59E0B;      /* Warning/tertiary - Amber */
```

### Semantic Colors

```css
/* Status & Semantic */
--color-success: #16A34A;              /* Success states */
--color-warning: #D97706;              /* Warnings */
--color-error: #DC2626;                /* Errors */
--color-info: #0EA5E9;                 /* Information */

/* Light variants for backgrounds */
--color-success-light: #DCFCE7;        /* Light green background */
--color-warning-light: #FEF3C7;        /* Light amber background */
--color-error-light: #FEE2E2;          /* Light red background */
--color-info-light: #CFFAFE;           /* Light cyan background */

/* Hover & Interactive */
--color-hover-primary: #3B82F6;        /* Hover state for primary */
--color-hover-secondary: #F3F4F6;      /* Generic hover background */
--color-active: #1F2937;               /* Active/selected state */

/* Shadows */
--shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
```

---

## 3. Typography System

### Font Stack
```css
/* Primary font family */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
  'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
  sans-serif;

/* Monospace for code */
font-family: 'JetBrains Mono', 'SFMono-Regular', 'Monaco', 'Cascadia Code',
  'Inconsolata', monospace;
```

### Type Scale

| Role | Size | Weight | Line Height | Letter Spacing | Usage |
|------|------|--------|-------------|----------------|-------|
| **Display/Hero** | 3.5rem (56px) | 700 | 1.2 | -0.02em | Page titles |
| **H1** | 2.25rem (36px) | 700 | 1.2 | -0.02em | Major sections |
| **H2** | 1.875rem (30px) | 600 | 1.3 | -0.015em | Section headers |
| **H3** | 1.5rem (24px) | 600 | 1.4 | -0.01em | Subsection headers |
| **H4** | 1.125rem (18px) | 600 | 1.4 | 0 | Small headers |
| **Body Large** | 1rem (16px) | 400 | 1.6 | 0 | Main text |
| **Body Base** | 0.95rem (15px) | 400 | 1.6 | 0 | Default text |
| **Body Small** | 0.875rem (14px) | 400 | 1.5 | 0 | Supporting text |
| **Label** | 0.75rem (12px) | 600 | 1.4 | 0.05em | Labels, badges |
| **Code** | 0.875rem (14px) | 400 | 1.6 | 0 | Code blocks |

### Text Hierarchy Best Practices

1. **Headings**: Bold weight (600–700), tighter line height (1.2–1.3)
2. **Body**: Regular weight (400), relaxed line height (1.6)
3. **Supporting**: Secondary color with slight size reduction
4. **Labels**: Uppercase, bold, letter-spacing for distinction
5. **Reduce cognitive load**: Max 3 text colors per section

---

## 4. Spacing System

```css
/* 8px base unit */
--spacing-0: 0;
--spacing-1: 0.25rem;   /* 4px */
--spacing-2: 0.5rem;    /* 8px */
--spacing-3: 0.75rem;   /* 12px */
--spacing-4: 1rem;      /* 16px */
--spacing-5: 1.25rem;   /* 20px */
--spacing-6: 1.5rem;    /* 24px */
--spacing-8: 2rem;      /* 32px */
--spacing-10: 2.5rem;   /* 40px */
--spacing-12: 3rem;     /* 48px */
--spacing-16: 4rem;     /* 64px */
```

### Component Padding Guidelines

- **Buttons**: 12px vertical, 16px horizontal (minimum 40px tall)
- **Input fields**: 12px vertical, 14px horizontal (40px height)
- **Cards**: 24px padding (20px on mobile)
- **Sections**: 32px vertical spacing
- **Sections gap**: 16–24px between panels
- **Text fields**: 14px padding

---

## 5. Corner Radius System

```css
--radius-sm: 6px;       /* Subtle, inputs */
--radius-md: 8px;       /* Buttons, small cards */
--radius-lg: 12px;      /* Cards, panels */
--radius-xl: 16px;      /* Large containers */
--radius-2xl: 20px;     /* Extra large elements */
--radius-full: 999px;   /* Pills, badges */
```

---

## 6. Component Design Specifications

### Header / Navigation
- **Background**: `#FFFFFF` with subtle bottom border (`#E5E7EB`)
- **Height**: 64px
- **Padding**: 16px 24px
- **Logo**: 24px height, dark text
- **Navigation items**: 14px, secondary text, hover state changes to primary text
- **User menu**: Minimal, clean avatar + dropdown
- **Shadow**: `--shadow-sm` (subtle drop shadow)

**Best Practices:**
- Keep navigation items to 4–5 max
- Use icon + label for clarity
- Generous touch targets (44px minimum)

### Cards / Panels
- **Background**: `#FFFFFF`
- **Border**: 1px solid `#E5E7EB`
- **Border radius**: 12–16px
- **Padding**: 24px
- **Shadow**: `--shadow-sm` to `--shadow-md`
- **Hover**: Subtle shadow increase to `--shadow-lg`, no color change

**Variants:**
- **Elevated**: `--shadow-md` + subtle border
- **Flat**: No shadow, border only
- **Interactive**: Hover shadow + `#F3F4F6` background
- **Focused**: Border color changes to `#3B82F6`

### Buttons

#### Primary Button
```css
Background: #3B82F6
Text: #FFFFFF
Padding: 12px 16px
Border radius: 8px
Font weight: 600
Border: none
Hover: background #2563EB, shadow --shadow-md, translateY(-1px)
Active: background #1D4ED8
Focus: outline 2px offset 2px color #3B82F6
Disabled: opacity 50%, cursor not-allowed
```

#### Secondary Button
```css
Background: #F3F4F6
Text: #111827
Border: 1px solid #E5E7EB
Hover: background #E5E7EB, border #D1D5DB
```

#### Ghost Button
```css
Background: transparent
Text: #3B82F6
Border: 1px solid #E5E7EB
Hover: background #F3F4F6, border #D1D5DB, text #2563EB
```

#### Danger Button
```css
Background: #DC2626
Text: #FFFFFF
Hover: background #B91C1C
```

**Button Guidelines:**
- Minimum 40px height for clickability
- Consistent 16px horizontal padding
- Max 2 primary buttons per section
- Use secondary for less important actions
- Avoid 4+ buttons in a row (stack or collapse)

### Input Fields & Textareas
```css
Background: #FFFFFF
Border: 1px solid #E5E7EB
Border radius: 8px
Padding: 12px 14px
Font: 15px / 1.6
Color: #111827
Placeholder: #9CA3AF
Focus: 
  - Border color: #3B82F6
  - Shadow: 0 0 0 3px rgba(59, 130, 246, 0.1)
  - No transform
```

**Best Practices:**
- Labels above inputs (not floating)
- Helper text below input (12px, secondary color)
- Error state: border + text color `#DC2626`, background `#FEE2E2`
- Success state: border + accent `#16A34A`, light background `#DCFCE7`

### Badges / Pills / Chips

#### Default Badge
```css
Background: #F3F4F6
Text: #111827
Border: 1px solid #E5E7EB
Border radius: 999px (pill)
Padding: 6px 12px
Font: 12px / 600
```

#### Status Badge (Success)
```css
Background: #DCFCE7
Text: #166534
Border: 1px solid #86EFAC
```

#### Status Badge (Warning)
```css
Background: #FEF3C7
Text: #92400E
Border: 1px solid #FCD34D
```

#### Status Badge (Error)
```css
Background: #FEE2E2
Text: #991B1B
Border: 1px solid #FECACA
```

### Alerts / Messages / Banners

#### Success Alert
```css
Background: #DCFCE7
Border: 1px solid #86EFAC
Border radius: 12px
Padding: 16px
Text: #166534
Icon: #16A34A
```

#### Warning Alert
```css
Background: #FEF3C7
Border: 1px solid #FCD34D
Text: #92400E
Icon: #D97706
```

#### Error Alert
```css
Background: #FEE2E2
Border: 1px solid #FECACA
Text: #991B1B
Icon: #DC2626
```

**Alert Guidelines:**
- Include icon (16px) + title (600 weight) + message
- Dismissible variant with X button
- Border radius: 12px
- Padding: 16px 20px
- Max width: 100% (responsive)

### File Explorer / Sidebar

**Structure:**
- Background: `#FFFFFF`
- Border: 1px right `#E5E7EB`
- Item height: 40px
- Item padding: 12px 16px
- Font: 14px / 400
- Text color: `#6B7280`

**States:**
- **Hover**: background `#F9FAFB`, text `#374151`
- **Active**: background `#EFF6FF`, left border 3px `#3B82F6`, text `#111827`
- **Icon**: 16px, margin-right 12px

### Code / Preview Blocks

```css
Background: #F9FAFB
Border: 1px solid #E5E7EB
Border radius: 12px
Padding: 16px
Font family: 'JetBrains Mono', monospace
Font size: 13px
Line height: 1.6
Color: #111827
Tab size: 2
Overflow: auto (with minimal scrollbar styling)
```

**Code Block Styling:**
- Syntax highlighting: muted colors (avoid neon)
- Line numbers: optional, secondary color `#9CA3AF`
- Highlight line: subtle `#F3F4F6` background

### Discussion / Messages Thread

**Message Container:**
- Background: `#F9FAFB` for user, `#FFFFFF` for system
- Border: 1px solid `#E5E7EB`
- Border radius: 12px
- Padding: 16px
- Margin bottom: 12px

**Message Structure:**
1. **Author**: 14px, 600 weight, primary text
2. **Timestamp**: 12px, secondary text
3. **Content**: 14px, primary text, line-height 1.6
4. **Avatar**: 32px, border-radius 8px

**Accepted Answer:**
- Left border: 3px `#16A34A`
- Background: `#DCFCE7` tinted
- Badge: "Accepted" in top-right, success badge styling

### Modals / Dialogs

```css
Background: #FFFFFF
Border: 1px solid #E5E7EB
Border radius: 16px
Shadow: --shadow-xl
Padding: 24px (or 32px for larger)
Overlay: rgba(0, 0, 0, 0.5)
Max width: 500px (default)
```

**Structure:**
- Close button: top-right, ghost style, 24px icon
- Title: H3, margin-bottom 8px
- Content: body text with 1.6 line-height
- Actions: footer with buttons (cancel left, confirm right)

---

## 7. Layout & Spacing Best Practices

### Dashboard Layout
```
┌─ HEADER ─────────────────────────────────────┐
│ CodeAtlas Logo | Nav Items | User Menu       │
├─────────────────────────────────────────────┤
│                                              │
│  ┌─ HERO ─────────────────────────┐         │
│  │ Welcome, [User]                │         │
│  │ Quick stats / Actions           │         │
│  └────────────────────────────────┘         │
│                                              │
│  ┌─ MAIN GRID ────────────────────┐         │
│  │ [Sidebar] | [Content] | [Side] │         │
│  │           |           | Panel  │         │
│  │                       |        │         │
│  └────────────────────────────────┘         │
│                                              │
└─────────────────────────────────────────────┘
```

### Spacing Rules
- **Between sections**: 32px
- **Between cards**: 24px
- **Between card rows**: 16px
- **Inside cards**: 24px padding
- **Between form fields**: 16px
- **Text line-height**: 1.6 for body, 1.2 for headings

### Responsive Breakpoints
```css
Mobile:    max-width 640px
Tablet:    641px to 1024px
Desktop:   1025px to 1440px
Wide:      1441px+
```

---

## 8. Visual Hierarchy Best Practices

### Example: Card with Content
```
┌─────────────────────────────────────────┐
│  📁 File Structure               [⋮]    │  ← H4 title, icon (20px), actions
│  src/components/common                │  ← Secondary text
├─────────────────────────────────────────┤
│  ├── Button.jsx              (+2 more) │  ← Body text with subtle details
│  ├── Header.jsx                        │
│  ├── Modal.jsx                         │
│                                        │
│  Updated 2 hours ago by @sarah        │  ← Helper text, tertiary
└─────────────────────────────────────────┘
```

### Color Usage
1. **Primary action**: `#3B82F6` (limited use)
2. **Text**: `#111827` for main, `#6B7280` for secondary
3. **Borders**: Always `#E5E7EB` unless semantically colored
4. **Backgrounds**: White or `#F3F4F6`, never multiple accent colors
5. **Status**: Only use semantic colors (success/warning/error) for actual status

---

## 9. Dark Mode Considerations (Optional Future)

If dark mode is needed, mirror these values:

```css
/* Dark Mode Palette */
--color-bg-primary-dark: #0F172A;
--color-bg-secondary-dark: #1E293B;
--color-text-primary-dark: #F1F5F9;
--color-text-secondary-dark: #CBD5E1;
--color-border-primary-dark: #334155;
--color-accent-primary-dark: #3B82F6;
```

---

## 10. Accessibility Standards

- **Color Contrast**: Minimum 4.5:1 for text (WCAG AA)
- **Focus states**: Always visible, at least 2px outline
- **Touch targets**: Minimum 44px × 44px
- **Motion**: Respect `prefers-reduced-motion`
- **Typography**: Sufficient line-height and letter-spacing
- **Icons**: Always paired with text labels
- **Form labels**: Always associated with inputs
- **Error messages**: Linked to form fields, clear language

---

## 11. Transition & Animation Guidelines

### Timing
```css
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
```

### Common Transitions
- **Hover state**: `--transition-fast`
- **Color change**: `--transition-base`
- **Modal open/close**: `--transition-slow`
- **Respect prefers-reduced-motion**: No animations if enabled

---

## 12. Component-Specific Guidelines

### Authentication Page
- **Background**: Gradient from `#F8FAFC` to `#FFFFFF`
- **Card**: Centered, max 900px width, `--shadow-lg`
- **Hero copy**: Left side (60%), form panel right (40%)
- **Typography**: Large, friendly, trust-building language
- **CTA buttons**: Primary button, full width on mobile

### Dashboard Header
- **Logo**: 28px height, dark navy color
- **Product name**: "CodeAtlas" in bold, 600 weight, 18px
- **Navigation**: Horizontal list, 14px links
- **User avatar**: 36px circle with initials
- **Dropdown menu**: Ghost button style

### File Explorer / Sidebar
- **Background**: `#FFFFFF` with subtle right border
- **Active state**: Left accent bar (3px `#3B82F6`) + light background
- **Nesting**: 12px indent per level
- **Icons**: 16px, monochrome

### Code Preview Panel
- **Background**: `#F9FAFB`
- **Line numbers**: Optional, `#9CA3AF`, right-aligned
- **Scrollbar**: Subtle, `#D1D5DB` on hover
- **Selection**: `#BFD FF E` background

### Q&A / Discussion Thread
- **User message**: Align left, white background
- **AI response**: Align right, light gray background
- **Accepted answer**: Green accent bar, success badge
- **Reply count**: Clickable, shows thread count

### Loading States
- **Skeleton**: `#E5E7EB` background with `#F3F4F6` shimmer
- **Spinner**: Rotating accent color (`#3B82F6`), 24px
- **Progress**: Gradient bar, smooth easing

---

## 13. Migration Checklist

### Phase 1: Foundation
- [ ] Update CSS variables for light theme
- [ ] Replace dark background gradients with light
- [ ] Update text colors to meet contrast ratios
- [ ] Adjust border colors to `#E5E7EB`
- [ ] Update shadows to be subtle

### Phase 2: Components
- [ ] Redesign header/navigation
- [ ] Update button styles (primary, secondary, ghost, danger)
- [ ] Refresh card/panel styling
- [ ] Update input fields and form elements
- [ ] Redesign badges/chips/status indicators

### Phase 3: Sections
- [ ] Update authentication page
- [ ] Redesign dashboard layout
- [ ] Refresh file explorer sidebar
- [ ] Update code preview styling
- [ ] Redesign Q&A / message threads

### Phase 4: Polish
- [ ] Hover states and transitions
- [ ] Focus states for accessibility
- [ ] Responsive adjustments
- [ ] Dark mode detection (optional)
- [ ] Performance optimization

---

## 14. Design Tokens Summary Table

| Token | Value | Usage |
|-------|-------|-------|
| `--color-bg-primary` | `#F8FAFC` | Page background |
| `--color-bg-secondary` | `#FFFFFF` | Cards, surfaces |
| `--color-text-primary` | `#111827` | Main text |
| `--color-text-secondary` | `#6B7280` | Supporting text |
| `--color-border-primary` | `#E5E7EB` | Default borders |
| `--color-accent-primary` | `#3B82F6` | Primary CTA |
| `--color-success` | `#16A34A` | Success states |
| `--color-warning` | `#D97706` | Warnings |
| `--color-error` | `#DC2626` | Errors |
| `--radius-md` | `8px` | Buttons, inputs |
| `--radius-lg` | `12px` | Cards |
| `--shadow-sm` | `0 1px 3px rgba(0,0,0,0.1)` | Cards |
| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Hover states |
| `--spacing-4` | `16px` | Standard gap |
| `--spacing-6` | `24px` | Card padding |

---

## 15. References & Inspiration

- **Linear**: Minimal, elegant, developer-focused
- **GitHub**: Clean, accessible, familiar to devs
- **Vercel**: Modern, light, premium feel
- **Stripe Dashboard**: Professional, readable, spacious
- **Notion**: Friendly, flexible, content-first

---

## 16. Tools & Implementation

### Tailwind CSS (Recommended)
If migrating to Tailwind, use this config:

```js
export default {
  theme: {
    extend: {
      colors: {
        'bg-primary': '#F8FAFC',
        'bg-secondary': '#FFFFFF',
        'text-primary': '#111827',
        'text-secondary': '#6B7280',
        'border-primary': '#E5E7EB',
        'accent-primary': '#3B82F6',
        'success': '#16A34A',
        'warning': '#D97706',
        'error': '#DC2626',
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '16px',
        lg: '24px',
        xl: '32px',
      },
      borderRadius: {
        sm: '6px',
        md: '8px',
        lg: '12px',
        xl: '16px',
      },
      boxShadow: {
        xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
      },
    },
  },
}
```

---

## Final Notes

This design system is meant to be **living and flexible**. Adjust spacing, colors, and typography based on user feedback and accessibility testing. The key is consistency and clarity—every design decision should serve the user's goal of understanding and exploring code.

**The UI should feel like a premium AI developer tool, not a generic admin panel.**
