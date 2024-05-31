$(document).ready(function() {
    $('input[name="gaming_genres"]').on('change', function(evt) {
        var checked = $('input[name="gaming_genres"]:checked');
        if (checked.length >= 3) {
            $('input[name="gaming_genres"]').not(':checked').prop('disabled', true);
        } else {
            $('input[name="gaming_genres"]').not(':checked').prop('disabled', false);
        }
    });
});