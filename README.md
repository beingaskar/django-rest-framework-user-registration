Features:
---------
* User registration

* User email verification

* Change password - with password reset email.

* View user profile

* Create team

* Invite people to team


API Documentation
-----------------

Postman collection : https://www.getpostman.com/collections/f803c13bd223791d1b21

i. User - Registration
Create/ Register a new user.

	Endpoint 	: /api/accounts/register/
	Request Type 	: POST
	Request Params 	: username, email, password, password_2, first_name, last_name, invite_code
	Non-mandatory params : invite_code

	Response Http status codes : HTTP_200_OK or HTTP_400_BAD_REQUEST
	
	Sample Input 	: https://api.myjson.com/bins/o1id5
	Sample Output 	: https://api.myjson.com/bins/v6pmh

ii. User - Email Verification
Verify the email inorder to activate the user account.

User will recieve an email on successful registration with the verification_code. 
	
	Endpoint 	: /api/accounts/verify/<verification_code>/
	Request Type 	: GET
	Request Params 	: invite_code
	
	Response Http status codes : HTTP_200_OK or HTTP_404_NO_CONTENT
	
iii. User - Login
Obtain authentication token given the user credentials.

	Endpoint 	: /api/accounts/login/
	Request Type 	: POST
	Request Params 	: email (or username) and password
	
	Response 	: { "token": <token> }
	HTTP status code: HTTP_200_OK or HTTP_400_BAD_REQUEST
	
iv. User - Request for Password Reset
Receive an email with password reset link.

	Endpoint 	: /api/accounts/password_reset/
	Request Type 	: POST
	Request Params 	: email
	Request Sample : {"email": "some_email_id@gmail.com"}
	
	HTTP status code: HTTP_200_OK

v. User - Password Change
Change the password. Link as recieved from email by above request (iv).
	
	Endpoint 	: /api/accounts/reset/<reset_code>/
	Request Type 	: POST
	Request Sample : {"new_password": "33441122", "new_password_2": "33441122"}
	
	HTTP status code: HTTP_200_OK or HTTP_400_BAD_REQUEST

vi. User - Retrieve Profile
Retrieve logged in users profile.

	Endpoint 	: /api/accounts/user-profile/
	Request Type 	: GET
	Request Headers : 
		Authorization : Token <token>
	
	HTTP status code: HTTP_200_OK or HTTP_401_UNAUTHORISED
	Response Sample : https://api.myjson.com/bins/18zyux
	
vii. Team - Create
Create a new team.

	Endpoint 	: /api/teams/create/
	Request Type 	: POST
	Request Headers : 
		Authorization : Token <token>
	Request Payload	: {"name": <team_name>, "description": <team_description>}
	
	HTTP status code: HTTP_200_OK or HTTP_400_BAD_REQUEST or HTTP_401_UNAUTHORISED

viii. Team - Invite
Invite people to join the team.

	Endpoint 	: /api/teams/<team_id>/invite/
	Request Type 	: POST
	Request Headers : 
		Authorization : Token <token>
	Request Payload	: {"emails": ["some_email_id@gmail.com"]}
	
	HTTP status code: HTTP_200_OK or HTTP_400_BAD_REQUEST or HTTP_401_UNAUTHORISED


## Run the project Locally ##

i. Clone the repository.

ii. Go to directory of manage.py and install the requirements.

	pip install -r requirements.txt
	
**Note:**
You may configure the virtual environment if required.

For instructions, click here : https://virtualenv.pypa.io/en/latest/installation/
    
iii. Create local_settings.py inside i2x_demo directory.

	EMAIL_HOST_USER = '<to_be_filled>'

	EMAIL_HOST_PASSWORD = '<to_be_filled>'

	DEFAULT_FROM_EMAIL = '<to_be_filled>'

**Note:**
By default, Sqlite3 database is used. You may also use different database in local_settings file if required.

iv. Run migrations

	python manage.py migrate

v. Ready to run the server.

	python manage.py runserver
	
## Configuration Variables ##

#### VERIFICATION_KEY_EXPIRY_DAYS ####

Validity (in days) of user account activation email. Defaulted to 2
	
#### SITE_NAME ####

Name of Website to be displayed on outgoing emails and elsewhere. Defauled to i2x Demo

#### PASSWORD_MIN_LENGTH #### 

A constraint that defines minimum length of password. Defaulted to 8

#### INVITATION_VALIDITY_DAYS #### 

Validity (in days) of user team invitation email. Defaulted to 7


## Try it online: ##
https://dry-stream-50652.herokuapp.com/
	
	
