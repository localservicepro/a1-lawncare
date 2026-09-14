/* ==========================================================================
   A1 Lawn Care Pty Ltd — site behaviour
   Vanilla JS, no dependencies. All motion respects prefers-reduced-motion.
   ========================================================================== */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------------------------------------------------------
     1. Sticky header state
     --------------------------------------------------------------- */
  var header = document.querySelector('.site-header');
  if (header) {
    var onScrollHeader = function () {
      header.classList.toggle('is-stuck', window.scrollY > 12);
    };
    onScrollHeader();
    window.addEventListener('scroll', onScrollHeader, { passive: true });
  }

  /* ---------------------------------------------------------------
     2. Mobile navigation + services dropdown
     --------------------------------------------------------------- */
  var navToggle = document.querySelector('.nav-toggle');
  var scrim = document.querySelector('.nav-scrim');

  function closeNav() {
    document.body.classList.remove('nav-open');
    if (navToggle) navToggle.setAttribute('aria-expanded', 'false');
  }

  if (navToggle) {
    navToggle.addEventListener('click', function () {
      var open = document.body.classList.toggle('nav-open');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  if (scrim) scrim.addEventListener('click', closeNav);

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeNav();
      document.querySelectorAll('.has-sub.is-open').forEach(function (item) {
        item.classList.remove('is-open');
        var btn = item.querySelector('button');
        if (btn) btn.setAttribute('aria-expanded', 'false');
      });
    }
  });

  document.querySelectorAll('.has-sub > button').forEach(function (btn) {
    var parent = btn.parentElement;
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = parent.classList.contains('is-open');
      document.querySelectorAll('.has-sub.is-open').forEach(function (other) {
        if (other !== parent) {
          other.classList.remove('is-open');
          other.querySelector('button').setAttribute('aria-expanded', 'false');
        }
      });
      parent.classList.toggle('is-open', !open);
      btn.setAttribute('aria-expanded', !open ? 'true' : 'false');
    });
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.has-sub')) {
      document.querySelectorAll('.has-sub.is-open').forEach(function (item) {
        item.classList.remove('is-open');
        item.querySelector('button').setAttribute('aria-expanded', 'false');
      });
    }
  });

  /* ---------------------------------------------------------------
     3. Scroll reveal
     --------------------------------------------------------------- */
  var revealables = document.querySelectorAll('.reveal, .reveal-stagger');
  if (revealables.length) {
    if (reduceMotion || !('IntersectionObserver' in window)) {
      revealables.forEach(function (el) { el.classList.add('is-visible'); });
    } else {
      var revealObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            revealObserver.unobserve(entry.target);
          }
        });
      // threshold 0: a section taller than the viewport can never reach a
      // higher ratio, so anything else leaves tall blocks permanently hidden.
      }, { rootMargin: '0px 0px -60px 0px', threshold: 0 });
      revealables.forEach(function (el) { revealObserver.observe(el); });
    }
  }

  /* ---------------------------------------------------------------
     4. Count-up statistics
     --------------------------------------------------------------- */
  var counters = document.querySelectorAll('[data-count-to]');
  if (counters.length) {
    var runCounter = function (el) {
      var target = parseFloat(el.getAttribute('data-count-to'));
      var suffix = el.getAttribute('data-count-suffix') || '';
      var prefix = el.getAttribute('data-count-prefix') || '';
      if (reduceMotion) { el.textContent = prefix + target + suffix; return; }
      var duration = 1500;
      var start = null;
      var step = function (ts) {
        if (start === null) start = ts;
        var progress = Math.min((ts - start) / duration, 1);
        var eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = prefix + Math.round(target * eased) + suffix;
        if (progress < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };

    if (!('IntersectionObserver' in window)) {
      counters.forEach(runCounter);
    } else {
      var counterObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            runCounter(entry.target);
            counterObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.5 });
      counters.forEach(function (el) { counterObserver.observe(el); });
    }
  }

  /* ---------------------------------------------------------------
     5. FAQ accordion — animated height, one open at a time per group
     --------------------------------------------------------------- */
  document.querySelectorAll('.faq details').forEach(function (details) {
    var answer = details.querySelector('.answer');
    var summary = details.querySelector('summary');
    if (!answer || !summary) return;

    var setHeight = function (open) {
      if (reduceMotion) { answer.style.height = open ? 'auto' : '0px'; return; }
      answer.style.height = open ? answer.scrollHeight + 'px' : '0px';
    };

    answer.style.height = details.open ? 'auto' : '0px';
    answer.style.transition = 'height .34s cubic-bezier(.22,1,.36,1)';

    summary.addEventListener('click', function (e) {
      e.preventDefault();
      var isOpen = details.open;

      if (!isOpen) {
        // Close siblings within the same .faq block.
        details.closest('.faq').querySelectorAll('details[open]').forEach(function (other) {
          if (other === details) return;
          var otherAnswer = other.querySelector('.answer');
          otherAnswer.style.height = otherAnswer.scrollHeight + 'px';
          requestAnimationFrame(function () { otherAnswer.style.height = '0px'; });
          otherAnswer.addEventListener('transitionend', function handler() {
            other.open = false;
            otherAnswer.removeEventListener('transitionend', handler);
          });
        });

        details.open = true;
        answer.style.height = '0px';
        requestAnimationFrame(function () { setHeight(true); });
        answer.addEventListener('transitionend', function handler() {
          answer.style.height = 'auto';
          answer.removeEventListener('transitionend', handler);
        });
      } else {
        answer.style.height = answer.scrollHeight + 'px';
        requestAnimationFrame(function () { answer.style.height = '0px'; });
        answer.addEventListener('transitionend', function handler() {
          details.open = false;
          answer.removeEventListener('transitionend', handler);
        });
      }
    });
  });

  /* ---------------------------------------------------------------
     6. Back to top
     --------------------------------------------------------------- */
  var toTop = document.querySelector('.to-top');
  if (toTop) {
    var onScrollTop = function () {
      toTop.classList.toggle('is-visible', window.scrollY > 620);
    };
    onScrollTop();
    window.addEventListener('scroll', onScrollTop, { passive: true });
    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }

  /* ---------------------------------------------------------------
     7. Quote forms
     ---------------------------------------------------------------
     Field names map 1:1 to the CRM contact record:

       full_name        -> {{contact.full_name}}
       email            -> {{contact.email}}
       phone            -> {{contact.phone}}
       property_address -> {{contact.property_address}}
       property_size    -> {{contact.property_size}}
       service_needed   -> {{contact.service_needed}}
       job_notes        -> {{contact.job_notes}}

     The LeadConnector external-tracking script loaded in <head> listens for
     the form's `submit` event and captures those named fields itself, so no
     endpoint is posted to here. We call preventDefault() only AFTER the event
     has been dispatched (our listener and the tracking listener both receive
     it), then send the visitor to the thank-you page.
     --------------------------------------------------------------- */
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var PHONE_RE = /^[0-9+()\s-]{8,}$/;

  function showError(field, message) {
    field.classList.add('has-error');
    var err = field.querySelector('.err');
    if (err) err.textContent = message;
  }

  function clearError(field) {
    field.classList.remove('has-error');
  }

  function validate(form) {
    var ok = true;
    var firstBad = null;

    form.querySelectorAll('.field').forEach(function (field) {
      var input = field.querySelector('input, select, textarea');
      if (!input || input.type === 'hidden') return;

      var value = (input.value || '').trim();
      clearError(field);

      if (input.required && !value) {
        showError(field, 'This field is required.');
        ok = false;
        if (!firstBad) firstBad = input;
        return;
      }
      if (value && input.type === 'email' && !EMAIL_RE.test(value)) {
        showError(field, 'Please enter a valid email address.');
        ok = false;
        if (!firstBad) firstBad = input;
        return;
      }
      if (value && input.type === 'tel' && !PHONE_RE.test(value)) {
        showError(field, 'Please enter a valid phone number.');
        ok = false;
        if (!firstBad) firstBad = input;
      }
    });

    if (firstBad) {
      firstBad.focus();
      firstBad.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });
    }
    return ok;
  }

  document.querySelectorAll('form.js-quote-form').forEach(function (form) {
    // Clear a field's error as soon as the visitor starts fixing it.
    form.addEventListener('input', function (e) {
      var field = e.target.closest('.field');
      if (field && field.classList.contains('has-error')) clearError(field);
    });

    form.addEventListener('submit', function (e) {
      // Honeypot — silently drop obvious bots.
      var hp = form.querySelector('input[name="company_website"]');
      if (hp && hp.value) { e.preventDefault(); return; }

      if (!validate(form)) {
        e.preventDefault();
        return;
      }

      // Stop the browser navigating; the tracking script has already seen
      // this same submit event and captured the named fields.
      e.preventDefault();
      form.classList.add('is-submitting');

      var name = form.querySelector('[name="full_name"]');
      try {
        sessionStorage.setItem('a1_lead_name', name ? name.value.trim() : '');
      } catch (err) { /* private browsing — not important */ }

      var redirect = form.getAttribute('data-redirect') || '/thank-you/';
      // Small delay so the tracking beacon has time to leave the page.
      window.setTimeout(function () { window.location.href = redirect; }, 650);
    });
  });

  /* ---------------------------------------------------------------
     8. Thank-you page personalisation
     --------------------------------------------------------------- */
  var tyName = document.querySelector('[data-lead-name]');
  if (tyName) {
    var stored = '';
    try { stored = sessionStorage.getItem('a1_lead_name') || ''; } catch (err) { stored = ''; }
    var firstName = stored.split(' ')[0];
    if (firstName) {
      tyName.textContent = 'Thanks, ' + firstName + '!';
    }
  }

  /* ---------------------------------------------------------------
     9. Quote modal
     ---------------------------------------------------------------
     Rendered on every page except /contact/, where the form is already the
     main content and the CTA is a plain anchor to it instead.
     --------------------------------------------------------------- */
  var quoteModal = document.getElementById('quote-modal');
  if (quoteModal) {
    var modalPanel = quoteModal.querySelector('.modal-panel');
    var lastFocused = null;
    var FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]),' +
                    ' select:not([disabled]), textarea:not([disabled]),' +
                    ' [tabindex]:not([tabindex="-1"])';

    var focusables = function () {
      return Array.prototype.filter.call(
        quoteModal.querySelectorAll(FOCUSABLE),
        function (el) { return el.offsetParent !== null; }
      );
    };

    var openModal = function () {
      lastFocused = document.activeElement;
      closeNav();
      quoteModal.hidden = false;
      document.body.classList.add('modal-open');
      // Force a frame so the opening transition actually runs.
      requestAnimationFrame(function () {
        quoteModal.classList.add('is-open');
        var first = quoteModal.querySelector('input, select, textarea');
        if (first) first.focus({ preventScroll: true });
      });
    };

    var closeModal = function () {
      quoteModal.classList.remove('is-open');
      document.body.classList.remove('modal-open');
      window.setTimeout(function () {
        // Guard against a re-open landing inside this timeout.
        if (!quoteModal.classList.contains('is-open')) quoteModal.hidden = true;
      }, reduceMotion ? 0 : 340);
      if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
    };

    document.querySelectorAll('[data-quote-open]').forEach(function (trigger) {
      trigger.addEventListener('click', function (e) {
        e.preventDefault();
        openModal();
      });
    });

    quoteModal.querySelectorAll('[data-modal-close]').forEach(function (btn) {
      btn.addEventListener('click', closeModal);
    });

    document.addEventListener('keydown', function (e) {
      if (quoteModal.hidden) return;
      if (e.key === 'Escape') { e.stopPropagation(); closeModal(); return; }
      if (e.key !== 'Tab') return;

      var items = focusables();
      if (!items.length) return;
      var first = items[0];
      var last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault(); last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault(); first.focus();
      } else if (!modalPanel.contains(document.activeElement)) {
        e.preventDefault(); first.focus();
      }
    });
  }

  /* ---------------------------------------------------------------
     10. Prefill the service dropdown from ?service= on the contact page
     --------------------------------------------------------------- */
  var params = new URLSearchParams(window.location.search);
  var wantedService = params.get('service');
  if (wantedService) {
    document.querySelectorAll('select[name="service_needed"]').forEach(function (select) {
      Array.prototype.forEach.call(select.options, function (option) {
        if (option.value.toLowerCase() === wantedService.toLowerCase()) {
          select.value = option.value;
        }
      });
    });
  }
})();
