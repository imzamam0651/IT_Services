# IT_Services
◆ Created a Django project “IT Services” with basic configurations.
◆ Created a superuser for the project(username- asad, password- 1234546).
◆ Created simple HTML template for “Home” view and integrated it with Django project.
◆ Configured Email API for the project with my gmail account. 
◆ Implemented User Registration, If the user will click register, a mail will be triggered to the email ID with 
  an OTP and redirecting anonymous user to new page asking for OTP confirmation, and registered the user if OTP 
  is correct. 
◆ Implemented user Authentication, such that if the session user is not logged in then he/she could not be 
  able to access home view and always redirected to Login page and if not registered then they can access the 
  registration page.
◆ Created one Model named “Service” with fields(Service Name, Payment Terms, Service Price, Service Package, 
  Service Tax, Service Image).
◆ Developed the functionality of CRUD operation for services:
a. Created a service(with “Create Service” Button in home view).
b. Single service view.
c. Updating/editing the service(with “Update” Button in Single service view).
d. Deleting the service(with “Delete” Button in Single service view).
e. List view of the services with limited details.
◆ Loaded these services inside the “Home” view HTML previously created with limited details.
◆ In “Service” Model also added one checkbox field named “Active” to make the service active/deactive. Such that, 
  if the checkbox is ticked the service is visible in home page, else it won’t be visible.
◆ Created a “Buy” button in home view for respective services such that clicking on it, will navigate to 
  new Subscription page asking for address, displaying net price with GST defined in service instance. Add “Subscribe” button to the page. 
◆ Added Razor Pay API to the “IT Services” project and implemented the API functionality in previously created, 
  Subscription page, such that on clicking of Subscribe button it will navigate to Razorpay page for the payment.