<script setup lang="ts">
const t = useT()
const h = t.hero
const k = h.kanbanPreview
</script>

<template>
  <header class="hero" role="banner">
    <div class="container">
      <div class="hero-inner">
        <div class="hero-content">
          <div class="hero-label">
            <span class="hero-label-dot" aria-hidden="true"></span>
            {{ h.badge }}
          </div>

          <h1>
            {{ h.headlineParts.line1 }}<br>
            {{ h.headlineParts.line2 }} <em>{{ h.headlineParts.emphasis }}</em><br>
            {{ h.headlineParts.line3 }}
          </h1>

          <p class="hero-sub">{{ h.subtext }}</p>

          <div class="hero-ctas">
            <a
              href="https://app.jobapplica.io/signup"
              class="btn btn-primary btn-lg"
              aria-label="Create a free JobApplica account"
            >
              {{ h.ctaPrimary }}
            </a>
            <a
              href="#how-it-works"
              class="btn btn-ghost btn-lg"
              aria-label="See how JobApplica works"
            >
              {{ h.ctaSecondary }}
            </a>
          </div>

          <p class="hero-note">{{ h.note }}</p>
        </div>

        <!-- Mini kanban preview -->
        <div class="hero-visual" aria-hidden="true">
          <div class="kanban-preview">
            <div class="kanban-header">
              <span class="kanban-title">{{ k.boardName }}</span>
              <span class="kanban-count">{{ k.boardCount }}</span>
            </div>
            <div class="kanban-cols">
              <div class="kanban-col">
                <div class="kanban-col-label">{{ k.columns.saved }}</div>
                <div class="kanban-card">
                  <div class="kanban-card-title">{{ k.cards.role1.title }}</div>
                  <div class="kanban-card-sub">{{ k.cards.role1.sub }}</div>
                  <span class="kanban-card-tag">{{ k.cards.role1.tag }}</span>
                </div>
                <div class="kanban-card">
                  <div class="kanban-card-title">{{ k.cards.role2.title }}</div>
                  <div class="kanban-card-sub">{{ k.cards.role2.sub }}</div>
                  <span class="kanban-card-tag">{{ k.cards.role2.tag }}</span>
                </div>
              </div>
              <div class="kanban-col">
                <div class="kanban-col-label">{{ k.columns.applied }}</div>
                <div class="kanban-card">
                  <div class="kanban-card-title">{{ k.cards.role3.title }}</div>
                  <div class="kanban-card-sub">{{ k.cards.role3.sub }}</div>
                  <span class="kanban-card-tag amber">{{ k.cards.role3.tag }}</span>
                </div>
                <div class="kanban-card">
                  <div class="kanban-card-title">{{ k.cards.role4.title }}</div>
                  <div class="kanban-card-sub">{{ k.cards.role4.sub }}</div>
                  <span class="kanban-card-tag amber">{{ k.cards.role4.tag }}</span>
                </div>
              </div>
              <div class="kanban-col">
                <div class="kanban-col-label">{{ k.columns.interview }}</div>
                <div class="kanban-card">
                  <div class="kanban-card-title">{{ k.cards.role5.title }}</div>
                  <div class="kanban-card-sub">{{ k.cards.role5.sub }}</div>
                  <span class="kanban-card-tag green">{{ k.cards.role5.tag }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>
