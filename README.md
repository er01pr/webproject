# JG Finance - A Stocks Trading Website
#### Video Demo: https://youtu.be/UpNCMnlZJ2I
#### Description:
This is the new and improved CS50 Finance Stock Trading website.
This project consist of new features like
- Ranking System. Here you can check your rank in comparison to all the users registered in the website. This feature compares your hold value, number of transactions, profit and loss. The user can choose how the rankings should be sorted.
- Change Password. This feature allows you to change your password.
- Add Cash. This feature allows you to add more cash to your portfolio.
- Flash messages. Instead of an annoying apology, flash messages will pops once you successfully or failed to do a task (buy,sell, or quote).
- Profit and Loss. This feature allows you to know if you gain or loss on a certain investment. You can also view your average Profit and Loss in your portfolio.
- Number of Transactions. This feature allows you to know how many trades have you done.
- Average Open. This feature allows you to know what's the average opening price of a stock in your portfolio. This is used to compute for your Profit and Loss.
- Register. This feature allows the user to register for an account. The user's passwords are encrypted or hashed for security purposes.

I used the API of IEX to get the stock's data. Those data are symbol, Company Name, Open Prices, Close Prices, latest Prices, and change Percent.

Here's the specification of the project from the CS50x Website.
#### Register
Complete the implementation of register in such a way that it allows a user to register for an account via a form.
- Require that a user input a username, implemented as a text field whose name is username. Render an apology if the user’s input is blank or the username already exists.
- Require that a user input a password, implemented as a text field whose name is password, and then that same password again, implemented as a text field whose name is confirmation. Render an apology if either input is blank or the passwords do not match
- Submit the user’s input via POST to /register.
- INSERT the new user into users, storing a hash of the user’s password, not the password itself. Hash the user’s password with generate_password_hash Odds are you’ll want to create a new template (e.g., register.html) that’s quite similar to login.html.

Once you’ve implemented register correctly, you should be able to register for an account and log in (since login and logout already work)! And you should be able to see your rows via phpLiteAdmin or sqlite3.

#### Quote
- Complete the implementation of quote in such a way that it allows a user to look up a stock’s current price.
- Require that a user input a stock’s symbol, implemented as a text field whose name is symbol.

#### Buy
- Complete the implementation of buy in such a way that it enables a user to buy stocks.
- Require that a user input a stock’s symbol, implemented as a text field whose name is symbol. Render an apology if the input is blank or the symbol does not exist (as per the return value of lookup).
- Require that a user input a number of shares, implemented as a text field whose name is shares. Render an apology if the input is not a positive integer.
- Render an apology, without completing a purchase, if the user cannot afford the number of shares at the current price.

#### Index
- Complete the implementation of index in such a way that it displays an HTML table summarizing, for the user currently logged in, which stocks the user owns, the numbers of shares owned, the current price of each stock, and the total value of each holding (i.e., shares times price). Also display the user’s current cash balance along with a grand total (i.e., stocks’ total value plus cash).

#### Sell
- Complete the implementation of sell in such a way that it enables a user to sell shares of a stock (that he or she owns).
- Require that a user input a stock’s symbol, implemented as a select menu whose name is symbol. Render an apology if the user fails to select a stock or if (somehow, once submitted) the user does not own any shares of that stock.
- Require that a user input a number of shares, implemented as a text field whose name is shares. Render an apology if the input is not a positive integer or if the user does not own that many shares of the stock.

#### history
- Complete the implementation of history in such a way that it displays an HTML table summarizing all of a user’s transactions ever, listing row by row each and every buy and every sell.
- For each row, make clear whether a stock was bought or sold and include the stock’s symbol, the (purchase or sale) price, the number of shares bought or sold, and the date and time at which the transaction occurred.

#### Personal Touch
- For personal touch I added
- Change Password
- Add Cash
- Rankings
- Profit and Loss
- Number of Transactions


That's it! It's a simple web application that lets you quote, buy and sell stocks! Thank you for reading!