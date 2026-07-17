export type BgThemePreview = {
  page: string;
  sidebar: string;
  border: string;
  skeleton: string;
  skeletonAlt: string;
  text: string;
}

export type BgThemeEntry = {
  label: string;
  bg: string;
  card: string;
  body: string;
  accent: string;
  accentFg: string;
  preview: BgThemePreview;
}

export const BG_THEMES: { light: Record<string, BgThemeEntry>; dark: Record<string, BgThemeEntry> } = {
  light: {
    white: {
      label: 'White', accent: '262.1 83.3% 57.8%', accentFg: '210 20% 98%', // violet L≈58% → white fg
      bg: '0 0% 100%', card: '0 0% 100%', body: '#ffffff',
      preview: {
        page: '#ffffff', sidebar: '#f4f4f5', border: 'rgba(0,0,0,0.07)',
        skeleton: 'rgba(0,0,0,0.09)', skeletonAlt: 'rgba(0,0,0,0.05)', text: '#18181b',
      },
    },
    canvas: {
      label: 'Canvas', accent: '35 70% 21%', accentFg: '210 20% 98%', // L≈21% dark → white fg
      bg: '38 55% 97%', card: '38 35% 98.5%', body: 'radial-gradient(ellipse 110% 65% at 15% 0%, #FFDEA8 0%, #FFFDF8 60%)',
      preview: {
        page: '#fffcf4', sidebar: '#f5edd8', border: 'rgba(150,90,20,0.12)',
        skeleton: 'rgba(140,85,15,0.13)', skeletonAlt: 'rgba(140,85,15,0.07)', text: '#5c3d10',
      },
    },
    arctic: {
      label: 'Arctic', accent: '216 61% 26%', accentFg: '210 20% 98%', // L≈26% dark → white fg
      bg: '214 55% 97%', card: '214 35% 98.5%', body: 'radial-gradient(ellipse 110% 65% at 15% 0%, #C4DCFF 0%, #F6FAFF 60%)',
      preview: {
        page: '#f4f8ff', sidebar: '#e2edf9', border: 'rgba(30,80,200,0.1)',
        skeleton: 'rgba(30,80,200,0.12)', skeletonAlt: 'rgba(30,80,200,0.06)', text: '#1a3a6b',
      },
    },
    blush: {
      label: 'Blush', accent: '347 65% 29%', accentFg: '210 20% 98%', // L≈29% dark → white fg
      bg: '348 55% 97%', card: '348 35% 98.5%', body: 'radial-gradient(ellipse 110% 65% at 15% 0%, #FFCAD8 0%, #FFF6F8 60%)',
      preview: {
        page: '#fff5f7', sidebar: '#fce4ea', border: 'rgba(180,30,60,0.1)',
        skeleton: 'rgba(180,30,60,0.12)', skeletonAlt: 'rgba(180,30,60,0.06)', text: '#7c1a30',
      },
    },
  },
  dark: {
    noir: {
      label: 'Noir', accent: '263.4 70% 50.4%', accentFg: '210 20% 98%', // L≈50% → white fg (6:1 contrast)
      bg: '224 71.4% 4.1%', card: '224 71.4% 4.1%', body: 'hsl(224 71.4% 4.1%)',
      preview: {
        page: '#07090e', sidebar: '#0d1017', border: 'rgba(255,255,255,0.06)',
        skeleton: 'rgba(255,255,255,0.09)', skeletonAlt: 'rgba(255,255,255,0.05)', text: '#9580e8',
      },
    },
    mocha: {
      label: 'Mocha', accent: '36 55% 62%', accentFg: '20 14.3% 4.1%', // L≈62% light → dark fg
      bg: '28 18% 6%', card: '28 14% 8%', body: 'radial-gradient(ellipse 110% 65% at 15% 0%, #1F1108 0%, #0D0906 60%)',
      preview: {
        page: '#0d0906', sidebar: '#160f08', border: 'rgba(255,190,90,0.09)',
        skeleton: 'rgba(255,190,90,0.11)', skeletonAlt: 'rgba(255,190,90,0.06)', text: '#d4a96a',
      },
    },
    abyss: {
      label: 'Abyss', accent: '209 62% 68%', accentFg: '215 42% 5%', // L≈68% light → dark fg
      bg: '215 42% 5%', card: '215 36% 7%', body: 'radial-gradient(ellipse 110% 65% at 15% 0%, #031425 0%, #060C17 60%)',
      preview: {
        page: '#060c17', sidebar: '#0a1220', border: 'rgba(90,170,255,0.09)',
        skeleton: 'rgba(90,170,255,0.11)', skeletonAlt: 'rgba(90,170,255,0.06)', text: '#7aaee0',
      },
    },
    midnight: {
      label: 'Midnight', accent: '263 65% 75%', accentFg: '264 36% 5%', // L≈75% light → dark fg
      bg: '264 36% 5%', card: '264 28% 7%', body: 'radial-gradient(ellipse 110% 65% at 15% 0%, #150827 0%, #0B0712 60%)',
      preview: {
        page: '#0b0712', sidebar: '#130a20', border: 'rgba(160,100,255,0.09)',
        skeleton: 'rgba(160,100,255,0.12)', skeletonAlt: 'rgba(160,100,255,0.06)', text: '#b494e8',
      },
    },
  },
};

// Flat map of all theme keys → accent + accentFg (lightweight, for consumers that don't need full BgThemeEntry)
export const THEME_ACCENTS: Record<string, { accent: string; accentFg: string }> = Object.fromEntries(
  [...Object.entries(BG_THEMES.light), ...Object.entries(BG_THEMES.dark)]
    .map(([key, t]) => [key, { accent: t.accent, accentFg: t.accentFg }])
);
