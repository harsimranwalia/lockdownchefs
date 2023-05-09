telegram_content = {

}

email_content = {
    "food_option":{
        "subject": "Today's breakfast recipe for {0} is here",
        "body_html": """<html>
                        <head></head>
                        <body>
                        <p>Good Morning!</p>
                        <p>Here comes your dose of breakfast goodness.</p>
                        <h2>{0}</h2>
                        <img src='{1}' style='text-align: left; min-width: 50px; max-width: 300px;'><br>
                        <a href='{2}'>View Recipe</a>
                        <p>Happy eating :)</p>
                        </body>
                        </html>
                    """
    }
}