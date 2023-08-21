# Canvas Bot. Integrate your canvas with discord servers!
 That name will have to be changed later.  

## To-do 
1. fix all db functions and create discord dialogs for choosing which notification intervals
2. figure out how the user will go to a certain assignment without having to scroll through the massive embed
3. create discord dialog for adding courses to your account (in case that course doesnt have assignments or you dont want to be notified for a few courses)
4. work on better assignment parsing from the canvas api and experiment with better ways to get upcoming assignments from the api
add the ability to attach courses to a server based on their access token and set up server functions:
    a. permanent channel for bots
    b. role selector
    c. admin queue for accepting courses into the server
    d. channel for each course with assignment notifications showing up within 30 mins by default (use same embed structure from dm)
5. actually create the system to deliver notifications to users at specified intervals
    study group and features in our own server
6. oauth support? so users can login with a link. this seems a little difficult because wed have to have our own domain to catch the response token in the      callback url

## Roadmap
Aiming for August or early September release date with all the features in the todo above. 

## Contributing
Fork this repo and make a pull request to suggest features and write code or documentation.   
