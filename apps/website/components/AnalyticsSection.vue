<template>
  <section id="analytics" class="analytics-section" aria-labelledby="analytics-heading">
    <div class="container">
      <div class="section-label"><span class="badge">Analytics</span></div>
      <h2 class="section-heading" id="analytics-heading">
        Know exactly <span class="gradient-text">where you stand</span>
      </h2>
      <p class="section-sub">The dashboard answers the questions every job seeker has but never tracks.</p>

      <div class="analytics-grid" role="list" aria-label="Example analytics statistics">
        <div class="stat-card" role="listitem">
          <div class="stat-num" style="color:#818cf8">42</div>
          <div class="stat-label">Applied</div>
        </div>
        <div class="stat-card" role="listitem">
          <div class="stat-num" style="color:#a78bfa">12</div>
          <div class="stat-label">Interviews</div>
        </div>
        <div class="stat-card" role="listitem">
          <div class="stat-num" style="color:#f59e0b">8</div>
          <div class="stat-label">Ghosted</div>
        </div>
        <div class="stat-card" role="listitem">
          <div class="stat-num" style="color:#ef4444">15</div>
          <div class="stat-label">Rejected</div>
        </div>
      </div>

      <div class="funnel-preview" aria-label="Application funnel example">
        <div style="font-size:13px;font-weight:600;color:var(--muted);text-align:center;margin-bottom:20px;text-transform:uppercase;letter-spacing:.05em;">Application Funnel</div>
        <div class="funnel-row">
          <span class="funnel-label">Applied</span>
          <div class="funnel-bar-bg"><div class="funnel-bar" style="width:100%;background:#6366f1" /></div>
          <span class="funnel-count">42</span>
        </div>
        <div class="funnel-row">
          <span class="funnel-label">Phone Screen</span>
          <div class="funnel-bar-bg"><div class="funnel-bar" style="width:40%;background:#f59e0b" /></div>
          <span class="funnel-count">17</span>
        </div>
        <div class="funnel-row">
          <span class="funnel-label">Interview</span>
          <div class="funnel-bar-bg"><div class="funnel-bar" style="width:21%;background:#f97316" /></div>
          <span class="funnel-count">9</span>
        </div>
        <div class="funnel-row">
          <span class="funnel-label">Technical</span>
          <div class="funnel-bar-bg"><div class="funnel-bar" style="width:12%;background:#a855f7" /></div>
          <span class="funnel-count">5</span>
        </div>
        <div class="funnel-row">
          <span class="funnel-label">Offer</span>
          <div class="funnel-bar-bg"><div class="funnel-bar" style="width:5%;background:#10b981" /></div>
          <span class="funnel-count">2</span>
        </div>
      </div>

      <p style="text-align:center;font-size:13px;color:var(--muted);margin-top:28px">
        Example data. Your real dashboard updates live as you track applications.
      </p>
    </div>
  </section>
</template>
