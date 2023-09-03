# PlayStyle Compass: Your Personalized Video Game Guide
## (Work in Progress)

### PlayStyle Compass is a personal guide to discovering video games tailored to your preferences, gaming history, and genre interests.

<details>
<summary><h2>PlayStyle Compass Changelog</h2></summary>

### Version 1.1:
- Improved the password reset email template.
- Users are now able to delete their accounts.
- Improved index template.
- Improved password reset templates.
- Users now have the capability to reset their passwords.
- Integrated [Sendgrid](https://sendgrid.com/) APIs to facilitate the sending of password reset emails.
- Improved the base.html styling.
- Refactored the get_recommendations view function.
- Added recommendations based on the gaming history.
- Improved UI for the gaming preferences and preferences pages.
- Implemented default image that automatically takes the place of missing game images.
- Added database filtering: The games are filtered so that duplicate entries are eliminated from the games database.
- Introduced an advanced search bar on the index page, empowering users to seamlessly search for their desired games. The search bar incorporates an autocomplete feature, enhancing user experience and efficiency.

### Version 1.0:
- Improved overall code structure.
- Created .js files for the scripts used.
- Users now have the ability to apply filters. These filters include preferred genres, preferred platforms, and games that align with both the selected platforms and genres.
- Improved the recommendations page: Now an image of each game is displayed and also more details about the game are provided.
- Code refactored
- Improved registration and login pages 
- Implemented feature: Integrated database connectivity to compare the user's preferences with the games stored in the games database. The outcome is a list of game recommendations tailored to the user's preferences.
- Created a database for seamless storage of the acquired data.
- Utilized [Giant Bomb's API](https://www.giantbomb.com/) to efficiently gather essential game data.
- Implemented an enhanced folder structure to ensure the project's long-term maintainability.
- Added a distinct logo that enhances the site's visual identity.
- Elevated the user experience with better UI across all pages.
- Introduced dedicated CSS files to ensure consistent styling.
- Implemented user registration and login functionality.
- Created basic templates for different pages.
- Users can provide their gaming history, select preferred genres, and choose platforms to play on.
- Data is saved in a database for future reference.

