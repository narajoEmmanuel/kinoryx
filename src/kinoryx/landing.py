"""Minimal entry page for the two KINORYX research workspaces.

The landing screen intentionally contains no datasets, charts, or scientific
controls. Existing Dashboard and Laboratory each retain their own route.
"""

HOME_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>KINORYX | Home</title>
  <style>
    :root { color-scheme: light; --ink: #18272D; --rule: #CAD2D4; --blue: #235D86; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; background: #FCFCFB; color: var(--ink);
           font-family: Arial, Helvetica, sans-serif; }
    .shell { min-height: 100vh; max-width: 1500px; margin: 0 auto;
             padding: 30px clamp(20px, 5vw, 76px); }
    .site-header { display:flex; align-items:center; justify-content:space-between;
                   gap:24px; border-bottom:1px solid var(--rule); padding-bottom:19px; }
    .brand { display:flex; gap:14px; align-items:center; color:var(--ink);
             text-decoration:none; font-size:1.4rem; font-weight:800;
             letter-spacing:0.22em; }
    .brand-symbol { display:inline-flex; justify-content:center; align-items:center;
                    border:2px solid var(--ink); width:34px; height:34px;
                    border-radius:50%; font-size:20px; font-weight:400; letter-spacing:0; }
    .site-menu { position:relative; }
    .site-menu summary { width:43px; height:43px; display:grid; place-items:center;
                         font-size:25px; cursor:pointer; list-style:none;
                         border:1px solid transparent; }
    .site-menu summary:hover,.site-menu summary:focus-visible { border-color:var(--rule); }
    .site-menu summary::-webkit-details-marker { display:none; }
    .site-menu nav { position:absolute; z-index:4; right:0; top:49px;
                     width:210px; border:1px solid var(--rule); background:#fff;
                     box-shadow:0 15px 40px rgba(0,0,0,.08); }
    .site-menu a { display:block; text-decoration:none; color:var(--ink);
                   padding:15px 18px; }
    .site-menu a:hover { background:#F4F6F7; }
    .intro { text-align:center; max-width:760px; margin:clamp(65px,13vh,150px) auto 0; }
    .eyebrow { font-size:.78rem; color:#586971; letter-spacing:.22em;
               font-weight:700; text-transform:uppercase; }
    h1 { margin:16px 0 12px; font-size:clamp(1.5rem, 3vw, 2.5rem);
         line-height:1.23; letter-spacing:-.04em; }
    .lead { color:#657179; max-width:500px; margin:0 auto 35px;
            font-size:1rem; line-height:1.65; }
    .entry-links { display:flex; align-items:stretch; flex-direction:column;
                   gap:17px; max-width:370px; margin:0 auto; }
    .entry-link { text-decoration:none; padding:22px 28px; background:#fff;
                  border:1px solid #1D303A; color:var(--ink); font-size:1.2rem;
                  font-weight:600; letter-spacing:.02em; transition:background .15s; }
    .entry-link:hover,.entry-link:focus-visible { background:#EDF3F6; outline-offset:3px; }
    .entry-desc { display:block; font-size:.76rem; font-weight:400;
                  letter-spacing:0; margin-top:8px; color:#69777C; }
    .foot { padding:50px 0 15px; text-align:center; color:#879196; font-size:.76rem; }
    @media (max-width: 560px) {
      .shell { padding:20px; } .brand { font-size:1.03rem; letter-spacing:.13em; }
      .intro { margin-top:68px; } .entry-link { padding:21px 16px; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header class="site-header">
      <a href="/" class="brand" aria-label="KINORYX home"><span class="brand-symbol" aria-hidden="true">✣</span>KINORYX</a>
      <details class="site-menu">
        <summary aria-label="Open navigation menu">☰</summary>
        <nav aria-label="Primary navigation">
          <a href="/">Home</a>
          <a href="/lab/">Laboratory</a>
          <a href="/dashboard/">Dashboard</a>
        </nav>
      </details>
    </header>
    <main class="intro">
      <div class="eyebrow">Human Movement Research</div>
      <h1>Choose your workspace</h1>
      <p class="lead">Explore raw recordings in the laboratory or continue to the existing biomechanics dashboard.</p>
      <div class="entry-links">
        <a class="entry-link" href="/lab/">Laboratory
          <span class="entry-desc">Scientific workflow and signal exploration</span>
        </a>
        <a class="entry-link" href="/dashboard/">Dashboard
          <span class="entry-desc">Existing biomechanics visualizations and analysis</span>
        </a>
      </div>
    </main>
    <footer class="foot">KINORYX | Research prototype</footer>
  </div>
</body>
</html>
"""
