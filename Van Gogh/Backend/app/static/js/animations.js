document.addEventListener('DOMContentLoaded', () => {

  gsap.registerPlugin(ScrollTrigger);

  // Hero parallax y entrada
  gsap.fromTo('.hero-content', 
    { opacity: 0, y: 60 },
    { opacity: 1, y: 0, duration: 1.2, ease: 'power3.out' }
  );

  gsap.fromTo('.hero',
    { scale: 1.1 },
    { scale: 1, duration: 1.5, ease: 'power2.out' }
  );

  // Swirl flotante
  gsap.to('.swirl-svg', {
    rotation: 360,
    duration: 60,
    repeat: -1,
    ease: 'none'
  });

  gsap.to('.swirl-svg-2', {
    rotation: -360,
    duration: 80,
    repeat: -1,
    ease: 'none'
  });

  // Product cards - stagger entrance
  gsap.from('.producto-card', {
    opacity: 0,
    y: 50,
    duration: 0.6,
    stagger: 0.15,
    ease: 'back.out(1.7)',
    scrollTrigger: {
      trigger: '.grid-productos',
      start: 'top 85%',
      toggleActions: 'play none none reverse'
    }
  });

  // Secciones con reveal
  gsap.utils.toArray('section').forEach(section => {
    const heading = section.querySelector('h2');
    if (heading) {
      gsap.from(heading, {
        opacity: 0,
        y: 40,
        duration: 0.8,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: heading,
          start: 'top 85%',
          toggleActions: 'play none none reverse'
        }
      });
    }
  });

  // Ofertas section parallax effect
  gsap.to('.ofertas', {
    backgroundPosition: '50% 30%',
    ease: 'none',
    scrollTrigger: {
      trigger: '.ofertas',
      start: 'top bottom',
      end: 'bottom top',
      scrub: true
    }
  });

  // Navbar shrink on scroll
  gsap.to('header', {
    padding: '0.5rem 5%',
    duration: 0.3,
    ease: 'power1.out',
    scrollTrigger: {
      trigger: 'body',
      start: 'top -80px',
      end: 'top -120px',
      toggleActions: 'play reverse play reverse'
    }
  });

  // Hover magnetic effect on buttons
  document.querySelectorAll('.btn, .btn-auth, .btn-comprar').forEach(btn => {
    btn.addEventListener('mouseenter', () => {
      gsap.to(btn, { scale: 1.05, duration: 0.3, ease: 'power2.out' });
    });
    btn.addEventListener('mouseleave', () => {
      gsap.to(btn, { scale: 1, duration: 0.3, ease: 'power2.out' });
    });
  });

  // Product card hover
  document.querySelectorAll('.producto-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
      gsap.to(card.querySelector('img'), { scale: 1.08, duration: 0.4, ease: 'power2.out' });
    });
    card.addEventListener('mouseleave', () => {
      gsap.to(card.querySelector('img'), { scale: 1, duration: 0.4, ease: 'power2.out' });
    });
  });

  // Paint splash reveal on hero heading
  const heroH2 = document.querySelector('.hero-content h2');
  if (heroH2) {
    const text = heroH2.textContent;
    heroH2.innerHTML = '';
    text.split('').forEach((char, i) => {
      const span = document.createElement('span');
      span.textContent = char;
      span.style.display = 'inline-block';
      heroH2.appendChild(span);
      gsap.from(span, {
        opacity: 0,
        y: -30,
        rotate: Math.random() * 30 - 15,
        duration: 0.4,
        delay: 0.5 + i * 0.04,
        ease: 'back.out(2)'
      });
    });
  }
});
