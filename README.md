Construction Quote Web Application
The Construction Quote Web Application is a Django-based tool created specifically for construction companies to manage and automate project quotations. It offers a streamlined way to handle client requests, calculate and adjust project costs, and monitor project progress—all within a responsive and user-friendly interface. The application supports role-based access, where admins and users have different privileges: admins can manage all aspects of quotations and project updates, while regular users can create requests and track project status. Real-time cost adjustments are integrated through AJAX, allowing for immediate updates that enhance client transparency and help the team stay informed.

Project Routes
The web application includes several routes designed to facilitate both client and admin interactions. The home page (/) is publicly accessible, providing an entry point to the application. Users can register (/register/) or log in (/login/) to access project-related features. Once logged in, users can view their projects on the /projects/ route and request new quotations on /projects/create/. Each project has a detail page (/projects/<id>/), allowing users to track specific project details. For admins, the /admin/dashboard/ route offers an overview of all projects and client interactions. Additionally, admins can edit project details and costs on the /admin/projects/<id>/edit/ page. The /logout/ route safely logs users out, preserving account security.

Project Packages
This application relies on several key packages that provide core functionality and enhance user experience. Django is the primary web framework, handling the application’s structure, user authentication, and routing. Django REST Framework (DRF) extends Django’s capabilities by offering RESTful API endpoints for improved data handling between the frontend and backend. For database integration, psycopg2-binary is included to support PostgreSQL connections, which are recommended for production environments. Bootstrap provides responsive styling, ensuring a consistent user experience across devices, and AJAX allows for real-time updates in the cost adjustment feature, delivering a dynamic and interactive feel to the interface. These packages are listed in the requirements.txt file for easy installation.

Installation
To install and run this application locally, start by ensuring you have Python and Git installed on your system. First, clone the project repository. Open your terminal, navigate to the directory where you want to store the project, and run:

bash
Copy code
git clone https://github.com/ASHJALE/ConstructionQuote.git
cd ConstructionQuote
Setting Up a Virtual Environment
Create a virtual environment to manage dependencies separately from your system’s global packages:

bash
Copy code
# Create a virtual environment
python -m venv venv

# Activate the virtual environment

# On Windows
venv\Scripts\activate
Installing Dependencies
Once the virtual environment is active, install the required packages using:

bash
Copy code
pip install -r requirements.txt
Configuring Environment Variables
In the root directory of the project, create a .env file to securely store environment variables. These variables include sensitive data like the Django secret key and database configuration. For example:

plaintext
Copy code
SECRET_KEY=your_django_secret_key
DEBUG=True
DATABASE_URL=your_database_url  # Replace with actual database configuration
Replace your_django_secret_key with a unique and secure key for your Django application. If using a PostgreSQL database, replace your_database_url with your database URL.

Running Migrations
After setting up the environment variables, apply Django’s database migrations to initialize the database schema. Run:

bash
Copy code
python manage.py migrate
This command sets up all the necessary tables in the database.

Creating a Superuser
Create a superuser to access the admin panel and manage the application’s data:

bash
Copy code
python manage.py createsuperuser
Follow the prompts to set up the superuser’s username, email, and password.

Running the Code
Once the setup is complete, you’re ready to run the application! Start the Django development server by running:

bash
Copy code
python manage.py runserver
This command launches the server, and you can access the application in your browser at http://127.0.0.1:8000/.

To log in as an admin, go to http://127.0.0.1:8000/admin/ and use the superuser credentials you created.
To use the application as a regular user, you can register at http://127.0.0.1:8000/register/.
How to Use the Application
After successfully logging into the Construction Quote Web Application, users can navigate various features to manage project quotations effectively. New users will need to create an account by filling out the registration form, which provides access to the application's functionalities. Once registered, users can log in to their dashboard, where they will see a summary of their existing projects and have the option to create new quotation requests. To initiate a new project, users can click on the "Create New Project" button, fill in the necessary details such as project name, description, and estimated costs, and upload any relevant documents.

After submitting a project request, users can easily view their projects on the dashboard. By clicking on a project name, they can access detailed information about that project, including its status, associated costs, and any comments made by admin users. For admin users, the dashboard offers a comprehensive view of all projects, enabling them to manage client requests effectively. Admins can adjust project costs, update project statuses, and edit project details through the admin interface.

To ensure security, users should log out of the application after completing their tasks. By following these steps, both users and admins can utilize the Construction Quote Web Application to streamline the process of managing construction project quotations, ensuring a more efficient workflow.
