/* ============================================================================
   boot.js  --  AIX / pSeries IPL boot sequence + hidden maintenance shell
   Landing page only. Injects its own DOM, so index.html just needs to load
   this file plus boot.css.

   Behaviour:
     * Full IPL plays ONCE EVER per browser (localStorage). Load index.html
       with #ipl in the URL, or run `reboot` in the shell, to see it again.
     * A subtle "#_" in the header drops you into an interactive AIX shell.
       Type `help` to look around; `cat DEVNOTES` is the payoff.
     * prefers-reduced-motion skips the animated boot entirely.
   ========================================================================== */
(function () {
  'use strict';

  /* ─────────────────────────────────────────────────────────────────────────
     EDIT ME: developer notes + shell "filesystem".
     This is the easter egg. Swap in whatever you want people to find.
     Keep it ASCII (no fancy dashes) so it stays on-brand.
     ───────────────────────────────────────────────────────────────────────── */
  var FILES = {
    'DEVNOTES':
      "DEVELOPER NOTES  --  triippiing/Wiki\n" +
      "last touched: 2026-07-17\n" +
      "\n" +
      "* Hand-built static HTML. No framework, no build step. serve.sh + a browser.\n" +
      "* Palette is the 'stone / paper' set in tokens.css. Ochre = accent,\n" +
      "  rust = warn, sage = ok. Do not add a sixth colour, it always looks wrong.\n" +
      "* chrome.js injects the sidebar, the reviewed-date cell, and (on the\n" +
      "  landing page) this shell. nav-data.js is the one source of truth for the\n" +
      "  sidebar tree.\n" +
      "* Runbook IDs (RB-XXX-YYY-NNN) live in the meta grid + footer only, never\n" +
      "  in the <title> or .page-title. Learned that one the hard way.\n" +
      "* Reviewed dates come from <meta name=\"reviewed\">, NOT git. A cosmetic\n" +
      "  commit must never make a stale runbook look fresh.\n" +
      "\n" +
      "TODO\n" +
      "  [ ] finish the VTL section\n" +
      "  [ ] dark mode for the landing page (runbooks already do it)\n" +
      "  [ ] write the DR failover runbook before someone actually needs it\n" +
      "\n" +
      "If you found this: hello. You are exactly the kind of person these\n" +
      "runbooks are written for. Type `help` to look around.\n",

    'motd':
      "*******************************************************************************\n" +
      "*                                                                             *\n" +
      "*   Welcome to wiki  (AIX 7.2)                                                *\n" +
      "*   Unauthorized access is prohibited.                                        *\n" +
      "*   All the good stuff is in the runbooks.                                    *\n" +
      "*                                                                             *\n" +
      "*******************************************************************************\n"
  };

  var FORTUNES = [
    "rootvg is not a backup strategy.",
    "The error was in errpt the whole time.",
    "smitty knew. smitty always knew.",
    "A clone of rootvg a day keeps the outage away.",
    "Real admins test the restore, not the backup."
  ];
  /* ───────────────────────────── end editable block ───────────────────────── */

  var DONE_KEY   = 'wiki_ipl_v1_done';
  var forceBoot  = location.hash === '#ipl' || /[?&]boot=1/.test(location.search);
  var reduce     = window.matchMedia &&
                   window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── tiny helpers ────────────────────────────────────────────────────────── */
  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }

  /* ══════════════════════════════════════════════════════════════════════════
     PART 1 -- the IPL boot sequence
     ════════════════════════════════════════════════════════════════════════ */

  // Operator-panel LED checkpoint codes, roughly in real IPL order:
  // E1xx = system firmware, 0xxx/9xxx = AIX boot, cxx = late-boot config.
  var LED_CODES = ['E1F1','E1F2','E1FB','E100','E105','E1AF','9081','2E7',
                   '0517','0518','0538','0553','0551','0552','0581','0570',
                   'c31','c32','c33','c46','c54','c07','OK  '];

  function runIPL(done) {
    var ov  = el('div', 'ipl');
    var scr = el('div', 'ipl-scr');
    var led = el('div', 'ipl-led');
    led.innerHTML = '<div class="win"><div class="code">' + LED_CODES[0] +
                    '</div></div><div class="cap">operator panel</div>';
    var skip = el('div', 'ipl-skip', 'press any key to skip IPL');
    ov.appendChild(scr);
    ov.appendChild(led);
    ov.appendChild(skip);
    document.body.appendChild(ov);
    document.body.style.overflow = 'hidden';
    setTimeout(function () { skip.classList.add('show'); }, 1400);

    var codeEl = led.querySelector('.code');
    var ledIx  = 0;
    var ledTimer = setInterval(function () {
      ledIx = Math.min(ledIx + 1, LED_CODES.length - 1);
      codeEl.textContent = LED_CODES[ledIx];
    }, 430);

    // skip machinery: sleep() short-circuits once `skipped` is set
    var skipped = false, pending = null;
    function Skip() {}
    function sleep(ms) {
      return new Promise(function (res, rej) {
        if (skipped) return rej(new Skip());
        var t = setTimeout(function () {
          pending = null;
          skipped ? rej(new Skip()) : res();
        }, ms);
        pending = function () { clearTimeout(t); rej(new Skip()); };
      });
    }
    function doSkip() {
      if (skipped) return;
      skipped = true;
      if (pending) pending();
    }
    window.addEventListener('keydown', doSkip, { once: true });
    ov.addEventListener('click', doSkip);

    function line(text, cls) {
      var e = el('span', 'ipl-line' + (cls ? ' ' + cls : ''), text);
      scr.appendChild(e);
      scr.scrollTop = scr.scrollHeight;
      return e;
    }
    // print an array of lines with a small gap between each
    function block(lines, gap, cls) {
      return lines.reduce(function (p, t) {
        return p.then(function () { line(t, cls); return sleep(gap); });
      }, Promise.resolve());
    }

    var now = new Date();
    var stamp = now.toString().replace(/\s*\(.*\)$/, '');

    Promise.resolve()
      // ── firmware / service processor ─────────────────────────────────────
      .then(function () { return sleep(300); })
      .then(function () {
        return block([
          'IBM IBM IBM IBM IBM IBM IBM IBM IBM IBM IBM IBM IBM IBM IBM IBM'
        ], 120, 'ibm');
      })
      .then(function () { line(''); return sleep(260); })
      .then(function () {
        return block([
          '  1 = SMS Menu             5 = Default Boot List',
          '  6 = Stored Boot List     8 = Open Firmware Prompt',
          ''
        ], 150, 'dim');
      })
      .then(function () {
        return block([
          '  memory        keyboard        network        scsi        speaker'
        ], 200, 'dim');
      })
      .then(function () { line(''); return sleep(500); })
      .then(function () {
        line('Elapsed time since release of system processors: ' +
             (24000 + Math.floor(Math.random() * 3000)) + ' mS', 'dim');
        return sleep(400);
      })
      // ── AIX boot banner ──────────────────────────────────────────────────
      .then(function () { line(''); return sleep(200); })
      .then(function () {
        line('-------------------------------------------------------------------------------', 'rule');
        line('                               Welcome to AIX.', 'white');
        line('              boot image timestamp: ' + stamp, 'dim');
        line('       processor count: 4      memory size: 16384 MB', 'dim');
        line('       boot device: /vdevice/v-scsi@30000002/disk@8100000000000000', 'dim');
        line('-------------------------------------------------------------------------------', 'rule');
        line('');
        return sleep(650);
      })
      .then(function () {
        return block([
          'AIX Version 7.2',
          'Starting NODE#000 physical CPU#001 as logical CPU#001 ... done.',
          'Starting NODE#000 physical CPU#002 as logical CPU#002 ... done.',
          'Starting NODE#000 physical CPU#003 as logical CPU#003 ... done.'
        ], 210, 'phos');
      })
      .then(function () { line(''); return sleep(300); })
      // ── rc.boot / device configuration ───────────────────────────────────
      .then(function () {
        return block([
          'Saving Base Customize Data to boot disk',
          'Starting the sync daemon',
          'Starting the error daemon',
          'System initialization completed.',
          'Setting tunable parameters ... complete'
        ], 190);
      })
      .then(function () { line(''); line('Configuring installed devices ...', 'white'); return sleep(300); })
      .then(function () {
        return block([
          '  sys0      Available   System Object',
          '  sysplanar0 Available  System Planar',
          '  hdisk0    Available   MPIO IBM 2076 FC Disk',
          '  hdisk1    Available   MPIO IBM 2076 FC Disk',
          '  en0       Available   Standard Ethernet Network Interface',
          '  rmt0      Available   IBM 3580 Ultrium Tape Drive'
        ], 150, 'dim');
      })
      .then(function () { line(''); return sleep(250); })
      // ── multi-user init ──────────────────────────────────────────────────
      .then(function () {
        return block([
          'Starting Multi-user Initialization',
          ' Performing auto-varyon of Volume Groups',
          ' Activating all paging spaces',
          '   swapon: Paging device /dev/hd6 activated.',
          ' Performing all automatic mounts',
          ' Checking filesystems ...',
          'Multi-user initialization completed'
        ], 200);
      })
      .then(function () { line(''); return sleep(300); })
      // ── SRC subsystems ───────────────────────────────────────────────────
      .then(function () {
        var subs = ['syslogd','errdemon','portmap','inetd','sendmail','snmpd',
                    'hostmibd','aixmibd','snmpmibd','sshd','ctrmc','cthags'];
        var pid = 3500 + Math.floor(Math.random() * 200);
        return subs.reduce(function (p, name) {
          return p.then(function () {
            pid += Math.floor(Math.random() * 90) + 10;
            line('0513-059 The ' + name +
                 ' Subsystem has been started. Subsystem PID is ' + pid + '.', 'phos');
            return sleep(120);
          });
        }, Promise.resolve());
      })
      .then(function () { line(''); return sleep(450); })
      // ── login + handoff ──────────────────────────────────────────────────
      .then(function () {
        line('');
        line('AIX Version 7.2', 'white');
        line('Copyright IBM Corporation, 1982, 2023.', 'dim');
        line('');
        return sleep(500);
      })
      .then(function () { line('Console login: root', 'white'); return sleep(550); })
      .then(function () { line("root's Password: ", 'white'); return sleep(700); })
      .then(function () {
        line('');
        line('Last login: ' + stamp + ' on /dev/vty0', 'dim');
        line('');
        line('Loading knowledge base ...', 'amber');
        return sleep(900);
      })
      .then(finish)
      .catch(function (e) { if (e instanceof Skip) finish(); else { console.error(e); finish(); } });

    var finished = false;
    function finish() {
      if (finished) return;
      finished = true;
      clearInterval(ledTimer);
      try { localStorage.setItem(DONE_KEY, '1'); } catch (_) {}
      ov.classList.add('fade');
      setTimeout(function () {
        ov.remove();
        document.body.style.overflow = '';
        if (location.hash === '#ipl') {
          history.replaceState(null, '', location.pathname + location.search);
        }
        if (done) done();
      }, 520);
    }
  }

  /* ══════════════════════════════════════════════════════════════════════════
     PART 2 -- the interactive maintenance shell
     ════════════════════════════════════════════════════════════════════════ */

  var shellEl, outEl, inputEl, psEl, cmdHist = [], hix = 0;
  var cwd = '/', oldPwd = '/', rbCache = null;

  // the shell prompt reflects the current directory, so `cd` is visible
  function promptStr() { return cwd === '/' ? '# ' : cwd.replace(/^\//, '') + ' # '; }
  function setCwd(p) { cwd = p; if (psEl) psEl.textContent = promptStr(); }

  // /runbooks is browsable: scrape the live cards on the page so the listing
  // never goes stale as runbooks are added or renamed.
  function getRunbooks() {
    if (rbCache) return rbCache;
    rbCache = [];
    document.querySelectorAll('a.card').forEach(function (a) {
      if (a.classList.contains('card-placeholder')) return;
      var href = a.getAttribute('href') || '';
      if (!href || href.charAt(0) === '#') return;
      var h4 = a.querySelector('h4');
      rbCache.push({
        href: href,
        name: decodeURIComponent(href.split('/').pop()),
        title: h4 ? h4.textContent.trim() : href
      });
    });
    return rbCache;
  }

  function buildShell() {
    shellEl = el('div', 'shell');
    var bar = el('div', 'shell-bar');
    bar.innerHTML = '<span class="dot"></span>' +
      '<span>root@wiki  --  /dev/pts/0  --  maintenance shell</span>' +
      '<span class="close" role="button" title="close (Esc)">[ close ]</span>';
    outEl = el('div', 'shell-out');

    var row = el('div', 'shell-row');
    psEl = el('span', 'shell-ps', promptStr());
    inputEl = el('input', 'shell-in');
    inputEl.setAttribute('autocomplete', 'off');
    inputEl.setAttribute('autocapitalize', 'off');
    inputEl.setAttribute('spellcheck', 'false');
    inputEl.setAttribute('aria-label', 'maintenance shell input');
    row.appendChild(psEl);
    row.appendChild(inputEl);

    shellEl.appendChild(bar);
    shellEl.appendChild(outEl);
    shellEl.appendChild(row);
    document.body.appendChild(shellEl);

    bar.querySelector('.close').addEventListener('click', closeShell);
    shellEl.addEventListener('mousedown', function (e) {
      if (e.target !== inputEl) { /* keep focus on the input */ }
    });
    shellEl.addEventListener('click', function () { inputEl.focus(); });
    inputEl.addEventListener('keydown', onKey);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && shellEl.classList.contains('open')) closeShell();
    });
  }

  function print(text, cls) {
    var e = el('div', cls, text == null ? '' : text);
    outEl.appendChild(e);
    outEl.scrollTop = outEl.scrollHeight;
  }

  function printNode(node) {
    outEl.appendChild(node);
    outEl.scrollTop = outEl.scrollHeight;
  }

  // AIX logo, lifted verbatim from neofetch (drawn entirely in c1 = green).
  var AIX_LOGO = ["           `:+ssssossossss+-`","        .oys///oyhddddhyo///sy+.","      /yo:+hNNNNNNNNNNNNNNNNh+:oy/","    :h/:yNNNNNNNNNNNNNNNNNNNNNNy-+h:","  `ys.yNNNNNNNNNNNNNNNNNNNNNNNNNNy.ys"," `h+-mNNNNNNNNNNNNNNNNNNNNNNNNNNNNm-oh"," h+-NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN.oy","/d`mNNNNNNN/::mNNNd::m+:/dNNNo::dNNNd`m:","h//NNNNNNN: . .NNNh  mNo  od. -dNNNNN:+y","N.sNNNNNN+ -N/ -NNh  mNNd.   sNNNNNNNo-m","N.sNNNNNs  +oo  /Nh  mNNs` ` /mNNNNNNo-m","h//NNNNh  ossss` +h  md- .hm/ `sNNNNN:+y",":d`mNNN+/yNNNNNd//y//h//oNNNNy//sNNNd`m-"," yo-NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNm.ss"," `h+-mNNNNNNNNNNNNNNNNNNNNNNNNNNNNm-oy","   sy.yNNNNNNNNNNNNNNNNNNNNNNNNNNs.yo","    :h+-yNNNNNNNNNNNNNNNNNNNNNNs-oh-","      :ys:/yNNNNNNNNNNNNNNNmy/:sy:","        .+ys///osyhhhhys+///sy+.","            -/osssossossso/-"];

  var FF_PALETTE = ['#262622', '#a35a35', '#63d68a', '#f0a830',
                    '#5a7a9c', '#8a6d9c', '#5c9c93', '#c8d0c4'];

  function renderFetch() {
    var wrap = el('div', 'ff');
    var logo = el('pre', 'ff-logo', AIX_LOGO.join('\n'));  // textContent: no injection
    var info = el('div', 'ff-info');
    var days = 3 + Math.floor(Math.random() * 40);
    var row = function (k, v) { return '<span class="k">' + k + ':</span> ' + v + '\n'; };
    info.innerHTML =
      '<span class="t">root</span>@<span class="t">wiki</span>\n' +
      '-----------------\n' +
      row('OS', 'AIX 7.2 powerpc') +
      row('Host', 'IBM Power System S924 (9009-42A)') +
      row('Kernel', '7.2.0.0') +
      row('Uptime', days + ' days') +
      row('Packages', getRunbooks().length + ' (runbook)') +
      row('Shell', 'ksh 93u+') +
      row('Terminal', '/dev/pts/0') +
      row('CPU', 'POWER9 (4) @ 3.8GHz') +
      row('Memory', '4096MiB / 16384MiB') +
      '<div class="ff-pal">' +
        FF_PALETTE.map(function (c) { return '<i style="background:' + c + '"></i>'; }).join('') +
      '</div>';
    wrap.appendChild(logo);
    wrap.appendChild(info);
    printNode(wrap);
  }

  function openShell() {
    if (!shellEl) buildShell();
    if (shellEl.classList.contains('open')) { inputEl.focus(); return; }
    if (!outEl.childElementCount) {
      print(FILES.motd, 'dim');
      print('');
      print('Type `help` for a list of commands.', 'dim');
      print('');
    }
    shellEl.classList.add('open');
    document.body.style.overflow = 'hidden';
    setTimeout(function () { inputEl.focus(); }, 30);
  }

  function closeShell() {
    if (!shellEl) return;
    shellEl.classList.remove('open');
    document.body.style.overflow = '';
  }

  function onKey(e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      var raw = inputEl.value;
      inputEl.value = '';
      print(promptStr() + raw, 'white');
      var cmd = raw.trim();
      if (cmd) { cmdHist.push(cmd); hix = cmdHist.length; }
      run(cmd);
      outEl.scrollTop = outEl.scrollHeight;
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (hix > 0) { hix--; inputEl.value = cmdHist[hix] || ''; }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (hix < cmdHist.length) { hix++; inputEl.value = cmdHist[hix] || ''; }
    } else if (e.key === 'l' && e.ctrlKey) {
      e.preventDefault();
      outEl.innerHTML = '';
    }
  }

  var LS = ['DEVNOTES', 'motd', 'runbooks/', '.secrets'];

  var COMMANDS = {
    help: function () {
      print('available commands:', 'phos');
      print('  ls            list files          cat <file>   show a file');
      print('  cd <dir>      change directory    open <name>  open a runbook');
      print('  uname -a      system info         oslevel      AIX level');
      print('  whoami / id   who you are         hostname     node name');
      print('  date          current date        uptime       how long up');
      print('  motd          message of the day  fortune      words of wisdom');
      print('  neofetch      system info + logo  fastfetch    (alias)');
      print('  clear         clear the screen    reboot       replay the IPL');
      print('  exit          leave the shell');
      print('');
      print('hint: try `cd runbooks/`, and `cat DEVNOTES` is worth a read.', 'dim');
    },
    ls: function (args) {
      var target = args.find(function (a) { return a.charAt(0) !== '-'; });
      var here = target ? '/' + target.replace(/^\/|\/$/g, '') : cwd;
      if (here === '/runbooks') {
        var rb = getRunbooks();
        if (!rb.length) { print('(no runbooks found)', 'dim'); return; }
        rb.forEach(function (r) { print('  ' + r.name, 'phos'); });
        print('');
        print(rb.length + ' runbooks.  type `open <name>` to read one.', 'dim');
        return;
      }
      var showAll = args.indexOf('-a') !== -1 || args.indexOf('-la') !== -1 || args.indexOf('-al') !== -1;
      var items = LS.filter(function (f) { return showAll || f[0] !== '.'; });
      print(items.join('   '), 'phos');
    },
    cd: function (args) {
      var t = (args[0] || '~').replace(/\/+$/, '');
      if (t === '.') return;                       // stay put
      if (t === '-') {                             // toggle to previous dir
        var prev = oldPwd; oldPwd = cwd; setCwd(prev);
        print(cwd, 'dim');
        return;
      }
      var dest;
      if (t === '' || t === '~' || t === '/' || t === '..') dest = '/';   // parent of /runbooks is /
      else if (t === 'runbooks' || t === '/runbooks') dest = '/runbooks';
      else { print('ksh: cd: ' + t + ': 0403-005 The specified directory does not exist.', 'rust'); return; }
      if (dest === cwd) { if (dest === '/runbooks') COMMANDS.ls([]); return; }
      oldPwd = cwd; setCwd(dest);
      if (dest === '/runbooks') COMMANDS.ls([]);
    },
    open: function (args) {
      var q = (args.find(function (a) { return a.charAt(0) !== '-'; }) || '').toLowerCase();
      if (!q) { print('open: usage: open <name>   (try `ls runbooks/` first)', 'rust'); return; }
      var rb = getRunbooks();
      var strip = function (s) { return s.toLowerCase().replace(/\.html$/, ''); };
      var hit = rb.find(function (r) { return strip(r.name) === strip(q); }) ||
                rb.find(function (r) { return strip(r.name).indexOf(strip(q)) !== -1; }) ||
                rb.find(function (r) { return r.title.toLowerCase().indexOf(q) !== -1; });
      if (!hit) { print('open: ' + q + ': no such runbook. try `ls runbooks/`.', 'rust'); return; }
      print('opening ' + hit.title + ' ...', 'amber');
      setTimeout(function () { location.href = hit.href; }, 350);
    },
    cat: function (args) {
      var f = args.find(function (a) { return a[0] !== '-'; });
      if (!f) { print('cat: usage: cat <file>', 'rust'); return; }
      if (f === '.secrets') {
        print('cat: .secrets: The file access permissions do not allow the specified action.', 'rust');
        print('(even root does not get everything. nice try.)', 'dim');
        return;
      }
      if (f === 'runbooks/' || f === 'runbooks') {
        print('cat: runbooks: 0403-016 Cannot find or open the file (it is a directory).', 'rust');
        return;
      }
      if (/\.html$/i.test(f)) {
        var rbHit = getRunbooks().find(function (r) { return r.name.toLowerCase() === f.toLowerCase(); });
        if (rbHit) { print('cat: ' + f + ': is an HTML runbook. use `open ' + f + '`.', 'rust'); return; }
      }
      if (FILES[f] != null) { print(FILES[f], f === 'DEVNOTES' ? 'phos' : 'dim'); return; }
      print('cat: ' + f + ': 0403-005 Cannot find or open the file.', 'rust');
    },
    uname: function (args) {
      if (args.indexOf('-a') !== -1)
        print('AIX wiki 2 7 00F8B1C24C00 powerpc', 'phos');
      else print('AIX', 'phos');
    },
    oslevel: function (args) {
      print(args.indexOf('-s') !== -1 ? '7200-05-04-2220' : '7.2.0.0', 'phos');
    },
    whoami: function () { print('root', 'phos'); },
    id: function () { print('uid=0(root) gid=0(system) groups=2(bin),3(sys),7(security)', 'phos'); },
    hostname: function () { print('wiki', 'phos'); },
    pwd: function () { print(cwd, 'phos'); },
    date: function () { print(new Date().toString().replace(/\s*\(.*\)$/, ''), 'phos'); },
    uptime: function () {
      var d = 3 + Math.floor(Math.random() * 40);
      print('  ' + new Date().toTimeString().slice(0, 5) +
            '   up ' + d + ' days,  4 users,  load average: 0.08, 0.11, 0.09', 'phos');
    },
    motd: function () { print(FILES.motd, 'dim'); },
    fortune: function () { print(FORTUNES[Math.floor(Math.random() * FORTUNES.length)], 'amber'); },
    neofetch: function () { renderFetch(); },
    fastfetch: function () { renderFetch(); },
    echo: function (args) { print(args.join(' '), 'phos'); },
    clear: function () { outEl.innerHTML = ''; },
    reboot: function () {
      print('Rebooting the system ...', 'amber');
      try { localStorage.removeItem(DONE_KEY); } catch (_) {}
      setTimeout(function () {
        location.hash = '#ipl';
        location.reload();
      }, 500);
    },
    exit: function () { closeShell(); },
    logout: function () { closeShell(); }
  };
  COMMANDS['shutdown'] = function (args) {
    if (args.indexOf('-Fr') !== -1 || args.indexOf('-r') !== -1) return COMMANDS.reboot();
    print('SHUTDOWN PROGRAM', 'amber');
    print('Stopping The Web ... (just kidding, use `reboot`)', 'dim');
  };

  function run(cmd) {
    if (!cmd) return;
    var parts = cmd.split(/\s+/);
    var name = parts[0];
    var args = parts.slice(1);
    if (name === 'sudo') { print('root is already all-powerful here.', 'dim'); return; }
    if (COMMANDS[name]) { COMMANDS[name](args); return; }
    print('ksh: ' + name + ':  not found.', 'rust');
  }

  /* ── header affordance: the subtle "#_" ──────────────────────────────────── */
  function addShellKey() {
    var host = document.querySelector('.header-meta') || document.querySelector('header');
    if (!host) return;
    var btn = el('button', 'shell-key');
    btn.type = 'button';
    btn.title = 'maintenance shell';
    btn.setAttribute('aria-label', 'open maintenance shell');
    btn.innerHTML = '#<span class="cur"></span>';
    btn.addEventListener('click', openShell);
    host.appendChild(btn);
  }

  // backtick as a quiet extra way in, once the page is live
  function keyHook(e) {
    if (e.key === '`' && document.activeElement &&
        document.activeElement.tagName !== 'INPUT' &&
        document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault();
      openShell();
    }
  }

  /* ── wire everything up ──────────────────────────────────────────────────── */
  function init() {
    addShellKey();
    document.addEventListener('keydown', keyHook);

    var alreadyBooted = false;
    try { alreadyBooted = localStorage.getItem(DONE_KEY) === '1'; } catch (_) {}

    if (forceBoot || (!alreadyBooted && !reduce)) {
      runIPL();
    } else if (!alreadyBooted && reduce) {
      // honour reduced-motion: no animation, but don't nag again
      try { localStorage.setItem(DONE_KEY, '1'); } catch (_) {}
    }
  }

  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', init);
  else init();
})();
