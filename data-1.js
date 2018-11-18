$(document).ready(function(){
    
	// Define variables that reference our script tags within the body of our page
	var topNavigation = $("#topNavigation").html();
    var sideNavigation = $("#sideNavigation").html();
    
	// Have MustacheJS render our script tags
	Mustache.parse(topNavigation);
	Mustache.parse(sideNavigation);
	
	// Define our data objects
	var topNav = Mustache.render(topNavigation, {
        item:
		[
            {
             //   name: "Home",
             //   link: "./home.html"
            },
            {
             //   name: "Traveling WOD",
             //   link: "./traveling.html"
            },
            {
             //   name: "Office WOD",
             //   link: "./office.html"
            },
            {
               name: "Current Workout",
               link: "./journal.html"
            },
			{
                //name: "Login",
                //link: "./login.html"
            },
            {
                name: "Register",
                link: "./signup.html"
            },
		]
    });
	
	var sideNav = Mustache.render(sideNavigation, {
        item:
		[
			{
                name: "LinkedIN",
                link: "#",
				image:"./images/In-2C-115px-R.png",
				altTag:"LinkedIN"
            },
            {
                name: "Facebook",
                link: "#",
				image:"./images/Like-Button_EN_RGB_114.png",
				altTag:"Facebook"
            },
            {
                name: "Instagram",
                link: "#",
				image:"./images/glyph-logo_May2016.png",
				altTag:"Instagram"
            },
			 {
                name: "Contact Us",
                link: "#",
				image:"./images/Small_Logo.jpg",
				altTag:"Contact Us"
            }
		]
    });
	
	// Place data into the HTML of our page with the html() jQuery method
	$("#render_topLinks").html(topNav);
	$("#render_sideLinks").html(sideNav);
	
	// Insert current year into the Copyright text in the footer.  Note: MustacheJS is not needed to do this.
	$("#currentYear").html(new Date().getFullYear());
	

$( function() {
    $( "#datepicker" ).datepicker();
  } );
});  