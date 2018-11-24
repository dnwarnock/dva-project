## DESCRIPTION
This package consists of three parts:
- mongo database
- backend web application
- frontend web application

The backend application acts as an API for serving data from mongo to a frontend application users can interact with.


## Installation
- Must use linux or OSX
- [install docker] (https://docs.docker.com/docker-for-mac/install/)
- [install docker-compose] (https://docs.docker.com/compose/install/)
- Build the backend with `cd backend && docker build -t dva-backend:local . && cd ..`
- Build the frontend with `cd frontend && docker build -t dva-frontend:local . && cd ..`
- [Get an API Key for Google Maps](https://developers.google.com/maps/documentation/javascript/get-api-key)
- Copy and paste your API Key on to line 12 of `frontend/src/main.js` in the value slot for the `key`
- Place your seed json files in the root directory of the project
- seed mongo by running `setup.sh`


## Run
- Start the application by running `docker-compose up` from the root directory of the project
- Visit `http://0.0.0.0:8080/` in a web browsers (preferably firefox or chrome)
- Type an address into the search bar and click on the address that matches the one you are interested in
- A table will be populated with similar properties that could be used in an appraisal dispute
- These properties will also be dotted on the map visible to the left of the table
- Clicking the export button will allow users to download their search results as a csv