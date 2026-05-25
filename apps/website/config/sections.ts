/**
 * Toggle each website section on or off.
 * Set a value to false to hide that section from the page.
 * Hero, Nav, and Footer are always shown.
 */
export const sections = {
  platformsStrip: true,
  problem:        true,
  howItWorks:     true,
  features:       true,
  analytics:      true,
  extension:      true,
  pricing:        false,
  finalCta:       true,
} satisfies Record<string, boolean>

/**
 * Toggle individual feature cards in the Features section.
 * Keys match the `label` field of each item in locales/en.json (lowercased).
 */
export const featureCards = {
  ai:     false,   // Job Discovery
  import: false,   // Smart Import
  ats:    true,   // Score Match
  cv:     true,  // AI Applications
  board:  true,  // Visual Pipeline
  email:  false,  // Email Intelligence
} satisfies Record<string, boolean>
