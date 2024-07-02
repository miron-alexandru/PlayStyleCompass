document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('resetButton').addEventListener('click', function () {
        const selects = document.querySelectorAll('.filter-container select');

        selects.forEach(function (select) {
            select.value = '';
        });

        document.querySelector('form').submit();
    });

    function handleSubmitForm() {
    document.getElementById('filterForm').submit();
    };

    document.getElementById('filter_by').addEventListener('change', handleSubmitForm);
    document.getElementById('sort_by').addEventListener('change', handleSubmitForm);
});