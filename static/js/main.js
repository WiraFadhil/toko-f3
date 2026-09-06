document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.getElementById('navToggle');
    var menu = document.getElementById('navMenu');

    if (toggle && menu) {
        toggle.addEventListener('click', function () {
            menu.classList.toggle('show');
        });

        document.addEventListener('click', function (event) {
            if (!toggle.contains(event.target) && !menu.contains(event.target)) {
                menu.classList.remove('show');
            }
        });
    }

    var adminToggle = document.getElementById('adminSidebarToggle');
    var adminSidebar = document.getElementById('adminSidebar');

    if (adminToggle && adminSidebar) {
        adminToggle.addEventListener('click', function () {
            adminSidebar.classList.toggle('open');
        });

        document.addEventListener('click', function (event) {
            if (adminSidebar.classList.contains('open') &&
                !adminSidebar.contains(event.target) &&
                !adminToggle.contains(event.target)) {
                adminSidebar.classList.remove('open');
            }
        });

        adminSidebar.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                adminSidebar.classList.remove('open');
            });
        });
    }
});