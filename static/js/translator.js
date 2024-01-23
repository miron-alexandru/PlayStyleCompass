const translate = (key) => {
    const translations = {
        'ro': {
            'Favorites': 'Favorite',
            'In Queue': 'Programate',
            'Reviews': 'Recenzii',
            'Select All': 'Selectează Tot',
            'Unselect All': 'Deselectează Tot',
            'Show Reviews': 'Afișează Recenzii',
            'Hide Reviews': 'Ascunde Recenzii',
            'No reviews for this game yet.': 'Încă nu există recenzii pentru acest joc.',
            '[Read more...]': '[Citește mai mult...]',
            '[Read less...]': '[Citește mai puțin...]',
            'Friend Request': 'Cerere de prietenie',
            'Author': 'Autor',
            'Title': 'Titlu',
            'Summary': 'Rezumat',
            'Rating': 'Evaluare',
            'I like this': 'Îmi place asta',
            'I dislike this': 'Nu-mi place asta',
            'Show': 'Afișează',
            'Hide': 'Ascunde',
            ' seconds': ' secunde',
        },
    };

    const pathSegments = window.location.pathname.split('/');
    const languageCode = pathSegments[1] || 'ro';

    return translations[languageCode]?.[key] || key;
};
