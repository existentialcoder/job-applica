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
  pricing:        true,
  finalCta:       true,
} satisfies Record<string, boolean>
