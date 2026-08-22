/* ============================================
   멘탈 위닝리티 — main.js
   1) 스크롤 등장 애니메이션 (IntersectionObserver)
   2) 아코디언 확장/축소 (커리큘럼 · FAQ)
   3) 헤더 스크롤 상태
   4) 앵커 부드러운 이동 (헤더 높이 보정)
   ============================================ */

(function () {
  'use strict';

  /* JS 사용 가능 표시 — CSS의 .no-js 폴백 해제 */
  document.documentElement.classList.remove('no-js');

  var prefersReducedMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches;

  /* --------------------------------------------
     1. 스크롤 등장 애니메이션
     -------------------------------------------- */
  function initScrollReveal() {
    var targets = document.querySelectorAll('.reveal');
    if (!targets.length) return;

    // IntersectionObserver 미지원 또는 모션 최소화 설정 → 즉시 전부 표시
    if (!('IntersectionObserver' in window) || prefersReducedMotion) {
      targets.forEach(function (el) {
        el.classList.add('is-visible');
      });
      return;
    }

    function show(el) {
      el.classList.add('is-visible');
      observer.unobserve(el); // 한 번만 실행
    }

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) show(entry.target);
        });
      },
      {
        root: null,
        rootMargin: '0px 0px -8% 0px',
        threshold: 0.12
      }
    );

    targets.forEach(function (el) {
      observer.observe(el);
    });

    /* 안전장치 —
       빠른 스크롤이나 앵커 점프로 요소가 프레임 사이에 화면을 통과해버리면
       IntersectionObserver는 임계값 교차를 감지하지 못해 콜백을 아예 발생시키지
       않는다. 그 경우 해당 섹션이 영영 투명하게 남으므로, 스크롤할 때마다
       "이미 지나쳐 올라간" 요소를 훑어서 강제로 표시한다. */
    var sweeping = false;

    function sweep() {
      var remaining = document.querySelectorAll('.reveal:not(.is-visible)');
      if (!remaining.length) {
        window.removeEventListener('scroll', onScroll);
        return;
      }
      var limit = window.innerHeight * 0.92;
      remaining.forEach(function (el) {
        if (el.getBoundingClientRect().top < limit) show(el);
      });
      sweeping = false;
    }

    function onScroll() {
      if (sweeping) return;
      sweeping = true;
      window.requestAnimationFrame(sweep);
    }

    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* --------------------------------------------
     2. 아코디언
     -------------------------------------------- */
  function initAccordions() {
    var accordions = document.querySelectorAll('.accordion');
    if (!accordions.length) return;

    accordions.forEach(function (accordion) {
      var items = accordion.querySelectorAll('.acc-item');

      items.forEach(function (item) {
        var trigger = item.querySelector('.acc-trigger');
        var panel = item.querySelector('.acc-panel');
        if (!trigger || !panel) return;

        // 초기 상태: 열려 있는 항목은 실제 높이를 지정
        if (item.classList.contains('is-open')) {
          panel.style.maxHeight = panel.scrollHeight + 'px';
          trigger.setAttribute('aria-expanded', 'true');
        } else {
          panel.style.maxHeight = '0px';
          trigger.setAttribute('aria-expanded', 'false');
        }

        trigger.addEventListener('click', function () {
          var isOpen = item.classList.contains('is-open');

          // 같은 아코디언 안의 다른 항목은 닫기 (한 번에 하나만 열림)
          items.forEach(function (other) {
            if (other === item) return;
            var otherPanel = other.querySelector('.acc-panel');
            var otherTrigger = other.querySelector('.acc-trigger');
            other.classList.remove('is-open');
            if (otherPanel) otherPanel.style.maxHeight = '0px';
            if (otherTrigger) otherTrigger.setAttribute('aria-expanded', 'false');
          });

          if (isOpen) {
            item.classList.remove('is-open');
            panel.style.maxHeight = '0px';
            trigger.setAttribute('aria-expanded', 'false');
          } else {
            item.classList.add('is-open');
            panel.style.maxHeight = panel.scrollHeight + 'px';
            trigger.setAttribute('aria-expanded', 'true');
          }
        });
      });
    });
  }

  /* 창 크기 변경 시 열려 있는 패널 높이 재계산 (반응형 대응) */
  function initAccordionResize() {
    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        document.querySelectorAll('.acc-item.is-open .acc-panel').forEach(
          function (panel) {
            panel.style.maxHeight = panel.scrollHeight + 'px';
          }
        );
      }, 150);
    });
  }

  /* --------------------------------------------
     3. 헤더 스크롤 상태
     -------------------------------------------- */
  function initHeaderScroll() {
    var header = document.getElementById('siteHeader');
    if (!header) return;

    var ticking = false;

    function update() {
      if (window.scrollY > 8) {
        header.classList.add('is-scrolled');
      } else {
        header.classList.remove('is-scrolled');
      }
      ticking = false;
    }

    window.addEventListener(
      'scroll',
      function () {
        if (!ticking) {
          window.requestAnimationFrame(update);
          ticking = true;
        }
      },
      { passive: true }
    );

    update();
  }

  /* --------------------------------------------
     4. 앵커 부드러운 이동
     (CSS scroll-padding-top으로 대부분 처리되지만
      구형 브라우저 폴백으로 유지)
     -------------------------------------------- */
  function initSmoothAnchors() {
    var supportsScrollBehavior =
      'scrollBehavior' in document.documentElement.style;
    if (supportsScrollBehavior) return; // CSS가 처리

    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
      link.addEventListener('click', function (e) {
        var id = link.getAttribute('href');
        if (!id || id === '#') return;

        var target = document.querySelector(id);
        if (!target) return;

        e.preventDefault();
        var header = document.getElementById('siteHeader');
        var offset = header ? header.offsetHeight + 16 : 0;
        var top =
          target.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo(0, top);
      });
    });
  }

  /* --------------------------------------------
     초기화
     -------------------------------------------- */
  function init() {
    initScrollReveal();
    initAccordions();
    initAccordionResize();
    initHeaderScroll();
    initSmoothAnchors();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
