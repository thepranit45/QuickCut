// Navbar scroll effect
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 30);
  });
}

// Mobile Hamburger & Overlay logic
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('navLinks');
const navOverlay = document.getElementById('navOverlay');

function toggleMobileMenu() {
  if (!navLinks || !hamburger) return;
  const isOpen = navLinks.classList.toggle('open');
  hamburger.classList.toggle('active', isOpen);
  if (navOverlay) navOverlay.classList.toggle('active', isOpen);
  document.body.style.overflow = isOpen ? 'hidden' : '';
}

function closeMobileMenu() {
  if (!navLinks || !hamburger) return;
  navLinks.classList.remove('open');
  hamburger.classList.remove('active');
  if (navOverlay) navOverlay.classList.remove('active');
  document.body.style.overflow = '';
}

if (hamburger) {
  hamburger.addEventListener('click', toggleMobileMenu);
}

if (navOverlay) {
  navOverlay.addEventListener('click', closeMobileMenu);
}

// Close mobile menu on link clicks
if (navLinks) {
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', closeMobileMenu);
  });
}

// Auto-dismiss messages
setTimeout(() => {
  document.querySelectorAll('.message').forEach(m => m.remove());
}, 5000);
