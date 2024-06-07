document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('resetButton').addEventListener('click', function () {
        const selects = document.querySelectorAll('.filter-container select');

        selects.forEach(function (select) {
            select.value = '';
        });

        document.querySelector('form').submit();
    });

    document.getElementById('sort_by').addEventListener('change', function() {
        document.getElementById('filterForm').submit();
    });
});