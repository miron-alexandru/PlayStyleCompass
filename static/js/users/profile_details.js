$(document).ready(function() {
    $('input[name="gaming_genres"], input[name="favorite_game_modes"]').on('change', function(evt) {
        var name = $(this).attr('name');
        var checked = $('input[name="' + name + '"]:checked');
        
        if (checked.length >= 3) {
            $('input[name="' + name + '"]').not(':checked').prop('disabled', true);
        } else {
            $('input[name="' + name + '"]').not(':checked').prop('disabled', false);
        }
    });
});