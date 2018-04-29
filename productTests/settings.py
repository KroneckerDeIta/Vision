# The application hostname.
application_hostname = "localhost"

# The application port.
application_port = "80"

# The application endpoint.
application_endpoint = "http://" + application_hostname + ":" + application_port

# The endpoint for user registration.
registration_endpoint = application_endpoint + "/api/register"

# The endpoint for entries.
entries_endpoint = application_endpoint + "/api/entries"
