# Too Easy Travel
**@TravelIsTooEasyBot** - telegram bot that can help you find the best hotels from hotels.com
## Author
**@Alex_solokhin**
## Basic Description
The bot uses Hotels.com API to search hotels with users requests. Easy to use responsive interface makes the searching process smooth and easy. The bot communicates only Russian and use russian locale.

Next commands are supported:
- **/start** - sends welcome message
- **/hello-world** - also sends welcome message
- **/lowprice** - sends the list of the cheapest hotels that suit user's requests
- **/highprice** - sends the list of the most expensive hotels that suit user's requests
- **/bestdeal** - sends the list of hotels in desirable price range and distance to city center range
- **/history** - sends user's search history
- **/help** - sends info on the bot's commands

## Files
- **main.py** - used to establish connection with the bot and handle all the commands. Run this file in order to launch the bot
- **Dialog_handler.py** - contains the logic for /lowprice, /highprice and /bestdeal. Inside the Dialog class there is a chain of methods that ask user for info, check it, make a request to API and send messages with searching results
- **Hotel_API.py** - contains the logic for hotels.com API. The class HotelAPIHandler takes search parameters, using its methods make a request for API and return the response
- **db_manage.py** - contains functions to interact with database
- **keyboards.py** - contains functions for creating different types of keyboards

#### main.py
###### Function greetings
The function to greet the user. Executed with commands /start and /hello-world

    :param message: message object

###### Function start_searching
The function for commands /lowprice, /highprice, /bestdeal. Create and call an exemplar for Dialog class that start the searching process

    :param message: message object

###### Function help_command
The function for command /help: send the info on bot's commands

    :param message: message object

###### Function history_command
The function for command /history. Calls for database and provides user with history of his searches.

    :param message: message object

###### Function get_text_messages
Provides the bot with reaction for user's messages that are not the command.

    :param message: message object

#### Dialog_handler.py
###### Class Dialog
Basic class for dialogs. Contains the chain of methods to collect the data from user and handle the request's results.
Dialog starts with calling of classes exemplar

    Args:
        message (Message): message object
        max_hotel (int): max number of hotels that the bot can show. 10 by default
        max_photo (int): max number of photos per one hotel that the bot can show. 10 by default

###### Asking methods
The number of methods that bot uses to demand some information from user.Each method takes a number of arguments, send the message with some text and call register_next_step_handler with arguments that should be delivered to the next methods with a chain. There are the following methods:
- ask_location
- ask_dates
- ask_hotel_num
- ask_need_photo
- ask_photo_num
- ask_price_limit
- ask_dist_limit

        :param message: message object
        :param bot: bot object
        :param answers: dict with data that bot collected through the chain
        :param text: text that bot send to the user

###### Checking methods
The number of methods that bot uses to check the information from user. Firstly it checks if user writes "Прервать поиск". In this case bot cancels the search. 
Then it checks if the format of answers is correct. If it's not, methods call the appropriate asking method and asks user to send the correct answer (sometimes use **raise** in order to do it).
Finally, it saves the data to the **answers** dict, and call the next asking function with **answers** as an argument in order to deliver it through the chain.
There are the following methods:
- check_location
- check_dates
- check_hotel_num
- check_need_photo
- check_photo_num
- check_price_limit
- check_dist_limit

        :param message: message object
        :param bot: bot object
        :param answers: dict with data that bot collected through the chain

###### Method proceed_result
This method proceed **answers** dict, call HotelApiHandler and deliver the response from API through the chain.

        :param bot: bot object
        :param answers: dict with data that bot collected through the chain
        :param text: the text that informs user that search has been started

###### Method send result
This method transform the API response to the human-readable form and send it to user.

        :param hotels_returned: The dict with API response. Contain the data about hotels that suits search criterias
        :param bot: bot object
        :param answers: dict with data that bot collected through the chain

###### Method save_results
This method write some data from user and API response to database. It's necessary for /history command

        :param bot: bot object
        :param answers: dict with data that bot collected through the chain

###### Method stop_dialog
Check if user send "Поиск прерван". Return **True** if it's so.

        :param message: message object
        :param bot: bot object

        :return: True or None
        :rtype: bool or None

#### Hotel_API.py
###### Class HotelAPIHandler
Basic class for hotels.com API. Takes search details as arguments and contains method to proceed it.

    Args:
        check-in (datetime): check-in date
        check-out (datetime): check-out date
        result_limit (int): max number of hotel in response
        need_photo (int): does user need photos (0 - for no, 1 for yes)
        photo_limit (int): number of photo per each hotel in response
        min_price (str): min price per night
        max_price (str): max price per night
        sorting (str): sorting order (depends on command)
        min_dist (float): min dist from city center
        max_dist (float): max dist from city center
        adults (str): number of adult guests (1 by default)

###### Method find_location
This method takes the string from user and tries to find locations more suitable for user input. Return the dict with suitable locations IDs.

        :param location: location string that user send
        :return: locations_id
        :rtype: Dict

###### Method find_hotels
This method takes the dict with locations IDs and search for hotels in those locations that suits search criteria. Return the dict with data on requested hotels.

        :param location_ids: dict with locations IDs
        :return: hotels_dict
        :rtype: Dict
  
###### Method request_photo
This method returns the list of links for requested hotels.

        :param hotel_id: hotel's id
        :return: photos_links
        :rtype: List

#### db_manage.py
###### Function connect
Creates the connection with database

    :return: connection
    :rtype: Connection

###### Function update_line
Updates the line in database

    :param query: sql-request for desirable line
    :param field_value: sql-request parametrs (if any)
    
###### Function get_line
Returns the line from database that suits sql-request

    :param query: sql-request for desirable line
    :param field_value: sql-request parametrs (if any)
    :return: query_line
    :rtype: Tuple
    
###### Function get_all_lines
Returns all the lines from database that suits sql-request

    :param query: sql-request for desirable line
    :param field_value: sql-request parametrs (if any)
    :return: query_lines
    :rtype: List[Tuple]
    
###### Function create_db_request
Creates database for the bot. Since the database is already created, the function isn't used in application. It could be hidden/deleted or saved in order to recreate database in the future.

#### keyboards.py
###### Keyboards function
The number of functions that create keyboards of different configurations. There are following functions:
- simple_keyboard
- yes_no_keyboard
- one_to_ten_keyboard
- help_keyboard


    :return: keyboard