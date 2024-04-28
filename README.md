# HoosReport - Project B-01

## Authors

- **Axel Ahlander** (cfr8gs) - Scrum Master - [Axel-Ahlander](https://github.com/Axel-Ahlander)
- **Michael He** (rue5vw) - DevOps Manager - [MichaelHeUVA](https://github.com/MichaelHeUVA)
- **Jaren Brensick** (ahk2dn) - Testing Manager - [Jaren-Bresnick](https://github.com/Jaren-Bresnick)
- **Joonhyuk Ko** (tah3af) - Software Architect - [joon0516](https://github.com/joon0516)
- **Michael Park** (tvq3bn) - Requirements Manager - [mikey6453](https://github.com/mikey6453)

## Project Website

[Visit the HoosReport Website](https://project-b-01-d00b72518ac8.herokuapp.com/)

## Steps To Run Locally

To run the application locally on your machine, follow these steps:

1. **Clone the Repository:**

   Clone our repository to your local machine using the command below:
   git clone https://github.com/uva-cs3240-s24/project-b-01.git

2. **Install Dependencies**

    pip install -r requirements.txt

3. **Creating Users**

   There are three types of user accounts you can create:

   - **Regular User:** To create a regular user, simply sign up on the website using either the regular sign-up form or through Google authentication.

   - **Django Admin:** To create a Django admin user, run the following command in your local development environment:
     ```
     python3 manage.py createsuperuser
     ```
     Follow the prompts to set up the username, email, and password.

   - **Site Admin:** To upgrade an existing user to a site admin, you must first have Django admin access. Log in to the Django admin panel, navigate to the 'Users' section, and select the regular user you wish to upgrade. Check the 'superuser status' box and click 'Save' to grant them site admin privileges.


4. **Configure the Site in Django Admin Settings**

    1. In the Django admin, create a new site with the Domain Name set to http://127.0.0.1:8000/ and ensure the site ID is set to 2.
    2. Create a social account with provider set to Google. Client ID/Secret key information is on OAuth.json


5. **Run the Program**

    python3 manage.py runserver


The application should now be accessible at http://127.0.0.1:8000/.

## Issues
