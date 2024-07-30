const translate = (key) => {
    const translations = {
        'ro': {
            'Favorites': 'Favorite',
            'In Queue': 'Programate',
            'Reviews': 'Recenzii',
            'Review': 'Recenzie',
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
            'No messages. Say something!': 'Niciun mesaj. Spune ceva!',
            'Are you sure you want to delete all messages?': 'Ești sigur că dorești să ștergi toate mesajele?',
            'Are you sure you want to visit this website?\n\n': 'Ești sigur că dorești să vizitezi acest website?\n\n',
            'Edit your message...': 'Editează mesajul...',
            'Save': 'Salvează',
            'Cancel': 'Anulare',
            'Edit': 'Editează',
            'This file was shared by another user. Do you trust this source and want to download: ': 'Acest fișier a fost partajat de alt utilizator. Ai încredere în această sursă și dorești să descarci: ',
            'File attached: ': 'Fișier atașat: ',
            'File Attachment: ': 'Atașament: ',
            'Loading Messages...': 'Se încarcă mesajele...',
        },
    };

    const pathSegments = window.location.pathname.split('/');
    const languageCode = pathSegments[1] || 'ro';

    return translations[languageCode]?.[key] || key;
};
