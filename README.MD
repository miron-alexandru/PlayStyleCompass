# PlayStyle Compass: Your Personalized Video Game Guide
- PlayStyle Compass is a personal guide to discovering video games tailored to your preferences, gaming history, and genre interests. Explore a vast library of games, franchises, and beloved characters, all tailored to your unique preferences and interests.

- Craft your own playstyle based on your interests and take our preference quiz for tailored game recommendations. Our detailed game data includes videos, descriptions, and everything you need to make informed decisions about your next gaming adventure.

- Create personalized lists of your favorite games and ones you can't wait to dive into. See who shares your gaming style and connect with like-minded players to discover new favorites together.

- Write and read reviews from fellow gamers, sharing your thoughts and insights on your favorite titles. Connect with friends, create friend lists, send messages, share your gaming experiences, and many other things to be discovered.



### How to run the website locally:
#### Option one:
* Open a command prompt or terminal
* Navigate to the project's root directory (containing manage.py)
* pip install -r requirements.txt
* Create a file named .env and paste the contents from 'env-example.txt' and then fill the variables with your data
* python manage.py makemigrations
* python manage.py migrate
* python manage.py runserver
* Open the url: http://127.0.0.1:8000/ on your browser to view the website

#### Option two:
* git clone https://github.com/KhadaAke/PlayStyleCompass.git
* cd PlayStyleCompass
* python -m venv env
* source env/Scripts/activate (env\Scripts\activate for Windows)
* pip install -r requirements.txt
* Create a file named .env and paste the contents from 'env-example.txt' and then fill the variables with your data
* python manage.py makemigrations
* python manage.py migrate
* python manage.py runserver
* Open the url: http://127.0.0.1:8000/ on your browser to view the website

Websites for .env configuration: [GiantBomb](https://www.giantbomb.com/) / [SendGrid](https://sendgrid.com/) / [RECAPTCHA](https://www.google.com/recaptcha/about/)


## Project Preview
![Home](project-preview/home.PNG)
![Account Actions](project-preview/acc-actions.PNG)
![Game Details](project-preview/view-game.PNG)
## All images can be found [here](https://github.com/miron-alexandru/PlayStyleCompass/tree/main/project-preview)


<details>
<summary><h2>PlayStyle Compass Changelog</h2></summary>

### Version v2.0:
* Chat Improvements: Date (day/month/year) displayed for each day in the chat / Solved a bug which caused the Edit message textarea to remain on screen and unresponsive.
* Chat Improvements: Changing the background color of the chat / Searching through messages.
* Users are able to send a certain number of messages in a timeframe (spamming prevented).
* Security measures for XSS attacks.
* Message content is changing in real time for both users after message editing.
* Chat CSS improvements.
* Users are able to edit their messages (available 2 minutes for each message).
* Implemented Typing Feature: When an user is typing in chat there is a "User is typing..." message displayed to the other user.
* Chat Improvements: Chat header with options and warnings before deleting messages and visiting links.
* Improved overall visuals & functionality of chat.
* Implemented Chat: Users are able to write messages to each other in real time.

### Version v1.9:
* Improved how to pagination with filtering is done on Game Library and News.
* Solved a bug which caused the pagination to break after navigating to more than one page on the Game Library.
* Implemented sorting and filtering on the News page.
* All articles button added.
* Added hover effects and title display for games/franchises displayed on the Index page.
* Latest news page with all the news.
* Implemented Latest News Articles (related to gaming) on the Index page: Articles from [GameSpot](https://www.gamespot.com/) are retrieved using the GameSpot API and displayed on the Index page.
* Improved how system requirements are displayed.
* Refactored views and helper functions.
* Updated Logo.
* Improved Used Profile: In the profile details a hyperlink to the Favorite Game/Franchise/Character and Last Game Played is created.
* Reorganized navbar items.
* Improved Game Library: Users are able to sort the games and also a new filter: by Franchise
* Implemented Game Library: Users are able to browse games based on different filters like genres, themes and others.
* Changed how game rating is calculated.
* New sorting options for game recommendations: By title and by rating.

### Version v1.8:
* New profile details: favorite franchise, last game finished, preferred streaming platform.
* Updated CSS/HTML on the user profile / profile details.
* Users are able to provide and display on their profile new information about themselves (e.g. favorite game, genres, gaming setup).
* Improvements for System Requirements (CSS/HTML).
* System Requirements for the Games are now displayed.
* Preferences Quiz tweaks.
* Improved QuizRecommendation algorithm: Refactored for better maintainability / Now each time the user is taking the quiz, the recommended games are not the same to add diversity for recommendations.
* Added translations for QuizQuestions.
* Improved overall code to adapt for antipatterns in Django.
* Improved Preference Quiz: Improvements in views, html, recommendation algorithm. / More questions / Created a class to be able to read questions from a csv file and create QuizQuestion objects more easily.
* Implemented Preference Quiz: Users are able to take a quiz with different questions related to gaming preferences and based on the responses to receive game recommendations.

### Version v1.7:
* Implemented pages with Single-player and Multiplayer games.
* Dates for notifications / messages are displayed based on the user timezone.
* Implemented fractional star rating game ratings.
* Refactored views for playstyle compass and users apps.
* Improved reviews section profile clicking.
* Search bar added on view game page.
* Full profile name displayed on hover (for longer profile names).
* Restricted length for username and profile name.
* Updated translations.
* Refactored js files.
* Unique GUID retrieved from API for Game objects so the id remains consistent after any database changes.
* Now users can get recommendations based on their favorite themes.
* New platforms and genres for users to choose for their favorites.
* CSS improvements for better visual appeal.
* Added gameplay videos for each game.
* New data for characters: images & birthday / New data for franchises: images

### Version v1.6
* Added headers & header descriptions to all pages that needed it.
* Organized html files in different folders for easier maintainability.
* Searching for characters is available in the search bar.
* Refactored misc functions.
* Implemented Characters: Users are able to view different game characters and specific details about them.
* Fixed BUGS: Bug that caused the navbar to not appear / Updated translations / Made search bar dynamic based on the page that it exists.
* Added popular franchises on Index
* Formatting / Refactoring.
* Users are now able to search franchises just like searching games.
* Added franchises page where users can explore different franchises and read details about each of them.
* New game information: Franchise.
* Improved password validators.
* Finished translation + Language switcher.
* Implemented multilanguage (English/Romanian).
* Improved live notifications system.
* Implemented live notifications using Websockets.
* Implemented sorting by date for messages & shared games.
* Users are able to send messages to each other.
* Added DLC in game info.
* Added comments to views where necessary.
* Improved Similar Playstyles (HTML/CSS).
* Similar Playstyles page implemented: Users can find other users with a similar playstyle.

### Version v1.5
* Selective deletion of shared games.
* Users are able to view both games other users shared with them and games they shared with other users.
* Implemented Game Sharing: Users are now able to share games with the other users.
* Users are now able to show or hide their favorites, game queue and reviews on their profile. 
* Views refactored in playstyle_compass and users.
* Solved delete account BUG which caused users to be able to delete their account without email confirmation.
* Refactored recommendation helper functions into a RecommendationEngine class.
* Default profile picture at registration.
* Dynamic page headers for Reviews, Game Queue, Favorites
* Save all button on preferences page improved.
* Profile name change functionality improved.
* Profile image resized before change for better performance.
* Navbar / Scrollbar / Css changes and/or improvements. 
* Like-dislike feature improved.
* User profile improvements: Reviews, Likes, Favorites, Game Queue stats are displayed on the profile.
* User profile improvements: Remove friend / Friend request / Profile picture change functionality.
* Implemented User Profile: Now users are able to see their profile and the profile of other users.

### Version v1.4
* CSS/HTML Refactoring / Improvements.
* Added css adjustments for small screens.
* Implemented Likes and Dislikes for the reviews: Users are able to like or dislike a review.
* Removed Upcoming games from user preferences / Game recommendations 
* HTML Refactored
* Minor bug fixes.
* Added Reviews page where users are able to see all the games that they wrote a review for.
* Profile image of user added on Friends List and Friend Requests pages.
* Added Show/Hide functionality for passwords.
* Implemented Games Queue page.
* Code refactoring / Bugs solved in reviews description.
* Friends List improvements: Users are no longer able to send friend requests to users that are already their friends.
* Friends List Implementation:
- Send, receive, accept, decline, and cancel friend requests.
- View incoming and sent requests.
- Manage Friends List and unfriend users.

### Version v1.3:
* Upcoming games added to navbar.
* Profile name change has a cooldown of 1 hour.
* Modified how average score and total reviews are fetched to improve functionality.
* Profile name must be unique.
* Each user is able to Edit or Delete their own reviews for the games.
* Reimplemented reviews functionality.
* Users are now able to write reviews for the games.
* Improved the search bar and small tweaks for the search results page.
* Implemented Top Rated Games page, and also each game has an average rating displayed based on the review scores.
* Now reviews for the games are displayed.
* Views refactored into new helper functions.
* Games that are not yet released removed from recommendations and moved to a new category: Upcoming Games.
* Implemented email change confirmation.
* Added sorting options for the recommended games based on the release date.
* Users are now able to mark games as favorites and they can find them on the Favorite Games page.
* Added popular and upcoming games on the Home Page.
* Code refactored, improved documentation.

### Version v1.2:
* Css improvements.
* Improved the save buttons and save all button functionality on the my playstyle page.
* Implemented Save all button to save all preferences after modifying them.
* Users are now able to modify their preferences individually.
* Users are now able to change their Profile Name
* Improved CSS, added icons for different forms using [FontAwesome](https://fontawesome.com/)
* Users are not able to resend the email verification link.
* Implemented reCAPTCHA.
* Implemented email confirmation for the registration.
* Added profile name for the users.
* Modified css for different templates and placement of the footer.
* Refactored misc functions.
* Refactored CSS.
* Implemented Contact Us - Now users are able to fill a form and send an email for inquiries and communication.
* Added image gallery for each game.
* Added Read more - Read less funcionality for the Overview.
* Added new information about the games (Overview, Developers).
* Implemented pagination for the games recommendation page.
* Users are now also able to change their profile picture by directly clicking on it.
* Improved folder structure.

### Version v1.1:
* Views refactored.
* Implemented Profile Picture feature: Users can now personalize their profiles by adding profile pictures.
* Changed css styles for different templates.
* Modifications to password change view and form.
* Users are now also abe to change their email or password.
* Improved the password reset email template.
* Users are now able to delete their accounts.
* Improved index template.
* Improved password reset templates.
* Users now have the capability to reset their passwords.
* Integrated [Sendgrid](https://sendgrid.com/) APIs to facilitate the sending of password reset emails.
* Improved the base.html styling.
* Refactored the get_recommendations view function.
* Added recommendations based on the gaming history.
* Improved UI for the gaming preferences and preferences pages.
* Implemented default image that automatically takes the place of missing game images.
* Added database filtering: The games are filtered so that duplicate entries are eliminated from the games database.
* Introduced an advanced search bar on the index page, empowering users to seamlessly search for their desired games. The search bar incorporates an autocomplete feature, enhancing user experience and efficiency.

### Version v1.0:
* Improved overall code structure.
* Created .js files for the scripts used.
* Users now have the ability to apply filters. These filters include preferred genres, preferred platforms, and games that align with both the selected platforms and genres.
* Improved the recommendations page: Now an image of each game is displayed and also more details about the game are provided.
* Code refactored
* Improved registration and login pages 
* Implemented feature: Integrated database connectivity to compare the user's preferences with the games stored in the games database. The outcome is a list of game recommendations tailored to the user's preferences.
* Created a database for seamless storage of the acquired data.
* Utilized [Giant Bomb's API](https://www.giantbomb.com/) to efficiently gather essential game data.
* Implemented an enhanced folder structure to ensure the project's long-term maintainability.
* Added a distinct logo that enhances the site's visual identity.
* Elevated the user experience with better UI across all pages.
* Introduced dedicated CSS files to ensure consistent styling.
* Implemented user registration and login functionality.
* Created basic templates for different pages.
* Users can provide their gaming history, select preferred genres, and choose platforms to play on.
* Data is saved in a database for future reference.

