(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('mobileMenuToggle');
    const drawer = document.getElementById('mobileDrawer');
    const backdrop = document.getElementById('mobileDrawerBackdrop');
    const closeBtn = document.getElementById('drawerCloseBtn');

    if (!drawer) return;

    function openDrawer() {
      drawer.classList.add('is-open');
      if (backdrop) backdrop.classList.add('is-open');
      document.body.classList.add('drawer-open');
    }

    function closeDrawer() {
      drawer.classList.remove('is-open');
      if (backdrop) backdrop.classList.remove('is-open');
      document.body.classList.remove('drawer-open');
    }

    if (toggleBtn) {
      toggleBtn.addEventListener('click', function (e) {
        e.preventDefault();
        if (drawer.classList.contains('is-open')) {
          closeDrawer();
        } else {
          openDrawer();
        }
      });
    }

    if (closeBtn) {
      closeBtn.addEventListener('click', function (e) {
        e.preventDefault();
        closeDrawer();
      });
    }

    if (backdrop) {
      backdrop.addEventListener('click', closeDrawer);
    }

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.classList.contains('is-open')) {
        closeDrawer();
      }
    });

    const drawerLinks = drawer.querySelectorAll('a');
    drawerLinks.forEach(function (link) {
      link.addEventListener('click', closeDrawer);
    });
  });
})();