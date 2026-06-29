/* ==========================================
   BVM — Bible Verse Memorization
   SGSS Bible Version
   ========================================== */

// ── Data Loading ──
let VERSES = [];
let currentIndex = 0;
let timerInterval = null;
let secondsRemaining = 300; // 5 minutes
let browseModalOpen = false;

const REFRESH_MINUTES = 5;
const REFRESH_SECONDS = REFRESH_MINUTES * 60;

// ── DOM Refrences ──
const verseText = document.getElementById('verseText');
const verseRef = document.getElementById('verseRef');
const verseNumber = document.getElementById('verseNumber');
const bookName = document.getElementById('bookName');
const bookProgress = document.getElementById('bookProgress');
const progressCount = document.getElementById('progressCount');
const progressFill = document.getElementById('progressFill');
const progressBooks = document.getElementById('progressBooks');
const timerFill = document.getElementById('timerFill');
const timerText = document.getElementById('timerText');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const randomBtn = document.getElementById('randomBtn');
const browseBtn = document.getElementById('browseBtn');
const browseModal = document.getElementById('browseModal');
const closeModal = document.getElementById('closeModal');
const verseList = document.getElementById('verseList');
const searchInput = document.getElementById('searchInput');
const verseCard = document.getElementById('verseCard');

// ── Timer Ring Constants ──
const CIRCUMFERENCE = 2 * Math.PI * 46; // ≈ 289.03

// ── Init ──
document.addEventListener('DOMContentLoaded', () => {
  loadVerses();
  initStars();
  initEvents();
});

function loadVerses() {
  function initFromData() {
    if (VERSES.length === 0) {
      verseText.textContent = 'No verses loaded.';
      return;
    }
    const saved = localStorage.getItem('bvm-current-index');
    if (saved !== null) {
      const idx = parseInt(saved, 10);
      if (!isNaN(idx) && idx >= 0 && idx < VERSES.length) {
        currentIndex = idx;
      }
    }
    showVerse(currentIndex);
    buildBookChips();
    updateTimer();
    startTimer();
  }

  // Try inline JSON (script tag with id="versesData")
  const script = document.getElementById('versesData');
  if (script && script.textContent) {
    try {
      const data = JSON.parse(script.textContent);
      VERSES = data.verses || [];
    } catch (e) {
      console.error('Failed to parse inline verses JSON');
    }
  }

  if (VERSES.length === 0) {
    // Fallback: fetch verses.json
    fetch('verses.json')
      .then(r => r.json())
      .then(data => {
        VERSES = data.verses || [];
        initFromData();
      })
      .catch(err => {
        console.error('Failed to load verses.json:', err);
        verseText.textContent = 'Failed to load verse data.';
      });
    return;
  }

  initFromData();
}

// ── Display Verse ──
function showVerse(index) {
  if (!VERSES.length || index < 0 || index >= VERSES.length) return;

  const v = VERSES[index];
  currentIndex = index;

  // Fade in animation
  verseCard.classList.remove('animating');
  void verseCard.offsetWidth;
  verseCard.classList.add('animating');

  verseText.textContent = v.text;
  verseRef.textContent = `— ${v.ref}`;
  verseNumber.textContent = `#${index + 1} of ${VERSES.length}`;
  bookName.textContent = v.book;

  // Calculate position within book
  const bookStart = getBookStartIndex(v.book);
  const verseInBook = index - bookStart + 1;
  bookProgress.textContent = `Verse ${verseInBook} of 5`;

  // Update progress
  const pct = ((index + 1) / VERSES.length) * 100;
  progressCount.textContent = `${index + 1} / ${VERSES.length}`;
  progressFill.style.width = `${pct}%`;

  // Update book chips
  updateBookChips(v.book, index);

  // Save position
  localStorage.setItem('bvm-current-index', index);

  // Reset timer
  secondsRemaining = REFRESH_SECONDS;
  updateTimer();

  // Update browse modal highlight if open
  if (browseModalOpen) {
    highlightCurrentInList();
    scrollToListCurrent();
  }
}

function getBookStartIndex(bookName) {
  for (let i = 0; i < VERSES.length; i++) {
    if (VERSES[i].book === bookName) return i;
  }
  return 0;
}

// ── Navigation ──
function goPrev() {
  if (currentIndex > 0) {
    showVerse(currentIndex - 1);
  }
}

function goNext() {
  if (currentIndex < VERSES.length - 1) {
    showVerse(currentIndex + 1);
  }
}

function goToRandom() {
  const idx = Math.floor(Math.random() * VERSES.length);
  showVerse(idx);
}

// ── Timer ──
function startTimer() {
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    secondsRemaining--;
    if (secondsRemaining <= 0) {
      secondsRemaining = REFRESH_SECONDS;
      goNext();
    }
    updateTimer();
  }, 1000);
}

function updateTimer() {
  const mins = Math.floor(secondsRemaining / 60);
  const secs = secondsRemaining % 60;
  timerText.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;

  // Update timer ring
  const offset = CIRCUMFERENCE * (1 - secondsRemaining / REFRESH_SECONDS);
  timerFill.setAttribute('stroke-dashoffset', offset);
}

// ── Book Chips ──
function buildBookChips() {
  const seen = new Set();
  progressBooks.innerHTML = '';
  for (const v of VERSES) {
    if (!seen.has(v.book)) {
      seen.add(v.book);
      const chip = document.createElement('span');
      chip.className = 'book-chip';
      chip.dataset.book = v.book;
      chip.textContent = v.short;
      chip.addEventListener('click', () => {
        const first = VERSES.findIndex(x => x.book === v.book);
        if (first >= 0) showVerse(first);
        closeBrowseModal();
      });
      progressBooks.appendChild(chip);
    }
  }
}

function updateBookChips(activeBook, activeIndex) {
  const chips = progressBooks.querySelectorAll('.book-chip');
  const completedCount = Math.floor(activeIndex / 5);
  chips.forEach((chip, i) => {
    chip.classList.remove('active', 'completed');
    if (chip.dataset.book === activeBook) {
      chip.classList.add('active');
    } else if (i < completedCount) {
      chip.classList.add('completed');
    }
  });
}

// ── Browse Modal ──
function openBrowseModal() {
  browseModalOpen = true;
  browseModal.classList.add('open');
  document.body.style.overflow = 'hidden';
  renderVerseList();
  highlightCurrentInList();
  scrollToListCurrent();
  setTimeout(() => searchInput.focus(), 300);
}

function closeBrowseModal() {
  browseModalOpen = false;
  browseModal.classList.remove('open');
  document.body.style.overflow = '';
  searchInput.value = '';
}

function renderVerseList(filterText) {
  verseList.innerHTML = '';
  const filter = (filterText || '').toLowerCase().trim();

  let displayed = VERSES;
  if (filter) {
    displayed = VERSES.filter(v =>
      v.text.toLowerCase().includes(filter) ||
      v.ref.toLowerCase().includes(filter) ||
      v.book.toLowerCase().includes(filter) ||
      v.short.toLowerCase().includes(filter) ||
      `${v.chapter}:${v.verse}` === filter ||
      `${v.short} ${v.chapter}:${v.verse}`.toLowerCase().includes(filter) ||
      `${v.book} ${v.chapter}:${v.verse}`.toLowerCase().includes(filter)
    );
  }

  if (displayed.length === 0) {
    verseList.innerHTML = '<div class="no-results">No verses match your search.</div>';
    return;
  }

  for (const v of displayed) {
    const item = document.createElement('div');
    item.className = 'verse-item';
    item.dataset.index = VERSES.indexOf(v);

    const shortText = v.text.length > 120 ? v.text.slice(0, 120) + '…' : v.text;

    item.innerHTML = `
      <span class="verse-item-ref">${v.ref}</span>
      <span class="verse-item-text">${shortText}</span>
      <span class="verse-item-number">#${VERSES.indexOf(v) + 1}</span>
    `;

    item.addEventListener('click', () => {
      const idx = parseInt(item.dataset.index, 10);
      if (!isNaN(idx) && idx >= 0) {
        showVerse(idx);
        closeBrowseModal();
      }
    });

    verseList.appendChild(item);
  }

  highlightCurrentInList();
}

function highlightCurrentInList() {
  verseList.querySelectorAll('.verse-item').forEach(el => {
    el.classList.toggle('current', parseInt(el.dataset.index, 10) === currentIndex);
  });
}

function scrollToListCurrent() {
  const current = verseList.querySelector('.verse-item.current');
  if (current) {
    current.scrollIntoView({ block: 'center', behavior: 'smooth' });
  }
}

// ── Stars Background ──
function initStars() {
  const canvas = document.getElementById('stars-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let stars = [];
  let animationId;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function create() {
    stars = [];
    const count = Math.floor((canvas.width * canvas.height) / 8000);
    for (let i = 0; i < count; i++) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 1.5 + 0.3,
        alpha: Math.random() * 0.6 + 0.1,
        speed: Math.random() * 0.012 + 0.003,
        dir: Math.random() > 0.5 ? 1 : -1
      });
    }
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const s of stars) {
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 255, 255, ${s.alpha})`;
      ctx.fill();
      s.alpha += s.speed * s.dir;
      if (s.alpha > 1 || s.alpha < 0.05) s.dir *= -1;
    }
    animationId = requestAnimationFrame(draw);
  }

  resize();
  create();
  draw();
  window.addEventListener('resize', () => { resize(); create(); });
}

// ── Events ──
function initEvents() {
  prevBtn.addEventListener('click', goPrev);
  nextBtn.addEventListener('click', goNext);
  randomBtn.addEventListener('click', goToRandom);

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (browseModalOpen) {
      if (e.key === 'Escape') closeBrowseModal();
      return;
    }
    switch (e.key) {
      case 'ArrowLeft':
      case 'a':
        goPrev();
        break;
      case 'ArrowRight':
      case 'd':
        goNext();
        break;
      case 'r':
        goToRandom();
        break;
      case 'b':
        openBrowseModal();
        break;
      case ' ':
        e.preventDefault();
        goNext();
        break;
    }
  });

  // Browse modal
  browseBtn.addEventListener('click', openBrowseModal);
  closeModal.addEventListener('click', closeBrowseModal);
  browseModal.addEventListener('click', (e) => {
    if (e.target === browseModal) closeBrowseModal();
  });

  // Search with debounce
  let searchTimeout;
  searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => renderVerseList(searchInput.value), 200);
  });
}
